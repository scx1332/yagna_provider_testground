To run this example you need poetry installed.

https://python-poetry.org/docs/basic-usage/

Run to install dependencies (especially yapapi)

```
poetry install
```

Check if you have money on your requestor account
```
yagna payment status
```

If not run
```
yagna payment fund
```

It should get you GLMs and ETH from faucet.

```
poetry run python volume_benchmark.py
```
or depending on your system configuration
```
poetry run python3 volume_benchmark.py
```











