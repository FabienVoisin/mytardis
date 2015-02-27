from haystack.forms import SearchForm
from django import forms

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

    def search(self):
        query = self.cleaned_data['q']
        if gender:
            query="%s AND source_gender:%s" % (query, gender)
        # NOTE: end_offset = 1 is just a quick hack way to stop haystack getting lots of search
        # results even though we dont need them. Fix this to properly set rows=0
        sqs = self.searchqueryset.raw_search(query, end_offset=1)
        if self.load_all:
            sqs = sqs.load_all()

        return sqs

