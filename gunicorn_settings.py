import os

workers = 16
worker_class = "sync"
timeout = 24 * 60 * 60
chdir = os.path.dirname(__file__)
proc_name = "mytardis_gunicorn"
