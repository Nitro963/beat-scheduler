#!/bin/bash
exec celery -A $CELERY_APP worker -l $LOG_LEVEL -P $POOL -n "${WORKER_NAME}@%h" -Q $WORKERS_QUEUES -E