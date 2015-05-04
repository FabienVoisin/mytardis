from django.contrib.auth.decorators import login_required, permission_required
from haystack.views import SearchView
from haystack.query import SearchQuerySet
from tardis.apps.acad.forms import RawSearchForm, AdvancedSearchForm
from tardis.tardis_portal.views import SearchQueryString
from tardis.tardis_portal.auth import decorators as authz
import logging
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.http import HttpResponseRedirect, HttpResponse,\
    HttpResponseForbidden, HttpResponseNotFound, Http404
from tardis.tardis_portal.models import Experiment, ExperimentParameter, \
    DatafileParameter, DatasetParameter, ObjectACL, DataFile, \
    DatafileParameterSet, ParameterName, GroupAdmin, Schema, \
    Dataset, ExperimentParameterSet, DatasetParameterSet, \
    License, UserProfile, UserAuthentication, Token
from tardis.tardis_portal.shortcuts import render_response_index, \
    return_response_error, return_response_not_found, \
    render_response_search, get_experiment_referer
from .models import Organism, Source, Sample, Extract, Library, Sequence,   Processing, Analysis

logger = logging.getLogger(__name__)

class AcadSearchView(SearchView):
    def __name__(self):
        return "AcadSearchView"

    def extra_context(self):
        extra = super(AcadSearchView, self).extra_context()
        # Results may contain Experiments, Datasets and DataFiles.
        # Group them into experiments, noting whether or not the search
        # hits were in the Dataset(s) or DataFile(s)
        logger.debug("self.__dict__ %s"%self.__dict__)
        logger.debug("self.form.__dict__ %s"%self.form.__dict__)
        logger.debug("self.results %s"%self.results)
        extra['query_string'] = self.form.query_string
        exp_results=self.results.facet('experiment_id_stored')
        exp_facets = exp_results.facet_counts()
        if exp_facets:
            experiment_facets = exp_facets['fields']['experiment_id_stored']
            experiment_ids = [int(f[0])
                              for f in experiment_facets if int(f[1]) > 0]
        else:
            experiment_ids = []

        access_list = []

        if self.request.user.is_authenticated():
            access_list.extend(
                [e.pk for e in
                 authz.get_accessible_experiments(self.request)])

        access_list.extend(
            [e.pk for e in Experiment.objects.exclude(
                public_access=Experiment.PUBLIC_ACCESS_NONE)])

        ids = list(set(experiment_ids) & set(access_list))
        experiments = Experiment.objects.filter(pk__in=ids)\
                                        .order_by('-update_time')
                                        
        #dataset_access_list=Dataset.objects.filter(experiments__pk__in=access_list)
        dataset_ids=Dataset.objects.filter(experiments__pk__in=access_list).values_list('id', flat=True).order_by('id')
        logger.debug("access_list %s dataset_ids %s"%(access_list, dataset_ids))
        
        #results = []
        #for e in experiments:
        #    result = {}
        #    result['sr'] = e
        #    result['dataset_hit'] = False
        #    result['datafile_hit'] = False
        #    result['experiment_hit'] = False
        #    results.append(result)

        extra['experiments'] = experiments
        extra['dataset_ids'] = dataset_ids

        source_results=self.results.facet('source_id')
        source_facets = source_results.facet_counts()
        if source_facets:
            source_facets = source_facets['fields']['source_id']
            #logger.info(source_facets)
            source_ids = [f[0]
                              for f in source_facets if int(f[1]) > 0]
        else:
            source_ids = []
        source_id_string=(",").join(["'"+s+"'" for s in set(source_ids)])
        sources=Source.objects.extra(where=["lower(id) IN (%s)" % source_id_string], order_by=["-date"])
        logger.debug("sources %s " % sources)
        #if self.form.cleaned_data['gender'] and self.form.cleaned_data['gender'] != "All":
        #    sources = sources.filter(gender=self.form.cleaned_data['gender'])
        #if self.form.cleaned_data['age'] and self.form.cleaned_data['age'] != "All":
        #    sources = sources.filter(age_cat=self.form.cleaned_data['age'])
        #    logger.info("filterd age %s sources %s " % (self.form.cleaned_data['age'], sources))
        #logger.info("filterd continent %s " % (self.form.cleaned_data.get('continent')))
        #if self.form.cleaned_data['continent'] and len(self.form.cleaned_data['continent'])>0:
        #    sources = sources.filter(geoloc_continent__in=self.form.cleaned_data['continent'])
        #if self.form.cleaned_data['carbondate'] != "1000,150000":
        #    logger.info("filterd carbondate %s " % (self.form.cleaned_data['carbondate']))
        #    carbon_date=self.form.cleaned_data['carbondate'].split(",")
        #    sources = sources.filter(carbondate_years__range=(carbon_date[0], carbon_date[1]))
        valid_sources=[]
        for source in sources:
            logger.debug("source %s datasets %s" % (source.id, source.get_datasets(dataset_ids)))
            if len(source.get_datasets(dataset_ids))>0:
                valid_sources.append(source)
        #    sqs = sqs.filter(source_geoloc_continent=self.cleaned_data['continent'])
        #for id in list(set(source_ids)):
        #    sources.extend(Source.objects.extra(where=["id LIKE '"+id+"'"]))
        #sources.sort(key=lambda source: source.date, reverse=False)
        extra['sources'] = valid_sources

        return extra

    # override SearchView's method in order to
    # return a ResponseContext
    def create_response(self):
        (paginator, page) = self.build_page()

        # Remove unnecessary whitespace
        # TODO this should just be done in the form clean...
        query = SearchQueryString(self.query)
        context = {
            'search_query': query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'subtitle': 'Search Results',
        }
        context.update(self.extra_context())

        return render_response_index(self.request, self.template, context)


def single_search(request):
    #search_query = FacetFixedSearchQuery(backend=HighlightSearchBackend())
    sqs = SearchQuerySet() #query=search_query)
    sqs.highlight()

    return AcadSearchView(
        template='search/acad_search.html',
        searchqueryset=sqs,
        form_class=RawSearchForm,
    ).__call__(request)

def search_source(request):

    """Either show the search source form or the result of the search
    source query.

    """

    if len(request.GET) == 0:
        c = Context({'searchForm': AdvancedSearchForm(), "gender_choices": Source.GENDERS, "age_cat_choices": Source.AGE_CATS, "continent_choices": Source.CONTINENTS, subtitle: 'Advanced Search'})
        url = 'search/advanced_search_form.html'
        return HttpResponse(render_response_search(request, url, c))

    #form = __getSearchExperimentForm(request)
    #experiments = __processExperimentParameters(request, form)

    # check if the submitted form is valid
    #if experiments is not None:
    #    bodyclass = 'list'
    #else:
    #    return __forwardToSearchExperimentFormPage(request)

    sqs = SearchQuerySet() #query=search_query)
    sqs.highlight()

    return AcadSearchView(
        template='search/acad_search.html',
        searchqueryset=sqs,
        form_class=AdvancedSearchForm,
    ).__call__(request)

def source_index(request):
    access_list = []
    if request.user.is_authenticated():
        access_list.extend(
            [e.pk for e in
             authz.get_accessible_experiments(request)])

    access_list.extend(
        [e.pk for e in Experiment.objects.exclude(
            public_access=Experiment.PUBLIC_ACCESS_NONE)])

    dataset_ids=Dataset.objects.filter(experiments__pk__in=access_list).values_list('id', flat=True).order_by('id')
    valid_sources=[]
    for source in Source.objects.all():
        #logger.info("source %s datasets %s" % (source.id, source.get_datasets(dataset_ids)))
        if len(source.get_datasets(dataset_ids))>0:
            valid_sources.append(source)
    context = {'sources': valid_sources, 'dataset_ids': dataset_ids, subtitle: 'Sources'}
    return render(request, 'source/index.html', context)

def source_detail(request, id):
    source = get_object_or_404(Source, pk=id)
    access_list = []
    if request.user.is_authenticated():
        access_list.extend(
            [e.pk for e in
             authz.get_accessible_experiments(request)])

    access_list.extend(
        [e.pk for e in Experiment.objects.exclude(
            public_access=Experiment.PUBLIC_ACCESS_NONE)])

    dataset_ids=Dataset.objects.filter(experiments__pk__in=access_list).values_list('id', flat=True).order_by('id')
    if len(source.get_datasets(dataset_ids))==0:
        #logger.error("Intruder trying to get access, stop it")
        return HttpResponseNotFound('<h1>Source not accessible</h1>')
    samples = source.sample_set.all()
    context = {'source': source, 'samples': samples, 'dataset_ids': dataset_ids, subtitle: source.id}
    return render(request, 'source/detail.html', context)
