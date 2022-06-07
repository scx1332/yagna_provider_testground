from dataclasses import dataclass
from datetime import timedelta, timezone
from contextlib import AbstractAsyncContextManager, AsyncExitStack
from types import TracebackType
from typing import Awaitable, Optional, Type

from yapapi.rest import payment, market, activity, Configuration
from .glmminingestimator import MiningEstimator


@dataclass
class SearchCriteria:
    name: str
    allocation: payment.Allocation
    subnet: Optional[str] = None
    scan_time: timedelta = timedelta(minutes=2)
    close_time: timedelta = timedelta(minutes=1)
    chunk_time: timedelta = timedelta(minutes=30)


class GolemCtx(AbstractAsyncContextManager):
    def __init__(self, conf: Configuration, mining_estimator: MiningEstimator):
        self._conf = conf
        self._exit_stack = AsyncExitStack()
        self._payment: Optional[payment.Payment] = None
        self._market: Optional[market.Market] = None
        self._activity: Optional[activity.ActivityService] = None
        self._mining_estimator = mining_estimator

    def miningEstimator(self):
        return self._mining_estimator

    async def payment(self) -> payment.Payment:
        if self._payment is None:
            payment_client = await self._exit_stack.enter_async_context(self._conf.payment())
            self._payment = payment.Payment(payment_client)
        return self._payment

    async def market(self) -> market.Market:
        if self._market is None:
            market_client = await self._exit_stack.enter_async_context(self._conf.market())
            self._market = market.Market(market_client)
        return self._market

    async def activity(self) -> activity.ActivityService:
        if self._activity is None:
            activity_client = await self._exit_stack.enter_async_context(self._conf.activity())
            self._activity = activity.ActivityService(activity_client)
        return self._activity

    async def __aenter__(self) -> AsyncExitStack:
        return await self._exit_stack.__aenter__()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        return await self._exit_stack.__aexit__(exc_type, exc_value, traceback)


__all__ = ["GolemCtx", "SearchCriteria"]
