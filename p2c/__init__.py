#!/usr/bin/python3

import os
import sys
import logging
import time
import datetime
from datetime import timedelta
from p2c.db import get_db, close_db, query_db
from p2c.lineups import getStatus, get_lineups, get_dongers
#don't you just love the conflicting styles in my function names


from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import apscheduler.schedulers
import atexit

#with posgres database_url is kind of required
'DATABASE_URL' in os.environ or sys.exit('DATABASE_URL must be in the environment')


#declaring the scheduler
scheduler = BackgroundScheduler()

HOMERS = {}
#dates hashed to who homered on those dates

over = ["O", "F"] #these status letters mean the games done
pregame = ["P", "PW"] #these mean the game hasn't started


#This is maybe not the most efficient way to get this to work but I couldn't really figure
#out how to get the apscheduler to work with flask contexts
def verifyClicks():
    app = create_app()
    with app.app_context():

        db = get_db()
        cur = db.cursor()
        print("*******STARTING CHECK*******")
        unverifiedPick = query_db(
            'SELECT * FROM pick WHERE click IS NULL')
        if unverifiedPick is None:
            print("NO UNVERIFIED PICKS")
            #TODO: Maybe shut down the scheduler if there's no unverified picks?
            #maybe we can restart it the second someone makes a pick
            #would this have other ramifications??????????
            #Just want to save server resourses
            return
            
        date = datetime.date.today()
        status = getStatus(date, "orioles")
        yesterday = date - timedelta(1)
        statusYes = getStatus(yesterday, "orioles")

        if not yesterday in HOMERS:
            HOMERS[yesterday] = None
        if not date in HOMERS:
            HOMERS[date] = None

        print("Status")
        print(statusYes)
        print(status)
            
        if HOMERS[date] is None and status in over:
            hrs, error = get_dongers(date, "orioles")
            if error != "":
                print(error)
            else:
                HOMERS[date] = hrs
        if HOMERS[yesterday] is None and statusYes in over:
             hrs, error = get_dongers(yesterday, "orioles")
             if error != "":
                 print(error)
             HOMERS[yesterday] = hrs
    #    print("*******CHECKING STATUS*******")
                
        if status in over or statusYes in over:
            print("******UNVERIFIED PICKS WITH POTENTIAL NEW STATUS********")
            for p in unverifiedPick:
                print("going through picks")
                s = getStatus(p['created'].date(), "orioles")
                if s not in over:
                #    print("******GAME NOT OVER YET*******")
                    continue
                print(p['created'].date())
                print(date)
                
                dongers = HOMERS[p['created'].date()]
                player = p['player']
                ident = p['id']
                uname = p['username']
                print("username: {}".format(uname))

            #    print(dongers)
                if player in dongers: #if your player clicks
                    cur.execute( #update the pick with the verification bit set
                        'UPDATE pick SET click = (%s)'
                        'WHERE id = (%s)',
                        ('1', ident))
                    cur.execute( #update the total score of the player
                        'UPDATE user SET score = score + 1 WHERE username = (%s)',
                        (uname, ))
                    print("updating {}'s click to yes".format(uname))
                    db.commit()
                    
                else: #player didn't click
                    print("previous: {}".format(p['click']))
                    cur.execute(#still need to set the verification bit 
                        'UPDATE pick SET click = (%s)'
                        'WHERE id = (%s)',
                        ('0', ident))
                    print("updating {}'s click to no".format(uname))
                    db.commit()


scheduler.start()
scheduler.add_job(
    func=verifyClicks,
    trigger=IntervalTrigger(seconds=33),
    id='verify picks',
    name='Verify if clicks should be awarded points or not',
    replace_existing=True)
log = logging.getLogger('apscheduler.executors.default')
log.setLevel(logging.INFO)  # DEBUG

fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
h = logging.StreamHandler()
h.setFormatter(fmt)
log.addHandler(h)


def create_app(test_config=None):
    #print("creating app")
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)


    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import pick
    app.register_blueprint(pick.bp)
    app.add_url_rule('/', endpoint='index')


    return app

    
