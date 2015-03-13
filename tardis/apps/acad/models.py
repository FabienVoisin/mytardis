from tardis.tardis_portal.models import Dataset
# Django models based on MODC08 Metadata Schema v1.3
from django.db import models

class Organism(models.Model):
    id = models.PositiveSmallIntegerField("NCBI taxonomy ID", primary_key=True)
    genus = models.CharField("Genus", max_length=255, blank=True)
    species = models.CharField("Species", max_length=255, blank=True)
    subspecies = models.CharField("Subspecies", max_length=255, blank=True)
    common = models.CharField("Common name", max_length=255, blank=True)

    def __unicode__(self):
        return self.get_organism_name()

    def get_organism_id(self):
        return str(self.id)

    def get_organism_name(self):
        return str(self.genus + " " + self.species + " " + self.subspecies).rstrip()

    def get_common_name(self):
        return self.common

    class Meta:
        app_label = 'acad'

class Source(models.Model):
    CONTINENTS = (
        ('africa', 'Africa'),
        ('antarctica', 'Antarctica'),
        ('asia', 'Asia'),
        ('australia', 'Australia'),
        ('europe', 'Europe'),
        ('namerica', 'North America'),
        ('samerica', 'South America')
    )
    GENDERS = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('u', 'Unknown')
    )
    AGE_CATS = (
        ('infant', 'Infant'),
        ('child', 'Child'),
        ('yadult', 'Young adult'),
        ('adult', 'Adult'),
        ('unknown', 'Unknown')
    )

    id = models.CharField("Source id", primary_key=True, max_length=255)
    id_type = models.CharField("Who assigned source id", max_length=255)
    other_id = models.CharField("Other id", max_length=255, blank=True)
    other_id_type = models.CharField("Who assigned other id", max_length=255, blank=True)
    date = models.DateField("Date source was collected")
    organism = models.ForeignKey(Organism)
    source_details = models.CharField("Details of sample", max_length=255)
    gender = models.CharField("Gender", choices=GENDERS, max_length=255)
    age_cat = models.CharField("Age category", choices=AGE_CATS, max_length=255)
    age_range = models.CharField("Estimated age range of source", max_length=255, blank=True)
    env_biome = models.CharField("Broad ecological context of where source collected", max_length=255, blank=True)
    env_feature = models.CharField("Geographic environmental features", max_length=255, blank=True)
    env_material = models.CharField("Material in which source was embedded, or material displaced", max_length=255, blank=True)
    geoloc_continent = models.CharField("Continent", choices=CONTINENTS, max_length=255)
    geoloc_country = models.CharField("Country or sea", max_length=255)
    geoloc_locale = models.CharField("Town, city or other locality", max_length=255, blank=True)
    geoloc_lat = models.FloatField(blank=True, null=True)
    geoloc_lon = models.FloatField(blank=True, null=True)
    geo_depth = models.PositiveIntegerField("Geographic location depth", blank=True, null=True)
    geo_altitude = models.PositiveIntegerField("Geographic location altitude", blank=True, null=True)
    geo_elev = models.PositiveIntegerField("Geographic location elevation", blank=True, null=True)
    period = models.CharField("Technological period of source", blank=True, max_length=255)
    carbondate_years = models.PositiveIntegerField("Estimated age of source in radiocarbon years", blank=True, null=True)
    carbondate_error = models.PositiveIntegerField("Estimated carbon date error range", blank=True, null=True)
    carbondate_id = models.CharField("Centre + id reference for carbon dating", blank=True, max_length=255)
    source_notes = models.TextField("Free text notes about source", blank=True)
    group_id = models.CharField("Group/set of sources collected on one trip/survey", max_length=255, blank=True)
    collectedby = models.CharField("Individual/team who collected source", max_length=255, blank=True)

    def __unicode__(self):
        return str(self.organism.get_common_name()) + " " + self.source_details + ", " + self.geoloc_country + " " + str(self.date)

    def get_organism(self):
        return str(self.organism)

    def get_source_id(self):
        return self.id
    
    def get_datasets(self, accssible_dataset_ids=None):
        samples = Sample.objects.filter(source=self)
        extracts = Extract.objects.filter(sample__in=samples)
        libraries = Library.objects.filter(extract__in=extracts)
        sequences = Sequence.objects.filter(library__in=libraries)
        processings = Processing.objects.filter(sequence__in=sequences)
        if accssible_dataset_ids is not None:
            return list(set([proc.analysis.dataset for proc in processings if proc.analysis.dataset.id in accssible_dataset_ids]))
        else:
            return list(set([proc.analysis.dataset for proc in processings]))

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('source_detail', args=[str(self.id)])

    class Meta:
        app_label = 'acad'

class Sample(models.Model):
    SAMPLE_CATS = (
        ('bone', 'Bone'),
        ('tooth', 'Tooth'),
        ('skin', 'Skin'),
        ('tissue', 'Tissue (all non-skin)'),
        ('calculus', 'Calculus'),
        ('feather', 'Feather'),
        ('horn', 'Horn'),
        ('egg', 'Egg'),
        ('sediment', 'Sediment'),
        ('ice', 'Ice'),
        ('hair', 'Hair'),
        ('coprolite', 'Coprolite'),
        ('insect', 'Insect'),
        ('mollusc', 'Mollusc'),
        ('vegetation', 'Vegetation'),
        ('wood', 'Wood'),
        ('seed', 'Seed (includes fruit)'),
        ('other', 'Other'),
        ('extractcontrol', 'Extraction control'),
    )
    ENV_PACKAGES = (
        ('air', 'Air'),
        ('built environment', 'Built environment'),
        ('host-associated', 'Host associated'),
        ('human-associated', 'Human associated'),
        ('human-skin', 'Human skin'),
        ('human-oral', 'Human oral'),
        ('human-gut', 'Human gut'),
        ('human-vaginal', 'Human vaginal'),
        ('microbial mat/biofilm', 'Microbial material/biofilm'),
        ('misc environment', 'Misc environment'),
        ('plant-associated', 'Plant associated'),
        ('sediment', 'Sediment'),
        ('soil', 'Soil'),
        ('wastewater/sludge', 'Wastewater/sludge'),
        ('water', 'Water'),
    )

    id = models.CharField("Sample id", primary_key=True, max_length=255)
    id_type = models.CharField("Who assigned source id", max_length=255)
    source = models.ForeignKey(Source)
    date = models.DateField("Date sample was collected")
    organism = models.ForeignKey(Organism)
    sample_cat = models.CharField("Category of sample", choices=SAMPLE_CATS, max_length=255)
    sample_details = models.CharField("Sample details/description", max_length=255)
    env_package = models.CharField("Environmental package/category of sample", max_length=255, choices=ENV_PACKAGES, blank=True)
    group_id = models.CharField("Group/set of sources collected on one trip/survey", max_length=255, blank=True)
    acad_loc = models.CharField("Where physically held in ACAD", max_length=255, blank=True)
    collectedby = models.CharField("Individual/team who collected source", max_length=255, blank=True)
    sample_notes = models.TextField("Free text notes about sample", blank=True)

    def __unicode__(self):
        return self.get_sample_cat_display() + " (" + self.sample_details + ") " + self.id

    def get_id(self):
        return self.id

    def get_datasets(self, accssible_dataset_ids=None):
        extracts = Extract.objects.filter(sample=self)
        libraries = Library.objects.filter(extract__in=extracts)
        sequences = Sequence.objects.filter(library__in=libraries)
        processings = Processing.objects.filter(sequence__in=sequences)
        if accssible_dataset_ids is not None:
            return list(set([proc.analysis.dataset for proc in processings if proc.analysis.dataset.id in accssible_dataset_ids]))
        else:
            return list(set([proc.analysis.dataset for proc in processings]))

    class Meta:
        app_label = 'acad'

class Extract(models.Model):
    id = models.CharField("Extract ID", primary_key=True, max_length=255)
    sample = models.ForeignKey(Sample)
    date = models.DateField("Date extract was done")
    protocol_ref = models.CharField("Publication describing library construction method", max_length=255)
    protocol_note = models.TextField("Free text note describing extraction method", blank=True)

    def __unicode__(self):
        return "Extract " + self.id + " " + str(self.date)

    class Meta:
        app_label = 'acad'

class Library(models.Model):
    class Meta:
        verbose_name_plural = 'libraries'
        app_label = 'acad'

    LIB_SOURCES = (
        ('genomic', 'Genomic'),
        ('metagenomic', 'Metagenomic'),
        ('transcriptomic', 'Transcriptomic'),
        ('metatranscriptomic', 'Metatranscriptomic'),
        ('synthetic', 'Synthetic'),
        ('viralrna', 'Viral RNA'),
        ('other', 'Other'),
    )
    ENRICH_METHOD = (
        ('PCR', 'PCR'),
        ('randomPCR', 'Random PCR'),
        ('RT-PCR', 'RT-PCR'),
        ('HMPR', 'HMPR'),
        ('MF', 'MF'),
        ('repfract', 'Repeat fractionation'),
        ('sizefract', 'Size fractionation'),
        ('MSLL', 'MSLL'),
        ('cDNA', 'cDNA'),
        ('ChIP', 'ChIP'),
        ('Mnase', 'Dnase'),
        ('hybrid', 'Hybrid selection'),
        ('restrict', 'Restriction digest'),
        ('5-methyl', '5-methylcytidine antibody'),
        ('MDBD2', 'MBD2 protein methyl-CpG binding domain'),
        ('CAGE', 'CAGE'),
        ('RACE', 'RACE'),
        ('MDA', 'MDA'),
        ('padlock', 'Padlock probes capture method'),
        ('Oligo-dT', 'Oligo-dT'),
        ('inverse', 'Inverse rRNA selection'),
        ('random', 'Random'),
        ('other', 'Other'),
        ('unspec', 'Unspecified'),
    )
    ENRICH_TARGET = (
        ('16S', '16S rNA'),
        ('18S', '18S rNA'),
        ('rcbl', 'RCBL'),
        ('matk', 'matK'),
        ('cox1', 'COX1'),
        ('its1', 'ITS1-5.8S-ITS2'),
        ('exome', 'Exome'),
        ('other', 'Other'),
    )

    id = models.CharField("Library ID", primary_key=True, max_length=255)
    extract = models.ForeignKey(Extract)
    date = models.DateField("Date library was made")
    source = models.CharField("Type of material", choices=LIB_SOURCES, max_length=255)
    layout = models.CharField("Layout/construction method", choices=(('single', 'Single'),('paired','Paired')), max_length=255)
    type = models.CharField("Type of library", choices=(('amplicon','Amplicon'),('shotgun','Shotgun')), max_length=255)
    protocol_ref = models.CharField("Publication describing library construction method", max_length=255)
    protocol_note = models.TextField("Free text note briefly describing construction method/protocol used", blank=True)
    repair_method = models.CharField("DNA repair method", max_length=255, default="None")
    enrich_method = models.CharField("Library enrichment method", max_length=255, choices=ENRICH_METHOD)
    enrich_target = models.CharField("Any gene/s or other features targeted", max_length=255, blank=True, choices=ENRICH_TARGET)
    enrich_target_subfrag = models.CharField("Any target subfragment", max_length=255, blank=True)
    amp_method = models.CharField("Method/enzyme used to amplify target", max_length=255, blank=True)

    def __unicode__(self):
        return "Library " + self.id + " " + str(self.date)

class Sequence(models.Model):
    SEQ_METHOD = (
        ('POOLCLONE', 'Pooled clone sequencing'),
        ('CLONE', 'Clone by clone sequencing'),
        ('WGS', 'Whole genome shotgun sequencing'),
        ('WGA', 'Whole genome amplification sequencing'),
        ('WCS', 'Random chromosome sequencing'),
        ('WXS', 'Random exon sequencing'),
        ('AMPLICON', 'Amplicon sequencing'),
        ('ChIP-Seq', 'Direct sequencing of chromatin immunoprecipitates'),
        ('RNA-Seq', 'Whole transcriptome shotgun sequencing'),
        ('MRE-Seq', 'Methylation-sensitive Restriction Enzyme sequencing strategy'),
        ('MeDIP-Seq', 'Methylated DNA Immunoprecipitation Sequencing strategy'),
        ('MBD-Seq', 'Direct sequencing of methylated fractions sequencing strategy'),
        ('MNase-Seq', 'Direct sequencing following MNase digestion'),
        ('DNase-Hypersensitivity', 'Sequencing of DNase-hypersensitive sites to identify regularatory elements'),
        ('Bisulfite-Seq', 'Sequencing following treatment of DNA with bisulfite to determine methylation status'),
        ('EST', 'Single pass sequencing of cDNA templates'),
        ('FL-cDNA', 'Full-length sequencing of cDNA templates'),
        ('miRNA-Seq', 'Micro RNA sequencing'),
        ('ncRNA-Seq', 'Non-coding RNA sequencing'),
        ('FINISHING', 'Sequencing intended to finish (close) gaps in existing coverage'),
        ('CTS', 'Concatenated tag sequencing'),
        ('Tn-Seq', 'Transposon RNA sequencing'),
        ('VALIDATION', 'Validation sequencing'),
        ('FAIRE-seq', 'Formaldehyde Assisted Isolation of Regulatory Elements sequencing'),
        ('SELEX', 'Systematic Evolution of Ligands by EXponential enrichment sequencing'),
        ('RIP-Seq', 'RNA-immunoprecipitation sequencing'),
        ('ChIA-PET', 'Chromatin Interaction Analysis by Paired-End Tag sequencing'),
        ('RAD-Seq', 'Restriction site Associated DNA sequencing'),
    )

    id = models.CharField("Sequence ID", primary_key=True, max_length=255)
    library = models.ForeignKey(Library)
    date = models.DateField("Date sequence was run")
    centre = models.CharField("Centre/lab/organisation where sequencing was performed", default="ACAD", max_length=255)
    method = models.CharField("Sequencing method used", max_length=255, choices=SEQ_METHOD)
    tech = models.CharField("Machine/technology used to generate sequence", max_length=255)
    tech_chem = models.PositiveSmallIntegerField("Sequencer chemistry version")
    tech_options = models.CharField("Sequencing options", max_length=255, default="Default")
    fileformat = models.CharField("Output file format", max_length=255, default="FASTQ")
    qualscale = models.CharField("Scale used for quality read score", max_length=255, default="Phred")
    error_rate = models.PositiveSmallIntegerField("Estimated error rate: 1 x 10^x", blank=True, null=True)
    error_method = models.CharField("Method of calculating estimated error rate", max_length=255, blank=True)
    demulti_prog = models.CharField("Index demultiplexing program", max_length=255, blank=True)
    demulti_prog_ver = models.CharField("Index demultiplexing program version", max_length=255, blank=True)
    demulti_prog_opt = models.CharField("Index demultiplexing program options", max_length=255, blank=True)

    def __unicode__(self):
        return "Sequence " + self.id + " " + str(self.date)

    class Meta:
        app_label = 'acad'

class Processing(models.Model):
    id = models.CharField("Processing ID", primary_key=True, max_length=255)
    sequence = models.ForeignKey(Sequence)
    analysis = models.ForeignKey('Analysis')
    reference = models.CharField("Reference genome or library to which sequence was aligned", max_length=255)
    fold_coverage = models.DecimalField("Average fold coverage of reference sequence", max_digits=6, decimal_places=3, blank=True, null=True)
    percent_coverage = models.DecimalField("Percentage coverage of reference sequence", max_digits=6, decimal_places=3, blank=True, null=True)
    contigs = models.PositiveSmallIntegerField("Number of contiguous sequences", blank=True, null=True)
    package = models.CharField("Software package primarily used in processing", max_length=255)
    package_ver = models.CharField("Software package version number", max_length=255)

    def __unicode__(self):
        return "Processing " + self.id

    class Meta:
        app_label = 'acad'

class Analysis(models.Model):
    class Meta:
        verbose_name_plural = 'analyses'
        app_label = 'acad'

    id = models.CharField("Analysis ID", primary_key=True, max_length=255)
    dataset = models.OneToOneField('tardis_portal.Dataset')
    package = models.CharField("Software package primarily used in analysis", max_length=255)
    package_ver = models.CharField("Software package version number", max_length=255)

    def __unicode__(self):
        return "Analysis " + self.id
