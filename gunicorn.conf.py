"""Gunicorn configuration file."""

import multiprocessing

# Binding
bind = "0.0.0.0:8000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2
worker_tmp_dir = "/dev/shm"

# Timeout
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Max requests (restart workers after N requests to prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50
