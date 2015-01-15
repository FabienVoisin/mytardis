from django.shortcuts import render, get_object_or_404
from .models import Source

def source_index(request):
    context = {'source_list': Source.objects.all()}
    return render(request, 'source/index.html', context)

def source_detail(request, id):
    source = get_object_or_404(Source, pk=id)
    context = {'source': source}
    return render(request, 'source/detail.html', context) 
