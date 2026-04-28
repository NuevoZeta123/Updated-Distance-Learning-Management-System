# gunicorn.conf.py — Tuned for DLMS on a 1-2 vCPU VPS

import multiprocessing

# Workers: (2 x CPU cores) + 1 is the standard formula
workers     = (multiprocessing.cpu_count() * 2) + 1
worker_class = 'sync'          # Use 'gevent' if you add async support
threads     = 2
timeout     = 120              # Seconds before killing unresponsive worker
keepalive   = 5

# Binding
bind        = '127.0.0.1:8000' # Nginx proxies to this; never expose direct

# Logging
accesslog   = '/var/log/dlms/gunicorn-access.log'
errorlog    = '/var/log/dlms/gunicorn-error.log'
loglevel    = 'warning'        # 'info' for debugging

# Process naming
proc_name   = 'dlms_gunicorn'

# Graceful reload on SIGHUP
reload      = False            # Set True only during active development

# Max requests before worker restart (prevents memory leaks)
max_requests        = 1000
max_requests_jitter = 100
