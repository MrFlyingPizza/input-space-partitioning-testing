# Exploration of Testing Through Input Space Partitioning

## Setup
**Linux only**

Create virtual environment.
```sh
python -m venv .venv
```
Activate virtual environment.
```sh
. .venv/bin/activate
```
Install dependencies.
```sh
pip install -r requirements.txt
```
Update dependency list if you install or remove dependencies.
```sh
pip freeze > requirements.txt
```

## Run
Run tests
```sh
pytest
```
Use option `-s` if you want to see stdout.