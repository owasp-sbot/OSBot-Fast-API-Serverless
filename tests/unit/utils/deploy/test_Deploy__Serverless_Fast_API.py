import requests
from unittest                                                                     import TestCase
from osbot_utils.utils.Env                                                        import get_env
from osbot_fast_api.api.Fast_API                                                  import ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, ENV_VAR__FAST_API__AUTH__API_KEY__NAME
from osbot_aws.deploy.Deploy_Lambda                                               import Deploy_Lambda
from osbot_utils.utils.Objects                                                    import __
from osbot_fast_api_serverless.utils.Version                                      import version__osbot_fast_api_serverless
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API                import Deploy__Serverless__Fast_API
from osbot_fast_api_serverless.deploy.Schema__AWS_Setup__Serverless__Fast_API     import Schema__AWS_Setup__Serverless__Fast_API
from osbot_fast_api_serverless.utils.testing.skip_tests                           import skip__if_not__in_github_actions
from tests.serverless_fast_api__objs_for_tests                                    import Serverless__Fast_API__TEST__AWS_ACCOUNT_ID, \
    Serverless__Fast_API__TEST__AWS_DEFAULT_REGION, setup_local_stack


class test_Deploy__Serverless_Fast_API(TestCase):
    @classmethod
    def setUpClass(cls):
        #skip__if_not__in_github_actions()
        setup_local_stack()                                                 # deploy lambda to localstack
        cls.deploy_serverless_fast_api = Deploy__Serverless__Fast_API()

    def test_deploy_lambda(self):
        with self.deploy_serverless_fast_api.deploy_lambda() as _:
            assert type(_) is Deploy_Lambda
            assert _.lambda_name()     == 'serverless_fast_api__dev'
            assert _.package.s3_bucket == '000000000000--osbot-lambdas--us-east-1'
            assert _.package.s3_bucket == f'{Serverless__Fast_API__TEST__AWS_ACCOUNT_ID}--osbot-lambdas--{Serverless__Fast_API__TEST__AWS_DEFAULT_REGION}'

    # tests for main methods

    def test_1__setup_aws_environment(self):
        with self.deploy_serverless_fast_api.setup_aws_environment() as _:
            assert type(_) is Schema__AWS_Setup__Serverless__Fast_API
            assert _.obj() == __(bucket__osbot_lambdas__exists = True                                    ,
                                 bucket__osbot_lambdas__name   = '000000000000--osbot-lambdas--us-east-1',
                                 current_aws_region            = 'us-east-1'                             )

    def test_2_upload_lambda_dependencies_to_s3(self):
        with self.deploy_serverless_fast_api as _:
            status__packages = _.upload_lambda_dependencies_to_s3()
            for package_name, status__package in status__packages.items():
                assert package_name                                   in ['mangum', 'osbot-fast-api']
                assert status__package.get('result__install_locally') is True
                assert status__package.get('result__upload_to_s3'   ) is True

    def test_3__create_or_update__lambda_function(self):
        with self.deploy_serverless_fast_api as _:
            #assert _.lambda_function().exists() is False
            assert _.deploy_lambda().lambda_name()       == 'serverless_fast_api__dev'
            assert _.deploy_lambda().package.lambda_name == 'serverless_fast_api__dev'
            assert _.create_or_update__lambda_function() is True

            assert _.lambda_function().exists() is True
            assert _.lambda_function().invoke().get('errorMessage') == ('The adapter was unable to infer a handler to use for the '
                                                                        'event. This is likely related to how the Lambda function '
                                                                        'was invoked. (Are you testing locally? Make sure the '
                                                                        'request payload is valid for a supported handler.)')

            lambda_configuration = _.lambda_function().info().get('Configuration')
            assert lambda_configuration.get('Architectures'   )                  == ['x86_64']
            assert lambda_configuration.get('Environment'     ).get('Variables') == {'FAST_API__AUTH__API_KEY__NAME' : get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME ),
                                                                                     'FAST_API__AUTH__API_KEY__VALUE': get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)}
            assert lambda_configuration.get('EphemeralStorage').get('Size') == 512
            assert lambda_configuration.get('FunctionName'    )             == 'serverless_fast_api__dev'
            assert lambda_configuration.get('MemorySize'      )             == 512

    def test_4__create__lambda_function__url(self):
        with self.deploy_serverless_fast_api as _:
            function_url = _.create__lambda_function__url()
            info_version_url = function_url + 'info/version'
            assert function_url.endswith('us-east-1.localhost.localstack.cloud:4566/')
            response__no_auth = requests.get(info_version_url)
            assert response__no_auth.status_code == 401
            assert response__no_auth.json()      == { 'data'   : None,
                                                      'error'  : None,
                                                      'message': 'Client API key is missing, you need to set it on a header or cookie',
                                                      'status' : 'error'}

            headers             = {_.api_key__name(): _.api_key__value()}
            response__with_auth = requests.get(info_version_url, headers=headers)
            assert response__with_auth.status_code  == 200
            assert response__with_auth.json()       == {'version': version__osbot_fast_api_serverless}

            #pprint(requests.get(function_url+ 'openapi.json', headers=headers).json())

    def test_5_check_deployment_files(self):
        with self.deploy_serverless_fast_api as _:
            with _.s3() as _:
                dependencies_zips = _.folder_files('000000000000--osbot-lambdas--us-east-1', 'lambdas-dependencies')
                assert dependencies_zips == ['mangum.zip', 'osbot-fast-api.zip']

    def test_6_delete_lamda_function(self):
        with self.deploy_serverless_fast_api as _:
            assert _.lambda_function().delete() is True
            assert _.lambda_function().exists() is False
