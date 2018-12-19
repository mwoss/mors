from django.contrib.auth.models import UserManager
from django.db import connections as pymongo_connections


class MongoUserManager(UserManager):
    def __getattr__(self, name):
        if name.startswith('mongo'):
            name = name[6:]
            return getattr(self._client, name)
        else:
            return super().__getattr__(name)

    @property
    def _client(self):
        return (
            pymongo_connections[self.db]
                .cursor()
                .db_conn[self.model._meta.db_table]
        )
