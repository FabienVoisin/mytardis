# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organism'
        db.create_table(u'acad_organism', (
            ('id', self.gf('django.db.models.fields.PositiveSmallIntegerField')(primary_key=True)),
            ('genus', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('species', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('subspecies', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('common', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('acad', ['Organism'])

        # Adding model 'Source'
        db.create_table(u'acad_source', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('id_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('other_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('other_id_type', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('organism', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acad.Organism'])),
            ('source_details', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('age_cat', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('age_range', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('geoloc_continent', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('geoloc_country', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('geoloc_locale', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('geoloc_lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('geoloc_lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('env_biome', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('env_feature', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('env_material', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('carbondate_years', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('carbondate_error', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('carbondate_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('source_notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('group_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('collectedby', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('acad', ['Source'])

        # Adding model 'Sample'
        db.create_table(u'acad_sample', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('id_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acad.Source'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('organism', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acad.Organism'])),
            ('sample_cat', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sample_details', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('env_package', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('group_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('acad_loc', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('collectedby', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('sample_notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acad', ['Sample'])

        # Adding model 'Extract'
        db.create_table(u'acad_extract', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acad.Sample'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('protocol_ref', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('protocol_note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('acad', ['Extract'])

        # Adding model 'Library'
        db.create_table(u'acad_library', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('extract', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acad.Extract'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('protocol_ref', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('protocol_note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('layout', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('repair_method', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
            ('enrich_method', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
            ('enrich_target', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('enrich_target_subfrag', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('amp_method', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('acad', ['Library'])

        # Adding model 'Sequence'
        db.create_table(u'acad_sequence', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('library', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acad.Library'], unique=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('centre', self.gf('django.db.models.fields.CharField')(default='ACAD', max_length=255)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tech', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tech_chem', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('tech_options', self.gf('django.db.models.fields.CharField')(default='Default', max_length=255)),
            ('fileformat', self.gf('django.db.models.fields.CharField')(default='FASTQ', max_length=255)),
            ('qualscale', self.gf('django.db.models.fields.CharField')(default='Phred', max_length=255)),
            ('error_rate', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('error_method', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('demulti_prog', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('demulti_prog_ver', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('demulti_prog_opt', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('acad', ['Sequence'])

        # Adding model 'Processing'
        db.create_table(u'acad_processing', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('sequence', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['acad.Sequence'], unique=True)),
            ('analysis', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acad.Analysis'])),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('fold_coverage', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=3, blank=True)),
            ('percent_coverage', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=3, blank=True)),
            ('contigs', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('acad', ['Processing'])

        # Adding model 'Analysis'
        db.create_table(u'acad_analysis', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('dataset', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tardis_portal.Dataset'], unique=True)),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('acad', ['Analysis'])


    def backwards(self, orm):
        # Deleting model 'Organism'
        db.delete_table(u'acad_organism')

        # Deleting model 'Source'
        db.delete_table(u'acad_source')

        # Deleting model 'Sample'
        db.delete_table(u'acad_sample')

        # Deleting model 'Extract'
        db.delete_table(u'acad_extract')

        # Deleting model 'Library'
        db.delete_table(u'acad_library')

        # Deleting model 'Sequence'
        db.delete_table(u'acad_sequence')

        # Deleting model 'Processing'
        db.delete_table(u'acad_processing')

        # Deleting model 'Analysis'
        db.delete_table(u'acad_analysis')


    models = {
        'acad.analysis': {
            'Meta': {'object_name': 'Analysis'},
            'dataset': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tardis_portal.Dataset']", 'unique': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {})
        },
        'acad.extract': {
            'Meta': {'object_name': 'Extract'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'protocol_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'protocol_ref': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acad.Sample']"})
        },
        'acad.library': {
            'Meta': {'object_name': 'Library'},
            'amp_method': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'enrich_method': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'enrich_target': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'enrich_target_subfrag': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'extract': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acad.Extract']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'layout': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'protocol_note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'protocol_ref': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repair_method': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'acad.organism': {
            'Meta': {'object_name': 'Organism'},
            'common': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.PositiveSmallIntegerField', [], {'primary_key': 'True'}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'subspecies': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'acad.processing': {
            'Meta': {'object_name': 'Processing'},
            'analysis': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acad.Analysis']"}),
            'contigs': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fold_coverage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'percent_coverage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sequence': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acad.Sequence']", 'unique': 'True'})
        },
        'acad.sample': {
            'Meta': {'object_name': 'Sample'},
            'acad_loc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'collectedby': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'env_package': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'id_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acad.Organism']"}),
            'sample_cat': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sample_details': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sample_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acad.Source']"})
        },
        'acad.sequence': {
            'Meta': {'object_name': 'Sequence'},
            'centre': ('django.db.models.fields.CharField', [], {'default': "'ACAD'", 'max_length': '255'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'demulti_prog': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'demulti_prog_opt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'demulti_prog_ver': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'error_method': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'error_rate': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fileformat': ('django.db.models.fields.CharField', [], {'default': "'FASTQ'", 'max_length': '255'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['acad.Library']", 'unique': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'qualscale': ('django.db.models.fields.CharField', [], {'default': "'Phred'", 'max_length': '255'}),
            'tech': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tech_chem': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'tech_options': ('django.db.models.fields.CharField', [], {'default': "'Default'", 'max_length': '255'})
        },
        'acad.source': {
            'Meta': {'object_name': 'Source'},
            'age_cat': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'age_range': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'carbondate_error': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'carbondate_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'carbondate_years': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'collectedby': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'env_biome': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'env_feature': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'env_material': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geoloc_continent': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geoloc_country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geoloc_lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'geoloc_locale': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geoloc_lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'id_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['acad.Organism']"}),
            'other_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'other_id_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source_details': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tardis_portal.dataset': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Dataset'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'directory': ('tardis.tardis_portal.models.fields.DirectoryField', [], {'null': 'True', 'blank': 'True'}),
            'experiments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'datasets'", 'symmetrical': 'False', 'to': "orm['tardis_portal.Experiment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'immutable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tardis_portal.Instrument']", 'null': 'True', 'blank': 'True'}),
            'storage_boxes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'datasets'", 'blank': 'True', 'to': "orm['tardis_portal.StorageBox']"})
        },
        'tardis_portal.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'handle': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_name': ('django.db.models.fields.CharField', [], {'default': "'Monash University'", 'max_length': '400'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tardis_portal.License']", 'null': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_access': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'tardis_portal.facility': {
            'Meta': {'object_name': 'Facility'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tardis_portal.instrument': {
            'Meta': {'object_name': 'Instrument'},
            'facility': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tardis_portal.Facility']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tardis_portal.license': {
            'Meta': {'object_name': 'License'},
            'allows_distribution': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '2000', 'blank': 'True'}),
            'internal_description': ('django.db.models.fields.TextField', [], {}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '400'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '2000'})
        },
        'tardis_portal.objectacl': {
            'Meta': {'ordering': "['content_type', 'object_id']", 'object_name': 'ObjectACL'},
            'aclOwnershipType': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'canDelete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'canRead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'canWrite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'effectiveDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'entityId': ('django.db.models.fields.CharField', [], {'max_length': '320'}),
            'expiryDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isOwner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'pluginId': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'tardis_portal.storagebox': {
            'Meta': {'object_name': 'StorageBox'},
            'description': ('django.db.models.fields.TextField', [], {'default': "'Default Storage'"}),
            'django_storage_class': ('django.db.models.fields.TextField', [], {'default': "'tardis.tardis_portal.storage.MyTardisLocalFileSystemStorage'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_size': ('django.db.models.fields.BigIntegerField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {'default': "'default'", 'unique': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['acad']