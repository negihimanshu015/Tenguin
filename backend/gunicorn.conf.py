import multiprocessing
import os

# Binding
bind = "0.0.0.0:8000"

# Worker process configuration
# Formula: (2 x $num_cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 4

# Timeout configuration
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-" 
loglevel = "info"

# Security & Process Management
max_requests = 1000
max_requests_jitter = 50
worker_tmp_dir = "/dev/shm"
preload_app = True

# Signal handling for Docker
forwarded_allow_ips = "*"
proxy_protocol = True
