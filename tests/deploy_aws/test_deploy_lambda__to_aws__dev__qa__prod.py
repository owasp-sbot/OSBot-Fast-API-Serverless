import pytest
from unittest                                                       import TestCase
from osbot_fast_api_serverless.utils.Version                        import version__osbot_fast_api_serverless
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API  import Deploy__Serverless__Fast_API, DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK


class test_deploy_lambda__to_aws__dev__qa__prod(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deploy_fast_api__dev  = Deploy__Serverless__Fast_API(stage = 'dev')
        cls.deploy_fast_api__qa   = Deploy__Serverless__Fast_API(stage = 'qa')
        cls.deploy_fast_api__prod = Deploy__Serverless__Fast_API(stage = 'prod')

        with cls.deploy_fast_api__dev as _:
            if _.aws_config.aws_configured() is False:
                pytest.skip("this test needs valid AWS credentials")

    def test_1__check_stages(self):
        assert self.deploy_fast_api__dev .stage == 'dev'
        assert self.deploy_fast_api__qa  .stage == 'qa'
        assert self.deploy_fast_api__prod.stage == 'prod'

    def test_2__create(self):
        assert self.deploy_fast_api__dev .create() is True
        assert self.deploy_fast_api__qa  .create() is True
        assert self.deploy_fast_api__prod.create() is True

    def test_3__invoke(self):
        assert self.deploy_fast_api__dev .invoke().get('errorMessage') == DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK
        assert self.deploy_fast_api__qa  .invoke().get('errorMessage') == DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK
        assert self.deploy_fast_api__prod.invoke().get('errorMessage') == DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK

    def test_3__invoke__function_url(self):
        version = {'version': version__osbot_fast_api_serverless}
        assert self.deploy_fast_api__dev .invoke__function_url('/info/version') == version
        assert self.deploy_fast_api__qa  .invoke__function_url('/info/version') == version
        assert self.deploy_fast_api__prod.invoke__function_url('/info/version') == version

    def test_4__delete(self):
        assert self.deploy_fast_api__dev .delete() is True
        assert self.deploy_fast_api__qa  .delete() is True
        assert self.deploy_fast_api__prod.delete() is True