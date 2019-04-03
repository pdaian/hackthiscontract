# Hack this Contract Website

## What is this

This is the code that runs the hackthiscontract.io website.

## Running it

1. `geth --rinkeby (starts ethereum node on the rinkeby test network)`
2. `source hackthiscontractenv/bin/activate (starts virtualenv)`
3. In dev: `python3 run.py` - In prod: `waitress-serve run:app`
4. `geth --rinkeby --rpc --rpccorsdomain "https://remix.ethereum.org"` (start JS console and enable remix debugging)

## Dependencies
* python3 + pip
* virtualenv

## Installation
1. `pip3 install -r requirements.txt`
2. Change the paths in `config.py` to match your system.

## Directory Structure

* `challenges` - Contains the solidity files, abis, and graders for each challenge.
* `static` - Website assets. CSS, images, etc.
* `templates` - Flask Jinja2 templates for some of the pages on hackthiscontract.
* `tests` - Unit tests.

## Nginx Config

Proxy Pass notes:

```
    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to displaying a 404.
        proxy_set_header        Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host:$server_port;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_pass http://127.0.0.1:8080;
}
```

