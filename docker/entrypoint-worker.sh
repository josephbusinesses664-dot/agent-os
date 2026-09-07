#!/bin/sh
# Worker: consume the task queue and execute tasks.
set -e
cd /app
exec python -m agentos.worker