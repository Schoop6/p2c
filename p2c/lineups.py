#!/usr/bin/env python3

#modified to work with the server
import sys
import re
from urllib.request import urlopen, Request
from urllib.error import URLError
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
    if gdURL is None:
        print("returning none")
        return None
    #print(gdURL)

    try:
        request = Request(gdURL)
        response = urlopen(request)
        gameday = response.read().decode("utf-8")
    except:
        #print("error in scoreboard url")
        return None

        
    status = re.search("status_ind=\"(\w+)\"", gameday)

    if not status:
        return None
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

    baseURL = "http://gd2.mlb.com/components/game/mlb/year_" + year + "/month_" + month + "/day_" + day


    #the url of the scoreboard for the game being asked for
    scoreboard = baseURL + "/scoreboard.xml"
    #if(args.debug):
    #print("scoreboard " + scoreboard)
      #  print("teamname: " + cities.get(team))
    
    #getting the gameday URL which has the lineups
    try:
        request = Request(scoreboard)
        response = urlopen(request)
        html = response.read().decode("utf-8")

    except URLError as err:
        #print("error in scoreboard url")
        return None


    gms = html.split("game id=")
    for g in gms:
        i = g.find(team.capitalize())
        if i != -1:
            endIndex = g.find("league=") - 2
            print("end " + str(endIndex))
            html = g[1:endIndex]
            
    
    html = "/gid_" + html

    gdURL = baseURL + html + "/boxscore.xml"
    print(gdURL)
    
    return gdURL

def get_dongers(date, team):
    print("Checking dongers")
    dongers = []
    error = ""
    team = team.lower()
    gdURL = get_GDurl(date, team)

    try:
        request = Request(gdURL)
        response = urlopen(request)
        gameday = response.read().decode("utf-8")

    except URLError as err:
        return dongers, err.code

    homeTeam = re.search('home_sname="(\w*|\w* \w*)"', gameday)

    if not homeTeam:
        return dongers, "could not find hometeam name"
    else:
        homeTeam = homeTeam.group(1)

    if homeTeam == cities.get(team):
        m = re.search('<batting .*team_flag="home"', gameday)
        if not m:
            return dongers, "Could not find home team on page"
        gameday = gameday[m.start():gameday.find('<text_data>', m.start())]
    else:
        m = re.search('<batting .*team_flag="away"', gameday)
        if not m:
            return dongers, "Could not find away team on page"
        gameday = gameday[m.start():gameday.find("<text_data>", m.start())]

        
    batters = gameday.split("<batter")
    batters.pop(0) #the first chunk is team stats
    for batter in batters: #check if they logged a donger today
        #print(batter)
        dongs = re.search('hr="(\d+)"', batter)
        if not dongs:
            return dongers, "Fatal error in formatting/regex"
        dongs = dongs.group(1)
        if int(dongs) > 0:
            name = re.search('name_display_first_last="(\w* \w*|\w* \w* \S*)"', batter)
            dongers.append(name.group(1))

    print(dongers)
    return dongers, error

    

#getlineup fuction
#returns the lineups as dictionary and error code as string
def get_lineups(date, team):
    lineups = []
    error = ""
    #  date = date - timedelta(1)
  #  print(date)
    team = team.lower()
    gdURL = get_GDurl(date, team)
    if gdURL is None:
        return lineups, "Off day today?"
    #connecting to gameday to get the lineup
    try:
        request = Request(gdURL)
        response = urlopen(request)
        gameday = response.read().decode("utf-8")

    #this should only really happen if there's a failure in how I got the url to begin with
    except URLError as err:
       # print(gdURL)
        return lineups, err.code
    
    homeTeam = re.search('home_sname="(\w*|\w* \w*)"', gameday)
    #print(homeTeam.group(1))
    if not homeTeam:
        return lineups, "could not find hometeam name"
    else:
        homeTeam = homeTeam.group(1)

    if homeTeam == cities.get(team):
        m = re.search('<batting .*team_flag="home"', gameday)
        if not m:
            return "Could not find home team on page"
        gameday = gameday[m.start():gameday.find('</batting', m.start())]
    else:
        m = re.search('<batting .*team_flag="away"', gameday)
        if not m:
            return "Could not find away team on page"
        gameday = gameday[m.start():gameday.find("</batting", m.start())]

    batters = gameday.split("<batter")
    for b in batters:
        #print(b)
        match = re.search('bo="\d00"', b)
        if match is None:
            continue
        match = re.search('name_display_first_last="(\w* \w*|\w* \w* \S*)"', b)
        print(match.group(1))
        lineups.append(match.group(1))
    
    if len(lineups) is 9:
        return lineups, ""
    else:
        return lineups, "Possible invalide lineup"
































