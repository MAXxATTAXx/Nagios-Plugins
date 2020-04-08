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

Nagios Plugin to check a Logstash instance total number of config reloads

Outputs total reloads since service startup to which optional thresholds
can be set to alert on.

When using --success it will output total succesful reloads and the optional
thesholds will be applied to this metric only

When using --failure it will output total failed reloads and the optional
thesholds will be applied to this metric only

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


class CheckLogstashConfigReloads(RestNagiosPlugin):

    def __init__(self):
        # Python 2.x
        super(CheckLogstashConfigReloads, self).__init__()
        # Python 3.x
        # super().__init__()
        self.name = 'Logstash'
        self.default_port = 9600
        # could add pipeline name to end of this endpoint but error would be less good 404 Not Found
        # Logstash 5.x /_node/pipeline <= use -5 switch for older Logstash
        # Logstash 6.x /_node/pipelines
        self.path = '/_node/stats/reloads'
        self.auth = False
        self.json = True
        self.msg = 'Logstash starts reloads msg not defined yet'

    def add_options(self):
        super(CheckLogstashConfigReloads, self).add_options()
        self.add_opt('--successes', action='store_true',
                     help='Test successful reloads of config files' + \
                          ' instead of the total')
        self.add_opt('--failures', action='store_true',
                     help='Test failed reloads of config files' + \
                          ' instead of the total')
        self.add_thresholds()

    def process_options(self):
        super(CheckLogstashConfigReloads, self).process_options()
        self.validate_thresholds(optional=True)

    def parse_json(self, json_data):
        reloads = json_data['reloads']
        successes = reloads['successes']
        failures = reloads['failures']
        total_reloads = successes + failures
        self.msg = 'Logstsh '
        if self.get_opt('successes'):
            self.msg = 'successful reloads = {}'.format(successes)
            self.check_thresholds(successes)
        elif self.get_opt('failures'):
            self.msg = 'failed reloads = {}'.format(failures)
            self.check_thresholds(failures)
        else:
            self.msg = 'total reloads = {}'.format(total_reloads)
            self.check_thresholds(total_reloads)

if __name__ == '__main__':
    CheckLogstashConfigReloads().main()
