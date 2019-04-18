#! /bin/bash

#this is just a script to run the commands to set up this directory to be run by flask

export FLASK_APP=p2c
export FLASK_ENV=development
export DATABASE_URL=postgres://pxbeelopsndiwq:1f933445a372e65f3a27f8242f968dd01c95c935b1b13055e4533b26c91c71f6@ec2-54-227-240-7.compute-1.amazonaws.com:5432/dfqsn7r16aadv1

flask run --no-reload
