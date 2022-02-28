#!/usr/bin/env python3
import asyncio
from typing import AsyncIterable
import os
from yapapi import Golem, Task, WorkContext
from yapapi.log import enable_default_logger
from yapapi.payload import vm
import pathlib

async def worker(ctx: WorkContext, tasks: AsyncIterable[Task]):
    script_dir = pathlib.Path(__file__).resolve().parent
    scene_path = str(script_dir / "vol_test.py")

    print(scene_path)

    async for task in tasks:
        script = ctx.new_script()
        script.upload_file(scene_path, "/golem/input/script.py")
        folder = "/golem/output"
        bigfilesize = 1000000000
        repetitions = 10



        future_result = script.run("/usr/local/bin/python", "/golem/input/script.py", "--folder", folder, "--bigfilesize", str(bigfilesize), "--repetitions", str(repetitions))

        yield script

        task.accept_result(result=await future_result)


async def main():
    package = await vm.repo(
        image_hash="1c76cf0cf3961709e7082b1cb9ae93d952e88ccbb5f42c01cc896cd0",
        image_url="http://52.17.188.4:8000/docker-vol_test-latest-6a534a2c87.gvmi"
    )

    tasks = [Task(data=None)]

    async with Golem(budget=1.0,
                     #subnet_tag="scx_vm_subnet",
                     subnet_tag="testnet",
                     payment_network="rinkeby") as golem:
        async for completed in golem.execute_tasks(worker, tasks, payload=package):
            print(completed.result.stdout)


if __name__ == "__main__":
    enable_default_logger(log_file="hello.log")

    loop = asyncio.new_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
