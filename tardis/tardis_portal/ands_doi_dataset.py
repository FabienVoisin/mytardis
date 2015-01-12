""" ands_doi_dataset.py """

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.importlib import import_module
from urllib2 import HTTPError

from tardis.tardis_portal.models import DatasetParameter, \
    DatasetParameterSet, ParameterName, Schema

import requests, json

import logging
logger = logging.getLogger(__name__)

DOI_NAME = 'doi_dataset'  # the ParameterName.name for the DOI


class DOIService(object):
    """
    DOIService

    Mints DOIs using ANDS' Cite My Data service
    POSTs DataCite XML to a web services endpoint
    09/01/2015: Modified based on ands_doi.py, may be they can be merged later
    """

    def __init__(self, dataset):
        """
        :param dataset: The dataset model object
        :type dataset: :class: `tardis.tardis_portal.models.Dataset`
        """
        if hasattr(settings, 'DOI_ENABLE') and settings.DOI_ENABLE:
            self.dataset = dataset

            provider = settings.DOI_XML_PROVIDER_DATASET
            module_name, constructor_name = provider.rsplit('.', 1)

            module = import_module(module_name)
            constructor = getattr(module, constructor_name)

            self.doi_provider = constructor(dataset)
            self.schema = Schema.objects.get(namespace=settings.DATASET_DOI_NAMESPACE)
            self.doi_name = ParameterName.objects.get(name=DOI_NAME)

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

    def get_doi(self):
        """
        :return: DOI or None
        :rtype string
        """
        doi_params = DatasetParameter.objects.filter(name=self.doi_name,
                                    parameterset__schema=self.schema,
                                    parameterset__dataset=self.dataset)
        if doi_params.count() == 1:
            return doi_params[0].string_value
        return None

    def _save_doi(self, doi):
        paramset = self._get_or_create_doi_parameterset()
        ep = DatasetParameter(parameterset=paramset, name=self.doi_name,\
                                    string_value=doi)
        ep.save()
        #if there has been no exception, turn self.dataset.immutable = True
        self.dataset.immutable = True
        print "Setting immutable"
        self.dataset.save(update_fields=['immutable'])
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
            rih = ri.RelatedInfoHandler(self.dataset.id)
            doi_info = {
                ri.type_name: 'website',
                ri.identifier_type_name: 'doi',
                ri.identifier_name: doi,
                ri.title_name: '',
                ri.notes_name: '',
            }
            rih.add_info(doi_info)
        return doi

    def _datacite_xml(self):
        return self.doi_provider.datacite_xml()

    def _get_or_create_doi_parameterset(self):
        eps, _ = DatasetParameterSet.objects.\
                    get_or_create(dataset=self.dataset,\
                        schema=self.schema)
        return eps

    @staticmethod
    def _read_doi(rj):
	if rj['response']['responsecode'] == 'MT001':
	    return rj['response']['doi']
	else:
	    raise Exception('unrecognised response: %s' % json.dumps(rj, sort_keys=True, indent=2, separators=(",", ": ")))

class DOIXMLProvider(object):
    """
    DOIXMLProvider

    provides datacite XML metadata for a given dataset
    """

    def __init__(self, dataset):
        self.dataset = dataset

    def datacite_xml(self):
        """
        :return: datacite XML for self.dataset
        :rtype: string
        """

        from datetime import date
        from django.template import Context
        import os
        template = os.path.join(settings.DOI_TEMPLATE_DIR, 'default.xml')

        ex = self.dataset.get_first_experiment()
        c = Context()
        c['title'] = ex.title
        c['institution_name'] = ex.institution_name
        c['publication_year'] = date.today().year
        c['creator_names'] = [a.author for a in ex.author_experiment_set.all()]
        doi_xml = render_to_string(template, context_instance=c)
        return doi_xml
