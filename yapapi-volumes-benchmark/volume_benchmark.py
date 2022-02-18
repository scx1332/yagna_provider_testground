#!/usr/bin/env python3
import asyncio
from typing import AsyncIterable

from yapapi import Golem, Task, WorkContext
from yapapi.log import enable_default_logger
from yapapi.payload import vm


async def worker(context: WorkContext, tasks: AsyncIterable[Task]):
    async for task in tasks:
        script = context.new_script()
        folder = "/golem/output"
        bigfilesize = 10000
        repetitions = 10


        future_result = script.run("/usr/local/bin/python", "vol_test.py", "--folder", folder, "--bigfilesize", str(bigfilesize), "--repetitions", str(repetitions))

        yield script

        task.accept_result(result=await future_result)


async def main():
    package = await vm.repo(
        image_hash="1c76cf0cf3961709e7082b1cb9ae93d952e88ccbb5f42c01cc896cd0",
        image_url="http://52.17.188.4:8000/docker-vol_test-latest-6a534a2c87.gvmi"
    )

    tasks = [Task(data=None)]

    async with Golem(budget=1.0,
                     subnet_tag="scx_vm_subnet",
                     #subnet_tag="testnet",
                     payment_network="rinkeby") as golem:
        async for completed in golem.execute_tasks(worker, tasks, payload=package):
            print(completed.result.stdout)


if __name__ == "__main__":
    enable_default_logger(log_file="hello.log")

    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
