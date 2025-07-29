import pytest
from unittest                                                      import TestCase
from osbot_fast_api.api.Fast_API                                   import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_utils.utils.Env                                         import get_env
from osbot_utils.utils.Objects                                     import __
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API import Deploy__Serverless__Fast_API


class test_deploy_lambda__to_aws(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.deploy_fast_api =  Deploy__Serverless__Fast_API()
        cls.aws_config      = cls.deploy_fast_api.aws_config
        cls.account_id      = cls.aws_config.account_id()
        cls.region_name     = cls.aws_config.region_name()
        with cls.deploy_fast_api as _:
            if _.aws_config.aws_configured() is False:
                pytest.skip("this test needs valid AWS credentials")
            assert cls.deploy_fast_api.s3().client().meta.endpoint_url == f'https://s3.{cls.aws_config.region_name()}.amazonaws.com'

    def test___init__(self):
        with self.deploy_fast_api as _:
            assert type(_) is Deploy__Serverless__Fast_API

    def test_1__upload_lambda_dependencies_to_s3(self):
        with self.deploy_fast_api as _:
            _.upload_lambda_dependencies_to_s3()
            bucket = _.lambda_files_bucket_name()
            assert 'lambdas-dependencies/osbot-fast-api.zip' in _.s3().find_files(bucket, 'lambdas-dependencies')

    def test_2__create_or_update__lambda_function(self):
        with self.deploy_fast_api as _:
            assert _.create_or_update__lambda_function() is True
            assert _.create__lambda_function__url     ().endswith('.lambda-url.eu-west-1.on.aws/')
            assert _.lambda_function().exists         () is True



    def test_3__lambda_configuration(self):
        with self.deploy_fast_api.lambda_configuration() as _:
            assert _.Architectures          == ['x86_64']
            assert _.Handler                == 'osbot_fast_api_serverless.fast_api.lambda_handler.run'
            assert _.CodeSize               < 10000
            assert _.Environment.Variables  == __(FAST_API__AUTH__API_KEY__NAME  = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME ),
                                                 FAST_API__AUTH__API_KEY__VALUE = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE))
            assert _.EphemeralStorage       == __(Size=512)
            assert _.FunctionName           == 'fast-api__serverless__dev'
            assert _.FunctionArn            == f'arn:aws:lambda:{self.region_name}:{self.account_id}:function:fast-api__serverless__dev'
            assert _.LastUpdateStatus       == 'Successful'
            assert _.LoggingConfig          ==__(LogFormat = 'Text'                                 ,
                                                 LogGroup  = '/aws/lambda/fast-api__serverless__dev')

            assert _.MemorySize             == 512
            assert _.Role                   == f'arn:aws:iam::{self.account_id}:role/temp_role_for_lambda_invocation'
            assert _.Runtime                == 'python3.11'
            assert _.State                  == 'Active'
            assert _.Timeout                == 60

    def test_4__delete_function(self):
        with self.deploy_fast_api as _:
            assert _.delete_function() is True