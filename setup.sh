#! /bin/bash

#this is just a script to run the commands to set up this directory to be run by flask

export FLASK_APP=p2c
export FLASK_ENV=development
export DATABASE_URL=postgres://hbvsvbpgcehanc:7e563ff061a8e08890965a78e51dfcddf9c6ca695116c4523a2b3e22d40462d5@ec2-54-227-245-146.compute-1.amazonaws.com:5432/db1v5m1odjep86

flask run --no-reload
