import pytest
from unittest                                                      import TestCase
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API import Deploy__Serverless__Fast_API


class test_deploy_lambda__to_aws(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.deploy_fast_api =  Deploy__Serverless__Fast_API()
        with cls.deploy_fast_api as _:
            if _.aws_config.aws_configured() is False:
                pytest.skip("this test needs valid AWS credentials")

    def test__init__(self):
        with self.deploy_fast_api as _:
            assert type(_) is Deploy__Serverless__Fast_API