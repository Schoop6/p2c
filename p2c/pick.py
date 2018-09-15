import datetime
from datetime import timedelta
from pytz import timezone
import time
import atexit
import logging

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from p2c.lineups import get_lineups, getStatus
from p2c.auth import login_required
from p2c.db import get_db, query_db

bp = Blueprint('pick', __name__)
tz = timezone("America/New_York")
#setting the timezone because heroku uses UTC





HOMERS = {}
#dates hashed to who homered on those dates

over = ["O", "F"] #these status letters mean the games done
pregame = ["P", "PW"]

#just checks if user already has a pick registered for today
#returns (Boolean, error message"") tuple
def checkPick():
    if g.user is None:
        return False, "Not logged in"
    uname = g.user['username']
    recent = query_db(
        'SELECT * FROM pick WHERE username = (%s) ORDER BY created DESC;', (uname,), True)
    if not recent:
        return False, "You have no recent picks"

    pickDate = recent['created']
    today = datetime.datetime.now(tz).date()
    if today == pickDate.date():
        return (True, "You've already picked {} today".format(recent['player']))
    else:
        return False, "Picked recently"


@bp.route('/leaderboard')
def leaderboard():
    leaders = []
    query = query_db('SELECT * FROM users ORDER BY score DESC')
    for l in query:
        leaders.append((l['username'], l['score']))
    return render_template('pick/leaderboard.html', leaders=leaders)

@bp.route('/myPick')
@login_required
def myPick():
    allPicks = []
    #list of all picks in a tuple of form (player, date, click)
    picksList = query_db(
        'SELECT * FROM pick WHERE username = (%s) ORDER BY created DESC;', (g.user['username'],))
    recentPick = query_db('SELECT * FROM pick WHERE username = (%s) ORDER BY created DESC;', (g.user['username'],), True)
    if not recentPick:
        return render_template('pick/myPick.html', lastPick="Nobody", time="Never", allPicks=None)
    #if recentPick isn't None we're gonna find all the picks they've made 
    for p in picksList:
        allPicks.append((p['player'], p['created'].date(), p['click']))
    if recentPick['click'] is None:
        return render_template('pick/myPick.html',lastPick=recentPick['player'],
                               time=recentPick['created'], allPicks=allPicks)
    else:
        print("click variable: {}".format(recentPick['click']))
        return render_template('pick/myPick.html',lastPick=recentPick['player'],
                               time=recentPick['created'], verified=recentPick['click'])
    

#@bp.route('/leaderboard')
#def leaderboard():
    #TODO make this a leaderboard page
    
@bp.route('/scores')
@login_required
def scores():
    points = query_db(
        'SELECT score FROM users WHERE username = (%s)', (g.user['username'],), True)
    if points is None: #should never have no entry for a logged in user
        return render_template('pick/scores.html',
                               score="something went horrible wrong", player=None, date=None)
    points = points['score']
    if not points == 0:
        cur.execute(
            'SELECT * FROM pick WHERE username = (%s) AND click = 1', (g.user['username'],))
        lastClick = curr.fetchone()
        
        if not lastClick: #should never have more than 0 points but no clicks verified
            return render_template('pick/scores.html',
                score="something went horrible wrong", player=None, date=None)
        else:
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
            stat = getStatus(datetime.datetime.now(tz).date(), "orioles")
            db = get_db()
            cur = db.cursor()
            if not stat in pregame:
                flash(stat + " Picks locked after game starts!")
            else:
                if picked is False:
                    flash("You've picked {}".format(pick))
                    cur.execute(
                        'INSERT INTO pick (username, player, created)'
                        'VALUES ((%s),(%s),(%s))',
                        (g.user['username'], pick, datetime.datetime.now()))
                    db.commit()
                    
                else:
                    flash("Your pick was updated to {}".format(pick))
                    pickEntry = query_db(
                        'SELECT * FROM pick WHERE username = (%s) ORDER BY created DESC;',
                        (g.user['username'],), True)
                    cur.execute(
                        'UPDATE pick SET player = (%s), created = (%s)'
                        'WHERE id = (%s)',
                        (pick, datetime.datetime.now(tz), pickEntry['id']))
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

    print("local time is {}".format(datetime.datetime.now(tz)))
    date = datetime.datetime.now(tz).date()
    lineup, error = get_lineups(date, "Orioles")
    if error is not "":
        print("Error: {}".format(error))
    return render_template('pick/index.html', lineup=lineup, error=error)
