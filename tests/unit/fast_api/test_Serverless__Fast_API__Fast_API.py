from unittest                                                  import TestCase
from fastapi                                                   import FastAPI
from osbot_fast_api.api.Fast_API                               import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_local_stack.local_stack.Local_Stack                 import Local_Stack
from osbot_utils.utils.Env                                     import get_env
from starlette.testclient                                      import TestClient
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API   import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info    import ROUTES_PATHS__INFO
from osbot_fast_api_serverless.utils.Version                   import version__osbot_fast_api_serverless
from osbot_fast_api_serverless.utils.testing.skip_tests        import skip__if_not__in_github_actions
from tests.serverless_fast_api__objs_for_tests                 import setup__serverless_fast_api__test_api, Serverless__Fast_API__Test_APIs


class test_Serverless__Fast_API__Fast_API(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.serverless_fast_api__test_api = setup__serverless_fast_api__test_api()
        cls.fast_api                      = cls.serverless_fast_api__test_api.fast_api
        cls.client                        = cls.serverless_fast_api__test_api.fast_api__client

    def test__init__(self):
        with self.serverless_fast_api__test_api as _:
            assert type(_)                  is Serverless__Fast_API__Test_APIs
            assert type(_.fast_api        ) is Serverless__Fast_API
            assert type(_.fast_api__app   ) is FastAPI
            assert type(_.fast_api__client) is TestClient
            assert type(_.local_stack     ) is Local_Stack
            assert self.fast_api            == _.fast_api
            assert self.client              == _.fast_api__client

    def test__client__root_path(self):
        path                = '/info/version'
        auth_key_name       = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME )
        auth_key_value      = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)
        headers             = {auth_key_name: auth_key_value}

        response__no_auth   = self.client.get(url=path                 )
        response__with_auth = self.client.get(url=path, headers=headers)

        assert response__no_auth.status_code == 401
        assert response__no_auth.json()      == { 'data'   : None                                                                 ,
                                                  'error'  : None                                                                 ,
                                                  'message': 'Client API key is missing, you need to set it on a header or cookie',
                                                  'status' : 'error'                                                              }

        assert auth_key_name                 is not None
        assert auth_key_value                is not None
        assert response__with_auth.json()    == {'version': version__osbot_fast_api_serverless }


    def test__check_if_local_stack_is_setup(self):
        skip__if_not__in_github_actions()
        with self.serverless_fast_api__test_api.local_stack as _:
            assert _.is_local_stack_configured_and_available() is True


    def test__config_fast_api_routes(self):
        assert self.fast_api.routes_paths() == ROUTES_PATHS__INFO

