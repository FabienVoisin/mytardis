'''
RESTful API for MyTardis models and data.
Implemented with Tastypie.

.. moduleauthor:: Grischa Meyer <grischa@gmail.com>
'''
import json as simplejson

import sys

from django.conf import settings
from django.conf.urls.defaults import url
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.core import signals
from django.core.serializers import json
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseForbidden

from tardis.tardis_portal.auth.decorators import \
    get_accessible_datafiles_for_user
from tardis.tardis_portal.auth.decorators import has_datafile_access
from tardis.tardis_portal.auth.decorators import has_datafile_download_access
from tardis.tardis_portal.auth.decorators import has_dataset_access
from tardis.tardis_portal.auth.decorators import has_dataset_write
from tardis.tardis_portal.auth.decorators import has_delete_permissions
from tardis.tardis_portal.auth.decorators import has_experiment_access
from tardis.tardis_portal.auth.decorators import has_write_permissions
from tardis.tardis_portal.auth.localdb_auth import django_user
from tardis.tardis_portal.models import ObjectACL
from tardis.tardis_portal.models.datafile import DataFile
from tardis.tardis_portal.models.datafile import DataFileObject
from tardis.tardis_portal.models.dataset import Dataset
from tardis.tardis_portal.models.experiment import Experiment
from tardis.tardis_portal.models.experiment import Author_Experiment
from tardis.tardis_portal.models.parameters import DatafileParameter
from tardis.tardis_portal.models.parameters import DatafileParameterSet
from tardis.tardis_portal.models.parameters import DatasetParameter
from tardis.tardis_portal.models.parameters import DatasetParameterSet
from tardis.tardis_portal.models.parameters import ExperimentParameter
from tardis.tardis_portal.models.parameters import ExperimentParameterSet
from tardis.tardis_portal.models.parameters import ParameterName
from tardis.tardis_portal.models.parameters import Schema
from tardis.tardis_portal.models.storage import StorageBox

from tardis.apps.acad.models import Organism, Source, Sample, Extract, Library, Sequence, Processing, Analysis

from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import SessionAuthentication
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.exceptions import NotFound
from tastypie.exceptions import Unauthorized
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash


class PrettyJSONSerializer(Serializer):
    json_indent = 2

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
                                sort_keys=True, ensure_ascii=False,
                                indent=self.json_indent) + "\n"

if settings.DEBUG:
    default_serializer = PrettyJSONSerializer()
else:
    default_serializer = Serializer()


class MyTardisAuthentication(object):
    '''
    custom tastypie authentication that works with both anonymous use and
    a number of available auth mechanisms.
    '''
    def is_authenticated(self, request, **kwargs):  # noqa # too complex
        '''
        handles backends explicitly so that it can return False when
        credentials are given but wrong and return Anonymous User when
        credentials are not given or the session has expired (web use).
        '''
        auth_info = request.META.get('HTTP_AUTHORIZATION')

        if 'HTTP_AUTHORIZATION' not in request.META:
            if hasattr(request.user, 'allowed_tokens'):
                tokens = request.user.allowed_tokens
            session_auth = SessionAuthentication()
            check = session_auth.is_authenticated(request, **kwargs)
            if check:
                if isinstance(check, HttpUnauthorized):
                    session_auth_result = False
                else:
                    request._authentication_backend = session_auth
                    session_auth_result = check
            else:
                request.user = AnonymousUser()
                session_auth_result = True
            request.user.allowed_tokens = tokens
            return session_auth_result
        else:
            if auth_info.startswith('Basic'):
                basic_auth = BasicAuthentication()
                check = basic_auth.is_authenticated(request, **kwargs)
                if check:
                    if isinstance(check, HttpUnauthorized):
                        return False
                    else:
                        request._authentication_backend = basic_auth
                        return check
            if auth_info.startswith('ApiKey'):
                apikey_auth = ApiKeyAuthentication()
                check = apikey_auth.is_authenticated(request, **kwargs)
                if check:
                    if isinstance(check, HttpUnauthorized):
                        return False
                    else:
                        request._authentication_backend = apikey_auth
                        return check

    def get_identifier(self, request):
        try:
            return request._authentication_backend.get_identifier(request)
        except AttributeError:
            return 'nouser'

default_authentication = MyTardisAuthentication()


class ACLAuthorization(Authorization):
    '''Authorisation class for Tastypie.
    '''
    def read_list(self, object_list, bundle):  # noqa # too complex
        if bundle.request.user.is_authenticated() and \
           bundle.request.user.is_superuser:
            return object_list
        if type(bundle.obj) == Experiment:
            experiments = Experiment.safe.all(bundle.request.user)
            return [exp for exp in experiments if exp in object_list]
        elif type(bundle.obj) == ExperimentParameterSet:
            experiments = Experiment.safe.all(bundle.request.user)
            return [eps for eps in object_list
                    if eps.experiment in experiments]
        elif type(bundle.obj) == ExperimentParameter:
            experiments = Experiment.safe.all(bundle.request.user)
            return [ep for ep in object_list
                    if ep.parameterset.experiment in experiments]
        elif type(bundle.obj) == Dataset:
            return [ds for ds in object_list
                    if has_dataset_access(bundle.request, ds.id)]
        elif type(bundle.obj) == DatasetParameterSet:
            return [dps for dps in object_list
                    if has_dataset_access(bundle.request, dps.dataset.id)]
        elif type(bundle.obj) == DatasetParameter:
            return [dp for dp in object_list
                    if has_dataset_access(bundle.request,
                                          dp.parameterset.dataset.id)]
        elif type(bundle.obj) == DataFile:
            all_dfs = set(
                get_accessible_datafiles_for_user(bundle.request))
            return list(all_dfs.intersection(object_list))
        elif type(bundle.obj) == DatafileParameterSet:
            datafiles = get_accessible_datafiles_for_user(bundle.request)
            return [dfps for dfps in object_list if dfps.datafile in datafiles]
        elif type(bundle.obj) == DatafileParameter:
            datafiles = get_accessible_datafiles_for_user(bundle.request)
            return [dfp for dfp in object_list
                    if dfp.parameterset.datafile in datafiles]
        elif type(bundle.obj) == Schema:
            return object_list
        elif type(bundle.obj) == ParameterName:
            return object_list
        else:
            return []

    def read_detail(self, object_list, bundle):  # noqa # too complex
        if bundle.request.user.is_authenticated() and \
           bundle.request.user.is_superuser:
            return True
        if type(bundle.obj) == Experiment:
            return has_experiment_access(bundle.request, bundle.obj.id)
        elif type(bundle.obj) == ExperimentParameterSet:
            return has_experiment_access(
                bundle.request, bundle.obj.experiment.id)
        elif type(bundle.obj) == ExperimentParameter:
            return has_experiment_access(
                bundle.request, bundle.obj.parameterset.experiment.id)
        elif type(bundle.obj) == Dataset:
            return has_dataset_access(bundle.request, bundle.obj.id)
        elif type(bundle.obj) == DatasetParameterSet:
            return has_dataset_access(bundle.request, bundle.obj.dataset.id)
        elif type(bundle.obj) == DatasetParameter:
            return has_dataset_access(
                bundle.request, bundle.obj.parameterset.dataset.id)
        elif type(bundle.obj) == DataFile:
            return has_datafile_access(bundle.request, bundle.obj.id)
        elif type(bundle.obj) == DatafileParameterSet:
            return has_datafile_access(
                bundle.request, bundle.obj.datafile.id)
        elif type(bundle.obj) == DatafileParameter:
            return has_datafile_access(
                bundle.request, bundle.obj.parameterset.datafile.id)
        elif type(bundle.obj) == User:
            # allow all authenticated users to read public user info
            # the dehydrate function also adds/removes some information
            authenticated = bundle.request.user.is_authenticated()
            public_user = bundle.obj.experiment_set.filter(
                public_access__gt=1).count() > 0
            return public_user or authenticated
        elif type(bundle.obj) == Schema:
            return True
        elif type(bundle.obj) == ParameterName:
            return True
        elif type(bundle.obj) == StorageBox:
            return bundle.request.user.is_authenticated()
        raise NotImplementedError(type(bundle.obj))

    def create_list(self, object_list, bundle):
        raise NotImplementedError(type(bundle.obj))

    def create_detail(self, object_list, bundle):  # noqa # too complex
        if not bundle.request.user.is_authenticated():
            return False
        if bundle.request.user.is_authenticated() and \
           bundle.request.user.is_superuser:
            return True
        if type(bundle.obj) == Experiment:
            return bundle.request.user.has_perm('tardis_portal.add_experiment')
        elif type(bundle.obj) in (ExperimentParameterSet,):
            if not bundle.request.user.has_perm(
                    'tardis_portal.change_experiment'):
                return False
            experiment_uri = bundle.data.get('experiment', None)
            if experiment_uri is not None:
                experiment = ExperimentResource.get_via_uri(
                    ExperimentResource(), experiment_uri, bundle.request)
                return has_write_permissions(bundle.request, experiment.id)
            elif getattr(bundle.obj.experiment, 'id', False):
                return has_write_permissions(bundle.request,
                                             bundle.obj.experiment.id)
            return False
        elif type(bundle.obj) in (ExperimentParameter,):
            return bundle.request.user.has_perm(
                'tardis_portal.change_experiment') and \
                has_write_permissions(bundle.request,
                                      bundle.obj.parameterset.experiment.id)
        elif type(bundle.obj) == Dataset:
            if not bundle.request.user.has_perm(
                    'tardis_portal.change_dataset'):
                return False
            perm = False
            for exp_uri in bundle.data.get('experiments', []):
                try:
                    this_exp = ExperimentResource.get_via_uri(
                        ExperimentResource(), exp_uri, bundle.request)
                except:
                    return False
                if has_write_permissions(bundle.request, this_exp.id):
                    perm = True
                else:
                    return False
            return perm
        elif type(bundle.obj) in (DatasetParameterSet,):
            if not bundle.request.user.has_perm(
                    'tardis_portal.change_dataset'):
                return False
            dataset_uri = bundle.data.get('dataset', None)
            if dataset_uri is not None:
                dataset = DatasetResource.get_via_uri(
                    DatasetResource(), dataset_uri, bundle.request)
                return has_dataset_write(bundle.request, dataset.id)
            elif getattr(bundle.obj.dataset, 'id', False):
                return has_dataset_write(bundle.request,
                                         bundle.obj.dataset.id)
            return False
        elif type(bundle.obj) in (DatasetParameter,):
            return bundle.request.user.has_perm(
                'tardis_portal.change_dataset') and \
                has_dataset_write(bundle.request,
                                  bundle.obj.parameterset.dataset.id)
        elif type(bundle.obj) == DataFile:
            dataset = DatasetResource.get_via_uri(DatasetResource(),
                                                  bundle.data['dataset'],
                                                  bundle.request)
            return all([
                bundle.request.user.has_perm('tardis_portal.change_dataset'),
                bundle.request.user.has_perm('tardis_portal.add_datafile'),
                has_dataset_write(bundle.request, dataset.id),
            ])
        elif type(bundle.obj) == DatafileParameterSet:
            dataset = Dataset.objects.get(
                pk=bundle.obj.datafile.dataset.id)
            return all([
                bundle.request.user.has_perm('tardis_portal.change_dataset'),
                bundle.request.user.has_perm('tardis_portal.add_datafile'),
                has_dataset_write(bundle.request, dataset.id),
            ])
        elif type(bundle.obj) == DatafileParameter:
            dataset = Dataset.objects.get(
                pk=bundle.obj.parameterset.datafile.dataset.id)
            return all([
                bundle.request.user.has_perm('tardis_portal.change_dataset'),
                bundle.request.user.has_perm('tardis_portal.add_datafile'),
                has_dataset_write(bundle.request, dataset.id),
            ])
        elif type(bundle.obj) == DataFileObject:
            return all([
                bundle.request.user.has_perm('tardis_portal.change_dataset'),
                bundle.request.user.has_perm('tardis_portal.add_datafile'),
                has_dataset_write(bundle.request,
                                  bundle.obj.datafile.dataset.id),
            ])
        raise NotImplementedError(type(bundle.obj))

    def update_list(self, object_list, bundle):
        raise NotImplementedError(type(bundle.obj))
        # allowed = []

        # # Since they may not all be saved, iterate over them.
        # for obj in object_list:
        #     if obj.user == bundle.request.user:
        #         allowed.append(obj)

        # return allowed

    def update_detail(self, object_list, bundle):  # noqa # too complex
        if not bundle.request.user.is_authenticated():
            return False
        if type(bundle.obj) == Experiment:
            return bundle.request.user.has_perm(
                'tardis_portal.change_experiment') and \
                has_write_permissions(bundle.request, bundle.obj.id)
        elif type(bundle.obj) == ExperimentParameterSet:
            return bundle.request.user.has_perm(
                'tardis_portal.change_experiment')  # and \
        #      has_write_permissions(bundle.request, bundle.obj.experiment.id)
        elif type(bundle.obj) == ExperimentParameter:
            return bundle.request.user.has_perm(
                'tardis_portal.change_experiment')
        elif type(bundle.obj) == Dataset:
            return False
        elif type(bundle.obj) == DatasetParameterSet:
            return False
        elif type(bundle.obj) == DatasetParameter:
            return False
        elif type(bundle.obj) == DataFile:
            return False
        elif type(bundle.obj) == DatafileParameterSet:
            return False
        elif type(bundle.obj) == DatafileParameter:
            return False
        elif type(bundle.obj) == Schema:
            return False
        elif type(bundle.obj) in [ Author_Experiment, Organism, Source, Sample, Extract, Library, Sequence, Processing, Analysis ]:
            return bundle.request.user.has_perm('tardis_portal.change_dataset')
        raise NotImplementedError(type(bundle.obj))

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        if type(bundle.obj) == Experiment:
            return bundle.request.user.has_perm(
                'tardis_portal.change_experiment') and \
                has_delete_permissions(bundle.request, bundle.obj.id)
        raise Unauthorized("Sorry, no deletes.")


def lookup_by_unique_id_only(resource):
    '''
    returns custom lookup function. initialise with resource type
    '''
    def lookup_kwargs_with_identifiers(self, bundle, kwargs):
        if 'id' not in kwargs and 'pk' not in kwargs:
            # new instance is required
            return {'id': -1}  # this will not match any exisitng resource
        return super(resource,
                     self).lookup_kwargs_with_identifiers(bundle, kwargs)

    return lookup_kwargs_with_identifiers


class UserResource(ModelResource):
    class Meta:
        authentication = default_authentication
        authorization = ACLAuthorization()
        queryset = User.objects.all()
        allowed_methods = ['get']
        fields = ['username', 'first_name', 'last_name']
        serializer = default_serializer

    def dehydrate(self, bundle):
        '''
        use cases:
        public user:
          anonymous:
            name, uri, email, id
          authenticated:
            other user:
              name, uri, email, id
            same user:
              name, uri, email, id, username
        private user:
          anonymous:
            none
          authenticated:
            other user:
              name, uri, id
            same user:
              name, uri, email, id, username
        '''
        authuser = bundle.request.user
        authenticated = authuser.is_authenticated()
        queried_user = bundle.obj
        public_user = queried_user.experiment_set.filter(
            public_access__gt=1).count() > 0
        same_user = authuser == queried_user

        # add the database id for convenience
        bundle.data['id'] = queried_user.id

        # allow the user to find out their username and email
        if same_user and authenticated:
            bundle.data['email'] = queried_user.email
        else:
            del(bundle.data['username'])

        # add public information
        if public_user:
            bundle.data['email'] = queried_user.email

        return bundle


class MyTardisModelResource(ModelResource):

    def lookup_kwargs_with_identifiers(self, bundle, kwargs):
        return lookup_by_unique_id_only(MyTardisModelResource)(
            self, bundle, kwargs)

    def patch_list(self, request, **kwargs):
        return super(MyTardisModelResource, self).patch_list(request, **kwargs)

    class Meta:
        authentication = default_authentication
        authorization = ACLAuthorization()
        serializer = default_serializer


class SchemaResource(MyTardisModelResource):

    def lookup_kwargs_with_identifiers(self, bundle, kwargs):
        return lookup_by_unique_id_only(SchemaResource)(self, bundle, kwargs)

    class Meta(MyTardisModelResource.Meta):
        queryset = Schema.objects.all()


class ParameterNameResource(MyTardisModelResource):
    schema = fields.ForeignKey(SchemaResource, 'schema')

    class Meta(MyTardisModelResource.Meta):
        queryset = ParameterName.objects.all()


class ParameterResource(MyTardisModelResource):
    name = fields.ForeignKey(ParameterNameResource, 'name')
    value = fields.CharField(blank=True)

    def hydrate(self, bundle):
        '''
        sets the parametername by uri or name
        if untyped value is given, set value via parameter method,
        otherwise use modelresource automatisms
        '''
        try:
            parname = ParameterNameResource.get_via_uri(
                ParameterNameResource(),
                bundle.data['name'], bundle.request)
        except NotFound:
            parname = bundle.related_obj._get_create_parname(
                bundle.data['name'])
        del(bundle.data['name'])
        bundle.obj.name = parname
        if 'value' in bundle.data:
            bundle.obj.set_value(bundle.data['value'])
            del(bundle.data['value'])
        return bundle


class ParameterSetResource(MyTardisModelResource):
    schema = fields.ForeignKey(SchemaResource, 'schema', full=True)

    def hydrate_schema(self, bundle):
        try:
            schema = SchemaResource.get_via_uri(SchemaResource(),
                                                bundle.data['schema'],
                                                bundle.request)
        except NotFound:
            try:
                schema = Schema.objects.get(namespace=bundle.data['schema'])
            except Schema.DoesNotExist:
                raise
        bundle.obj.schema = schema
        del(bundle.data['schema'])
        return bundle


class ExperimentParameterSetResource(ParameterSetResource):
    '''API for ExperimentParameterSets
    '''
    experiment = fields.ForeignKey(
        'tardis.tardis_portal.api.ExperimentResource', 'experiment')
    parameters = fields.ToManyField(
        'tardis.tardis_portal.api.ExperimentParameterResource',
        'experimentparameter_set',
        related_name='parameterset', full=True, null=True)

    def save_m2m(self, bundle):
        super(ExperimentParameterSetResource, self).save_m2m(bundle)

    class Meta(ParameterSetResource.Meta):
        queryset = ExperimentParameterSet.objects.all()


class ExperimentParameterResource(ParameterResource):
    parameterset = fields.ForeignKey(ExperimentParameterSetResource,
                                     'parameterset')

    class Meta(ParameterResource.Meta):
        queryset = ExperimentParameter.objects.all()


class ExperimentResource(MyTardisModelResource):
    '''API for Experiments
    also creates a default ACL and allows ExperimentParameterSets to be read
    and written.

    TODO: catch duplicate schema submissions for parameter sets
    '''
    created_by = fields.ForeignKey(UserResource, 'created_by')
    parameter_sets = fields.ToManyField(
        ExperimentParameterSetResource,
        'experimentparameterset_set',
        related_name='experiment',
        full=True, null=True)

    class Meta(MyTardisModelResource.Meta):
        queryset = Experiment.objects.all()
        filtering = {
            'id': ('exact', ),
            'title': ('exact',),
        }

    def dehydrate(self, bundle):
        exp = bundle.obj
        authors = [{'name': a.author, 'url': a.url}
                   for a in exp.author_experiment_set.all()]
        bundle.data['authors'] = authors
        lic = exp.license
        if lic is not None:
            bundle.data['license'] = {
                'name': lic.name,
                'url': lic.url,
                'description': lic.internal_description,
                'image_url': lic.image_url,
                'allows_distribution': lic.allows_distribution,
            }
        owners = exp.get_owners()
        bundle.data['owner_ids'] = [o.id for o in owners]
        return bundle

    def hydrate_m2m(self, bundle):
        '''
        create ACL before any related objects are created in order to use
        ACL permissions for those objects.
        '''
        if getattr(bundle.obj, 'id', False):
            experiment = bundle.obj
            # TODO: unify this with the view function's ACL creation,
            # maybe through an ACL toolbox.
            acl = ObjectACL(content_type=experiment.get_ct(),
                            object_id=experiment.id,
                            pluginId=django_user,
                            entityId=str(bundle.request.user.id),
                            canRead=True,
                            canWrite=True,
                            canDelete=True,
                            isOwner=True,
                            aclOwnershipType=ObjectACL.OWNER_OWNED)
            acl.save()

        return super(ExperimentResource, self).hydrate_m2m(bundle)

    def obj_create(self, bundle, **kwargs):
        '''experiments need at least one ACL to be available through the
        ExperimentManager (Experiment.safe)
        Currently not tested for failed db transactions as sqlite does not
        enforce limits.
        '''
        user = bundle.request.user
        bundle.data['created_by'] = user
        bundle = super(ExperimentResource, self).obj_create(bundle, **kwargs)
        return bundle

    def obj_get_list(self, bundle, **kwargs):
        '''
        responds to EPN query for Australian Synchrotron
        '''
        if hasattr(bundle.request, 'GET') and 'EPN' in bundle.request.GET:
            epn = bundle.request.GET['EPN']
            exp_schema = Schema.objects.get(
                namespace='http://www.tardis.edu.au'
                '/schemas/as/experiment/2010/09/21')
            epn_pn = ParameterName.objects.get(schema=exp_schema, name='EPN')
            parameter = ExperimentParameter.objects.get(name=epn_pn,
                                                        string_value=epn)
            experiment_id = parameter.parameterset.experiment.id
            experiment = Experiment.objects.filter(pk=experiment_id)
            if experiment[0] in Experiment.safe.all(bundle.request.user):
                return experiment

        return super(ExperimentResource, self).obj_get_list(bundle,
                                                            **kwargs)


class DatasetParameterSetResource(ParameterSetResource):
    dataset = fields.ForeignKey(
        'tardis.tardis_portal.api.DatasetResource', 'dataset')
    parameters = fields.ToManyField(
        'tardis.tardis_portal.api.DatasetParameterResource',
        'datasetparameter_set',
        related_name='parameterset', full=True, null=True)

    class Meta(ParameterSetResource.Meta):
        queryset = DatasetParameterSet.objects.all()


class DatasetParameterResource(ParameterResource):
    parameterset = fields.ForeignKey(DatasetParameterSetResource,
                                     'parameterset')

    class Meta(ParameterResource.Meta):
        queryset = DatasetParameter.objects.all()


class StorageBoxResource(MyTardisModelResource):
    class Meta(MyTardisModelResource.Meta):
        queryset = StorageBox.objects.all()


class DatasetResource(MyTardisModelResource):
    experiments = fields.ToManyField(
        ExperimentResource, 'experiments', related_name='datasets')
    experiment = fields.ForeignKey(ExperimentResource, 'experiment')
    parameter_sets = fields.ToManyField(
        DatasetParameterSetResource,
        'datasetparameterset_set',
        related_name='dataset',
        full=True, null=True)
    storage_boxes = fields.ToManyField(
        StorageBoxResource,
        'storage_boxes',
        related_name='datasets',
        null=True)

    class Meta(MyTardisModelResource.Meta):
        queryset = Dataset.objects.all()
        filtering = {
            'id': ('exact', ),
            'experiments': ALL_WITH_RELATIONS,
            'description': ('exact', ),
            'directory': ('exact', ),
        }

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/files/'
                r'(?:(?P<file_path>.+))?$' % self._meta.resource_name,
                self.wrap_view('get_datafiles'),
                name='api_get_datafiles_for_dataset'),
        ]

    def get_datafiles(self, request, **kwargs):
        file_path = kwargs.get('file_path', None)
        dataset_id = kwargs['pk']

        datafiles = DataFile.objects.filter(dataset__id=dataset_id)
        auth_bundle = self.build_bundle(request=request)
        auth_bundle.obj = DataFile()
        self.authorized_read_list(
            datafiles, auth_bundle
            )
        del kwargs['pk']
        del kwargs['file_path']
        kwargs['dataset__id'] = dataset_id
        if file_path is not None:
            kwargs['directory__startswith'] = file_path
        df_res = DataFileResource()
        return df_res.dispatch('list', request, **kwargs)

class S3Response(StreamingHttpResponse):
    """
    A streaming HTTP response class optimized for S3.
    """

    def close(self):
        for closable in self._closable_objects:
            try:
                closable.close(fast=True)
            except Exception:
                pass
        signals.request_finished.send(sender=self._handler_class)
        # The following is a heavy-handed way of ensuring S3 connections are freed.
        # We've seen dangling interrupted connections even after the above close().
        # Might be related to https://bugs.python.org/issue23865 .
        sys.exit(0)

class DataFileResource(MyTardisModelResource):
    dataset = fields.ForeignKey(DatasetResource, 'dataset')
    parameter_sets = fields.ToManyField(
        'tardis.tardis_portal.api.DatafileParameterSetResource',
        'datafileparameterset_set',
        related_name='datafile',
        full=True, null=True)
    datafile = fields.FileField()
    replicas = fields.ToManyField(
        'tardis.tardis_portal.api.ReplicaResource',
        'file_objects',
        related_name='datafile', full=True)
    temp_url = None

    class Meta(MyTardisModelResource.Meta):
        queryset = DataFile.objects.all()
        filtering = {
            'directory': ('exact', 'startswith'),
            'dataset': ALL_WITH_RELATIONS,
            'filename': ('exact', ),
        }
        resource_name = 'dataset_file'

    def download_file(self, request, **kwargs):
        '''
        curl needs the -J switch to get the filename right
        auth needs to be added manually here
        '''
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if not has_datafile_download_access(request=request, datafile_id=kwargs['pk']):
            return HttpResponseForbidden()

        file_record = self._meta.queryset.get(pk=kwargs['pk'])
        self.authorized_read_detail(
            [file_record],
            self.build_bundle(obj=file_record, request=request))
        file_object = file_record.get_file()
        response = S3Response(file_object.key, content_type=file_record.mimetype)
        response['Content-Length'] = file_record.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % \
                                          file_record.filename
        self.log_throttled_access(request)
        return response

    def hydrate(self, bundle):
        dataset = DatasetResource.get_via_uri(DatasetResource(),
                                              bundle.data['dataset'],
                                              bundle.request)
        if 'attached_file' in bundle.data:
            # have POSTed file
            newfile = bundle.data['attached_file'][0]

            if 'md5sum' not in bundle.data and 'sha512sum' not in bundle.data:
                from tardis.tardis_portal.util import generate_file_checksums
                md5, sha512, size, _ = generate_file_checksums(
                    newfile)
                bundle.data['md5sum'] = md5

            bundle.data['replicas'] = [{'file_object': newfile}]
            del(bundle.data['attached_file'])
        elif 'replicas' not in bundle.data:
            # no replica specified: return upload path and create dfo for
            # new path
            sbox = dataset.get_staging_storage_box()
            if sbox is None:
                raise NotImplementedError
            dfo = DataFileObject(
                datafile=bundle.obj,
                storage_box=sbox)
            self.temp_url = dfo.get_save_location()
        return bundle

    def post_list(self, request, **kwargs):
        response = super(DataFileResource, self).post_list(request,
                                                           **kwargs)
        if self.temp_url is not None:
            response.content = self.temp_url
            self.temp_url = None
        return response

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('download_file'), name="api_download_file"),
        ]

    def deserialize(self, request, data, format=None):
        '''
        from https://github.com/toastdriven/django-tastypie/issues/42
        modified to deserialize json sent via POST. Would fail if data is sent
        in a different format.
        uses a hack to get back pure json from request.POST
        '''
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            jsondata = request.POST['json_data']
            data = super(DataFileResource, self).deserialize(
                request, jsondata, format='application/json')
            data.update(request.FILES)
            return data
        return super(DataFileResource, self).deserialize(request,
                                                         data, format)

    def put_detail(self, request, **kwargs):
        '''
        from https://github.com/toastdriven/django-tastypie/issues/42
        '''
        if request.META.get('CONTENT_TYPE').startswith('multipart') and \
                not hasattr(request, '_body'):
            request._body = ''

        return super(DataFileResource, self).put_detail(request, **kwargs)


class DatafileParameterSetResource(ParameterSetResource):
    datafile = fields.ForeignKey(
        DataFileResource, 'datafile')
    parameters = fields.ToManyField(
        'tardis.tardis_portal.api.DatafileParameterResource',
        'datafileparameter_set',
        related_name='parameterset', full=True, null=True)

    class Meta(ParameterSetResource.Meta):
        queryset = DatafileParameterSet.objects.all()


class DatafileParameterResource(ParameterResource):
    parameterset = fields.ForeignKey(DatafileParameterSetResource,
                                     'parameterset')

    class Meta(ParameterResource.Meta):
        queryset = DatafileParameter.objects.all()


class LocationResource(MyTardisModelResource):
    class Meta(MyTardisModelResource.Meta):
        queryset = StorageBox.objects.all()


class ReplicaResource(MyTardisModelResource):
    datafile = fields.ForeignKey(DataFileResource, 'datafile')

    class Meta(MyTardisModelResource.Meta):
        queryset = DataFileObject.objects.all()
        filtering = {
            'verified': ('exact',),
            'url': ('exact', 'startswith'),
        }

    def hydrate(self, bundle):
        if 'url' in bundle.data:
            bundle.data['uri'] = bundle.data['url']
            del(bundle.data['url'])
        datafile = bundle.related_obj
        bundle.obj.datafile = datafile
        bundle.data['datafile'] = datafile
        if 'location' in bundle.data:
            try:
                bundle.obj.storage_box = StorageBox.objects.get(
                    name=bundle.data['location'])
            except StorageBox.DoesNotExist:
                bundle.obj.storage_box = datafile\
                          .dataset.get_default_storage_box()
            del(bundle.data['location'])
        else:
            bundle.obj.storage_box = datafile\
                      .dataset.get_default_storage_box()

        bundle.obj.save()
        if 'file_object' in bundle.data:
            bundle.obj.file_object = bundle.data['file_object']
            bundle.data['file_object'].close()
            del(bundle.data['file_object'])
        return bundle

class AuthorExperimentResource(MyTardisModelResource):
    experiment = fields.ForeignKey(ExperimentResource, 'experiment')

    class Meta(MyTardisModelResource.Meta):
        queryset = Author_Experiment.objects.all()

class OrganismResource(MyTardisModelResource):
    class Meta(MyTardisModelResource.Meta):
        queryset = Organism.objects.all()

class SourceResource(MyTardisModelResource):
    organism = fields.ForeignKey(OrganismResource, 'organism')

    class Meta(MyTardisModelResource.Meta):
        queryset = Source.objects.all()

class SampleResource(MyTardisModelResource):
    source = fields.ForeignKey(SourceResource, 'source')
    organism = fields.ForeignKey(OrganismResource, 'organism')

    class Meta(MyTardisModelResource.Meta):
        queryset = Sample.objects.all()

class ExtractResource(MyTardisModelResource):
    sample = fields.ForeignKey(SampleResource, 'sample')

    class Meta(MyTardisModelResource.Meta):
        queryset = Extract.objects.all()

class LibraryResource(MyTardisModelResource):
    extract = fields.ForeignKey(ExtractResource, 'extract')

    class Meta(MyTardisModelResource.Meta):
        queryset = Library.objects.all()

class SequenceResource(MyTardisModelResource):
    library = fields.OneToOneField(LibraryResource, 'library')

    class Meta(MyTardisModelResource.Meta):
        queryset = Sequence.objects.all()

class AnalysisResource(MyTardisModelResource):
    dataset = fields.ForeignKey(DatasetResource, 'dataset')

    class Meta(MyTardisModelResource.Meta):
        queryset = Analysis.objects.all()

class ProcessingResource(MyTardisModelResource):
    sequence = fields.OneToOneField(SequenceResource, 'sequence')
    analysis = fields.ForeignKey(AnalysisResource, 'analysis')

    class Meta(MyTardisModelResource.Meta):
        queryset = Processing.objects.all()
