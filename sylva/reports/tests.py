# -*- coding: utf-8 -*-
import json
from datetime import datetime

from django.test import TestCase

from userena.models import UserenaSignup

from reports.models import ReportTemplate, Report
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

    # History probably deserves its own test case , TODO
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
        # This could be probelematic.
        self.assertEqual(len(body["reports"][0]["reports"]), 2)  # 2 reports.
        self.assertEqual(body["name"], "Template2")

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
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)

    def test_builder_endpoint(self):
        url = reverse('builder', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)

    # def test_builder_endpoint_new(self):
    #     url = reverse('builder', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.post(url)
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)
    #
    # def test_builder_endpoint_edit(self):
    #     url = reverse('builder', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.post(url, {"slug": "name_of_template"})
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)


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
        t = ReportTemplate.objects.get(pk=template_id)
        self.assertIsNotNone(t)
        t.delete()
        try:
            ReportTemplate.objects.get(pk=template_id)
            exists = True
        except ReportTemplate.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)


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
        r = Report.objects.get(pk=rid)
        self.assertIsNotNone(r)
        r.delete()
        try:
            Report.objects.get(pk=rid)
            exists = True
        except Report.DoesNotExist:
            exists = False
        self.assertEqual(exists, False)
