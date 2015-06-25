# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Graph.slug'
        db.alter_column(u'graphs_graph', 'slug', self.gf('sylva.fields.AutoSlugField')(unique=True, max_length=200, populate_from=['name']))

    def backwards(self, orm):

        # Changing field 'Graph.slug'
        db.alter_column(u'graphs_graph', 'slug', self.gf('sylva.fields.AutoSlugField')(max_length=200, unique=True))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'data.data': {
            'Meta': {'object_name': 'Data'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['engines.Instance']", 'null': 'True', 'blank': 'True'}),
            'last_modified_nodes': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_modified_relationships': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_analytics': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_nodes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_queries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_relationships': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_storage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'engines.instance': {
            'Meta': {'object_name': 'Instance'},
            'activated': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'activation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'cert_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'encrypted_password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'engine': ('django.db.models.fields.CharField', [], {'default': "'engines.gdb.backends.neo4j'", 'max_length': '50'}),
            'fragment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'default': "'localhost'", 'max_length': '250', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instances'", 'to': u"orm['auth.User']"}),
            'path': ('django.db.models.fields.CharField', [], {'default': "'db/data'", 'max_length': '250'}),
            'plain_password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'default': "'7474'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'default': "'http'", 'max_length': '8'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'private'", 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        u'graphs.graph': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(['owner', 'name'],)", 'object_name': 'Graph'},
            'data': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.Data']", 'unique': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'graphs'", 'to': u"orm['auth.User']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'relaxed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'schema': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['schemas.Schema']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('sylva.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '200', 'populate_from': "['name']", 'blank': 'True'})
        },
        u'schemas.schema': {
            'Meta': {'object_name': 'Schema'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['graphs']