import sys
import re
import urllib.request
import urllib.error

#getting input from user
#assuming for now the team is baltimore orioles

team = "Orioles"

while True:
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

#getting the gameday URL which has the lineups
try:
    with urllib.request.urlopen(scoreboard) as response:
        html = response.read().decode("utf-8")

except urllib.error.HTTPError as err:
    if err.code == 404:
        sys.exit("error invalid url.  make sure date is correct")
    else:
        raise

startIndex = html.find("game_data_directory", html.find(team)) + 21
endIndex = html.find("league", startIndex)-10
html = html[startIndex:endIndex]

gdURL = "http://gd2.mlb.com" + html + "/boxscore.xml"

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


homeTeam = re.search('home_sname="(\w*)"', gameday).group(1)

if not homeTeam:
    sys.exit("could not find hometeam")

if homeTeam == "Baltimore":
    gameday = gameday[gameday.find('batting team_flag="home"'):
                      gameday.find('pitching team_flag="home"')]
else:
    gameday = gameday[gameday.find('batting team_flag="home"'):]

match = re.findall('name_display_first_last="(\w* \w*)"', gameday)

if not match:
    sys.exit("could not match lineup on gameday")

i = 0

while i<9:
    print(match[i])
    i+=1
































