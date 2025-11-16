# Chase Center Calendar

[![Build Status](https://drone.albertyw.com/api/badges/albertyw/chase-center-calendar/status.svg)](https://drone.albertyw.com/albertyw/chase-center-calendar)
[![Maintainability](https://qlty.sh/gh/albertyw/projects/chase-center-calendar/maintainability.svg)](https://qlty.sh/gh/albertyw/projects/chase-center-calendar)
[![Code Coverage](https://qlty.sh/gh/albertyw/projects/chase-center-calendar/coverage.svg)](https://qlty.sh/gh/albertyw/projects/chase-center-calendar)
[![Varsnap Status](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/varsnap_badge.svg)](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/)

This website generates an iCal format calendar of Chase Center events, importable into
Google Calendar, Apple Calendar, and many other calendar apps

Development
-----------

### Setup
Using [python venv](https://docs.python.org/3/library/venv.html) and
[direnv](https://github.com/direnv/direnv)

```bash
python3.14 -m venv env
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
