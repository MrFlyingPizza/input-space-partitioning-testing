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
Install the pre-commit hook.
```sh
pre-commit install
```

Update the requirements file if you install or remove dependencies.
```sh
pip freeze > requirements.txt
```

## Run
### Tests
```sh
pytest
```
Use option `-s` if you want to see stdout.

### Generate Value Handlers Dict
Generate the dict that contains all input category names and their values as dicts which will be used to obtain functions to setup tests.
```sh
python generate_value_handlers.py
```
