from fastapi                                                 import FastAPI
from osbot_utils.utils.Env                                   import set_env
from osbot_aws.testing.Temp__Random__AWS_Credentials         import Temp_AWS_Credentials
from osbot_local_stack.local_stack.Local_Stack               import Local_Stack
from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from starlette.testclient                                    import TestClient
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API import Serverless__Fast_API

Serverless__Fast_API__TEST__AWS_ACCOUNT_ID     = '000000000000'               # default local-stack account id for lambdas
Serverless__Fast_API__TEST__AWS_DEFAULT_REGION = 'us-east-1'                  # default local-stack region for lambdas

class Serverless__Fast_API__Test_APIs(Type_Safe):
    fast_api        : Serverless__Fast_API  = None
    fast_api__app   : FastAPI               = None
    fast_api__client: TestClient            = None
    local_stack     : Local_Stack           = None
    setup_completed : bool                  = False

serverless_fast_api_test_api = Serverless__Fast_API__Test_APIs()


def setup_local_stack() -> Local_Stack:                                         # todo: refactor this to the OSBot_Local_Stack code base
    Temp_AWS_Credentials().with_localstack_credentials()
    local_stack = Local_Stack().activate()
    return local_stack

def setup__serverless_fast_api__test_api():
        with serverless_fast_api_test_api as _:
            if serverless_fast_api_test_api.setup_completed is False:
                _.fast_api         = Serverless__Fast_API().setup()
                _.fast_api__app    = _.fast_api.app()
                _.fast_api__client = _.fast_api.client()
                _.local_stack      = setup_local_stack()
                _.setup_completed  = True
        return serverless_fast_api_test_api
