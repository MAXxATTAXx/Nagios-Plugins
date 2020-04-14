#!/usr/bin/env python
#  coding=utf-8
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2017-11-25 20:29:31 +0100 (Sat, 25 Nov 2017)
#
#  https://github.com/harisekhon/nagios-plugins
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Nagios Plugin to check a Logstash instance event parsing time in millisenconds

Outputs the average parsing time in milliseconds for all events, from input to output.

Ensure Logstash options:
  --http.host should be set to 0.0.0.0 if querying remotely
  --http.port should be set to the same port that you are querying via this plugin's --port switch

Tested on Logstash 6.8

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import traceback
srcdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(srcdir, 'pylib')
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon import RestNagiosPlugin
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'MAXxATTAXx'
__version__ = '0.1'


class CheckLogstashEventsLatency(RestNagiosPlugin):

    def __init__(self):
        # Python 2.x
        super(CheckLogstashEventsLatency, self).__init__()
        # Python 3.x
        # super().__init__()
        self.name = 'Logstash'
        self.default_port = 9600
        # could add pipeline name to end of this endpoint but error would be less good 404 Not Found
        # Logstash 5.x /_node/pipeline <= use -5 switch for older Logstash
        # Logstash 6.x /_node/pipelines
        self.path = '/_node/stats/events'
        self.auth = False
        self.json = True
        self.msg = 'Logstash starts reloads msg not defined yet'

    def add_options(self):
        super(CheckLogstashEventsLatency, self).add_options()
        self.add_thresholds(default_warning=75, default_critical=100)

    def process_options(self):
        super(CheckLogstashEventsLatency, self).process_options()
        self.validate_thresholds(integer=False, optional=True)

    def parse_json(self, json_data):
        events = json_data['events']
        out_events = events['out']
        time_millis = events['duration_in_millis'] / out_events if out_events > 0 else 0
        self.msg = 'Logstash avg parsing time = {0:.4f}ms'.format(time_millis)
        self.check_thresholds(time_millis)
        self.msg += ' | event_parsing_time={0:.4f}ms'.format(time_millis)
        self.msg += '{}'.format(self.get_perf_thresholds())

if __name__ == '__main__':
    CheckLogstashEventsLatency().main()
