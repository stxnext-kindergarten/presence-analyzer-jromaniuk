# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods, invalid-name
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

    def test_mainpage(self):
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

    def test_user_mean_time_weekday_view__should_use_not_existing_user__result_is_404_http_exception(self): # pylint: disable=line-too-long
        """
        Test user mean time weekday on non existing user
        """
        resp = self.client.get(
            '/api/v1/mean_time_weekday/9',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp.status_code, 404)

    def test_user_mean_time_weekday_view__should_rise_no_xhr_before_no_user__result_is_501_http_exception(self): # pylint: disable=line-too-long
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

    def test_presence_weekday_view__should_retrieve_presence_data__result_is_a_extended_weekday_list(self): # pylint: disable=line-too-long
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

    def test_presence_weekday_view__should_rise_no_xhr_before_no_user__result_is_501_http_exception(self): # pylint: disable=line-too-long
        """
        Test user presence weekday
        """
        resp = self.client.get(
            '/api/v1/presence_weekday/9',
            headers={}
        )
        self.assertEqual(resp.status_code, 501)

    def test_presence_weekday_view__should_use_not_existing_user_result_is_404_http_exception(self):
        """
        Test user mean time weekday on non existing user
        """
        resp = self.client.get(
            '/api/v1/presence_weekday/9',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(resp.status_code, 404)


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
