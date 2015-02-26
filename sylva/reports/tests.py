# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from models import ReportTemplate, Report
from graphs.models import Graph
from schemas.models import Schema


class ReportTemplateTest(TestCase):

    def setUp(self):
        self.u = User.objects.create(username='john', password='doe',
                                     is_active=True, is_staff=True)
        self.u.set_password('hello')
        self.u.save()
        schema = Schema.objects.create()
        self.graph = Graph.objects.create(name="test_graph", schema=schema,
                                          owner=self.u)
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

    def setUp(self):
        self.u = User.objects.create(username='dave', password='bshow',
                                     is_active=True, is_staff=True)
        self.u.set_password('excellent')
        self.u.save()
        schema = Schema.objects.create()
        self.graph = Graph.objects.create(name="test_graph2", schema=schema,
                                          owner=self.u)
        self.template = ReportTemplate(name="test3", start_date=datetime.now(),
                                       frequency="h", last_run=datetime.now(),
                                       layout={"hello": "davebshow"},
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
