#! /bin/bash

#this is just a script to run the commands to set up this directory to be run by flask

export FLASK_APP=p2c
export FLASK_ENV=development
export DATABASE_URL='/instance/p2c.sqlite'

flask run --no-reload
