from django.contrib import admin

from .models import Organism, Source, Sample, Extract, Library, Sequence, Processing, Analysis

admin.site.register(Organism)
admin.site.register(Source)
admin.site.register(Sample)
admin.site.register(Extract)
admin.site.register(Library)
admin.site.register(Sequence)
admin.site.register(Processing)
admin.site.register(Analysis)
