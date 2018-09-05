import datetime
from datetime import timedelta
import lineups
import time
import atexit
import logging

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from p2c.auth import login_required
from p2c.db import get_db

bp = Blueprint('pick', __name__)


    


HOMERS = {}
#dates hashed to who homered on those dates

over = ["O", "F"] #these status letters mean the games done
pregame = ["P", "PW"]

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



@bp.route('/myPick')
@login_required
def myPick():
    db = get_db()
    picks = db.execute(
        'SELECT * FROM pick WHERE username = ? ORDER BY created DESC;', (g.user['username'],))
    recentPick = picks.fetchone()
    print(recentPick['click'])
    if not recentPick:
        return render_template('pick/myPick.html', lastPick="Nobody", time="Never")
    else:
        return render_template('pick/myPick.html',lastPick=recentPick['player'],
                               time=recentPick['created'], verified=recentPick['click'])
    



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