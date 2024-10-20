#!/bin/bash

git add .
git commit -m "Syncing all data."
git pull origin main
git push origin main

if test -d .venv/bin/activate; then
    source .venv/bin/activate
else
    python3 -m venv .venv
    source .venv/bin/activate
fi

pip install -U discord.py aiosqlite PyNaCL

python3 main.py