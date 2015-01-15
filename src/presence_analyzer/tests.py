# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from flask import Response
from presence_analyzer import main, utils, views

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods, invalid-name, line-too-long
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage__should_change_location__result_is_redirect_with_302_status_code(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users_view__should_call_xhr_request__result_is_users_list(self):
        """
        Test users listing.
        """
        resp = self.client.get(
            '/api/v1/users',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_users_view__should_call_not_xhr_request__result_is_501_http_exception(self):
        """
        Test users view
        """
        resp = self.client.get(
            '/api/v1/users',
            headers={}
        )
        self.assertEqual(resp.status_code, 501)

    def test_user_mean_time_weekday_view__should_use_not_existing_user__result_is_404_http_exception(self):
        """
        Test user mean time weekday on non existing user
        """
        resp = self.client.get(
            '/api/v1/mean_time_weekday/9',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp.status_code, 404)

    def test_user_mean_time_weekday_view__should_rise_no_xhr_before_no_user__result_is_501_http_exception(self):
        """
        Test user mean time weekday
        """
        resp = self.client.get(
            '/api/v1/mean_time_weekday/9',
            headers={}
        )
        self.assertEqual(resp.status_code, 501)

    def test_user_mean_time_weekday_view__should_use_existing_user__result_is_a_weekday_list(self):
        """
        Test user mean time weekday
        """
        resp = self.client.get(
            '/api/v1/mean_time_weekday/10',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        data = json.loads(resp.data)
        result = [x[0] for x in data]
        expected = [u"Mon", u"Tue", u"Wed", u"Thu", u"Fri", u"Sat", u"Sun"]
        self.assertListEqual(expected, result)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

    def test_presence_weekday_view__should_retrieve_presence_data__result_is_a_extended_weekday_list(self):
        """
        Test user presence weekday
        """
        resp = self.client.get(
            '/api/v1/presence_weekday/10',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        data = json.loads(resp.data)
        result = [x[0] for x in data]
        expected = [u"Weekday", u"Mon", u"Tue", u"Wed", u"Thu", u"Fri", u"Sat", u"Sun"]
        self.assertListEqual(expected, result)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

    def test_presence_weekday_view__should_rise_no_xhr_before_no_user__result_is_501_http_exception(self):
        """
        Test user presence weekday
        """
        resp = self.client.get(
            '/api/v1/presence_weekday/9',
            headers={}
        )
        self.assertEqual(resp.status_code, 501)

    def test_presence_weekday_view__should_use_not_existing_user__result_is_404_http_exception(self):
        """
        Test user mean time weekday on non existing user
        """
        resp = self.client.get(
            '/api/v1/presence_weekday/9',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp.status_code, 404)

    def test_presence_start_end_view__should_use_existing_user__result_is_start_end_list(self):
        """
        Test user presence weekday
        """
        resp = self.client.get(
            '/api/v1/presence_start_end/10',
            headers={}
        )
        result = json.loads(resp.data)
        expected = {
            u'1': {u'start': u'1970 01 01 09:39:05', u'end': u'1970 01 01 17:59:52', u'weekday': u'Tue'},
            u'2': {u'start': u'1970 01 01 09:19:52', u'end': u'1970 01 01 16:07:37', u'weekday': u'Wed'},
            u'3': {u'start': u'1970 01 01 15:18:46', u'end': u'1970 01 01 18:53:51', u'weekday': u'Thu'}

        }
        self.assertDictEqual(expected, result)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_jsonify(self):
        """
        Test jsonify
        """
        @utils.jsonify
        def test():
            """
            Test function
            """
            return "test"
        result = test()
        expected = '"test"'
        self.assertIsInstance(result, Response)
        self.assertEqual(result.headers[0], ('Content-Type', u'application/json'))
        self.assertEqual(expected, result.response[0])

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday__should_calculate_start_end_interval__result_is_list_of_intervals(self):
        """
        Test group by weekday
        """
        date1 = datetime.date(2000, 1, 1)
        start1 = datetime.time(0, 0, 10)
        end1 = datetime.time(0, 0, 30)
        date2 = datetime.date(2000, 1, 8)
        start2 = datetime.time(0, 0, 20)
        end2 = datetime.time(0, 0, 40)
        data = {
            date1: {'start': start1, 'end': end1},
            date2: {'start': start2, 'end': end2}
        }

        result = utils.group_by_weekday(data)
        expected = [[], [], [], [], [], [20, 20], []]

        self.assertListEqual(expected, result)

    def test_group_by_weekday_start_end__should_group_by_weekday__result_dict_of_integers_per_weekday(self):
        """
        Test group by weekday start end
        """
        date1 = datetime.date(2000, 1, 1)
        start1 = datetime.time(0, 0, 10)
        end1 = datetime.time(0, 0, 30)
        date2 = datetime.date(2000, 1, 8)
        start2 = datetime.time(0, 0, 20)
        end2 = datetime.time(0, 0, 40)
        data = {
            date1: {'start': start1, 'end': end1},
            date2: {'start': start2, 'end': end2}
        }
        result = utils.group_by_weekday_start_end(data)
        expected = {5: {'weekday': 'Sat', 'start': [10, 20], 'end': [30, 40]}}
        self.assertDictEqual(result, expected)

    def test_avg_time_weekday__should_convert_list_of_datetime_to_weekday_avg__result_is_dict_of_avg_datetime(self):
        """
        Test avg time weekday
        """
        dates = {1: {'weekday': 1, 'start': [10, 20], 'end': [30, 40]}}
        result = utils.avg_time_weekday(dates)
        expected = {1: {'weekday': 1, 'start': "1970 01 01 00:00:15", 'end': "1970 01 01 00:00:35"}}
        self.assertDictEqual(expected, result)

    def test_seconds_since_midnight__should_transform_time_to_seconds__result_is_number_of_seconds(self):
        """
        Test seconds since midnight
        """
        time = datetime.time(0, 1, 10)
        result = utils.seconds_since_midnight(time)
        expected = 70
        self.assertEqual(expected, result)

    def test_interval__should_subtract_two_dates__result_is_number_of_seconds(self):
        """
        Test interval
        """
        start = datetime.datetime(1999, 12, 01, 0, 0, 1)
        end = datetime.datetime(1999, 12, 01, 0, 2, 1)
        result = utils.interval(start, end)
        expected = 120
        self.assertEqual(expected, result)

    def test_mean__should_add_all_list_elements_and_divide_sum_by_list_length__result_is_f_average(self):
        """
        Test mean.
        """
        result = utils.mean([1, 2, 3])
        expected = 2.0
        self.assertEqual(type(result), type(expected))
        self.assertEqual(result, expected)

    def test_mean__should_get_empty_list__result_is_avarage_equal_zero(self):
        """
        Test mean.
        """
        result = utils.mean([])
        expected = 0
        self.assertEqual(expected, result)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
