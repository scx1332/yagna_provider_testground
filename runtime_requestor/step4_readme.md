##Step 4

Add this directory to the PATH, so you can run yagna from anywhere on your system.

for example on linux add to .bashrc:

```
export PATH="$HOME/golem/yagna_provider_testground/requestor_run_config:$PATH"
```

On windows you can edit environment setting for your account.

On linux check yagna location

```
which yagna
```

On Windows:

```
where yagna.exe
```

If you successfully go through the steps 0-4 you can go to ../yapapi-volumes-benchmark to test requestor.

Before running the requestor make sure you have requestor and provider running.
