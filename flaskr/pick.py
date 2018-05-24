import datetime
import lineups

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('pick', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if(request.method == 'POST'):
        pick = request.form.get("player", False)
        flash(pick)
        print(pick)


    # db = get_db()
    #  posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).
    date = datetime.datetime.now()
    lineup, error = lineups.get_lineups(date, "Orioles")
    return render_template('pick/index.html', lineup=lineup, error=error)
