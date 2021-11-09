#!/bin/sh
# flask depends on this env variable to find the main file
export FLASK_APP=api.py

# now we just need to ask flask to run
flask run

# * Serving Flask app "hello"
# * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)