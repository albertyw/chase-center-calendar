# Chase Center Calendar

[![Build Status](https://drone.albertyw.com/api/badges/albertyw/chase-center-calendar/status.svg)](https://drone.albertyw.com/albertyw/chase-center-calendar)
[![Varsnap Status](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/varsnap_badge.svg)](https://www.varsnap.com/project/e671c842-e385-4ce0-a321-7d8659906c68/)

This website generates an iCal format calendar of Chase Center events, importable into
Google Calendar, Apple Calendar, and many other calendar apps

Development
-----------

### Setup (using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)):

```bash
mkvirtualenv app -p python3.9
pip install -r requirements.txt
pip install -r requirements-test.txt
ln -s .env.development .env
npm install
```

### Spinning up the server:

```bash
npm run minify
python app/serve.py
```

### Running tests:

```bash
flake8
mypy app --ignore-missing-imports --strict
shellcheck --exclude=SC1091 bin/*.sh
coverage run -m unittest discover
npm test
```
