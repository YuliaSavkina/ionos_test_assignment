#!/bin/sh

# prepare environment
virtualenv venv --python=python3.7
source venv/bin/activate
pip install -r requirements.txt

# copy ssh keys to a proper place
cp -R ssh/ ~/.ssh/
chmod 400 ~/.ssh/id_rsa

# run tests
python cloud_api_test.py

