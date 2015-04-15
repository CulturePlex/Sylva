# -*- coding: utf-8 -*-
import json
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from userena.models import UserenaSignup
from guardian.shortcuts import assign_perm

from reports.models import ReportTemplate, Report
from graphs.models import Graph
from schemas.models import Schema
from django.core.urlresolvers import reverse


class EndpointTest(TestCase):

    fixtures = ["schemas.json", "graphs.json", "queries.json", "reports.json"]

    def setUp(self):
        test_user = UserenaSignup.objects.create_user(username="admin",
            email="admin@admin.com", password="admin")
        test_user = UserenaSignup.objects.activate_user(
            test_user.userena_signup.activation_key)
        response = self.client.login(
        username="admin", password='admin')
        self.assertTrue(response)
        graph = Graph.objects.get(pk=1)
        graph.owner = test_user
        graph.save()

    def test_list_endpoint(self):
        url = reverse('list', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)

    def test_templates_endpoint(self):
        url = reverse('templates', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertIsNone(body["template"])
        self.assertIsNone(body["queries"])
        self.assertEqual(resp.status_code, 200)

    def test_templates_endpoint_new(self):
        url = reverse('templates', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url, {'queries': 'true'})
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)

    # def test_templates_endpoint_edit(self):
    #     url = reverse('templates', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.get(url, {'queries': 'true', 'template': 'name_of_template'})
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)
    #
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

    # def test_delete_endpoint_del(self):
    #     url = reverse('delete', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.post(url)
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)

    # def test_delete_endpoint_check(self):
    #     url = reverse('delete', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.get(url, {'template': 'name_of_template'})
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)

    def test_history_endpoint(self):
        url = reverse('history', kwargs={"graph_slug": "dh2014"})
        resp = self.client.get(url)
        body = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)

    # def test_history_endpoint_hist(self):
    #     url = reverse('history', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.get(url, {"template": "name_of_template"})
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)
    #
    # def test_history_endpoint_inst(self):
    #     url = reverse('history', kwargs={"graph_slug": "dh2014"})
    #     resp = self.client.get(url, {"report": "name_of_report"})
    #     body = json.loads(resp.content)
    #     self.assertEqual(resp.status_code, 200)

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

        self.graph = Graph.objects.get(pk=1)
        self.template = ReportTemplate(name="test", start_date=datetime.now(),
                                       frequency="h", last_run=datetime.now(),
                                       layout={"hello": "world"},
                                       description="Some", graph=self.graph)
        self.template.save()
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
