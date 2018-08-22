#!/usr/bin/env python3

#modified to work with the server
import sys
import re
import urllib2
import datetime
from datetime import timedelta

#parsing com line args (right now we'll only have one argument which will print out debug statements)

#dictionary mapping of teamnames to cities for looking up URL
cities = {"orioles":"Baltimore", "yankees":"NY Yankees", "red sox":"Boston", "rays":"Tampa Bay", "blue jays":"Toronto",
          "indians":"Cleveland", "twins":"Minnesota", "royals":"Kansas City", "white sox":"Chi White Sox", "tigers":"Detroit",
          "astros":"Houston", "angels":"LA Angels", "mariners":"Seattle", "rangers":"Texas", "athletics":"Oakland",
          "nationals":"Washington", "marlins":"Miami", "braves":"Atlanta", "mets":"NY Mets", "phillies":"Philadelphia",
          "cubs":"Chi Cubs", "brewers":"Milwaukee", "cardinals":"St. Louis", "pirates":"Pittsburgh", "reds":"Cincinnati",
          "dodgers":"LA Dodgers", "diamondbacks":"Arizona", "rockies":"Colorado", "padres":"San Diego", "giants":"San Fransisco"}

def getStatus(date, team):
    gdURL = get_GDurl(date, team)

    try:
        response = urllib2.urlopen(gdURL)
        gameday = response.read().decode("utf-8")
    except urllib2.HTTPError, err:
        #print("error in scoreboard url")
        return err.code

        
    status = re.search("status_ind=\"(\w+)\"", gameday)

    if not status:
        return "Error, no status"
    else:
        return status.group(1)

    

#helper function that gets the game day url for date and team passed in
def get_GDurl(date, team):
    team = team.lower()
    
    month = str(date.month)

    day = str(date.day)
    
    year = str(date.year)
    #if day and month are only 1 character they need to have a leading 0
    if len(day) == 1:
        day = "0"+day
    if len(month) == 1:
        month = "0"+month

    #the url of the scoreboard for the game being asked for
    scoreboard = "http://gd2.mlb.com/components/game/mlb/year_" + year + "/month_" + month + "/day_" + day + "/scoreboard_windows.xml"
    #if(args.debug):
     #   print("scoreboard " + scoreboard)
      #  print("teamname: " + cities.get(team))
    
    #getting the gameday URL which has the lineups
    try:
        response = urllib2.urlopen(scoreboard)
        html = response.read().decode("utf-8")

    except urllib2.HTTPError, err:
        #print("error in scoreboard url")
        return lineups, err.code


    startIndex = html.find("game_data_directory", html.find(cities.get(team))) + 21

    if(int(year) >= 2018):
        endIndex = html.find("inning_break_length", startIndex) - 10
    else:
        endIndex = html.find("league", startIndex)-10
    
    html = html[startIndex:endIndex]


    gdURL = "http://gd2.mlb.com" + html + "/boxscore.xml"
    
    return gdURL

def get_dongers(date, team):
    dongers = []
    error = ""
    team = team.lower()
    gdURL = get_GDurl(date, team)

    try:
        response = urllib2.urlopen(gdURL)
        gameday = response.read().decode("utf-8")

    except urllib2.HTTPError, err:
        return dongers, err.code

    homeTeam = re.search('home_sname="(\w*)|(\w* \w*)"', gameday)

    if not homeTeam:
        return dongers, "could not find hometeam name"
    else:
        homeTeam = homeTeam.group(1)

    if homeTeam == cities.get(team):
        gameday = gameday[gameday.find('batting team_flag="home"'):
                          gameday.find('pitching team_flag="home"')]
    else:
        gameday = gameday[gameday.find('batting team_flag="away"'):]

    batters = gameday.split("name_display_first_last=")
    batters.pop(0) #there's just a bunch of leading junk to shave off
    for batter in batters: #check if they logged a donger today
      #  print batter
        dongs = re.search('so="\d+"\s*hr="(\d+)"\s*rbi', batter)
        if not dongs:
            return dongers, "Fatal error in formatting/regex"

        dongs = dongs.group(1)
        if int(dongs) > 0:
            name = re.search('"(\w* \w*)"', batter)
            dongers.append(name.group(1))

    return dongers, error

    

#getlineup fuction
#returns the lineups as dictionary and error code as string
def get_lineups(date, team):
    lineups = []
    error = ""
  #  date = date - timedelta(1)
   # print(date)
    team = team.lower()
    gdURL = get_GDurl(date, team)
  #  print(gdURL)
    #connecting to gameday to get the lineup
    try:
        response = urllib2.urlopen(gdURL)
        gameday = response.read().decode("utf-8")

    #this should only really happen if there's a failure in how I got the url to begin with
    except urllib2.HTTPError, err:
       # print(gdURL)
        return lineups, err.code
    homeTeam = re.search('home_sname="(\w*)|(\w* \w*)"', gameday)

    if not homeTeam:
        return lineups, "could not find hometeam name"
    else:
        homeTeam = homeTeam.group(1)

    if homeTeam == cities.get(team):
        gameday = gameday[gameday.find('batting team_flag="home"'):
                          gameday.find('pitching team_flag="home"')]
    else:
        gameday = gameday[gameday.find('batting team_flag="away"'):]
        
    match = re.findall('name_display_first_last="(\w* \w*)"\s*pos=".*"\s*bo="\d00"', gameday)

    if not match:
        return lineups, "could not match lineup on gameday"
    else:
        return match, ""
































