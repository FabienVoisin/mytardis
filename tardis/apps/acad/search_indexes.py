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
        for continent in Source.CONTINENTS:
            if continent[0]==obj.geoloc_continent:
                return continent[1]
        return obj.geoloc_continent
    
    def prepare_source_gender(self, obj):
        for gender in Source.GENDERS:
            if gender[0]==obj.gender:
                return gender[1]
        return obj.gender

    def prepare_source_age_cat(self, obj):
        for cat in Source.AGE_CATS:
            if cat[0]==obj.age_cat:
                return cat[1]
        return obj.age_cat
    
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
        for cat in Sample.SAMPLE_CATS:
            if cat[0]==obj.sample_cat:
                return cat[1]
        return obj.sample_cat

    def prepare_sample_env_package(self, obj):
        for env in Sample.ENV_PACKAGES:
            if env[0]==obj.env_package:
                return env[1]
        return obj.env_package

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
        for src in Library.LIB_SOURCES:
            if src[0]==obj.source:
                return src[1]
        return obj.source

    def prepare_library_enrich_method(self, obj):
        for method in Library.ENRICH_METHOD:
            if method[0]==obj.enrich_method:
                return method[1]
        return obj.enrich_method

    def prepare_library_enrich_target(self, obj):
        for target in Library.ENRICH_TARGET:
            if target[0]==obj.enrich_target:
                return target[1]
        return obj.enrich_target

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
    analysis_note=indexes.CharField(model_attr='analysis__note')
    experiment_id_stored=indexes.MultiValueField(indexed=True, stored=True)

    def prepare_experiment_id_stored(self, obj):
        return [exp.id for exp in obj.analysis.dataset.experiments.all()]
    
    def get_model(self):
        return Processing
    