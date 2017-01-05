""" ands_doi.py """

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.importlib import import_module
from urllib2 import HTTPError

from tardis.tardis_portal.models import ExperimentParameter, \
    ExperimentParameterSet, ParameterName, Schema, \
    DatasetParameter, DatasetParameterSet

import requests, json
import re

import logging
logger = logging.getLogger(__name__)

class DOIService(object):
    """
    DOIService

    Mints DOIs using ANDS' Cite My Data service
    POSTs DataCite XML to a web services endpoint
    """

    def __init__(self, obj):
        """
        :param obj: The experiment or dataset model object to be minted
        :type django.db.model: :class: `django.db.model`
        """
        if hasattr(settings, 'DOI_ENABLE') and settings.DOI_ENABLE:
            self.obj = obj
            obj_type = type(obj).__name__
            DOI_SETTINGS = "%s_DOI" % obj_type.upper()
            if hasattr(settings, DOI_SETTINGS):
                ds = getattr(settings, DOI_SETTINGS)
                self.schema = Schema.objects.get(namespace=ds['NAMESPACE'])
                self.doi_name = ParameterName.objects.get(name=ds['PARAMETERNAME']) # e.g. doi or doi_experiment or doi_dataset
            else:
                raise Exception('DOI is enabled, but lacking of information: %s does not exist.' % DOI_SETTINGS)

        else:
            raise Exception('DOI is not enabled')

    def get_or_mint_doi(self, url):
        """
        :param url: the URL the DOI will resolve to
        :type url: string
        :return: the DOI string
        :rtype string
        """
        doi = self.get_doi()
        if not doi:
            doi = self._mint_doi(url)
            logger.info("minted DOI %s" % doi)
            self._save_doi(doi)
        return doi

    def update_doi(self, doi, url):
        base_url = "https://researchdata.ands.org.au/api/doi/update.json/" # put me in settings.py eventually
        app_id = settings.DOI_APP_ID
        mint_url = "%s?app_id=%s&doi=%s&url=%s" % (base_url, app_id, doi, url)
        datacite_xml = self._datacite_xml()
        post_data = {'xml': datacite_xml}

        if hasattr(settings, 'DOI_DEBUG_XML') and settings.DOI_DEBUG_XML:
            logger.info("Updating DOI %s with DataCite XML: %s" % (doi, datacite_xml))

        if hasattr(settings, 'DOI_SHARED_SECRET') and settings.DOI_SHARED_SECRET:
            post_data['shared_secret'] = settings.DOI_SHARED_SECRET

        doi_response = requests.post(mint_url, data = post_data)
        doi = DOIService._read_doi(doi_response.json(), "MT002")
        logger.info("Updated metadata for DOI %s" % doi)
        return doi

    def _mint_doi(self, url):
        base_url = settings.DOI_MINT_URL
        app_id = settings.DOI_APP_ID
        mint_url = "%s?app_id=%s&url=%s" % (base_url, app_id, url)
        datacite_xml = self._datacite_xml()
        post_data = {'xml': datacite_xml}

        if hasattr(settings, 'DOI_DEBUG_XML') and settings.DOI_DEBUG_XML:
            logger.info("Minting DOI with DataCite XML: %s" % datacite_xml)

        if hasattr(settings, 'DOI_SHARED_SECRET') and settings.DOI_SHARED_SECRET:
            post_data['shared_secret'] = settings.DOI_SHARED_SECRET

        doi_response = requests.post(mint_url, data = post_data)
        doi = DOIService._read_doi(doi_response.json(), "MT001")
        if hasattr(settings, 'DOI_RELATED_INFO_ENABLE') and settings.DOI_RELATED_INFO_ENABLE:
            import tardis.apps.related_info.related_info as ri
            rih = ri.RelatedInfoHandler(self.obj.id)
            doi_info = {
                ri.type_name: 'website',
                ri.identifier_type_name: 'doi',
                ri.identifier_name: doi,
                ri.title_name: '',
                ri.notes_name: '',
            }
            rih.add_info(doi_info)
        return doi

    @staticmethod
    def _read_doi(rj, responsecode):
        if rj['response']['responsecode'] == responsecode:
            return rj['response']['doi']
        else:
            logger.error('unrecognised response: %s' % json.dumps(rj, sort_keys=True, indent=2, separators=(",", ": ")))
            raise Exception('unrecognised response: %s' % json.dumps(rj, sort_keys=True, indent=2, separators=(",", ": ")))

class ExperimentDOIService(DOIService):
    def get_doi(self):
        """
        :return: DOI or None
        :rtype string
        """
        doi_params = ExperimentParameter.objects.filter(name=self.doi_name,
                                    parameterset__schema=self.schema,
                                    parameterset__experiment=self.obj)
        if doi_params.count() == 1:
            return doi_params[0].string_value
        return None

    def get_or_mint_doi(self, url):
        doi = super(ExperimentDOIService, self).get_or_mint_doi(url)
        if doi:
            self._mint_datasets()
        return doi

    def update_doi(self, doi, url):
        doi = super(ExperimentDOIService, self).update_doi(doi, url)
        if doi:
            self._update_datasets()
        return doi

    def _save_doi(self, doi):
        paramset = self._get_or_create_doi_parameterset()
        ep = ExperimentParameter(parameterset=paramset, name=self.doi_name,\
                                    string_value=doi)
        ep.save()
        #if there has been no exception, turn self.obj.locked = True
        self.obj.locked = True
        self.obj.save(update_fields=['locked'])
        return doi

    def _get_or_create_doi_parameterset(self):
        eps, _ = ExperimentParameterSet.objects.\
                    get_or_create(experiment=self.obj,\
                        schema=self.schema)
        return eps

    def _datacite_xml(self):
        """
        :return: datacite XML for self.experiment
        :rtype: string
        """

        from datetime import date
        from django.template import Context
        import os
        template = os.path.join(settings.DOI_TEMPLATE_DIR, 'default.xml')

        if hasattr(settings, 'SITE_LONGTITLE'):
            site_longtitle = settings.SITE_LONGTITLE
        else:
            site_longtitle = "MyTardis"

        ex = self.obj

        c = Context()
        c['title'] = ex.title
        c['contributors'] = [i.lstrip() for i in re.split(';', ex.institution_name)]
        c['publisher'] = site_longtitle
        c['publication_year'] = ex.publication_year
        c['creator_names'] = [a.author for a in ex.author_experiment_set.all()]
        c['resource_type'] = 'Collection'
        c['description'] = ex.description
        if ex.license:
            c['rights_name'] = ex.license.name
            c['rights_url'] = ex.license.url
        c['num_datasets'] = ex.datasets.all().count()
        c['num_files'] = ex.get_datafiles().count()
        c['data_size'] = ex.get_size()
        if self.get_doi():
            c['doi'] = self.get_doi()

        doi_xml = render_to_string(template, context_instance=c)
        return doi_xml

    def _mint_datasets(self):
        datasets = self.obj.datasets.all()
        for ds in datasets:
            doi_url = settings.DOI_BASE_URL + ds.get_absolute_url()
            doi_service = DatasetDOIService(ds, self.obj)
            doi_service.get_or_mint_doi(doi_url)

    def _update_datasets(self):
        datasets = self.obj.datasets.all()
        for ds in datasets:
            doi_service = DatasetDOIService(ds)
            doi = doi_service.get_doi()
            doi_url = settings.DOI_BASE_URL + ds.get_absolute_url()
            doi_service.update_doi(doi, doi_url)

class DatasetDOIService(DOIService):
    """
    DOIService

    Mints DOIs using ANDS' Cite My Data service
    It needs associated Experiment when it is constructed or priorly set
    """

    def __init__(self, obj, ex = None):
        if ex:
            self.experiment = ex
        else:
            self.experiment = obj.experiment
        if self.experiment is None:
            raise Exception('Associated experiment has to be set explictly')

        super(DatasetDOIService, self).__init__(obj)

    def get_doi(self):
        """
        :return: DOI or None
        :rtype string
        """
        doi_params = DatasetParameter.objects.filter(name=self.doi_name,
                                    parameterset__schema=self.schema,
                                    parameterset__dataset=self.obj)
        if doi_params.count() == 1:
            return doi_params[0].string_value
        return None

    def _save_doi(self, doi):
        paramset = self._get_or_create_doi_parameterset()
        ep = DatasetParameter(parameterset=paramset, name=self.doi_name,\
                                    string_value=doi)
        ep.save()
        # if there has been no exception, turn self.obj.immutable = True,
        # save experiment used during minting
        self.obj.immutable = True
        self.obj.experiment_id = self.experiment.id
        self.obj.save(update_fields=['immutable', 'experiment'])
        return doi

    def _get_or_create_doi_parameterset(self):
        dps, _ = DatasetParameterSet.objects.\
                    get_or_create(dataset=self.obj,\
                        schema=self.schema)
        return dps

    def _datacite_xml(self):
        """
        :return: datacite XML for self.obj
        :rtype: string
        """

        from datetime import date
        from django.template import Context
        import os
        template = os.path.join(settings.DOI_TEMPLATE_DIR, 'default.xml')

        if hasattr(settings, 'SITE_LONGTITLE'):
            site_longtitle = settings.SITE_LONGTITLE
        else:
            site_longtitle = "MyTardis"

        ex = self.experiment

        c = Context()
        c['title'] = self.obj.description
        c['contributors'] = [i.lstrip() for i in re.split(';', ex.institution_name)]
        c['publisher'] = site_longtitle
        c['publication_year'] = ex.publication_year
        c['creator_names'] = [a.author for a in ex.author_experiment_set.all()]
        c['parent_doi'] = ExperimentDOIService(ex).get_doi()
        c['resource_type'] = 'Dataset'
        if ex.license:
            c['rights_name'] = ex.license.name
            c['rights_url'] = ex.license.url
        c['num_files'] = self.obj.datafile_set.count()
        c['data_size'] = self.obj.get_size()
        if self.get_doi():
            c['doi'] = self.get_doi()

        doi_xml = render_to_string(template, context_instance=c)
        return doi_xml
