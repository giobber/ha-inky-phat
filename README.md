# ha-inky-phat

## To install
```shell
$ sudo apt install python3-venv python3-dev
$ git clone git@github.com:giobber/ha-inky-phat.git
$ cd ha-inky-phat
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv)$ pip install -r requirements.in
(.venv)$ pip install -r requirements.dev.in 
```

## To run
```shell
$ source .venv/bin/activate
(.venv)$ ./main.py
or
(.venv)$ python main.py
```

## Cronjob
To refresh automatically
```shell
$ crontab -e
```
then add the rule
```cron
* * * * * <path-to-project>/.venv/bin/python <path-to-project>/main.py update
```
