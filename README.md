# Chase Center Calendar

[![Build Status](https://drone.albertyw.com/api/badges/albertyw/chase-center-calendar/status.svg)](https://drone.albertyw.com/albertyw/chase-center-calendar)
[![Maintainability](https://api.codeclimate.com/v1/badges/0881f70f35acc2b901f8/maintainability)](https://codeclimate.com/github/albertyw/chase-center-calendar/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/0881f70f35acc2b901f8/test_coverage)](https://codeclimate.com/github/albertyw/chase-center-calendar/test_coverage)
[![Varsnap Status](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/varsnap_badge.svg)](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/)

This website generates an iCal format calendar of Chase Center events, importable into
Google Calendar, Apple Calendar, and many other calendar apps

Development
-----------

### Setup
Using [python venv](https://docs.python.org/3/library/venv.html) and
[direnv](https://github.com/direnv/direnv)

```bash
python3.13 -m venv env
printf "source env/bin/activate\nunset PS1\n" > .envrc
direnv allow
pip install -e .[test]
ln -s .env.development .env
npm install
```

### Spinning up the server:

```bash
npm run build:dev
python app/serve.py
```

### Running tests:

```bash
ruff check .
mypy .
shellcheck --exclude=SC1091 bin/*.sh
coverage run -m unittest discover
npm test
```
