from parser import DataParser
from datetime import datetime, timedelta
from pymongo import MongoClient
from requests import get

class Updater():

    def __init__(self, credentials=None):
        self.users = [] # list of weather stations and passwords
        self.db = MongoClient().weatherlink # link to mongodb database called water
        self.parser = DataParser() # data parser

        # load all weather stations and passwords from file if possible
        if credentials is None:
            pass
        else:
            with open(credentials, 'r') as file:
                for line in file:
                    a = line.split()
                    self.users.append((a[0], a[1]))

    def last_updated(self, ws):
        # if weather-data collection is empty, return -1
        if self.db['weather-data'].count() == 0:
            return -1

        last = self.db['weather-data'].find({
            'stationId': ws
        }).sort([
            ("date.year", -1),
            ("date.month", -1),
            ("date.day", -1),
            ("time.hour", -1),
            ("time.minute", -1)
        ])

        # if result the result of the search query is empty, return -1
        if last.count() == 0:
            return -1

        # return the date and time of the last update
        return {
            'date': last[0]['date'],
            'time': last[0]['time']
        }

    def update_all(self):
        for u in [user[0] for user in self.users]:
            self.update_one(u)

    def update_one(self, ws):
        if ws in [user[0] for user in self.users]:
            recent = self.last_updated(ws)
            print('Updating {str}'.format(str=ws), flush=True)

            user_dt = [user for user in self.users if ws in user][0]

            if recent == -1:
                with open('bin/wd-{str}'.format(str=ws), 'wb') as file:
                    headers = get('http://weatherlink.com/webdl.php?timestamp=0&user={u}&pass={p}&action=headers'.format(u=user_dt[0], p=user_dt[1]))
                    response = get('http://weatherlink.com/webdl.php?timestamp=0&user={u}&pass={p}&action=data'.format(u=user_dt[0], p=user_dt[1]))
                    file.write(response.content)
                    self.db['weather-data'].insert_many(self.parser.parse('bin/wd-{str}'.format(str=ws), ws)) # insert to the 'weather-data' collection
                    print('{str} has been updated'.format(str=ws), flush=True)
            else:
                timedatestamp = self.generate_next_timedatestamp(
                    recent['date']['year'],
                    recent['date']['month'],
                    recent['date']['day'],
                    recent['time']['hour'],
                    recent['time']['minute']
                )
                with open('bin/wd-{str}'.format(str=ws), 'wb') as file:
                    headers = get('http://weatherlink.com/webdl.php?timestamp={ts}&user={u}&pass={p}&action=headers'.format(ts=timedatestamp, u=user_dt[0], p=user_dt[1]))
                    response = get('http://weatherlink.com/webdl.php?timestamp={ts}&user={u}&pass={p}&action=data'.format(ts=timedatestamp, u=user_dt[0], p=user_dt[1]))
                    file.write(response.content)
                    data = self.parser.parse('bin/wd-{str}'.format(str=ws), ws)
                    if len(data) == 0:
                        print('{str} is already up-to-date'.format(str=ws), flush=True)
                    else:
                        self.db['weather-data'].insert_many(data) # insert to the 'weather-data' collection
                        print('{str} has been updated'.format(str=ws), flush=True)
        else:
            print('"{s}"'.format(s=ws) + ' not found in list of weather stations', flush=True)

    def generate_timedatestamp(self, year, month, day, hour, minute):
        # get hex string of datestamp
        date_stamp = format(day + month*32 + (year-2000)*512, '04X')

        # get hex string of timestamp
        time_stamp = format(100*hour + minute, '04X')

        # concatenate date_stamp and time_stamp and return its decimal notation
        return int(date_stamp + time_stamp, 16)

    def generate_next_timedatestamp(self, year, month, day, hour, minute):
        next = datetime(year, month, day, hour, minute) + timedelta(minutes=15)
        return self.generate_timedatestamp(next.year, next.month, next.day, next.hour, next.minute)
