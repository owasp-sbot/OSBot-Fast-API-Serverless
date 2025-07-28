LAMBDA_DEPENDENCIES =  ['osbot-fast-api', 'mangum']  # use 'osbot-fast-api==0.7.32' to lock to a particular version of osbot-fast-api



load_dependencies(LAMBDA_DEPENDENCIES)

from osbot_fast_api_serverless.fast_api.Serverless__Fast_API import Serverless__Fast_API

with Serverless__Fast_API() as _:
    _.setup()
    handler = _.handler()
    app     = _.app()

def run(event, context=None):
    return handler(event, context)