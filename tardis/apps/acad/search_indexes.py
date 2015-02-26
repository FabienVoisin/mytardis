from haystack import indexes

from .models import Organism, Source, Sample, Extract, Library, Sequence,   Processing, Analysis
import logging

logger = logging.getLogger(__name__)

class SourceIndex(indexes.SearchIndex, indexes.Indexable):
    text=indexes.CharField(document=True, use_template=True)
    source_id_stored=indexes.CharField(model_attr='id')
    source_id_type=indexes.CharField(model_attr='id_type')
    #source_other_id=indexes.CharField(model_attr='other_id')
    #source_other_id_type=indexes.CharField(model_attr='other_id_type')
    organism_common=indexes.CharField(model_attr='organism__common')
    organism_genus=indexes.CharField(model_attr='organism__genus')
    organism_species=indexes.CharField(model_attr='organism__species')
    organism_subspecies=indexes.CharField(model_attr='organism__subspecies')
    source_date = indexes.DateField(model_attr='date')
    source_details=indexes.CharField(model_attr='source_details')
    source_gender=indexes.CharField(model_attr='gender')
    source_age_cat=indexes.CharField(model_attr='age_cat')
    source_age_range=indexes.CharField(model_attr='age_range')
    source_geoloc_continent=indexes.CharField(model_attr='geoloc_continent')
    source_geoloc_country=indexes.CharField(model_attr='geoloc_country')
    source_geoloc_locale=indexes.CharField(model_attr='geoloc_locale')
    source_geoloc_lat=indexes.FloatField(model_attr='geoloc_lat', default=None)
    source_geoloc_lon=indexes.FloatField(model_attr='geoloc_lon', default=None)
    source_geoloc=indexes.LocationField(default=None)
    source_geo_depth=indexes.IntegerField(model_attr='geo_depth', default=None)
    source_geo_altitude=indexes.IntegerField(model_attr='geo_altitude', default=None)
    source_geo_elev=indexes.IntegerField(model_attr='geo_elev', default=None)
    source_env_biome = indexes.CharField(model_attr='env_biome')
    source_env_feature = indexes.CharField(model_attr='env_feature')
    source_env_material = indexes.CharField(model_attr='env_material')
    source_carbondate_years=indexes.IntegerField(model_attr='carbondate_years', default=None)
    source_carbondate_error=indexes.IntegerField(model_attr='carbondate_error', default=None)
    source_carbondate_id=indexes.CharField(model_attr='carbondate_id')
    source_source_notes=indexes.CharField(model_attr='source_notes')
    #source_group_id=indexes.CharField(model_attr='group_id')
    #source_collectedby=indexes.CharField(model_attr='collectedby')

    def prepare_source_geoloc(self, obj):
        # If you're just storing the floats...
        return "%s,%s" % (obj.geoloc_lat, obj.geoloc_lon)
    
    def prepare_source_geoloc_continent(self, obj):
        return obj.get_geoloc_continent_display()
    
    def prepare_source_gender(self, obj):
        return obj.get_gender_display()

    def prepare_source_age_cat(self, obj):
        return obj.get_age_cat_display()
    
    def get_model(self):
        return Source

class SampleIndex(indexes.SearchIndex, indexes.Indexable):
    text=indexes.CharField(document=True, use_template=True)
    sample_id_stored=indexes.CharField(model_attr='id')
    sample_id_type=indexes.CharField(model_attr='id_type')
    source_id_stored=indexes.CharField(model_attr='source__id')
    organism_common=indexes.CharField(model_attr='organism__common')
    organism_genus=indexes.CharField(model_attr='organism__genus')
    organism_species=indexes.CharField(model_attr='organism__species')
    organism_subspecies=indexes.CharField(model_attr='organism__subspecies')
    sample_date = indexes.DateField(model_attr='date')
    sample_details=indexes.CharField(model_attr='sample_details')
    sample_cat=indexes.CharField(model_attr='sample_cat')
    sample_env_package=indexes.CharField(model_attr='env_package')
    sample_notes=indexes.CharField(model_attr='sample_notes')

    def prepare_sample_cat(self, obj):
        return obj.get_sample_cat_display()

    def prepare_sample_env_package(self, obj):
        return obj.get_env_package_display()

    def get_model(self):
        return Sample

class ExtractIndex(indexes.SearchIndex, indexes.Indexable):
    text=indexes.CharField(document=True, use_template=True)
    extract_id_stored=indexes.CharField(model_attr='id')
    sample_id_stored=indexes.CharField(model_attr='sample__id')
    source_id_stored=indexes.CharField(model_attr='sample__source__id')
    extract_date = indexes.DateField(model_attr='date')
    extract_protocol_ref=indexes.CharField(model_attr='protocol_ref')
    extract_protocol_note=indexes.CharField(model_attr='protocol_note')

    def get_model(self):
        return Extract
    
class LibraryIndex(indexes.SearchIndex, indexes.Indexable):
    text=indexes.CharField(document=True, use_template=True)
    library_id_stored=indexes.CharField(model_attr='id')
    extract_id_stored=indexes.CharField(model_attr='extract__id')
    sample_id_stored=indexes.CharField(model_attr='extract__sample__id')
    source_id_stored=indexes.CharField(model_attr='extract__sample__source__id')
    library_date = indexes.DateField(model_attr='date')
    library_source=indexes.CharField(model_attr='source')
    library_layout=indexes.CharField(model_attr='layout')
    library_type=indexes.CharField(model_attr='type')
    library_protocol_ref=indexes.CharField(model_attr='protocol_ref')
    library_protocol_note=indexes.CharField(model_attr='protocol_note')
    library_repair_method=indexes.CharField(model_attr='repair_method')
    library_enrich_method=indexes.CharField(model_attr='enrich_method')
    library_enrich_target=indexes.CharField(model_attr='enrich_target')
    library_enrich_target_subfrag=indexes.CharField(model_attr='enrich_target_subfrag')
    library_amp_method=indexes.CharField(model_attr='amp_method')

    def prepare_library_source(self, obj):
        return obj.get_source_display()

    def prepare_library_enrich_method(self, obj):
        return obj.get_enrich_method_display()

    def prepare_library_enrich_target(self, obj):
        return obj.get_enrich_target_display()

    def prepare_library_type(self, obj):
        return obj.get_type_display()

    def get_model(self):
        return Library

class SequenceIndex(indexes.SearchIndex, indexes.Indexable):
    text=indexes.CharField(document=True, use_template=True)
    sequence_id_stored=indexes.CharField(model_attr='id')
    library_id_stored=indexes.CharField(model_attr='library__id')
    extract_id_stored=indexes.CharField(model_attr='library__extract__id')
    sample_id_stored=indexes.CharField(model_attr='library__extract__sample__id')
    source_id_stored=indexes.CharField(model_attr='library__extract__sample__source__id')
    sequence_date = indexes.DateField(model_attr='date')
    sequence_centre=indexes.CharField(model_attr='centre')
    sequence_method=indexes.CharField(model_attr='method')
    sequence_tech=indexes.CharField(model_attr='tech')
    sequence_tech_chem=indexes.IntegerField(model_attr='tech_chem')
    sequence_tech_options=indexes.CharField(model_attr='tech_options')
    sequence_fileformat=indexes.CharField(model_attr='fileformat')
    sequence_qualscale=indexes.CharField(model_attr='qualscale')
    sequence_error_rate=indexes.IntegerField(model_attr='error_rate')
    sequence_error_method=indexes.CharField(model_attr='error_method')
    sequence_demulti_prog=indexes.CharField(model_attr='demulti_prog')
    sequence_demulti_prog_ver=indexes.CharField(model_attr='demulti_prog_ver')
    sequence_demulti_prog_opt=indexes.CharField(model_attr='demulti_prog_opt')

    def prepare_sequence_method(self, obj):
        return obj.get_method_display()

    def get_model(self):
        return Sequence

class ProcessingIndex(indexes.SearchIndex, indexes.Indexable):
    text=indexes.CharField(document=True, use_template=True)
    processing_id_stored=indexes.CharField(model_attr='id')
    sequence_id_stored=indexes.CharField(model_attr='sequence__id')
    library_id_stored=indexes.CharField(model_attr='sequence__library__id')
    extract_id_stored=indexes.CharField(model_attr='sequence__library__extract__id')
    sample_id_stored=indexes.CharField(model_attr='sequence__library__extract__sample__id')
    source_id_stored=indexes.CharField(model_attr='sequence__library__extract__sample__source__id')
    processing_reference=indexes.CharField(model_attr='reference')
    processing_fold_coverage=indexes.DecimalField(model_attr='fold_coverage')
    processing_percent_coverage=indexes.DecimalField(model_attr='percent_coverage')
    processing_contigs=indexes.IntegerField(model_attr='contigs')
    
    def get_model(self):
        return Processing
    
class AnalysisIndex(indexes.SearchIndex, indexes.Indexable):
    text=indexes.CharField(document=True, use_template=True)
    analysis_id_stored=indexes.CharField(model_attr='id')
    source_id_stored=indexes.MultiValueField(indexed=True, stored=True)
    experiment_id_stored=indexes.MultiValueField(indexed=True, stored=True)

    def prepare_source_id_stored(self, obj):
        return [processing.sequence.library.extract.sample.source.id for processing in obj.processing_set.all()]

    def prepare_experiment_id_stored(self, obj):
        return [exp.id for exp in obj.dataset.experiments.all()]

    def get_model(self):
        return Analysis
