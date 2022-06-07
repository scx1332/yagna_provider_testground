import asyncio
from typing import AsyncGenerator, Tuple

import async_timeout, ya_market
from rich.pretty import pprint
from yapapi.props.builder import DemandBuilder
from yapapi.props.inf import ExeUnitRequest
from yapapi.rest import market, activity
from datetime import datetime, timezone
from rich.console import Console
from yapapi import props as yp
from .ctx import *
from .display import print_offer, print_invoice
from .glmminingestimator import MiningEstimator

_FAKE_REQUEST = ExeUnitRequest(
    package_url="hash:sha3:9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae:http://yacn2.dev.golem.network:8000/local-image-c76719083b.gvmi"
)


async def find_workers(
    ctx: GolemCtx, criteria: SearchCriteria, payment_platform: str, exe_unit_name: str
) -> AsyncGenerator[Tuple[activity.Activity, str, datetime, market.Agreement], None]:

    console = Console()
    payment_api = await ctx.payment()
    market_api = await ctx.market()
    activity_api = await ctx.activity()

    async def _find():
        expiration = datetime.now(timezone.utc) + criteria.chunk_time
        builder = DemandBuilder()
        builder.add(yp.NodeInfo(name=criteria.name, subnet_tag=criteria.subnet))
        builder.add(yp.Activity(expiration=expiration))
        builder.add(_FAKE_REQUEST)
        builder.ensure("(golem.runtime.name={})".format(exe_unit_name))
        decoration = await payment_api.decorate_demand([criteria.allocation.id])
        for constraint in decoration.constraints:
            builder.ensure(constraint)

        retry_map = set()
        reject_map = set()
        builder.properties.update({p.key: p.value for p in decoration.properties})
        async with market_api.subscribe(builder.properties, builder.constraints) as subscription:
            async for event in subscription.events():
                if event.is_draft:
                    agr = await event.create_agreement()
                    try:
                        det = await agr.details()
                        if await agr.confirm():
                            new_activity = await activity_api.new_activity(agr.id)
                            print_offer(console, event, det)
                            if event.issuer in retry_map:
                                reject_map.add(event.issuer)
                            retry_map.add(event.issuer)
                            yield new_activity, event.issuer, (
                                expiration - criteria.close_time
                            ), agr
                    except Exception as e:
                        print("fatal=", e)
                    finally:
                        pass
                else:
                    try:
                        usage_vector = event.props.get("golem.com.usage.vector")
                        linear_coeffs = event.props.get("golem.com.pricing.model.linear.coeffs")
                        if len(usage_vector) + 1 != len(linear_coeffs):
                            raise Exception("usage_vector.len() + 1 != linear_coeffs.len()")

                        changed_pricing = False
                        for idx in range(0, len(linear_coeffs)):
                            if idx < len(linear_coeffs) - 1:
                                coeff_name = usage_vector[idx]
                            else:
                                coeff_name = "starting_price"

                            src_coeff_value = linear_coeffs[idx]
                            if coeff_name == "golem.usage.mining.hash":
                                if exe_unit_name == "hminer":
                                    target_coeff_value = ctx.miningEstimator().get_cached_glm_etc_hash()
                                else:
                                    target_coeff_value = ctx.miningEstimator().get_cached_glm_eth_hash()
                            else:
                                target_coeff_value = 0
                            if src_coeff_value != target_coeff_value:
                                print(
                                    "Negotiating prices in usage vector: field: {} old value: {} new value: {}".format(
                                        coeff_name, src_coeff_value, target_coeff_value
                                    )
                                )
                                linear_coeffs[idx] = target_coeff_value
                                changed_pricing = True

                        offer_timeout = event.props.get(
                            "golem.com.payment.debit-notes.accept-timeout?"
                        )
                        demand_props = dict(**builder.properties)
                        if changed_pricing:
                            demand_props["golem.com.pricing.model.linear.coeffs"] = linear_coeffs
                        if offer_timeout:
                            demand_props["golem.com.payment.debit-notes.accept-timeout?"] = min(
                                offer_timeout, 120
                            )
                        demand_props[
                            "golem.com.payment.chosen-platform"
                        ] = payment_platform  # "polygon-polygon-glm"

                        if event.issuer in reject_map:
                            print("rejected ", event)
                            await event.reject("restarts too offen")
                        else:
                            result = await event.respond(demand_props, builder.constraints)
                            console.print(f"Counter offer from {event.issuer}")
                            pprint(event.props, console=console)
                        # for key, val in event.props.items():
                        #    console.print(f"{key}={json.dumps(val)}")
                    except ya_market.ApiException as e:
                        print(f"Skip offer {event.id} from {event.issuer}\n", e.body)
                    except Exception as e:
                        print("skip error", e.__class__.__name__, e)
                        pass

    while True:
        try:
            console.log("scan")
            async with async_timeout.timeout(criteria.scan_time.total_seconds()):
                async for _activity, _provider_id, _expiration, _agreement in _find():
                    yield _activity, _provider_id, _expiration, _agreement
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
        except Exception as e:
            console.log(e.__class__.__name__)
            console.log(e)
            await asyncio.sleep(10)
