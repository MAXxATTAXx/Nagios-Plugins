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

Nagios Plugin to check a Logstash pipeline event idle time in millisenconds

Outputs the amount of time a logstash pipeline spent waiting for a worker to process an event.

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
    from harisekhon.utils import ERRORS
    from harisekhon.utils import validate_chars
    from harisekhon import RestNagiosPlugin
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'MAXxATTAXx'
__version__ = '0.1'


class CheckLogstashPipelineLatency(RestNagiosPlugin):

    def __init__(self):
        # Python 2.x
        super(CheckLogstashPipelineLatency, self).__init__()
        # Python 3.x
        # super().__init__()
        self.name = 'Logstash'
        self.default_port = 9600
        # could add pipeline name to end of this endpoint but error would be less good 404 Not Found
        # Logstash 5.x /_node/pipeline <= use -5 switch for older Logstash
        # Logstash 6.x /_node/pipelines
        self.path = '/_node/stats/pipelines'
        self.auth = False
        self.json = True
        self.msg = 'Logstash starts reloads msg not defined yet'
        self.pipeline = None


    def add_options(self):
        super(CheckLogstashPipelineLatency, self).add_options()
        self.add_opt('-i', '--pipeline', default='main', help='Pipeline to expect is configured (default: main)')
        self.add_opt('-l', '--list', action='store_true', help='List pipelines and exit (only for Logstash 6+)')
        self.add_thresholds(default_warning=75, default_critical=100)

    def process_options(self):
        super(CheckLogstashPipelineLatency, self).process_options()
        self.pipeline = self.get_opt('pipeline')
        validate_chars(self.pipeline, 'pipeline', 'A-Za-z0-9_-')
        self.validate_thresholds(optional=True)

    def parse_json(self, json_data):
        pipelines = json_data['pipelines']
        if self.get_opt('list'):
            print('Logstash Pipelines:\n')
            for pipeline in pipelines:
                print(pipeline)
            sys.exit(ERRORS['UNKNOWN'])
        pipeline = None
        if self.pipeline in pipelines:
            pipeline = pipelines[self.pipeline]
        self.msg = "Logstash pipeline '{}' ".format(self.pipeline)
        if pipeline:
            events = pipeline['events']
            events_time = self.calculate_time(events['queue_push_duration_in_millis'], events['out'])

            self.msg += 'avg wait time = {0:.4f}ms'.format(events_time)
            self.check_thresholds(events_time)
            self.msg += ' | event_wait_time={0:.4f}ms'.format(events_time)
            self.msg += '{}'.format(self.get_perf_thresholds())
        else:
            self.critical()
            self.msg += 'does not exist!'

    @staticmethod
    def process_plugins(memo, plugin):
        return {
            'time': plugin['events']['duration_in_millis'] + memo['time'],
            'events': plugin['events']['out'] + memo['events']
        }

    @staticmethod
    def calculate_time(time, events):
        return time/events if events > 0 else 0

if __name__ == '__main__':
    CheckLogstashPipelineLatency().main()
