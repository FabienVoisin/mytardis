""" ands_doi.py """

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.importlib import import_module
from urllib2 import HTTPError

from tardis.tardis_portal.models import ExperimentParameter, \
    ExperimentParameterSet, ParameterName, Schema, \
    DatasetParameter, DatasetParameterSet

import requests, json

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
                self.doi_name = ParameterName.objects.get(name=ds['PRAMETERNAME']) # e.g. doi or doi_experiment or doi_dataset
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

    def _mint_doi(self, url):
        base_url = settings.DOI_MINT_URL
        app_id = settings.DOI_APP_ID
        mint_url = "%s?app_id=%s&url=%s" % (base_url, app_id, url)
        post_data = {'xml': self._datacite_xml()}

        if hasattr(settings, 'DOI_SHARED_SECRET') and settings.DOI_SHARED_SECRET:
            post_data['shared_secret'] = settings.DOI_SHARED_SECRET

        doi_response = requests.post(mint_url, data = post_data)
        doi = DOIService._read_doi(doi_response.json())
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
    def _read_doi(rj):
        if rj['response']['responsecode'] == 'MT001':
            return rj['response']['doi']
        else:
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

    def _mint_doi(self, url):
        doi = super(ExperimentDOIService, self)._mint_doi(url)
        if doi:
            self._mint_datasets()
        return doi

    def _save_doi(self, doi):
        paramset = self._get_or_create_doi_parameterset()
        ep = ExperimentParameter(parameterset=paramset, name=self.doi_name,\
                                    string_value=doi)
        ep.save()
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

        ex = self.obj
        c = Context()
        c['title'] = ex.title
        c['institution_name'] = ex.institution_name
        c['publication_year'] = date.today().year
        c['creator_names'] = [a.author for a in ex.author_experiment_set.all()]
        doi_xml = render_to_string(template, context_instance=c)
        return doi_xml

    def _mint_datasets(self):
        datasets = self.obj.datasets.all()
        for ds in datasets:
            doi_url = settings.DOI_BASE_URL + ds.get_absolute_url()
            doi_service = DatasetDOIService(ds)
            doi_service.get_or_mint_doi(doi_url)

class DatasetDOIService(DOIService):
    """
    DOIService

    Mints DOIs using ANDS' Cite My Data service
    POSTs DataCite XML to a web services endpoint
    09/01/2015: Modified based on ands_doi.py, may be they can be merged later
    """

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
        #if there has been no exception, turn self.obj.immutable = True
        self.obj.immutable = True
        self.obj.save(update_fields=['immutable'])
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

        ex = self.obj.get_first_experiment()
        c = Context()
        c['title'] = ex.title
        c['institution_name'] = ex.institution_name
        c['publication_year'] = date.today().year
        c['creator_names'] = [a.author for a in ex.author_experiment_set.all()]
        doi_xml = render_to_string(template, context_instance=c)
        return doi_xml