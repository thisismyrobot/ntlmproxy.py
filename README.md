# ntlmproxy.py

A Python-based http proxy server that wraps requests in NTLM authentication.

## Why?

There are a ton of tools for HTTP scanning (eg Nikito) but a lot of them don't
work very well on a "corporate" network with AD authentication.

This proxy sits between client(s) and a target, doing that legwork.

## Requirements

Python 3.7+

## First-time setup

    python -m pip install pipenv
    python -m pipenv install

## Usage

    pipenv run python ntlmproxy.py [target website root] [domain]\[username]

Eg:

    pipenv run python proxy.py https://www.example.com CONTOSO\doej

Then point your favourite web browsing tool at http://localhost:8080.

## Capabilities

Can point to HTTP or HTTPS websites, handles GET, POST and HEAD.
