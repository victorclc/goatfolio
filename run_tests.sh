#!/bin/bash

function runTests() {
  serviceName=$1
  cd "$serviceName"

  echo "Creating test virtual environment..."
  python -m venv test-env 1> /dev/null
  source test-env/Scripts/activate

  echo "Installing dependencies..."
  pip install -r requirements.txt &> /dev/null
  pip install pytest &> /dev/null

  echo "Setting up environment variables..."
  if [[ "$OSTYPE" == "msys" ]]; then
    export PYTHONPATH="../../libs;src;tests"
  else
    export PYTHONPATH="../../libs:src:tests"
  fi

  echo "Running tests"
  if ! python -m pytest -v tests/; then
    echo "$serviceName tests failed"
    exit 1
  fi
  echo "$serviceName passed."

  cd -
}

runTests 'services/portfolio-api'
runTests 'services/vandelay-api'

echo "All tests passed."
