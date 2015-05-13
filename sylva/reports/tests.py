# -*- coding: utf-8 -*-
import json
from datetime import datetime
from django.test import TestCase

from userena.models import UserenaSignup

from reports.models import ReportTemplate, Report
from reports.views import _get_bucket, paginate
from queries.models import Query
from graphs.models import Graph
from django.core.urlresolvers import reverse

"""
TODO:
paginator
pdf preview
pdf generation/celery
careful history endpoint test for bucket generation
"""

class EndpointTest(TestCase):

    fixtures = ["schemas.json", "graphs.json", "queries.json", "reports.json"]

    def setUp(self):
        test_user = UserenaSignup.objects.create_user(username="admin",
            email="admin@admin.com", password="admin")
        test_user = UserenaSignup.objects.activate_user(
            test_user.userena_signup.activation_key)
        response = self.client.login(username="admin", password='admin')
        self.assertTrue(response)
        self.graph = Graph.objects.get(pk=1)
        self.graph.owner = test_user
        self.graph.save()

    def test_list_endpoint(self):
        url = reverse('list', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(body["templates"]), 2)

    def test_list_endpoint404(self):
        url = reverse('list', kwargs={"graph_slug": "dh201"})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_templates_endpoint(self):
        url = reverse('templates', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(body["template"])
        self.assertFalse(body["queries"])

    def test_templates_endpoint_new(self):
        url = reverse('templates', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {'queries': 'true'})
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(body["queries"]), 2)

    def test_templates_endpoint_edit(self):
        url = reverse('templates', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {'queries': 'true', 'template': 'template1'})
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["template"]["name"], "Template1")
        self.assertTrue(body["template"]["layout"])
        self.assertEqual(len(body["queries"]), 2)

    def test_templates_endpoint_edit404(self):
        url = reverse('templates', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {'queries': 'true', 'template': 'doesnotexist'})
        self.assertEqual(resp.status_code, 404)

    # This test requires an actual graph backend.
    # def test_templates_endpoint_preview(self):
    #     url = reverse('templates', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.get(url, {'template': 'name_of_template'})
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)

    def test_delete_endpoint(self):
        url = reverse('delete', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(body)

    def test_delete_endpoint_del(self):
        template = ReportTemplate(name="endpointdelete",
            start_date=datetime.now(), frequency="h", last_run=datetime.now(),
            layout={"hello": "johndoe"}, description="Some", graph=self.graph)
        template.save()
        template_id = template.id
        t = ReportTemplate.objects.get(pk=template_id)
        self.assertIsNotNone(t)
        url = reverse('delete', kwargs={"graph_slug": "dh2014"})
        resp = self.client.post(url, json.dumps({"template": template.slug}),
            content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        try:
            ReportTemplate.objects.get(pk=template_id)
            exists = True
        except ReportTemplate.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)

    def test_delete_endpoint_del404(self):
        url = reverse('delete', kwargs={"graph_slug": "dh2014"})
        resp = self.client.post(url, json.dumps({"template": "doesnotexist"}),
            content_type="application/json")
        self.assertEqual(resp.status_code, 404)

    def test_delete_endpoint_check(self):
        url = reverse('delete', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {'template': 'template2'})
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body["num_reports"], 2)

    def test_history_endpoint(self):
        url = reverse('history', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(body["reports"])

    def test_history_endpoint_hist(self):
        url = reverse('history', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {"template": "template2"})
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        start_date = datetime(2015, 4, 15, 0, 0, 0)
        delta = datetime.now() - start_date
        num_days = delta.days + 2  # Include the starting date and interval
        import math
        self.assertTrue(body["num_pages"], math.ceil(float(num_days) / 5))

    def test_history_endpoint_hist404(self):
        url = reverse('history', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {"template": "doesnotexist"})
        self.assertEqual(resp.status_code, 404)

    def test_history_endpoint_no_history(self):
        url = reverse('history', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {"template": "template1"})
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(body["reports"])

    def test_history_endpoint_inst(self):
        url = reverse('history', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {"report": 1})
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(body["table"]), 2)

    def test_history_endpoint_inst404(self):
        url = reverse('history', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {"report": 100000})
        self.assertEqual(resp.status_code, 404)

    def test_builder_endpoint(self):
        url = reverse('builder', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)

    def test_builder_endpoint_new_edit(self):
        url = reverse('builder', kwargs={"graph_slug": "dh2014"})
        # Create!
        post_body = {"template": {
            "name": "TestTemplate",
            "frequency": "d",
            "description": "This is a test.",
            "collabs": [],
            "layout": {"layout": [[{"displayQuery": 1}], [{"displayQuery": ""}]]},
            "date": "10/10/2015",
            "time": "12:30"
        }}
        resp = self.client.post(url, json.dumps(post_body),
            content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        try:
            new_template = ReportTemplate.objects.get(pk=3)
            exists = True
        except ReportTemplate.DoesNotExist:
            exists = False
        self.assertTrue(exists)
        # Now edit!
        post_body["template"]["name"] = "edited"
        post_body["template"]["slug"] = new_template.slug
        resp2 = self.client.post(url, json.dumps(post_body),
            content_type="application/json")
        self.assertEqual(resp2.status_code, 200)
        new_template = ReportTemplate.objects.get(pk=3)
        self.assertEqual(new_template.name, "edited")

    def test_builder_endpoint_new_error(self):
        url = reverse('builder', kwargs={"graph_slug": "dh2014"})
        post_body = {"template": {
            "name": '',
            "frequency": "d",
            "description": "This is a test.",
            "collabs": [],
            "layout": {"layout": [[{"displayQuery": 1}], [{"displayQuery": 2}]]},
            "date": "10/10/2015",
            "time": "12:30"
        }}
        resp = self.client.post(url, json.dumps(post_body),
            content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content)
        self.assertTrue(body.get("errors", False))

    def test_builder_endpoint_edit_error(self):
        url = reverse('builder', kwargs={"graph_slug": "dh2014"})
        post_body = {"template": {
            "name": '',
            "frequency": "d",
            "description": "This is a test.",
            "collabs": [],
            "layout": {"layout": [[{"displayQuery": 1}], [{"displayQuery": 2}]]},
            "date": "10/10/2015",
            "time": "12:30",
            "slug": "template1"
        }}
        resp = self.client.post(url, json.dumps(post_body),
            content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content)
        self.assertTrue(body.get("errors", False))

    def test_builder_endpoint_edit404(self):
        url = reverse('builder', kwargs={"graph_slug": "dh2014"})
        post_body = {"template": {
            "name": 'test404',
            "frequency": "d",
            "description": "This is a test.",
            "collabs": [],
            "layout": {"layout": [[{"displayQuery": 1}], [{"displayQuery": 2}]]},
            "date": "10/10/2015",
            "time": "12:30",
            "slug": "doesnotexist"
        }}
        resp = self.client.post(url, json.dumps(post_body),
            content_type="application/json")
        self.assertEqual(resp.status_code, 404)

    def test_builder_endpoint_badquery404(self):
        url = reverse('builder', kwargs={"graph_slug": "dh2014"})
        post_body = {"template": {
            "name": 'testbadquery404',
            "frequency": "d",
            "description": "This is a test.",
            "collabs": [],
            "layout": {"layout": [[{"displayQuery": 1}], [{"displayQuery": 10}]]},
            "date": "10/10/2015",
            "time": "12:30"
        }}
        resp = self.client.post(url, json.dumps(post_body),
            content_type="application/json")
        self.assertEqual(resp.status_code, 404)


class HistoryUtilsTest(TestCase):

    def test_get_bucket(self):
        buckets = [datetime(2015, 5, 13, 0, 0),
                   datetime(2015, 5, 12, 0, 0),
                   datetime(2015, 5, 11, 0, 0),
                   datetime(2015, 5, 10, 0, 0)]
        date1 = datetime(2015, 5, 11, 12, 0, 0, 862562)
        date2 = datetime(2015, 5, 10, 16, 0, 0, 862562)
        date3 = datetime(2015, 5, 12, 13, 0, 0, 862562)
        date4 = datetime(2015, 5, 13, 11, 0, 0, 862562)
        b1 = _get_bucket(date1, buckets)
        b2 = _get_bucket(date2, buckets)
        b3 = _get_bucket(date3, buckets)
        b4 = _get_bucket(date4, buckets)
        self.assertEqual(b1, "2015-05-11T00:00:00")
        self.assertEqual(b2, "2015-05-10T00:00:00")
        self.assertEqual(b3, "2015-05-12T00:00:00")
        self.assertEqual(b4, "2015-05-13T00:00:00")

    def test_paginator(self):
        buckets = [datetime(2015, 5, 14, 0, 0), datetime(2015, 5, 13, 0, 0),
                   datetime(2015, 5, 12, 0, 0), datetime(2015, 5, 11, 0, 0),
                   datetime(2015, 5, 10, 0, 0), datetime(2015, 5, 9, 0, 0),
                   datetime(2015, 5, 8, 0, 0), datetime(2015, 5, 7, 0, 0),
                   datetime(2015, 5, 6, 0, 0), datetime(2015, 5, 5, 0, 0),
                   datetime(2015, 5, 4, 0, 0), datetime(2015, 5, 3, 0, 0),
                   datetime(2015, 5, 2, 0, 0), datetime(2015, 5, 1, 0, 0),
                   datetime(2015, 4, 30, 0, 0), datetime(2015, 4, 29, 0, 0),
                   datetime(2015, 4, 28, 0, 0), datetime(2015, 4, 27, 0, 0),
                   datetime(2015, 4, 26, 0, 0), datetime(2015, 4, 25, 0, 0),
                   datetime(2015, 4, 24, 0, 0), datetime(2015, 4, 23, 0, 0),
                   datetime(2015, 4, 22, 0, 0), datetime(2015, 4, 21, 0, 0),
                   datetime(2015, 4, 20, 0, 0), datetime(2015, 4, 19, 0, 0),
                   datetime(2015, 4, 18, 0, 0), datetime(2015, 4, 17, 0, 0),
                   datetime(2015, 4, 16, 0, 0), datetime(2015, 4, 15, 0, 0)]
        pgntr, output, next_page_num, prev_page_num = paginate(
            buckets, 5, 1
        )
        self.assertEqual(len(output.object_list), 5)
        self.assertEqual(next_page_num, 2)
        self.assertIsNone(prev_page_num)
        pgntr, output, next_page_num, prev_page_num = paginate(
            buckets, 3, 2
        )
        self.assertEqual(len(output.object_list), 3)
        self.assertEqual(output.object_list[0], datetime(2015, 5, 11, 0, 0))
        self.assertEqual(output.object_list[1], datetime(2015, 5, 10, 0, 0))
        self.assertEqual(output.object_list[2], datetime(2015, 5, 9, 0, 0))
        self.assertEqual(next_page_num, 3)
        self.assertEqual(prev_page_num, 1)
        pgntr, output, next_page_num, prev_page_num = paginate(
            buckets, 5, 6
        )
        self.assertEqual(len(output.object_list), 5)
        self.assertIsNone(next_page_num)
        self.assertEqual(prev_page_num, 5)




class ReportTemplateTest(TestCase):

    fixtures = ["schemas.json", "graphs.json", "queries.json", "reports.json"]

    def setUp(self):
        self.query1 = Query.objects.get(pk=1)
        self.query2 = Query.objects.get(pk=2)
        self.graph = Graph.objects.get(pk=1)
        self.template = ReportTemplate(name="test", start_date=datetime.now(),
                                       frequency="h", last_run=datetime.now(),
                                       layout={"hello": "world"},
                                       description="Some", graph=self.graph)
        self.template.save()
        self.template.queries.add(self.query1)
        self.template.queries.add(self.query2)
        self.template_id = self.template.id

    def test_template_creation(self):
        self.assertIsNotNone(self.template)
        self.assertEqual(self.template.name, "test")

    def test_template_update(self):
        template = ReportTemplate.objects.get(pk=self.template_id)
        template.name = "test this yo!"
        template.save()
        self.assertEqual(template.name, "test this yo!")

    def test_report_delete(self):
        template = ReportTemplate(name="test2", start_date=datetime.now(),
                                  frequency="h", last_run=datetime.now(),
                                  layout={"hello": "johndoe"},
                                  description="Some", graph=self.graph)
        template.save()
        template_id = template.id
        try:
            t = ReportTemplate.objects.get(pk=template_id)
            exists = True
        except ReportTemplate.DoesNotExist:
            exists = False
        self.assertTrue(exists)
        t.delete()
        try:
            ReportTemplate.objects.get(pk=template_id)
            exists = True
        except ReportTemplate.DoesNotExist:
            exists = False
        self.assertFalse(exists)


class ReportTest(TestCase):

    fixtures = ["schemas.json", "graphs.json", "queries.json", "reports.json"]

    def setUp(self):
        self.graph = Graph.objects.get(pk=1)
        self.template = ReportTemplate(name="test", start_date=datetime.now(),
                                       frequency="h", last_run=datetime.now(),
                                       layout={"hello": "world"},
                                       description="Some", graph=self.graph)
        self.template.save()
        self.template_id = self.template.id
        self.datetime = datetime.now()
        self.report = Report(date_run=self.datetime, table={"hello": "again"},
                             template=self.template)
        self.report.save()

    def test_report_creation(self):
        self.assertIsNotNone(self.report)
        self.assertEqual(self.report.date_run, self.datetime)

    def test_report_delete(self):
        report = Report(date_run=datetime.now(), table={"hello": "again"},
                        template=self.template)
        report.save()
        rid = report.id
        try:
            r = Report.objects.get(pk=rid)
            exists = True
        except ReportTemplate.DoesNotExist:
            exists = False
        self.assertTrue(exists)
        r.delete()
        try:
            Report.objects.get(pk=rid)
            exists = True
        except Report.DoesNotExist:
            exists = False
        self.assertFalse(exists)
