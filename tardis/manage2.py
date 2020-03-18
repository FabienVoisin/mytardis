#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

sys.path[0:0] = [
  '/data/mytardis/mytardis/eggs/nose-1.3.6-py2.7.egg',
  '/data/mytardis/mytardis/eggs/coverage-3.6-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/django_nose-1.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/nosexcover-1.0.10-py2.7.egg',
  '/data/mytardis/mytardis',
  '/data/mytardis/mytardis/eggs/setuptools-16.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/bpython-0.14.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/python_ldap-2.4.19-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/python_memcached-1.54-py2.7.egg',
  '/data/mytardis/mytardis/eggs/docutils-0.12-py2.7.egg',
  '/data/mytardis/mytardis/eggs/flexmock-0.9.7-py2.7.egg',
  '/data/mytardis/mytardis/eggs/compare-0.2b0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_jasmine-0.4.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_smartagent-0.1.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/html2text-2015.4.14-py2.7.egg',
  '/data/mytardis/mytardis/eggs/poster-0.8.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/requests-2.7.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pygraphviz-1.2-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/gunicorn-19.3.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/gevent-1.0.2-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/greenlet-0.4.7-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/Django-1.5.5-py2.7.egg',
  '/data/mytardis/mytardis/eggs/six-1.9.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/curtsies-0.1.19-py2.7.egg',
  '/data/mytardis/mytardis/eggs/Pygments-2.0.2-py2.7.egg',
  '/data/mytardis/mytardis/eggs/elasticstack-0.1.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/geopy-1.10.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pwgen-0.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/paramiko-1.15.2-py2.7.egg',
  '/data/mytardis/mytardis/eggs/bleach-1.4.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_tastypie-0.9.16_tzfix-py2.7.egg',
  '/data/mytardis/mytardis/eggs/PyYAML-3.10-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/ua_parser-0.3.3-py2.7.egg',
  '/data/mytardis/mytardis/eggs/user_agents-0.1.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_user_agents-0.2.2-py2.7.egg',
  '/data/mytardis/mytardis/eggs/rdfextras-0.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/rdflib-4.0.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pystache-0.5.3-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_mustachejs-0.6.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/Wand-0.3.2-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pyoai-2.4.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/iso8601-0.1.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pytz-2013b-py2.7.egg',
  '/data/mytardis/mytardis/eggs/python_magic-0.4.6-py2.7.egg',
  '/data/mytardis/mytardis/eggs/httplib2-0.8-py2.7.egg',
  '/data/mytardis/mytardis/eggs/South-0.8.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/beautifulsoup4-4.2.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/elasticsearch-1.3.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_celery-3.1.16-py2.7.egg',
  '/data/mytardis/mytardis/eggs/celery-3.1.18-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_bootstrap_form-2.0.6-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_haystack-2.3.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_form_utils-0.2.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_extensions-1.1.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/django_registration-1.0-py2.7.egg',
  '/data/mytardis/mytardis/eggs/elementtree-1.2.6.post20050316-py2.7.egg',
  '/data/mytardis/mytardis/eggs/feedparser-5.1.3-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pyparsing-1.5.7-py2.7.egg',
  '/data/mytardis/mytardis/eggs/lxml-3.2.1-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/blessings-1.6-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pyelasticsearch-1.2.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/ecdsa-0.13-py2.7.egg',
  '/data/mytardis/mytardis/eggs/pycrypto-2.6.1-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/html5lib-0.99999-py2.7.egg',
  '/data/mytardis/mytardis/eggs/python_dateutil-2.4.2-py2.7.egg',
  '/data/mytardis/mytardis/eggs/mimeparse-0.1.3-py2.7.egg',
  '/data/mytardis/mytardis/eggs/SPARQLWrapper-1.6.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/isodate-0.5.1-py2.7.egg',
  '/data/mytardis/mytardis/eggs/urllib3-1.10.4-py2.7.egg',
  '/data/mytardis/mytardis/eggs/kombu-3.0.26-py2.7.egg',
  '/data/mytardis/mytardis/eggs/billiard-3.3.0.20-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/simplejson-3.7.2-py2.7-linux-x86_64.egg',
  '/data/mytardis/mytardis/eggs/amqp-1.4.6-py2.7.egg',
  '/data/mytardis/mytardis/eggs/anyjson-0.3.3-py2.7.egg',
  ]

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tardis.test_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)