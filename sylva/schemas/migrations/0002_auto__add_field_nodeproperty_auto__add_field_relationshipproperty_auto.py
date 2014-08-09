# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NodeProperty.auto'
        db.add_column('schemas_nodeproperty', 'auto',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'RelationshipProperty.auto'
        db.add_column('schemas_relationshipproperty', 'auto',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'NodeProperty.auto'
        db.delete_column('schemas_nodeproperty', 'auto')

        # Deleting field 'RelationshipProperty.auto'
        db.delete_column('schemas_relationshipproperty', 'auto')


    models = {
        'schemas.nodeproperty': {
            'Meta': {'ordering': "('order', 'key')", 'object_name': 'NodeProperty'},
            'auto': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'datatype': ('django.db.models.fields.CharField', [], {'default': "u'u'", 'max_length': '1'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['schemas.NodeType']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('sylva.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '750', 'populate_from': "['key']", 'blank': 'True'}),
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
            'slug': ('sylva.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '200', 'populate_from': "['name']", 'blank': 'True'}),
            'total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'validation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'schemas.relationshipproperty': {
            'Meta': {'ordering': "('order', 'key')", 'object_name': 'RelationshipProperty'},
            'auto': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'datatype': ('django.db.models.fields.CharField', [], {'default': "u'u'", 'max_length': '1'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': "orm['schemas.RelationshipType']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('sylva.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '750', 'populate_from': "['key']", 'blank': 'True'}),
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
            'slug': ('sylva.fields.AutoSlugField', [], {'db_index': 'False', 'unique': 'True', 'max_length': '200', 'populate_from': "['name']", 'blank': 'True'}),
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
