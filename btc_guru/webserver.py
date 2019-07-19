from flask import Flask, request, session, redirect, abort, url_for
from flask_jsontools import jsonapi
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from helpers.database import InfluxdbApiQuery
from datetime import timedelta
from helpers import ApiJSONEncoder
import os


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__, static_folder='web')
app.json_encoder = ApiJSONEncoder
app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100/day"]
)


@app.route('/')
@limiter.exempt
def index():
    return app.send_static_file('index.html')


@app.route('/timeseries', methods=['GET'])
def timeseries():
    return InfluxdbApiQuery(request.args).query()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
