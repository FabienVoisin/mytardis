from django.shortcuts import render, get_object_or_404
from tardis.tardis_portal.models import Dataset
from .models import Source, Analysis, Processing

def dataset(request, id):
    dataset = get_object_or_404(Dataset, pk=id)
    context = {'dataset': dataset, 'analysis': dataset.analysis}
    return render(request, 'dataset.html', context)

def source_index(request):
    context = {'source_list': Source.objects.all()}
    return render(request, 'source/index.html', context)

def source_detail(request, id):
    source = get_object_or_404(Source, pk=id)
    samples = source.sample_set.all()
    context = {'source': source, 'samples': samples}
    return render(request, 'source/detail.html', context)