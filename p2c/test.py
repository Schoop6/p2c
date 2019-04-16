#!/usr/bin/env python3

import lineups
import datetime
import argparse

date = datetime.date.today() - datetime.timedelta(1)


def test1():
    lineups.get_lineups(date, "Orioles")

def test2():
    print(lineups.get_dongers(date, "Orioles"))

    
test2()
    
