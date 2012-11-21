# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Data'
        db.create_table('data_data', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['engines.Instance'], null=True, blank=True)),
            ('total_nodes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_relationships', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_queries', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_storage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('options', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('data', ['Data'])

        # Adding model 'MediaNode'
        db.create_table('data_medianode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data', to=orm['data.Data'])),
        ))
        db.send_create_signal('data', ['MediaNode'])

        # Adding model 'MediaFile'
        db.create_table('data_mediafile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('media_node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='files', to=orm['data.MediaNode'])),
            ('media_label', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('media_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('data', ['MediaFile'])

        # Adding model 'MediaLink'
        db.create_table('data_medialink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('media_node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links', to=orm['data.MediaNode'])),
            ('media_label', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('media_link', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('data', ['MediaLink'])


    def backwards(self, orm):
        # Deleting model 'Data'
        db.delete_table('data_data')

        # Deleting model 'MediaNode'
        db.delete_table('data_medianode')

        # Deleting model 'MediaFile'
        db.delete_table('data_mediafile')

        # Deleting model 'MediaLink'
        db.delete_table('data_medialink')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'data.data': {
            'Meta': {'object_name': 'Data'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['engines.Instance']", 'null': 'True', 'blank': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_nodes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_queries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_relationships': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_storage': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'data.mediafile': {
            'Meta': {'object_name': 'MediaFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'media_label': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'media_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['data.MediaNode']"})
        },
        'data.medialink': {
            'Meta': {'object_name': 'MediaLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_label': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'media_link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'media_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['data.MediaNode']"})
        },
        'data.medianode': {
            'Meta': {'object_name': 'MediaNode'},
            'data': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': "orm['data.Data']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node_id': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'engines.instance': {
            'Meta': {'object_name': 'Instance'},
            'cert_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'encrypted_password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'engine': ('django.db.models.fields.CharField', [], {'default': "'engines.gdb.backends.neo4j'", 'max_length': '50'}),
            'fragment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'default': "'localhost'", 'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instances'", 'to': "orm['auth.User']"}),
            'path': ('django.db.models.fields.CharField', [], {'default': "'db/data'", 'max_length': '250'}),
            'plain_password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'default': "'7474'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'default': "'http'", 'max_length': '8'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['data']