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
from common.common import open_config, get_or_create_yagna_key

config = open_config()

SUBNET_NAME = config["subnet"]


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


async def main():
    package = await vm.repo(
        image_hash="1c76cf0cf3961709e7082b1cb9ae93d952e88ccbb5f42c01cc896cd0",
        image_url="http://52.17.188.4:8000/docker-vol_test-latest-6a534a2c87.gvmi"
    )

    tasks = [Task(data=None)]

    async with Golem(budget=1.0,
                     subnet_tag=SUBNET_NAME,
                     payment_network="rinkeby") as golem:
        async for completed in golem.execute_tasks(worker, tasks, payload=package):
            print(completed.result.stdout)


if __name__ == "__main__":
    enable_default_logger(log_file="hello.log")

    yagna_exe = "yagna"

    get_or_create_yagna_key(yagna_exe)

    payment_init_command = f"{yagna_exe} payment init --sender --network rinkeby"
    print(f"Running command: {payment_init_command}")
    payment_init = subprocess.Popen(payment_init_command, shell=True)
    payment_init.communicate()
    print(f"Initialization finished. Running main loop...")

    loop = asyncio.new_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
