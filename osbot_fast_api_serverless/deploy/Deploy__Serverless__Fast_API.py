from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency                     import Lambda__Dependency
from osbot_utils.helpers.Random_Guid                                           import Random_Guid
from osbot_utils.utils.Env                                                     import get_env
from osbot_fast_api.api.Fast_API                                               import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_aws.AWS_Config                                                      import AWS_Config
from osbot_aws.deploy.Deploy_Lambda                                            import Deploy_Lambda
from osbot_utils.decorators.methods.cache_on_self                              import cache_on_self
from osbot_utils.helpers.Safe_Id                                               import Safe_Id
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_fast_api_serverless.fast_api.lambda_handler                         import run, LAMBDA_DEPENDENCIES
from osbot_fast_api_serverless.deploy.Schema__AWS_Setup__Serverless__Fast_API  import Schema__AWS_Setup__Serverless__Fast_API

BASE__LAMBDA_NAME  = 'serverless_fast_api'        # make this a Safe_Str__Lambda_Name



class Deploy__Serverless__Fast_API(Type_Safe):
    stage    : Safe_Id = Safe_Id('dev')

    @cache_on_self
    def aws_config(self):
        return AWS_Config()

    @cache_on_self
    def api_key__name(self):
        return get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME, "api_key__name")

    @cache_on_self
    def api_key__value (self):
        return get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, Random_Guid())

    @cache_on_self
    def s3(self):
        return self.lambda_function().s3()

    @cache_on_self
    def deploy_lambda(self):
        with Deploy_Lambda(run, lambda_name=self.lambda_name()) as _:
            _.add_osbot_aws()
            _.set_env_variable(ENV_VAR__FAST_API__AUTH__API_KEY__NAME , self.api_key__name ())
            _.set_env_variable(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, self.api_key__value())
            return _

    # main methods


    def create_or_update__lambda_function(self):
        with self.deploy_lambda() as _:
            result = _.update()
            if result == "Successful":
                return True
            if result == 'Pending':
                result = self.lambda_function().wait_for_function_update_to_complete(wait_time=0.5)                # todo: see if there a is a better to proactively handle the first install (I think the delay that happens on first install is caused by the download of the docker image for running the lambda inside localstack)
                if result == "Successful":
                    return True
            raise Exception(f"Lambda update failed: {result}")

    def create__lambda_function__url(self):
        with self.lambda_function() as _:
            if _.function_url_exists():
                function_url = _.function_url()
            else:
                result = _.function_url_create_with_public_access()
                function_url = result.get('function_url_create').get('FunctionUrl')
            return function_url

    def lambda_name(self):
        return f'{BASE__LAMBDA_NAME}__{self.stage}'

    def lambda_function(self):
        return self.deploy_lambda().lambda_function()

    def lambda_files_bucket_name(self):
        return self.lambda_function().s3_bucket

    def setup_aws_environment(self):

        kwargs = dict(bucket__osbot_lambdas__exists = self.s3().bucket_exists(self.lambda_files_bucket_name()),
                      bucket__osbot_lambdas__name   = self.lambda_files_bucket_name(),
                      current_aws_region            = self.aws_config().region_name())

        aws_setup = Schema__AWS_Setup__Serverless__Fast_API(**kwargs)
        with aws_setup as _:
            if _.bucket__osbot_lambdas__exists is False:
                result = self.s3().bucket_create(_.bucket__osbot_lambdas__name, _.current_aws_region)
                if result.get('status') == 'ok':
                    _.bucket__osbot_lambdas__exists = True
                else:
                    raise Exception(result)
        return aws_setup


    def upload_lambda_dependencies_to_s3(self):
        upload_results = {}
        for package_name in LAMBDA_DEPENDENCIES:
            with Lambda__Dependency(package_name=package_name) as _:
                upload_results[package_name] = _.install_and_upload()
        return upload_results

        # with Lambda__Upload_Package() as _:
        #     return _.upload_lambda_dependencies(LAMBDA_DEPENDENCIES)
        #     status__packages = {}
            # for package in LAMBDA_DEPENDENCIES:
            #     if
            #     with capture_duration()  as duration__install_locally:
            #         result__install_locally = lambda_upload_package.install_locally(package)
            #     with capture_duration() as duration__upload_to_s3:
            #         result__upload_to_s3    = lambda_upload_package.upload_to_s3(package)
            #
            #     status__package = dict(duration__install_locally = duration__install_locally.seconds,
            #                            duration__upload_to_s3    = duration__upload_to_s3   .seconds,
            #                            result__install_locally   = result__install_locally  ,
            #                            result__upload_to_s3      = result__upload_to_s3     )
            #     status__packages[package] = status__package
            # return status__packages


