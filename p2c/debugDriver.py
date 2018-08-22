#! /usr/bin/env python

import lineups
import datetime


retVal = lineups.get_lineups(datetime.datetime.now(), "Orioles") 

print(retVal)

