#!/bin/bash
# makes sure the program ends if any of the comands produces an error
set -e

echo "Running the type checker"
pyright

echo "Running the formatter. You van fix errors automatically with 'black .'"
black . --check

echo "Running the linters"
flake8 server/
isort server/

echo "Running the django test with coverage"
pytest --cov-report term-missing --cov server
