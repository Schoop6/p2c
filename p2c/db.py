import psycopg2

import os
import click
from flask import current_app, g
from flask.cli import with_appcontext
from urllib.parse import uses_netloc, urlparse



def connect_db():
    uses_netloc.append("postgres")
    URL = urlparse(os.environ['DATABASE_URL'])
    #this is a global var used by the db module
    return psycopg2.connect(
        database = URL.path[1:],
        user = URL.username,
        password = URL.password,
        host = URL.hostname,
        port = URL.port
        )

def get_db():
    if 'db' not in g:
        g.db = connect_db()
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def make_dicts(curr, row):
    return dict((curr.description[idx][0], value)
                for idx, value in enumerate(row))

#this will return in a dictionary form like the
#fetchall/fetchone of sqlite3
def query_db(query, args=(), one=False):
    db = get_db()
    curr = db.cursor()
    curr.execute(query, args)
    rv = []
    row = curr.fetchone()
    while row is not None:
        rv.append(make_dicts(curr, row))
        row = curr.fetchone()
    curr.close()
    return (rv[0] if rv else None) if one else rv
        
        
def init_db():
    db = get_db()
    curr = db.cursor()
    with current_app.open_resource('schema.sql') as f:
        curr.execute(f.read())
    db.commit()
    db.close()
    curr.close()
        
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


        
