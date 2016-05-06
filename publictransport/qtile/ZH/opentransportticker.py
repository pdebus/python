#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import base
import datetime
import requests
import time

QUERY_URL = 'http://transport.opendata.ch/v1/connections?'
PARAMS = '&direct=1&limit=2'
FROMFIELDS = '&fields[]=connections/from/departureTimestamp&fields[]=connections/from/station'
TOFIELDS = '&fields[]=connections/to/arrivalTimestamp&fields[]=connections/to/station'


class OpenTransportTicker(base.ThreadedPollText):
    ''' Prints out next connections from chosen location to chosen destination
        based on Opentransport data for Zurich
    '''

    defaults = [
        (
            'update_interval',
            300,
            'Update time in seconds'
        ),
        (
            'start_dest_list',
            ['008591256:008591123','008591272:008591122'],
            "List of start and destination pairs, e.g.['008591256:008591123','008591272:008591122']"
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
        query = QUERY_URL + "from=" + start + "&to=" + dest + PARAMS + FROMFIELDS + TOFIELDS

        try:
            result = requests.get(query).json()['connections']
        except Exception:
            # HTTPError? JSON Error? KeyError? Doesn't matter, return None
            return None

        data = ''
        for c in result:
            src = c['from']['station']['name']
            dep = datetime.datetime.fromtimestamp(c['from']['departureTimestamp']).strftime('%H:%M')
            delta = c['from']['departureTimestamp']-time.time()
            if delta<1800: 
                mins = "(" + str(int(delta / 60)) + str("')")
            else:
                mins = ""
            tgt = c['to']['station']['name']
            arr = datetime.datetime.fromtimestamp(c['to']['arrivalTimestamp']).strftime('%H:%M')
            data += src + ", " + str(dep) + mins + " > " + tgt + ", " + str(arr) + "\n"
        return data[:-1]
