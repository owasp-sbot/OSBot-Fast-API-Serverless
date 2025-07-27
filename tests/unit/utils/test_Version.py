import osbot_fast_api_serverless
from unittest                                 import TestCase
from osbot_utils.utils.Files                  import parent_folder, file_name
from osbot_fast_api_serverless.utils.Version  import Version, version__osbot_fast_api_serverless


class test_Version(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.version = Version()

    def test_path_code_root(self):
        assert self.version.path_code_root() == osbot_fast_api_serverless.path

    def test_path_version_file(self):
        with self.version as _:
            assert parent_folder(_.path_version_file()) == osbot_fast_api_serverless.path
            assert file_name    (_.path_version_file()) == 'version'

    def test_value(self):
        assert self.version.value() == version__osbot_fast_api_serverless