import aiohttp
import json
import asyncio

UPDATE_EVERY_SECONDS_SUCCESS = 1800
UPDATE_EVERY_SECONDS_FAIL = 300
DEFAULT_PRICE_ETH = 0.00141
DEFAULT_PRICE_ETC = 0.00081


class MiningEstimator:
    def __init__(self):
        self._cached_glm_eth = None
        self._cached_glm_etc = None

    def get_cached_glm_eth_hash(self):
        if self._cached_glm_eth:
            return self._cached_glm_eth * 1000
        else:
            return DEFAULT_PRICE_ETH

    def get_cached_glm_etc_hash(self):
        if self._cached_glm_etc:
            return self._cached_glm_etc * 1000
        else:
            return DEFAULT_PRICE_ETC

    async def get_usd_earnings_per_sec_per_mh(self, coin):
        megahashes = 1000
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.nanopool.org/v1/{0}/approximated_earnings/{1}".format(coin, megahashes)
            ) as response:
                t = await response.text()
                mainjson = json.loads(t)
                double_res = mainjson["data"]["day"]["dollars"]
                return double_res / 24 / 3600 / megahashes

    async def get_glm_price_in_usd(self):
        contract_address = "0x7DD9c5Cba05E151C895FDe1CF355C9A1D5DA6429"
        base_currency = "usd"
        chain = "ethereum"
        url = "https://api.coingecko.com/api/v3/simple/token_price/{0}?contract_addresses={1}&vs_currencies={2}".format(
            chain, contract_address, base_currency
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                t = await response.text()
                mainjson = json.loads(t)
                return mainjson[contract_address.lower()][base_currency]

    async def get_glm_per_mh_per_sec(self, coin, verbose=True):
        usd_per_sec_per_mh = await self.get_usd_earnings_per_sec_per_mh(coin)

        if verbose:
            print(
                "Typical earnings on 50MH/s card: {0:.3f} USD/day".format(
                    usd_per_sec_per_mh * 3600 * 24 * 50
                )
            )

        glm_price_in_usd = await self.get_glm_price_in_usd()

        if verbose:
            print("Golem price: {0:.3f} USD".format(glm_price_in_usd))

        if glm_price_in_usd > 0.0000001:
            glm_per_sec_per_mh = usd_per_sec_per_mh / glm_price_in_usd
        else:
            raise Exception("Invalid golem price")

        return glm_per_sec_per_mh

    async def update_price_main_loop(self):
        while True:
            succeeded = False
            try:
                result1 = await self.get_glm_per_mh_per_sec("eth", False)
                result2 = await self.get_glm_per_mh_per_sec("etc", False)
                if result1 > 0:
                    self._cached_glm_eth = result1
                if result2 > 0:
                    self._cached_glm_etc = result2

                print("get_glm_per_mh_per_sec eth returned {}".format(result1))
                print("get_glm_per_mh_per_sec etc returned {}".format(result2))
                succeeded = True
            except Exception as ex:
                print("Error when downloading current price: {}".format(ex))
                succeeded = False

            if succeeded:
                print("Waiting after success: {}s.".format(UPDATE_EVERY_SECONDS_SUCCESS))
                await asyncio.sleep(UPDATE_EVERY_SECONDS_SUCCESS)
            else:
                print("Waiting after failure: {}s.".format(UPDATE_EVERY_SECONDS_FAIL))
                await asyncio.sleep(UPDATE_EVERY_SECONDS_FAIL)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    me = MiningEstimator()
    loop.run_until_complete(me.update_price_main_loop())
