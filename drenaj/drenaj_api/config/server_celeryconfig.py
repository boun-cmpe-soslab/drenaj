__author__ = 'onur'

from kombu import Queue

from drenaj_api.config.config import BROKER_HOSTNAME

CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1

BROKER_URL = 'amqp://guest:guest@%s' % BROKER_HOSTNAME

CELERY_DEFAULT_QUEUE = 'control'

CELERY_DEFAULT_EXCHANGE = 'campaigns'

CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'

CELERY_QUEUES = (
    #Queue('timelines', routing_key='*.timeline.*'),
    #Queue('streamings', routing_key='*.streaming.*'),
    Queue('control', routing_key='control'),
    Queue('offline_jobs', routing_key='offline_jobs'),
)

# from datetime import timedelta
#
# CELERYBEAT_SCHEDULE = {
#     'dispatch_timeline_harvester_tasks_every_three_minutes': {
#         'task': 'check_watchlist_and_dispatch_tasks',
#         'schedule': timedelta(seconds=60*3),
#     },
# }

from celery.beat import crontab

CELERYBEAT_SCHEDULE = {
    'dispatch_timeline_harvester_tasks_every_five_minutes': {
        'task': 'check_watchlist_and_dispatch_tasks',
        'schedule': crontab('*/5'),
    },
}