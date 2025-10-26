import requests
from unittest                                                                       import TestCase
from osbot_aws.aws.lambda_.schemas.Schema__Lambda__Dependency__Local_Install__Data  import Schema__Lambda__Dependency__Local_Install__Data
from osbot_utils.utils.Misc                                                         import list_set
from osbot_utils.utils.Env                                                          import get_env
from osbot_fast_api.api.Fast_API                                                    import ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, ENV_VAR__FAST_API__AUTH__API_KEY__NAME
from osbot_aws.deploy.Deploy_Lambda                                                 import Deploy_Lambda
from osbot_utils.testing.__                                                         import __
from osbot_fast_api_serverless.fast_api.lambda_handler                              import LAMBDA_DEPENDENCIES
from osbot_fast_api_serverless.utils.Version                                        import version__osbot_fast_api_serverless
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API                  import Deploy__Serverless__Fast_API, BASE__LAMBDA_NAME__FAST_API__SERVERLESS
from osbot_fast_api_serverless.deploy.Schema__AWS_Setup__Serverless__Fast_API       import Schema__AWS_Setup__Serverless__Fast_API
from osbot_fast_api_serverless.utils.testing.skip_tests                             import skip__if_not__in_github_actions
from tests.serverless_fast_api__objs_for_tests                                      import Serverless__Fast_API__TEST__AWS_ACCOUNT_ID, Serverless__Fast_API__TEST__AWS_DEFAULT_REGION, setup_local_stack


class test_Deploy__Serverless_Fast_API(TestCase):
    @classmethod
    def setUpClass(cls):
        #skip__if_not__in_github_actions()
        setup_local_stack()                                                 # deploy lambda to localstack
        cls.ephemeral_storage = 1048
        cls.memory_size       = 1024
        cls.deploy_serverless_fast_api = Deploy__Serverless__Fast_API(ephemeral_storage=cls.ephemeral_storage, memory_size=cls.memory_size)

    def test_deploy_lambda(self):
        with self.deploy_serverless_fast_api.deploy_lambda() as _:
            assert type(_) is Deploy_Lambda
            assert _.lambda_name()     == 'fast-api__serverless__dev'
            assert _.lambda_name()     == f'{BASE__LAMBDA_NAME__FAST_API__SERVERLESS}__{_.stage}'
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

            assert type(status__packages)     is dict
            assert list_set(status__packages) == sorted(LAMBDA_DEPENDENCIES)

            for package_name, status__package in status__packages.items():
                local_result = status__package['local_result']

                assert package_name                      in LAMBDA_DEPENDENCIES
                assert list_set(status__package)         == ['local_result', 's3_exists']
                assert status__package['s3_exists']      is True
                assert type(local_result)                is Schema__Lambda__Dependency__Local_Install__Data
                assert len(local_result.installed_files)  > 20
                #local_result.print_obj()



    def test_3__create_or_update__lambda_function(self):
        with self.deploy_serverless_fast_api as _:
            _.lambda_function().delete()

            #assert _.lambda_function().exists() is False
            assert _.deploy_lambda().lambda_name()       == 'fast-api__serverless__dev'
            assert _.deploy_lambda().package.lambda_name == 'fast-api__serverless__dev'
            assert _.create_or_update__lambda_function() is True

            assert _.lambda_function().exists() is True
            assert '/osbot_aws/aws/lambda_/boto3__lambda.py'       in _.deploy_lambda().files() # make sure the deployment helper file is there (to load dependencies without needing the full osbot-aws)

            assert _.lambda_function().invoke().get('errorMessage') == ('The adapter was unable to infer a handler to use for the '
                                                                        'event. This is likely related to how the Lambda function '
                                                                        'was invoked. (Are you testing locally? Make sure the '
                                                                        'request payload is valid for a supported handler.)')

            lambda_configuration = _.lambda_function().info().get('Configuration')

            assert lambda_configuration.get('Architectures'   )                  == ['x86_64']
            assert lambda_configuration.get('Environment'     ).get('Variables') == { ENV_VAR__FAST_API__AUTH__API_KEY__NAME : get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME ),
                                                                                      ENV_VAR__FAST_API__AUTH__API_KEY__VALUE: get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)}
            assert lambda_configuration.get('EphemeralStorage').get('Size') == self.ephemeral_storage
            assert lambda_configuration.get('FunctionName'    )             == 'fast-api__serverless__dev'
            assert lambda_configuration.get('MemorySize'      )             == self.memory_size
            assert lambda_configuration.get('CodeSize'        )             < 20000 # code size should be small (and not 500k when it included the full osbot-aws)




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
                for package_name in LAMBDA_DEPENDENCIES:
                    assert f"{package_name}.zip" in dependencies_zips

    def test_6_delete_lamda_function(self):
        with self.deploy_serverless_fast_api as _:
            assert _.lambda_function().delete() is True
            assert _.lambda_function().exists() is False
