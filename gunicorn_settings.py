import multiprocessing
import os

workers = max(16, multiprocessing.cpu_count() * 8)
worker_class = "sync"
timeout = 24 * 60 * 60
chdir = os.path.dirname(__file__)
proc_name = "mytardis_gunicorn"
