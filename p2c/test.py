#!/usr/bin/env python3

import lineups
import datetime

def test1():
    date = datetime.date.today() - datetime.timedelta(1)
    lineups.get_lineups(date, "Orioles")


test1()
    
