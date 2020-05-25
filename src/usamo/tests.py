import shutil
import tempfile

from django.db import OperationalError, connections
from django.test.runner import DiscoverRunner

from usamo.settings import settings


class TempMediaRunner(DiscoverRunner):

    def setup_test_environment(self, **kwargs):
        super(TempMediaRunner, self).setup_test_environment(**kwargs)
        self.backup = {}
        settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
        self.backup['MEDIA_ROOT'] = settings.MEDIA_ROOT
        self.temp_media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.temp_media_root

    def teardown_databases(self, old_config, **kwargs):
        def close_sessions(conn):
            close_sessions_query = """
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE
                    datname = current_database() AND
                    pid <> pg_backend_pid();
            """
            with conn.cursor() as cursor:
                try:
                    cursor.execute(close_sessions_query)
                except OperationalError:
                    pass

        for alias in connections:
            connections[alias].close()
            close_sessions(connections[alias])
        super().teardown_databases(old_config, **kwargs)

    def teardown_test_environment(self, **kwargs):
        super(TempMediaRunner, self).teardown_test_environment(**kwargs)
        shutil.rmtree(settings.MEDIA_ROOT)
        for name, value in self.backup.items():
            setattr(settings, name, value)
        del settings.DEFAULT_FILE_STORAGE

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        try:
            test_results = super(TempMediaRunner, self).run_tests(test_labels, extra_tests, **kwargs)
        finally:
            shutil.rmtree(settings.MEDIA_ROOT)
