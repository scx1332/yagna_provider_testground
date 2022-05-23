#!/usr/bin/env python3
import asyncio
from typing import AsyncIterable
import os
from yapapi import Golem, Task, WorkContext
from yapapi.log import enable_default_logger
from yapapi.payload import vm
import pathlib
import subprocess
import json
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from datetime import datetime

from common.common import open_config, set_yagna_app_key_to_env
from yapapi import events
from yapapi.rest.activity import CommandExecutionError

from yapapi import (
    Golem,
    windows_event_loop_fix,
    NoPaymentAccountError,
    __version__ as yapapi_version,
)

config = open_config()

SUBNET_NAME = config["subnet"]

GSB_PORT = config["requestor_port_gsb"]
API_PORT = config["requestor_port_yagna"]

os.environ["GSB_URL"] = f"tcp://127.0.0.1:{GSB_PORT}"
os.environ["YAGNA_API_URL"] = f"http://127.0.0.1:{API_PORT}"
#os.environ["YAGNA_MARKET_URL"] = f"http://127.0.0.1:{API_PORT}/market-api/v1/"
#os.environ["YAGNA_ACTIVITY_URL"] = f"http://127.0.0.1:{API_PORT}/activity-api/v1/"
#os.environ["YAGNA_PAYMENT_URL"] = f"http://127.0.0.1:{API_PORT}/payment-api/v1/"

agreements = {}

def print_env_info(golem: Golem):
    print(
        f"yapapi version: {yapapi_version}\n"
        f"Using subnet: {golem.subnet_tag}, "
        f"payment driver: {golem.payment_driver}, "
        f"and network: {golem.payment_network}\n"
    )



async def worker(ctx: WorkContext, tasks: AsyncIterable[Task]):
    script_dir = pathlib.Path(__file__).resolve().parent
    scene_path = str(script_dir / "vol_test_sent_to_provider.py")

    print(scene_path)

    async for task in tasks:
        script = ctx.new_script()
        script.upload_file(scene_path, "/golem/input/vol_test.py")
        folder = "/golem/output"
        bigfilesize = 10000
        repetitions = 10
        future_result = script.run("/usr/local/bin/python", "/golem/input/vol_test.py", "--folder", folder, "--bigfilesize", str(bigfilesize), "--repetitions", str(repetitions))

        yield script

        task.accept_result(result=await future_result)

def submit_status_subtask(provider_name, provider_id, task_data, status, time=None):
    url = 'http://api:8002/v1/status/subtask/blender'
    task_id = os.getenv('TASKID')
    if time:
        post_data = {'id': task_id, 'status': status, 'provider': provider_name,
                     'provider_id': provider_id, 'task_data': task_data, 'time': time}
    else:
        post_data = {'id': task_id, 'status': status,
                     'provider': provider_name, 'provider_id': provider_id, 'task_data': task_data, }

    #requests.post(url, data=post_data)


def submit_status(status, total_time=None):
    url = 'http://api:8002/v1/status/task/blender'
    task_id = os.getenv('TASKID')
    if total_time:
        post_data = {'id': task_id, 'status': status,
                     'time_spent': total_time}
    else:
        post_data = {'id': task_id, 'status': status, }
    #requests.post(url, data=post_data)


provider_node = ""
invoice_id = ""
start_time = datetime.now()

def event_consumer(event):
    if isinstance(event, events.AgreementCreated):
        agreements[event.agr_id] = [
            event.provider_id, event.provider_info.name]
        global provider_node
        provider_node = event.provider_info.name
        print(f"Got agreement with: {event.provider_info.name}")
    elif isinstance(event, events.InvoiceReceived):
        print(f"Got invoice: {event.inv_id}")
        global invoice_id
        invoice_id = event.inv_id
    elif isinstance(event, events.TaskStarted):
        agreements[event.task_data] = datetime.now()
        submit_status_subtask(
            provider_name=agreements[event.agr_id][1], provider_id=agreements[event.agr_id][0], task_data=event.task_data, status="Computing")
    elif isinstance(event, events.TaskFinished):
        time_spent = datetime.now() - agreements[int(event.task_id)]
        submit_status_subtask(
            provider_name=agreements[event.agr_id][1], provider_id=agreements[event.agr_id][0], task_data=int(event.task_id), status="Finished", time=time_spent)
    elif isinstance(event, events.WorkerFinished):
        exc = event.exc_info
        reason = str(exc) or repr(exc) or "unexpected error"
        if isinstance(exc, CommandExecutionError):
            submit_status_subtask(
                provider_name=agreements[event.agr_id][1], provider_id=agreements[event.agr_id][0], task_data=event.job_id, status="Failed")
    elif isinstance(event, events.ComputationFinished):
        if not event.exc_info:
            submit_status(status="Finished", total_time={
                datetime.now() - start_time})
        else:
            _exc_type, exc, _tb = event.exc_info
            if isinstance(exc, CancelledError):
                submit_status(status="Cancelled", total_time={
                    datetime.now() - start_time})
            else:
                submit_status(status="Failed", total_time={
                    datetime.now() - start_time})

async def main():
    package = await vm.repo(
        image_hash="1c76cf0cf3961709e7082b1cb9ae93d952e88ccbb5f42c01cc896cd0",
        image_url="http://52.17.188.4:8000/docker-vol_test-latest-6a534a2c87.gvmi"
    )

    tasks = [Task(data=None)]

    async with Golem(budget=1.0,
                     subnet_tag=SUBNET_NAME,
                     payment_network="rinkeby",
                     event_consumer=event_consumer) as golem:
        print_env_info(golem)
        async for completed in golem.execute_tasks(worker, tasks, payload=package):
            print(completed.result.stdout)


if __name__ == "__main__":
    enable_default_logger(log_file="hello.log")

    yagna_exe = os.path.join("..", "runtime_requestor", "yagna")

    set_yagna_app_key_to_env(yagna_exe)

    payment_init_command = f"{yagna_exe} payment init --sender"
    print(f"Running command: {payment_init_command}")
    payment_init = subprocess.Popen(payment_init_command, shell=True)
    payment_init.communicate()
    print(f"Initialization finished. Running main loop...")

    loop = asyncio.new_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)

    job_descriptor = {}
    job_descriptor["job_name"] = "volume_benchmark"
    job_descriptor["job_quantity"] = 1.0
    job_descriptor["job_time"] = (datetime.now() - start_time).total_seconds()


    print(f"Finished: provider node: {provider_node}, invoice id: {invoice_id}")
    print(json.dumps(job_descriptor))
