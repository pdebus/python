#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import base
import requests
import time

MVGAPI = "https://www.mvg.de/fahrinfo/api/"
MVGROUTING = "routing/"
MVGAPISTATION = "location/query"
MVGAUTHKEY = "5af1beca494712ed38d313714d4caff6"

HEADERS = {
            'Accept': "application/json, text/javascript, *'.'/*; q=0.01",
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
            'X-MVG-Authorization-Key': MVGAUTHKEY            
            }


class OpenTransportTicker(base.ThreadedPollText):
    ''' Prints out next connections from chosen location to chosen destination
        based on MVG JSON API
    '''

    defaults = [
        (
            'update_interval',
            300,
            'Update time in seconds'
        ),
        (
            'start_dest_list',
            ['40:1260'],
            "List of start and destination pairs, e.g.['40:1260']"
       ),
       (
            'selected_pair',
            0,
            'Initially selected start/destination pair'
        ), 
    ]


    def __init__(self, **config):
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(OpenTransportTicker.defaults)

    def button_press(self, x, y, button):
        if button == 1:
            self.next_Connection()

    def next_Connection(self):
        self.selected_pair = (self.selected_pair + 1) % len(self.start_dest_list)
        self.update(self.poll())

    def poll(self):
        start = self.start_dest_list[self.selected_pair].split(":")[0]
        dest = self.start_dest_list[self.selected_pair].split(":")[1]
        query = MVGAPI + MVGROUTING + "?fromStation=" + start + "&toStation=" + dest

        try:
            result = requests.get(query, headers=HEADERS).json()['connectionList']
        except Exception:
            # HTTPError? JSON Error? KeyError? Doesn't matter, return None
            return None

        data = ''
        numOfConnections = 0
        for c in result:
            src = c['from']['name']
            dep = time.strftime("%H:%M", time.localtime(int(c['departure']) / 1000))
            delta = int(c['departure']) / 1000 -int(time.mktime(time.localtime()))
            if delta < 1800 and delta > 0: 
                mins = "(" + str(int(delta / 60)) + str("')")
            else:
                mins = ""
            tgt = c['to']['name']
            arr = time.strftime("%H:%M", time.localtime(int(c['arrival']) / 1000))
            if delta > 0:
                data += src + ", " + str(dep) + mins + " > " + tgt + ", " + str(arr) + "\n"
                numOfConnections += 1
            if numOfConnections >= 2:
                break

        return data[:-1]
