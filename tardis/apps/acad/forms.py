from haystack.forms import SearchForm
from django import forms
from .models import Source
import logging

logger = logging.getLogger(__name__)

class RawSearchForm(SearchForm):

    def search(self):
        query = self.cleaned_data['q']
        # NOTE: end_offset = 1 is just a quick hack way to stop haystack getting lots of search
        # results even though we dont need them. Fix this to properly set rows=0
        sqs = self.searchqueryset.raw_search(query, end_offset=1)
        if self.load_all:
            sqs = sqs.load_all()

        return sqs

class AdvancedSearchForm(SearchForm):
    gender=forms.CharField(required=False)
    age=forms.CharField(required=False)
    continent=forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                         choices=Source.CONTINENTS, required=False)
    carbondate=forms.CharField(required=False)

    def search(self):
        logger.info("%s %s %s %s" % (self.cleaned_data['q'],self.cleaned_data['gender'],self.cleaned_data['age'],self.cleaned_data['continent']))
        query = self.cleaned_data['q']
        # NOTE: end_offset = 1 is just a quick hack way to stop haystack getting lots of search
        # results even though we dont need them. Fix this to properly set rows=0
        sqs = self.searchqueryset.raw_search(query, end_offset=1)
        #if self.cleaned_data['gender'] and self.cleaned_data['gender'] != "All":
        #    sqs = sqs.filter(source_gender=self.cleaned_data['gender'])
        #if self.cleaned_data['age'] and self.cleaned_data['age'] != "All":
        #    sqs = sqs.filter(source_age_cat=self.cleaned_data['age'])
        #if self.cleaned_data['continent'] and len(self.cleaned_data['continent'])>0:
        #    sqs = sqs.filter(source_geoloc_continent=self.cleaned_data['continent'])
        #if self.load_all:
        #    sqs = sqs.load_all()

        return sqs

