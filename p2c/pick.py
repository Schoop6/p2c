import datetime
from datetime import timedelta
import lineups
import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('pick', __name__)

HOMERS = {}
#dates hashed to who homered on those dates

over = ["O", "F"] #these status letters mean the games done
pregame = ["P", "PW"]

#schedules the verification to happen every 33 mins
#from stackOverflow
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=verifyClicks,
    trigger=IntervalTrigger(minutes=1),
    id='verify clicks',
    name='Verify if clicks occurred',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


#just checks if user already has a pick registered for today
#returns (Boolean, error message"") tuple
def checkPick():
    db = get_db()
    if g.user is None:
        return False, "Not logged in"
    picks = db.execute(
        'SELECT * FROM pick WHERE username = ? ORDER BY created DESC;', (g.user['username'],))
    if not picks:
        return False, "not picks"
    recent = picks.fetchone()
    if not recent:
        return False, "not recent"

    pickDate = recent['created']
    today = datetime.date.today()
    if today == pickDate.date():
        return (True, "You've already picked {} today".format(recent['player']))
    else:
        return False, "Picked recently"


def verifyClicks():
    db = get_db()
    
    unverifiedPicks = db.execute(
        'SELECT * FROM pick WHERE verified = NULL')
    if unverifiedPicks is None:
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


        

@bp.route('/myPick')
@login_required
def myPick():
    db = get_db()
    picks = db.execute(
        'SELECT * FROM pick WHERE username = ? ORDER BY created DESC;', (g.user['username'],))
    recentPick = picks.fetchone()
    if not recentPick:
        return render_template('pick/myPick.html', lastPick="None")
    else:
        return render_template('pick/myPick.html',
                               lastPick=recentPick['player'], time=recentPick['created'])



@bp.route('/scores')
@login_required
def scores():
    db = get_db()
    points = db.execute(
        'SELECT score FROM user WHERE username = ?', (g.user['username'],)).fetchone()
    if points is None:
        return render_template('pick/scores.html',
                               score="something went horrible wrong", player=None, date=None)
    points = points['score']
    if not points == 0:
        lastClick = db.execute(
            'SELECT * FROM pick WHERE username = ? AND click = 1', (g.user['username'],))
        if not lastClick:
            return render_template('pick/scores.html',
                score="something went horrible wrong", player=None, date=None)
        else:
            lastClick = lastClick.fetchone()

        return render_template('pick/scores.html',
                               score=points, player=lastClick['player'],
                               date=lastClick['created'].date())
    else:
        return render_template('pick/scores.html', score=0, player="Nobody", date="Never")


@bp.route('/', methods=('GET', 'POST'))
def index():
    if(request.method == 'POST'):
        if g.user is None:
            flash("Must be logged in to pick")
        else:
            picked, msg = checkPick()
            pick = request.form.get("player", False)
            stat = lineups.getStatus(datetime.date.today(), "orioles")
            db = get_db()
            if not stat in pregame:
                flash(stat + " Picks locked after game starts!")
            else:
                if picked is False:
                    flash("You've picked {}".format(pick))
                    db.execute(
                        'INSERT INTO pick (username, player, created)'
                        'VALUES (?,?,?)',
                        (g.user['username'], pick, datetime.datetime.now()))
                    db.commit()
                    
                else:
                    flash("Your pick was updated to {}".format(pick))
                    pickEntry = db.execute(
                        'SELECT * FROM pick WHERE username = ? ORDER BY created DESC;',
                        (g.user['username'],)).fetchone()
                    db.execute(
                        'UPDATE pick SET player = ?, created = ?'
                        'WHERE id = ?',
                        (pick, datetime.datetime.now(), pickEntry['id']))
                    db.commit()
    
    # db = get_db()
    #  posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).
    else:
        pickToday, error = checkPick()
        if pickToday is True:
            flash(error) #just flashes the players name to the user
        else:
            flash(error)

            
    date = datetime.date.today()
    lineup, error = lineups.get_lineups(date, "Orioles")
    if error is not "":
        print("Error: {}".format(error))
    return render_template('pick/index.html', lineup=lineup, error=error)
