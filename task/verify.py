import os
import sys

#this just so we have access to the p2c module guaranteed
path = '/home/tallndawkward/p2c/'
if path not in sys.path:
    sys.path.append(path)

from p2c import create_app
from db import get_db, close_db


#this is just to make things work with pythonanywhere which apparently doesn't support
#ap scheduler.  instead it has its own scheduler which will call verify clicks

def verifyClicks():
    app = create_app()
    with app.app_context():

        db = get_db()
     #   print("*******STARTING CHECK*******")
        unverifiedPicks = db.execute(
            'SELECT * FROM pick WHERE click IS NULL')
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
            hrs, error = lineups.get_dongers(date, "orioles")
            if error != "":
                print(error)
            else:
                HOMERS[date] = hrs
        if HOMERS[yesterday] is None and statusYes in over:
             hrs, error = lineups.get_dongers(yesterday, "orioles")
             if error != "":
                 print(error)
             HOMERS[yesterday] = hrs
    #    print("*******CHECKING STATUS*******")
                
        if status in over or statusYes in over:
            print("******UNVERIFIED PICKS WITH POTENTIAL NEW STATUS********")
            for p in unverifiedPicks:
                s = lineups.getStatus(p['created'].date(), "orioles")
                if s not in over:
                #    print("******GAME NOT OVER YET*******")
                    continue
                dongers = HOMERS[p['created'].date()]
                player = p['player']
                ident = p['id']
                uname = p['username']
                print(uname)
                db = get_db()

                print(type(dongers))
            #    print(dongers)
                if player in dongers: #if your player clicks
                    db.execute( #update the pick with the verification bit set
                        'UPDATE pick SET click = ?'
                        'WHERE id = ?',
                        (1, ident))
                    db.execute( #update the total score of the player
                        'UPDATE user SET score = score + 1 WHERE username = ?',
                        (uname, ))
                    print(uname)
                    db.commit()
                else: #player didn't click
                    db.execute(#still need to set the verification bit 
                        'UPDATE pick SET click = ?'
                        'WHERE id = ?',
                        (0, ident))
                    db.commit()
