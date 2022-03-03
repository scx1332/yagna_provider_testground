To run this example you need poetry installed.

https://python-poetry.org/docs/basic-usage/

Run to install dependencies (especially yapapi)

```
poetry install
```

Check if you have assets on your requestor account using:
```
yagna payment status
```

If not run
```
yagna payment fund
```

It should get you GLMs and ETH from faucet. If faucet fails, you have to tranfer tokens to your test account manually.

```
poetry run python volume_benchmark.py
```
or depending on your system configuration
```
poetry run python3 volume_benchmark.py
```











