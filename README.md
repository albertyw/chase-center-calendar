# Chase Center Calendar

[![Build Status](https://drone.albertyw.com/api/badges/albertyw/chase-center-calendar/status.svg)](https://drone.albertyw.com/albertyw/chase-center-calendar)
[![Updates](https://pyup.io/repos/github/albertyw/chase-center-calendar/shield.svg)](https://pyup.io/repos/github/albertyw/chase-center-calendar/)
[![Maintainability](https://api.codeclimate.com/v1/badges/0881f70f35acc2b901f8/maintainability)](https://codeclimate.com/github/albertyw/chase-center-calendar/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/0881f70f35acc2b901f8/test_coverage)](https://codeclimate.com/github/albertyw/chase-center-calendar/test_coverage)
[![Varsnap Status](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/varsnap_badge.svg)](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/)

This website generates an iCal format calendar of Chase Center events, importable into
Google Calendar, Apple Calendar, and many other calendar apps

Development
-----------

### Setup (using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)):

```bash
mkvirtualenv app -p python3.11
pip install -r requirements.txt
pip install -r requirements-test.txt
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
mypy . --ignore-missing-imports --strict
shellcheck --exclude=SC1091 bin/*.sh
coverage run -m unittest discover
npm test
```
