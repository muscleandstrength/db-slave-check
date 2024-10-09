# DB Slave Check

This script runs checks against a slave database to ensure slave io and sql
are running. Sends an email alert via sendgrid's mail API if either are down.

A Sqlite database tracks notifications and will cause the script to
incrementally back off to avoid an avalanche of notifications.

## Installation
Install and activate the python virtual environment
```$ python3 -m venv venv```
```$ source venv/bin/activate```

Install dependencies
Check slave depends on
- mysql-connector-python 
- sendgrid 
- python-dotenv

For simplicity, they can be installed via the requirements.txt manifest

```$ pip install -r requirements.txt```                              

## Configuration
Configuration is performed via the environment, either provide values in .env (there is a skeleton example in .env.dist)
or pass them through shell exports or when invoking ```checkslave.py``` (or its wrapper ```run_check.sh```).

Available configuration values:
- MYSQL_SLAVE_HOST
- MYSQL_SLAVE_PORT
- MYSQL_SLAVE_USER
- MYSQL_SLAVE_PASSWORD
- SENDGRID_API_KEY
- FROM_EMAIL
- TO_EMAIL

## Running
Either run ```python checkslave.py``` directly or its wrapper ```run_check.sh```

The script is intended for use in a crontab task that runs every minute i.e.

```* * * * * /path/to/run_check.sh```
