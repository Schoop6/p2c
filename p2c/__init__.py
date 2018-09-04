import os
import logging
import time
import datetime
from datetime import timedelta
from p2c.db import get_db


from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit


HOMERS = {}
#dates hashed to who homered on those dates

over = ["O", "F"] #these status letters mean the games done
pregame = ["P", "PW"]


#This is maybe not the most efficient way to get this to work but I couldn't really figure
#out how to get the apscheduler to work with flask contexts
def verifyClicks():
    app = create_app()
    with app.app_context():

        db = get_db()

        unverifiedPicks = db.execute(
            'SELECT * FROM pick WHERE click = NULL')
        if unverifiedPicks is None:
            print("NO UNVERIFIED PICKS")
            #TODO: Maybe shut down the scheduler if there's no unverified picks?
            #maybe we can restart it the second someone makes a pick
            #would this have other ramifications??????????
            #Just want to save server resourses
            return
    
        date = datetime.date.today()
        status = lineups.getStatus(date, "orioles")
        yesterday = date - timedelta(1)
        statusYes = lineups.getStatus(yesterday, "orioles")

        if not yesterday in HOMERS:
            HOMERS[yesterday] = None
        if not date in HOMERS:
            HOMERS[date] = None
    
        if HOMERS[date] is None and status in over:
            HOMERS[date] = lineups.get_dongers(date, "orioles")
        if HOMERS[yesterday] is None and statusYes in over:
            HOMERS[yesterday] = lineups.get_dongers(yesterday, "orioles")

        if status is over or statusYes in over:
            for p in unverifiedPicks:
                dongers = HOMERS[p['created'].date]
                player = p['player']
                ident = p['id']
                uname = p['username']
            
                if player in dongers: #if your player clicks
                    db.execute( #update the pick with the verification bit set
                        'UPDATE pick SET click = ?'
                        'WHERE id = ?',
                        (1, ident))
                    db.execute( #update the total score of the player
                        'UPDATE user SET score = score + 1'
                        'WHERE username = ?',
                        (uname, ))
                    db.commit()
                else: #player didn't click
                    db.execute(#still need to set the verification bit 
                        'UPDATE pick SET click = ?'
                        'WHERE id = ?',
                        (0, ident))
                    db.commit()




scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=verifyClicks,
    trigger=IntervalTrigger(minutes=33),
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

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'p2c.sqlite'),
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

    
