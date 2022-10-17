import json

from celery.backends.redis import RedisBackend as BackendBase
from celery.exceptions import BackendStoreError


class RedisBackend(BackendBase):
    def set(self, key, value, **retry_policy):
        res = json.loads(value)
        del res['kwargs']
        del res['args']
        value = json.dumps(res)
        if isinstance(value, str) and len(value) > self._MAX_STR_VALUE_SIZE:
            raise BackendStoreError('value too large for Redis backend')
        return self.ensure(self._set, (key, value), **retry_policy)
