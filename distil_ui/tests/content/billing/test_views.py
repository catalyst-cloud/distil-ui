# Copyright (C) 2017-2024 Catalyst Cloud Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import json

from freezegun import freeze_time
from unittest import mock

from distil_ui.content.billing import views
from openstack_dashboard.test import helpers as test

BILLITEM = collections.namedtuple('BillItem',
                                  ['id', 'resource', 'count', 'cost'])

FAKE_COST = [
    {
        "date": "2016-08-31",
        "total_cost": 617.0,
        "status": "open",
        "paid": True,
        "breakdown": {"Network": 9.64},
        "details": [
            {
                "quantity": 744.0,
                "resource_name": "150.242.40.138",
                "cost": 4.46,
                "cost_taxed": 5.13,
                "product": "NZ-POR-1.n1.ipv4",
                "rate": 0.006,
                "unit": "Hour(s)"
            },
            {
                "quantity": 744.0,
                "resource_name": "150.242.40.139",
                "cost": 4.46,
                "cost_taxed": 5.13,
                "product": "NZ-POR-1.n1.ipv4",
                "rate": 0.006,
                "unit": "Hour(s)"
            },
        ],
    },
    {
        "date": "2016-09-30",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2016-10-31",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2016-11-30",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2016-12-31",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2017-01-31",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2017-02-28",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2017-03-31",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2017-04-30",
        "total_cost": 0,
        "status": None,
        "paid": True,
        "breakdown": {},
        "details": [],
    },
    {
        "date": "2017-05-31",
        "total_cost": 653.0,
        "status": "paid",
        "paid": True,
        "breakdown": {"Block Storage": 75.88},
        "details": [
            {
                "quantity": 7440.0,
                "resource_name": "docker - root disk",
                "cost": 3.72,
                "cost_taxed": 4.28,
                "product": "NZ-POR-1.b1.standard",
                "rate": 0.0005,
                "unit": "Gigabyte-hour(s)",
            },
            {
                "quantity": 23808.0,
                "resource_name": "docker_tmp",
                "cost": 11.9,
                "cost_taxed": 13.69,
                "product": "NZ-POR-1.b1.standard",
                "rate": 0.0005,
                "unit": "Gigabyte-hour(s)",
            },
            {
                "quantity": 7440.0,
                "resource_name": "postgresql - root disk",
                "cost": 3.72,
                "cost_taxed": 4.28,
                "product": "NZ-POR-1.b1.standard",
                "rate": 0.0005,
                "unit": "Gigabyte-hour(s)",
            },
            {
                "quantity": 14880.0,
                "resource_name": "dbserver_dbvol",
                "cost": 7.44,
                "cost_taxed": 8.56,
                "product": "NZ-POR-1.b1.standard",
                "rate": 0.0005,
                "unit": "Gigabyte-hour(s)",
            },
            {
                "quantity": 37200.0,
                "resource_name": "server_dockervol",
                "cost": 18.6,
                "cost_taxed": 21.39,
                "product": "NZ-POR-1.b1.standard",
                "rate": 0.0005,
                "unit": "Gigabyte-hour(s)",
            },
            {
                "quantity": 37200.0,
                "resource_name": "docker_uservol",
                "cost": 18.6,
                "cost_taxed": 21.39,
                "product": "NZ-POR-1.b1.standard",
                "rate": 0.0005,
                "unit": "Gigabyte-hour(s)",
            },
            {
                "quantity": 23808.0,
                "resource_name": "docker_swap",
                "cost": 11.9,
                "cost_taxed": 13.69,
                "product": "NZ-POR-1.b1.standard",
                "rate": 0.0005,
                "unit": "Gigabyte-hour(s)",
            },
        ],
    },
    {
        "date": "2017-06-30",
        "total_cost": 689.0,
        "status": "paid",
        "paid": True,
        "breakdown": {"Compute": 767.06},
        "details": [
            {
                "quantity": 744.0,
                "resource_name": "postgresql",
                "cost": 184.51,
                "cost_taxed": 212.19,
                "product": "NZ-POR-1.c1.c4r8",
                "rate": 0.248,
                "unit": "Hour(s)",
            },
            {
                "quantity": 744.0,
                "resource_name": "docker",
                "cost": 582.55,
                "cost_taxed": 669.93,
                "product": "NZ-POR-1.c1.c8r32",
                "rate": 0.783,
                "unit": "Hour(s)",
            },
        ],
    },
    {
        "date": "2017-07-10",
        "total_cost": 60.5,
        "status": None,
        "breakdown": {
            "Virtual Machine": 30.0,
            "Network": 2,
            "Object Storage": 13.5,
        },
        "details": [
            {
                "quantity": 30000.0,
                "resource_name": "new_instance",
                "cost": 15.0,
                "cost_taxed": 17.25,
                "product": "REGIONTWO.b1.standard",
                "rate": 0.0005,
                "unit": "second",
                "resource_id": "22",
            },
            {
                "quantity": 200,
                "resource_name": "my_block",
                "cost": 2,
                "cost_taxed": 2.3,
                "product": "REGIONONE.b1.standard",
                "rate": 0.01,
                "unit": "hour",
                "resource_id": "8",
            },
            {
                "quantity": 30000.0,
                "resource_name": "my_instance",
                "cost": 15.0,
                "cost_taxed": 17.25,
                "product": "REGIONONE.b1.standard",
                "rate": 0.0005,
                "unit": "second",
                "resource_id": "2",
            },
            {
                "quantity": 30000.0,
                "resource_name": "other_instance",
                "cost": 15.0,
                "cost_taxed": 17.25,
                "product": "REGIONONE.b1.standard",
                "rate": 0.0005,
                "unit": "second",
                "resource_id": "3",
            },
            {
                "quantity": 50000.0,
                "resource_name": "my_container",
                "cost": 13.5,
                "cost_taxed": 15.53,
                "product": "NZ.o1.standard",
                "rate": 0.00027,
                "unit": "gigabyte",
                "resource_id": "1",
            }
        ],
    }
]

FAKE_CREDITS = {
    'credits': [
        {
            'code': 'a9iberAn',
            'type': 'Cloud Trial Credit',
            'expiry_date': '2017-09-30',
            'balance': 300.0,
            'recurring': False,
            'start_date': '2017-08-02 22:16:28',
        },
    ],
}


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


class ContentBillingViewsTest(test.TestCase):
    def setUp(self):
        super(ContentBillingViewsTest, self).setUp()
        self.project_id = "fake_project_id"
        kwargs = {"project_id": self.project_id}
        self.view = views.IndexView()
        self.view.kwargs = kwargs
        self.view.request = FakeRequest()

    @mock.patch('distil_ui.api.distil_v2.get_cost')
    @mock.patch('distil_ui.api.distil_v2.get_credits')
    @mock.patch('horizon.views.HorizonTemplateView.get_context_data')
    @freeze_time("2017-08-10")
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
