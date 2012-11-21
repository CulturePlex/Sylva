# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Schema'
        db.create_table('schemas_schema', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('options', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('schemas', ['Schema'])

        # Adding model 'NodeType'
        db.create_table('schemas_nodetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('slug', self.gf('base.fields.AutoSlugField')(db_index=False, unique=True, max_length=200, blank=True)),
            ('plural_name', self.gf('django.db.models.fields.CharField')(max_length=175, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schemas.Schema'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('validation', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inheritance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schemas.NodeType'], null=True, blank=True)),
        ))
        db.send_create_signal('schemas', ['NodeType'])

        # Adding model 'RelationshipType'
        db.create_table('schemas_relationshiptype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('slug', self.gf('base.fields.AutoSlugField')(db_index=False, unique=True, max_length=200, blank=True)),
            ('plural_name', self.gf('django.db.models.fields.CharField')(max_length=175, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('schema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schemas.Schema'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('validation', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inverse', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('plural_inverse', self.gf('django.db.models.fields.CharField')(max_length=175, null=True, blank=True)),
            ('inheritance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schemas.RelationshipType'], null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='outgoing_relationships', null=True, to=orm['schemas.NodeType'])),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='incoming_relationships', null=True, to=orm['schemas.NodeType'])),
            ('arity_source', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('arity_target', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('schemas', ['RelationshipType'])

        # Adding model 'NodeProperty'
        db.create_table('schemas_nodeproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('base.fields.AutoSlugField')(db_index=False, unique=True, max_length=750, blank=True)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('datatype', self.gf('django.db.models.fields.CharField')(default=u'u', max_length=1)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('validation', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='properties', to=orm['schemas.NodeType'])),
        ))
        db.send_create_signal('schemas', ['NodeProperty'])

        # Adding model 'RelationshipProperty'
        db.create_table('schemas_relationshipproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('base.fields.AutoSlugField')(db_index=False, unique=True, max_length=750, blank=True)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('datatype', self.gf('django.db.models.fields.CharField')(default=u'u', max_length=1)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('validation', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('relationship', self.gf('django.db.models.fields.related.ForeignKey')(related_name='properties', to=orm['schemas.RelationshipType'])),
        ))
        db.send_create_signal('schemas', ['RelationshipProperty'])


    def backwards(self, orm):
        # Deleting model 'Schema'
        db.delete_table('schemas_schema')

        # Deleting model 'NodeType'
        db.delete_table('schemas_nodetype')

        # Deleting model 'RelationshipType'
        db.delete_table('schemas_relationshiptype')

        # Deleting model 'NodeProperty'
        db.delete_table('schemas_nodeproperty')

        # Deleting model 'RelationshipProperty'
        db.delete_table('schemas_relationshipproperty')


    models = {
        'schemas.nodeproperty': {
            'Meta': {'ordering': "('order', 'key')", 'object_name': 'NodeProperty'},
            'datatype': ('django.db.models.fields.CharField', [], {'default': "u'u'", 'max_length': '1'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['schemas.NodeType']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('base.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '750', 'blank': 'True'}),
            'validation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'schemas.nodetype': {
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'NodeType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inheritance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schemas.NodeType']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'plural_name': ('django.db.models.fields.CharField', [], {'max_length': '175', 'null': 'True', 'blank': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schemas.Schema']"}),
            'slug': ('base.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'validation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'schemas.relationshipproperty': {
            'Meta': {'ordering': "('order', 'key')", 'object_name': 'RelationshipProperty'},
            'datatype': ('django.db.models.fields.CharField', [], {'default': "u'u'", 'max_length': '1'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['schemas.RelationshipType']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('base.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '750', 'blank': 'True'}),
            'validation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'schemas.relationshiptype': {
            'Meta': {'ordering': "('order', 'inverse', 'name')", 'object_name': 'RelationshipType'},
            'arity_source': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'arity_target': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inheritance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schemas.RelationshipType']", 'null': 'True', 'blank': 'True'}),
            'inverse': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'plural_inverse': ('django.db.models.fields.CharField', [], {'max_length': '175', 'null': 'True', 'blank': 'True'}),
            'plural_name': ('django.db.models.fields.CharField', [], {'max_length': '175', 'null': 'True', 'blank': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schemas.Schema']"}),
            'slug': ('base.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'outgoing_relationships'", 'null': 'True', 'to': "orm['schemas.NodeType']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'incoming_relationships'", 'null': 'True', 'to': "orm['schemas.NodeType']"}),
            'total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'validation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'schemas.schema': {
            'Meta': {'object_name': 'Schema'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['schemas']