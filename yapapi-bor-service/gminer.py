#!/usr/bin/env python3
import argparse
import asyncio
import contextlib
import decimal
import random
import sys
from asyncio import TimeoutError
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, Dict

import requests
import ya_payment
import yapapi.rest.payment
from rich.console import Console
from rich.table import Table
from yapapi.log import enable_default_logger
from yapapi.rest import Configuration, payment
from yapapi.rest.activity import PollingBatch, Activity
from ctx import *
from discovery import find_workers
from glmminingestimator import MiningEstimator
from decimal import Decimal
from common import set_yagna_app_key_to_env
import logging

async def extract_provider_name(agr: yapapi.rest.market.Agreement) -> Optional[str]:
    agreement_details = await agr.get_details()
    return agreement_details.provider_view.properties.get("golem.node.id.name") or "-"


async def pay_invoices(console: Console, ctx: GolemCtx, allocation: payment.Allocation):
    payment_api = await ctx.payment()
    issuers = set()
    invoices_received: Dict[str, Decimal] = dict()
    invoices_settled: Dict[str, Decimal] = dict()

    async for invoice in payment_api.invoices():
        issuers.add(invoice.issuer_id)
        if invoice.status == "RECEIVED":
            invoices_received[invoice.issuer_id] = invoices_received.get(
                invoice.issuer_id, 0
            ) + Decimal(invoice.amount)
        elif invoice.status == "SETTLED":
            invoices_settled[invoice.issuer_id] = invoices_settled.get(
                invoice.issuer_id, 0
            ) + Decimal(invoice.amount)

        if invoice.status == "RECEIVED" and decimal.Decimal(invoice.amount) < 1.5:
            with contextlib.suppress(Exception):
                await invoice.accept(amount=invoice.amount, allocation=allocation)

    table = Table("Issuer", "Received", "Settled")
    for issuer in issuers:
        table.add_row(issuer, str(invoices_received.get(issuer)), str(invoices_settled.get(issuer)))
    console.print(table)


def get_requestor_id(conf: Configuration) -> str:
    me = requests.get(
        "http://127.0.0.1:7465/me", headers={"authorization": f"Bearer {conf.app_key}"}
    ).json()
    return me["identity"]


async def send_offer(
    console: Console,
    activity: Activity,
    exp: datetime,
    pool: str,
    wallet: str,
    worker_name: str,
    pool_password: Optional[str],
):
    try:
        console.print("try to send", worker_name)
        await try_send_offer(console, activity, exp, pool, wallet, worker_name, pool_password)
    except Exception as e:
        print(f"Failed to execute on ${worker_name}")
        console.print(e)


async def try_send_offer(
    console: Console,
    activity: Activity,
    exp: datetime,
    pool: str,
    wallet: str,
    worker_name: str,
    pool_password: Optional[str],
):
    args = []
    if pool_password is not None:
        args.extend(["--password", pool_password])

    _cmds = [
        {"deploy": {}},
        {"start": {}},
    #    {"run": {"entry_point": "dupa", "args": ["user", "add", "u1", "pass1"]}},
    ]
    result: PollingBatch = await activity.send(_cmds)
    console.log(f"batch {activity.id} started, expires at {exp.astimezone()}")
    async for step in result:
        console.log(f"batch {activity.id}", step)

    while datetime.now(timezone.utc) < exp:
        console.log(f"batch {activity.id} expires at {exp.astimezone()}")
        await asyncio.sleep(60)

    console.log(f"batch {activity.id}: terminating")

    tres = await activity.send([{"terminate": {}}])
    async for step in tres:
        print("step=", step)


async def run_proxy(
    conf: Configuration,
    subnet_tag: str,
    pool: str,
    wallet: str,
    pool_password: str,
    timeout: int,
    payment_platform: str,
    exeunit_name: str,
    amount: Decimal = Decimal(10),
):
    console = Console()
    requestor_id = get_requestor_id(conf)
    console.log(f"Starting proxy: platform={payment_platform}")
    ctx = GolemCtx(conf)

    agreements = set()

    async with ctx:
        payment_api = await ctx.payment()
        console.log("[payment] cleaning old allocations")
        async for allocation in payment_api.allocations():
            console.log(f"[payment] deleting allocation {allocation.id} for {allocation.amount}")
            await allocation.delete()

        console.log("platform=", payment_platform)
        async with payment_api.new_allocation(
            amount=amount, payment_platform=payment_platform, payment_address=requestor_id
        ) as allocation:
            await pay_invoices(console, ctx, allocation)

            async def log_invoices():
                try:
                    console.log("waiting for invoices")
                    async for invoice in payment_api.incoming_invoices():
                        console.print("new invoice", invoice.to_dict())
                        try:
                            await invoice.accept(
                                amount=invoice.amount, allocation=criteria.allocation
                            )
                        except ya_payment.ApiException as e:
                            console.log("failed to accept invoice", e)
                except ya_payment.ApiException as e:
                    console.log("failed to gen invoices", e)

            async def log_debit_notes():
                try:
                    console.log("waiting for debit notes")
                    async for debit_note in payment_api.incoming_debit_notes():
                        console.log("new debit note", debit_note.to_dict())
                        try:
                            if debit_note.agreement_id in agreements:
                                await debit_note.accept(
                                    amount=debit_note.total_amount_due,
                                    allocation=criteria.allocation,
                                )
                            else:
                                console.log("invalid debit note")
                        except ya_payment.ApiException as e:
                            console.log("failed to accept debit note", e)
                except ya_payment.ApiException as e:
                    console.log("failed to get debit notes", e)

            services = set()

            services.add(asyncio.create_task(log_invoices()))
            services.add(asyncio.create_task(log_debit_notes()))

            jobs = set()

            criteria = SearchCriteria(
                name="bor+",
                allocation=allocation,
                subnet=subnet_tag,
                chunk_time=timedelta(minutes=timeout),
            )

            while len(services) >= 2:
                await asyncio.sleep(random.randint(5, 45))

                try:
                    async for activity, provider_id, expiration, agr in find_workers(
                        ctx, criteria, payment_platform, exeunit_name
                    ):
                        worker_name = f"{requestor_id}/{await extract_provider_name(agr)}:{provider_id}/{activity.id}"
                        agreements.add(agr.id)
                        jobs.add(
                            asyncio.create_task(
                                send_offer(
                                    console,
                                    activity,
                                    expiration,
                                    pool,
                                    wallet,
                                    worker_name,
                                    pool_password,
                                )
                            )
                        )
                        logging.info("worker=", worker_name)
                        f_done, f_pending = await asyncio.wait(
                            services.union(jobs), timeout=0.1, return_when=asyncio.FIRST_COMPLETED
                        )
                        if len(f_done) > 1:
                            logging.info("done=", len(f_done))

                        services.difference_update(f_done)
                        jobs.difference_update(f_done)
                        if len(services) != 2:
                            logging.info("service failed, exiting")
                            break
                except asyncio.exceptions.CancelledError:
                    print(f"!!! Cancel !!! services={len(services)}, jobs={len(jobs)}")
                    pass


def build_parser(description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--driver", help="Payment driver name, for example `erc20`", default="erc20"
    )
    parser.add_argument("--network", help="Network name, for example `goerli`", default="rinkeby")
    parser.add_argument("--pool", default="staging-backend.chessongolem.app:3334")
    parser.add_argument("--wallet", default="0x5bc945a05ac36700f808f4d03e192f3b0d7eeb6d")
    parser.add_argument("--timeout", default=30, help="mining timeout in minutes", type=int)
    parser.add_argument("--pool-password", default="x")
    parser.add_argument(
        "--subnet-tag", default="scx_vm_subnet", help="Subnet name; default: %(default)s"
    )
    parser.add_argument(
        "--exe-unit", default="gminer", help="gminer for ETH, hminer for ETC default: %(default)s"
    )
    parser.add_argument(
        "--log-file", default=None, help="Log file for YAPAPI; default: %(default)s"
    )
    return parser


def main():
    parser = build_parser("gmine")
    args = parser.parse_args()

    subnet = args.subnet_tag
    sys.stderr.write(f"Using subnet: {subnet}\n")

    exe_unit = args.exe_unit
    sys.stderr.write(f"Using exe unit: {exe_unit}\n")

    # Use automatic app key extraction for convenience
    set_yagna_app_key_to_env("yagna");

    if args.network == "mumbai":
        payment_platform = "erc20-mumbai-tglm"
    elif args.network == "polygon":
        payment_platform = "erc20-polygon-glm"
    elif args.network == "rinkeby":
        payment_platform = "erc20-rinkeby-tglm"
    else:
        raise Exception("unsupported network")

    #logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    enable_default_logger()
    try:
        asyncio.run(
            run_proxy(
                Configuration(),
                subnet_tag=subnet,
                pool=args.pool,
                wallet=args.wallet,
                pool_password=args.pool_password,
                timeout=args.timeout,
                payment_platform=payment_platform,
                exeunit_name=exe_unit,
                amount=Decimal(50),
            )
        )
    except asyncio.exceptions.CancelledError:
        print('!!! Cancel !!!')
        pass
    except TimeoutError:
        print('!!! Timeout !!!')
        pass


if __name__ == "__main__":
    main()
