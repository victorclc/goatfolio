#!/bin/bash

function runTests() {
  serviceName=$1
  cd "$serviceName"

  echo "Creating test virtual environment..."
  python3 -m venv test-env 1> /dev/null
  if [[ "$OSTYPE" == "msys" ]]; then
    source test-env/Scripts/activate
  else
    source test-env/bin/activate
  fi


  echo "Installing dependencies..."
  pip3 install -r requirements.txt &> /dev/null
  pip3 install pytest &> /dev/null

  echo "Setting up environment variables..."
  if [[ "$OSTYPE" == "msys" ]]; then
    export PYTHONPATH="../../libs;src;tests"
  else
    export PYTHONPATH="../../libs:src:tests"
  fi

  echo "Running tests"
  if ! python3 -m pytest -v tests/; then
    echo "$serviceName tests failed"
    exit 1
  fi
  echo "$serviceName passed."

  cd -
}
export AWS_REGION='us-east-2'

runTests 'services/portfolio-api'
runTests 'services/vandelay-api'

echo "All tests passed."
