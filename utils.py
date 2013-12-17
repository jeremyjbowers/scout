#!/usr/bin/env python
import csv
import time

from bs4 import BeautifulSoup
from pymongo import MongoClient, DESCENDING
import requests

BASE_URL = 'http://scouts.baseballhall.org/adsearch'
STATES = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

client = MongoClient()
db = client.apps
scouting_reports = db.scouting_reports
scouting_reports.create_index([
    ('player.last_name', DESCENDING),
    ('year', DESCENDING),
    ('scout.last_name', DESCENDING),
    ('player.state', DESCENDING)
])
wazer_wine = db.wazer_wine
wazer_wine.create_index([
    ('location', DESCENDING),
    ('producer', DESCENDING),
    ('year', DESCENDING),
    ('classification', DESCENDING),
    ('wine_type', DESCENDING)
])

def load_wines():
    wazer_wine.remove()
    r = requests.get('https://docs.google.com/spreadsheet/pub?key=0AkYn1TPmL58XdDBUMUJabDdueXVWcnNzM2NwQVkxV1E&output=csv')
    with open('wazer.csv', 'wb') as writefile:
        writefile.write(r.content)

    with open('wazer.csv', 'rb') as readfile:
        wazer_reader = csv.DictReader(readfile)
        for row in wazer_reader:
            wazer_wine.insert(row)


def load_reports():
    borked = 0
    updated = 0
    empty_reports = scouting_reports.find({"report_url": None})
    s = requests.Session()
    for report in empty_reports:
        report_url = 'http://scouts.baseballhall.org/%s' % report['link'].split('&playerid=')[0]
        time.sleep(1)
        print report_url
        r = s.get(report_url)
        if r.status_code != 200:
            borked += 1
            print '-'
        else:
            soup = BeautifulSoup(r.content)
            report['report_url'] = 'http://scouts.baseballhall.org%s' % soup.select('#content img')[0]['src']
            unique_dict = {'report_id': report['report_id']}
            scouting_reports.update(unique_dict, report, upsert=True, multi=False)
            updated += 1
            print '+'

    print "Updated: %s\nBorked: %s" % (updated, borked)


def load_players():
    borked = 0
    updated = 0
    for state in STATES:
        if scouting_reports.find({"player.state": state}).count() == 0:
            payload = {
                'playername': '',
                'scoutname': '',
                'birthloc': '',
                'birthstate': state,
                'school': '',
                'form_id': '619303',
                'submit': 'Search',
            }
            time.sleep(5)
            print '%s.' % state

            r = requests.post(BASE_URL, data=payload)
            if r.status_code != 200:
                print '-'
                borked += 1
            else:
                soup = BeautifulSoup(r.content)
                results = soup.select('table.results tr')[1:]

                for row in results:
                    report_dict = {}
                    report_dict['link'] = row.select('td a')[0]['href']
                    report_dict['report_id'] = row.select('td a')[0]['href'].split('reportid=')[1].split('&')[0]
                    report_dict['year'] = None
                    report_dict['report_url'] = None
                    try:
                        report_dict['year'] = int(row.select('td a')[2].string)
                    except:
                        pass

                    report_dict['player'] = {}
                    report_dict['player']['first_name'] = row.select('td a')[0].string.split(', ')[1]
                    report_dict['player']['last_name'] = row.select('td a')[0].string.split(', ')[0]
                    report_dict['player']['player_id'] = row.select('td a')[0]['href'].split('playerid=')[1]
                    report_dict['player']['state'] = state

                    unique_dict = {'report_id': report_dict['report_id']}
                    scouting_reports.update(unique_dict, report_dict, upsert=True, multi=False)

                    print '> %s (%s): %s %s (%s)' % (
                        report_dict['report_id'],
                        report_dict['year'],
                        report_dict['player']['first_name'],
                        report_dict['player']['last_name'],
                        report_dict['player']['state']
                    )
                updated += 1
    print "Updated: %s\nBorked: %s" % (updated, borked)
