import unittest
from contextlib import contextmanager

from django.db import connection
from django.db.backends.postgresql.creation import DatabaseCreation
from django.test import SimpleTestCase


@unittest.skipUnless(connection.vendor == 'postgresql', "PostgreSQL-specific tests")
class PostgreSQLDatabaseCreationTests(SimpleTestCase):

    @contextmanager
    def changed_test_settings(self, **kwargs):
        settings = connection.settings_dict['TEST']
        saved_values = {}
        for name in kwargs:
            if name in settings:
                saved_values[name] = settings[name]

        for name, value in kwargs.items():
            settings[name] = value
        try:
            yield
        finally:
            for name, value in kwargs.items():
                if name in saved_values:
                    settings[name] = saved_values[name]
                else:
                    del settings[name]

    def check_sql_table_creation_suffix(self, settings, expected):
        with self.changed_test_settings(**settings):
            creation = DatabaseCreation(connection)
            suffix = creation.sql_table_creation_suffix()
            self.assertEqual(suffix, expected)

    def test_sql_table_creation_suffix_with_none_settings(self):
        settings = dict(CHARSET=None, TEMPLATE=None)
        self.check_sql_table_creation_suffix(settings, "")

    def test_sql_table_creation_suffix_with_encoding(self):
        settings = dict(CHARSET='UTF8')
        self.check_sql_table_creation_suffix(settings, "WITH ENCODING 'UTF8'")

    def test_sql_table_creation_suffix_with_template(self):
        settings = dict(TEMPLATE='template0')
        self.check_sql_table_creation_suffix(settings, 'WITH TEMPLATE "template0"')

    def test_sql_table_creation_suffix_with_encoding_and_template(self):
        settings = dict(CHARSET='UTF8', TEMPLATE='template0')
        self.check_sql_table_creation_suffix(settings, '''WITH ENCODING 'UTF8' TEMPLATE "template0"''')
