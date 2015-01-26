# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""
import csv
import logging
import pdb
import requests
import os
import time

from datetime import datetime
from flask import Response
from functools import wraps, partial
from json import dumps
from presence_analyzer.main import app
from xml.etree import ElementTree as etree
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def get_users_data():
    """
    Get User data from xml.
    :return dict:
    """
    root = etree.parse(app.config['USERS_DATA'])
    server = root.find('server')
    port = server.find('port').text  # pylint: disable=no-member
    protocol = server.find('protocol').text  # pylint: disable=no-member
    host = server.find('host').text  # pylint: disable=no-member
    users = {}
    for user in root.iter('user'):
        id = int(user.get('id'))
        name = user.find('name').text.encode('utf-8')
        url = user.find('avatar').text.encode('utf-8')
        avatar = "{0}://{1}:{2}{3}".format(protocol, host, port, url)
        users[id] = {
            'name': name,
            'avatar': avatar
        }
    return users


def download_users_xml():
    """
    Download file.
    """
    root_dir = os.path.dirname(os.path.realpath(__file__))
    DEBUG_CFG = os.path.join('{0}/../../'.format(root_dir),'parts', 'etc', 'debug.cfg')
    app.config.from_pyfile(DEBUG_CFG)
    url = app.config['USERS_DATA_EXTERNAL']
    r = requests.get(url)
    with open(app.config['USERS_DATA'], 'w') as f:
        f.write(r.text.encode('ISO-8859-1'))


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_by_weekday_start_end(items):
    """
    Groups presence entries by weekday.
    """
    result = {}  # one list for every day in week

    for date in items:
        start, end = items[date]['start'], items[date]['end']
        if date.weekday() not in result:
            result[date.weekday()] = {
                'weekday': date.strftime("%a"),
                'start': [],
                'end': []
            }
        result[date.weekday()]['start'].append(seconds_since_midnight(start))
        result[date.weekday()]['end'].append(seconds_since_midnight(end))

    return result


def avg_time_weekday(items):
    """
    Count avg for Groups presence entries by weekday.
    """
    for day in items.values():
        day['start'] = stringify_average_date(day['start'])
        day['end'] = stringify_average_date(day['end'])
    return items


def stringify_average_date(list):
    """
    Stringify avg date
    """
    return time.strftime("%Y %m %d %H:%M:%S", time.gmtime(mean(list)))


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
