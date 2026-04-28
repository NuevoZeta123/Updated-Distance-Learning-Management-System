import serverless_wsgi
from dlms_app import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)