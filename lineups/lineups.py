#!/usr/bin/env python3

import sys
import re
import urllib.request
import urllib.error
import datetime
from argparse import ArgumentParser


#parsing com line args (right now we'll only have one argument which will print out debug statements)
parser = ArgumentParser()
parser.add_argument('-d', '--debug',
                    action = 'store_true',
                    help = 'Print out debug statements if flag is set')

args = parser.parse_args()

#dictionary mapping of teamnames to cities for looking up URL
cities = {"orioles":"Baltimore", "yankees":"NY Yankees", "red sox":"Boston", "rays":"Tampa Bay", "blue jays":"Toronto",
          "indians":"Cleveland", "twins":"Minnesota", "royals":"Kansas City", "white sox":"Chi White Sox", "tigers":"Detroit",
          "astros":"Houston", "angels":"LA Angels", "mariners":"Seattle", "rangers":"Texas", "athletics":"Oakland",
          "nationals":"Washington", "marlins":"Miami", "braves":"Atlanta", "mets":"NY Mets", "phillies":"Philadelphia",
          "cubs":"Chi Cubs", "brewers":"Milwaukee", "cardinals":"St. Louis", "pirates":"Pittsburgh", "reds":"Cincinnati",
          "dodgers":"LA Dodgers", "diamondbacks":"Arizona", "rockies":"Colorado", "padres":"San Diego", "giants":"San Fransisco"}
          
#getting input from user

while True:
    team = input("Enter teamname: ")
    team = team.lower()
    
    date = input("Enter date (dd/mm/yyyy): ")
    
    match = re.search('\d{1,2}\/\d{1,2}\/\d{4}', date)
    if not match:
        print("Please format date dd/mm/yyyy")
        continue; #if formated inproperly user needs to reenter data
    
    month = re.search('(\d{1,2})\/\d{1,2}\/\d{4}', date).group(1)

    day = re.search('\d{1,2}\/(\d{1,2})\/\d{4}', date).group(1)
    
    year = re.search('\d{1,2}\/\d{1,2}\/(\d{4})', date).group(1)

    if day and month and year:
        if int(day) <= 31 and int(month) <= 12: #some validation of input
            break

#if day and month are only 1 character they need to have a leading 0
if len(day) == 1:
    day = "0"+day
if len(month) == 1:
    month = "0"+month

scoreboard = "http://gd2.mlb.com/components/game/mlb/year_" + year + "/month_" + month + "/day_" + day + "/scoreboard_windows.xml"

if(args.debug):
    print("scoreboard " + scoreboard)
    print("teamname: " + cities.get(team))
    
#getting the gameday URL which has the lineups
try:
    with urllib.request.urlopen(scoreboard) as response:
        html = response.read().decode("utf-8")

except urllib.error.HTTPError as err:
    if err.code == 404:
        sys.exit("error invalid url.  make sure date is correct")
    else:
        raise

#seems that in 2018 there is an inning_break_length variable after the html instead
#of the league variable

startIndex = html.find("game_data_directory", html.find(cities.get(team))) + 21

if(year == "2018"):
    endIndex = html.find("inning_break_length", startIndex) - 10
else:
    if(args.debug):
        print(year)
    endIndex = html.find("league", startIndex)-10
    
html = html[startIndex:endIndex]

gdURL = "http://gd2.mlb.com" + html + "/boxscore.xml"

if(args.debug):
    print("gameday: " + gdURL)

#connecting to gameday to get the lineup
try:
    with urllib.request.urlopen(gdURL) as response:
        gameday = response.read().decode("utf-8")

#this should only really happen if there's a failure in how I got the url to begin with
except urllib.error.HTTPError as err:
    if err.code == 404:
        sys.exit("error invalid url.  make sure date is correct")
    else:
        raise

homeTeam = re.search('home_sname="(\w*)|(\w* \w*)"', gameday)

if not homeTeam:
    sys.exit("could not find hometeam")
else:
    homeTeam = homeTeam.group(1)

if homeTeam == cities.get(team):
    gameday = gameday[gameday.find('batting team_flag="home"'):
                      gameday.find('pitching team_flag="home"')]
else:
    gameday = gameday[gameday.find('batting team_flag="away"'):]

match = re.findall('name_display_first_last="(\w* \w*)"\s*pos=".*"\s*bo="\d00"', gameday)

if not match:
    sys.exit("could not match lineup on gameday")

i = 0

while i<9:
    print(match[i])
    i+=1
































