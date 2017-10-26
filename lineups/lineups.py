import sys
import re
import urllib.request

#getting input from user
#assuming for now the team is baltimore orioles

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


scoreboard = "http://gd2.mlb.com/components/game/mlb/year_" + year + "/month_" + month + "/day_" + day + "/scoreboard_windows.xml"

print (scoreboard)

with urllib.request.urlopen(scoreboard) as response:
    html = response.read()

if not html:
    sys.exit("error invalid url.  invalid date?")








































