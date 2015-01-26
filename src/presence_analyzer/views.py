# -*- coding: utf-8 -*-
"""
Defines views.
"""
import calendar
import logging

from flask import redirect, abort, request, render_template
from presence_analyzer.main import app
from presence_analyzer.utils import(
    avg_time_weekday,
    get_data,
    get_users_data,
    group_by_weekday,
    group_by_weekday_start_end,
    jsonify,
    mean
)
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday.html')


@app.route('/<tab>.html')
def index(tab):
    """
    Renders template.
    """
    tabs = {
        'presence_weekday': 'Presence by weekday',
        'mean_time_weekday': 'Mean time weekday',
        'presence_start_end': 'Presence start-end',
    }

    if tab not in tabs:
        log.debug('Page %s not found!', tab)
        abort(404)

    return render_template("base.html", tab=tab, tabs=tabs)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    if not request.is_xhr:
        log.debug('Not xhr request')
        abort(501)

    data = get_data()
    user_data = get_users_data()
    return [
        {'user_id': i, 'name': user_data.get(i).get('name'), 'avatar': user_data.get(i).get('avatar')}
        for i in data.keys() if user_data.get(i)
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()

    if not request.is_xhr:
        log.debug('Not xhr request')
        abort(501)

    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()

    if not request.is_xhr:
        log.debug('Not xhr request')
        abort(501)

    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Return timeline data.
    """
    data = get_data()
    result = avg_time_weekday(
        group_by_weekday_start_end(data[user_id])
    )

    return result
