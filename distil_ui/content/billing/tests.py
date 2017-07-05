# Copyright (c) 2017 Catalyst IT Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import datetime
import json

from freezegun import freeze_time
import mock
from mox3 import mox

from distil_ui.content.billing import base
from distil_ui.content.billing import views
from django.utils import timezone
from horizon import forms
from openstack_dashboard.test import helpers as test

BILLITEM = collections.namedtuple('BillItem',
                                  ['id', 'resource', 'count', 'cost'])

FAKE_COST = [{'total_cost': 617.0, 'details': [{'quantity': 744.0, 'resource_name': '150.242.40.138', 'cost': 4.46, 'product': 'NZ-POR-1.n1.ipv4', 'rate': 0.006, 'unit': 'Hour(s)'}, {'quantity': 744.0, 'resource_name': '150.242.40.139', 'cost': 4.46, 'product': 'NZ-POR-1.n1.ipv4', 'rate': 0.006, 'unit': 'Hour(s)'}], 'breakdown': {'Network': 9.64}, 'paid': True, 'date': '2016-08-31', 'status': 'open'}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2016-09-30', 'status': None}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2016-10-31', 'status': None}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2016-11-30', 'status': None}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2016-12-31', 'status': None}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2017-01-31', 'status': None}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2017-02-28', 'status': None}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2017-03-31', 'status': None}, {'total_cost': 0, 'details': [], 'breakdown': {}, 'paid': True, 'date': '2017-04-30', 'status': None}, {'total_cost': 653.0, 'details': [{'quantity': 7440.0, 'resource_name': 'docker - root disk', 'cost': 3.72, 'product': 'NZ-POR-1.b1.standard', 'rate': 0.0005, 'unit': 'Gigabyte-hour(s)'}, {'quantity': 23808.0, 'resource_name': 'docker_tmp', 'cost': 11.9, 'product': 'NZ-POR-1.b1.standard', 'rate': 0.0005, 'unit': 'Gigabyte-hour(s)'}, {'quantity': 7440.0, 'resource_name': 'postgresql - root disk', 'cost': 3.72, 'product': 'NZ-POR-1.b1.standard', 'rate': 0.0005, 'unit': 'Gigabyte-hour(s)'}, {'quantity': 14880.0, 'resource_name': 'dbserver_dbvol', 'cost': 7.44, 'product': 'NZ-POR-1.b1.standard', 'rate': 0.0005, 'unit': 'Gigabyte-hour(s)'}, {'quantity': 37200.0, 'resource_name': 'server_dockervol', 'cost': 18.6, 'product': 'NZ-POR-1.b1.standard', 'rate': 0.0005, 'unit': 'Gigabyte-hour(s)'}, {'quantity': 37200.0, 'resource_name': 'docker_uservol', 'cost': 18.6, 'product': 'NZ-POR-1.b1.standard', 'rate': 0.0005, 'unit': 'Gigabyte-hour(s)'}, {'quantity': 23808.0, 'resource_name': 'docker_swap', 'cost': 11.9, 'product': 'NZ-POR-1.b1.standard', 'rate': 0.0005, 'unit': 'Gigabyte-hour(s)'}], 'breakdown': {'Block Storage': 75.88}, 'paid': True, 'date': '2017-05-31', 'status': 'paid'}, {'total_cost': 689.0, 'details': [{'quantity': 744.0, 'resource_name': 'postgresql', 'cost': 184.51, 'product': 'NZ-POR-1.c1.c4r8', 'rate': 0.248, 'unit': 'Hour(s)'}, {'quantity': 744.0, 'resource_name': 'docker', 'cost': 582.55, 'product': 'NZ-POR-1.c1.c8r32', 'rate': 0.783, 'unit': 'Hour(s)'}], 'breakdown': {'Compute': 767.06}, 'paid': True, 'date': '2017-06-30', 'status': 'paid'}, {'details': [{'quantity': 30000.0, 'resource_name': 'new_instance', 'cost': 15.0, 'product': 'REGIONTWO.b1.standard', 'rate': 0.0005, 'unit': 'second', 'resource_id': '22'}, {'quantity': 200, 'resource_name': 'my_block', 'cost': 2, 'product': 'REGIONONE.b1.standard', 'rate': 0.01, 'unit': 'hour', 'resource_id': '8'}, {'quantity': 30000.0, 'resource_name': 'my_instance', 'cost': 15.0, 'product': 'REGIONONE.b1.standard', 'rate': 0.0005, 'unit': 'second', 'resource_id': '2'}, {'quantity': 30000.0, 'resource_name': 'other_instance', 'cost': 15.0, 'product': 'REGIONONE.b1.standard', 'rate': 0.0005, 'unit': 'second', 'resource_id': '3'}, {'quantity': 50000.0, 'resource_name': 'my_container', 'cost': 13.5, 'product': 'NZ.o1.standard', 'rate': 0.00027, 'unit': 'gigabyte', 'resource_id': '1'}], 'status': None, 'date': '2017-07-10', 'breakdown': {'Virtual Machine': 30.0, 'Network': 2, 'Object Storage': 13.5}, 'total_cost': 60.5}]  # noqa

FAKE_CREDITS = {'credits': [{'code': 'a9iberAn', 'type': 'Cloud Trial Credit', 'expiry_date': '2017-09-30', 'balance': 300.0, 'recurring': False, 'start_date': '2017-08-02 22:16:28'}]}  # noqa


class FakeUser(object):
    roles = [{'name': 'admin'}]
    authorized_tenants = ["tenant_name"]
    tenant_id = "fake_project_id"

    def is_authenticated(self):
        return True


class FakeRequest(object):
    def _get(x, y):
        if x == 'format' and y == 'html':
            return 'csv'
        return None

    def is_ajax(self):
        return False

    user = FakeUser()
    session = mock.MagicMock()
    GET = mock.MagicMock()
    GET.get = _get


class BaseBillingTests(test.TestCase):
    """FIXME(flwang): Move this test to rest_api_tests.py

    Now we're putting the api test at here, since we don't want to hack
    horizon too much. That means we don't want to put the api.py under /api
    folder, at least for now.
    """

    def setUp(self):
        super(BaseBillingTests, self).setUp()
        self.mocker = mox.Mox()
        self.billing = base.BaseBilling(FakeRequest(), 'my_project_id')
        self.year = 2017
        self.month = 1
        self.day = 30

    def test_today(self):
        delta = datetime.timedelta(seconds=1)
        self.assertTrue(self.billing.today - timezone.now() < delta)

    def test_get_start(self):
        start = datetime.datetime(self.year, self.month, self.day, 0, 0, 0)
        self.assertEqual(self.billing.get_start(self.year, self.month,
                                                self.day),
                         timezone.make_aware(start, timezone.utc))

    def test_get_end(self):
        end = datetime.datetime(self.year, self.month, self.day, 23, 59, 59)
        self.assertEqual(self.billing.get_end(self.year, self.month, self.day),
                         timezone.make_aware(end, timezone.utc))

    def test_get_date_range(self):
        args_start = (self.billing.today.year, self.billing.today.month, 1)
        args_end = (self.billing.today.year, self.billing.today.month,
                    self.billing.today.day)
        start = self.billing.get_start(*args_start)
        end = self.billing.get_end(*args_end)
        self.assertEqual(self.billing.get_date_range(),
                         (start, end))

    @mock.patch('distil_ui.content.billing.base.BaseBilling.get_form')
    def test_get_date_range_valid_form(self, mock_get_form):
        start = datetime.datetime(self.year, self.month, self.day, 0, 0, 0)
        end = datetime.datetime(self.year, self.month, self.day, 23, 59, 59)
        myform = forms.DateForm({'start': start, 'end': end})
        myform.data = {'start': start, 'end': end}
        myform.cleaned_data = {'start': start, 'end': end}
        mock_get_form.return_value = myform
        self.assertEqual(self.billing.get_date_range(),
                         (timezone.make_aware(start, timezone.utc),
                          timezone.make_aware(end, timezone.utc)))

    def test_init_form(self):
        start = datetime.date(self.billing.today.year,
                              self.billing.today.month, 1)
        end = datetime.date.today()
        self.assertEqual(self.billing.init_form(), (start, end))

    def test_get_form(self):
        start = datetime.date(self.billing.today.year,
                              self.billing.today.month, 1).strftime("%Y-%m-%d")
        end = datetime.date.today().strftime("%Y-%m-%d")
        self.assertEqual(self.billing.get_form().initial,
                         {"start": start, "end": end})

    def test_get_billing_list(self):
        self.assertEqual(self.billing.get_billing_list(None, None), [])


class ViewsTests(test.TestCase):
    def setUp(self):
        super(ViewsTests, self).setUp()
        self.project_id = "fake_project_id"
        kwargs = {"project_id": self.project_id}
        self.view = views.IndexView()
        self.view.kwargs = kwargs
        self.view.request = FakeRequest()

    @mock.patch('distil_ui.api.distil_v2.get_cost')
    @mock.patch('distil_ui.api.distil_v2.get_credits')
    @mock.patch('horizon.views.HorizonTemplateView.get_context_data')
    def test_get_context_data(self, mock_get_context_data,
                              mock_get_credits, mock_get_cost):
        mock_get_cost.return_value = FAKE_COST
        mock_get_credits.return_value = FAKE_CREDITS
        mock_get_context_data.return_value = {}
        kwargs = {"project_id": self.project_id}
        context = self.view.get_context_data(**kwargs)

        expect_line_chart_data = [{"values": [{"p": "open",
                                               "x": 0, "y": 617.0},
                                              {"p": None, "x": 1, "y": 0},
                                              {"p": None, "x": 2, "y": 0},
                                              {"p": None, "x": 3, "y": 0},
                                              {"p": None, "x": 4, "y": 0},
                                              {"p": None, "x": 5, "y": 0},
                                              {"p": None, "x": 6, "y": 0},
                                              {"p": None, "x": 7, "y": 0},
                                              {"p": None, "x": 8, "y": 0},
                                              {"p": "paid",
                                               "x": 9, "y": 653.0},
                                              {"p": "paid",
                                               "x": 10, "y": 689.0},
                                              {"p": None,
                                               "x": 11, "y": 60.5}],
                                   "key": "Cost"},
                                  {"values":
                                   [{"x": 0, "y": 178.09},
                                    {"x": 1, "y": 178.09},
                                    {"x": 2, "y": 178.09},
                                    {"x": 3, "y": 178.09},
                                    {"x": 4, "y": 178.09},
                                    {"x": 5, "y": 178.09},
                                    {"x": 6, "y": 178.09},
                                    {"x": 7, "y": 178.09},
                                    {"x": 8, "y": 178.09},
                                    {"x": 9, "y": 178.09},
                                    {"x": 10, "y": 178.09},
                                    {"x": 11, "y": 178.09}],
                                   "key": "Avg Cost", "color": "#fdd0a2"}]
        self.assertDictEqual(json.loads(context["line_chart_data"])[0],
                             expect_line_chart_data[0])

        expect_credits = {"credits": [{"balance": 300.0, "code": "a9iberAn",
                                       "start_date": "2017-08-02 22:16:28",
                                       "expiry_date": "2017-09-30",
                                       "recurring": False,
                                       "type": "Cloud Trial Credit"}]}
        self.assertDictEqual(json.loads(context["credits"]), expect_credits)

        expect_axis = ['Sep 2016', 'Oct 2016', 'Nov 2016', 'Dec 2016',
                       'Jan 2017', 'Feb 2017', 'Mar 2017', 'Apr 2017',
                       'May 2017', 'Jun 2017', 'Jul 2017', 'Aug 2017']
        self.assertEqual(context["x_axis_line_chart"], expect_axis)

    @freeze_time("2017-08-10")
    def test_get_x_axis_for_line_chart(self):
        x_axis = self.view._get_x_axis_for_line_chart()
        expect = ['Sep 2016', 'Oct 2016', 'Nov 2016', 'Dec 2016',
                  'Jan 2017', 'Feb 2017', 'Mar 2017', 'Apr 2017',
                  'May 2017', 'Jun 2017', 'Jul 2017', 'Aug 2017']
        self.assertEqual(x_axis, expect)
