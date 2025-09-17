#!/bin/bash

if [[ "$OSTYPE" == "darwin"* ]]; then
  source ~/pythonEnv/bin/activate
  python3 ./scripts/build.py
else
  python ./scripts/build.py
fi
