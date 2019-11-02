import getpass
import sys
import urllib.parse

import flask
import requests
import requests_ntlm
import waitress
import waitress.task


app = flask.Flask(__name__)
session = requests.Session()
config = {}


def log(method, path, result):
    sys.stdout.write(f'{method} /{path} {result}\n')
    sys.stdout.flush()


@app.route('/', defaults={'path': ''}, methods = ['HEAD', 'GET', 'POST'])
@app.route('/<path:path>', methods = ['HEAD', 'GET', 'POST'])
def handle(path):

    target_url = f'{url.scheme}://{url.netloc}/{path}'

    request_headers = dict(flask.request.headers)
    request_headers.update({
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT',
        'Host': url.netloc,
        'If-None-Match': '',
        'Accept-Encoding': 'identity',
    })

    method = flask.request.method
    response = None
    try:
        if method in ('HEAD', 'GET'):
            response = session.get(
                target_url,
                headers=request_headers,
                verify=False,
                timeout=30,
                params=flask.request.args,
            )
        elif method == 'POST':
            response = session.post(
                target_url,
                headers=request_headers,
                data=flask.request.form,
                verify=False,
                timeout=30,
                params=flask.request.args,
            )
    except requests.exceptions.ReadTimeout:
        log(method, path, 504)
        flask.abort(504)

    log(method, path, response.status_code)

    response_headers = dict(response.headers)
    response_headers['Content-Encoding'] = 'identity'
    response_headers['Content-Length'] = len(response.content)
    response_headers['Cache-Control'] = 'private, no-store, max-age=0'

    clean_response_headers = {}
    for response_header in response_headers.keys():
        if response_header.lower() not in waitress.task.hop_by_hop:
            clean_response_headers[response_header] = response_headers[response_header]

    return flask.Response(
        response.content,
        headers=clean_response_headers
    )


if __name__ == '__main__':

    # Disable SSL warnings...
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Grab the config.
    try:
        url = urllib.parse.urlparse(sys.argv[1])
        user = sys.argv[2]
    except IndexError:
        print('Usage: ntlmproxy.py [root URL] [username]')
        exit(1)

    if url.scheme == '':
        print('Missing URL scheme!')
        exit(1)

    if url.netloc == '':
        print('Invalid domain!')
        exit(1)

    if url.path not in ('', '/'):
        print('URL must be to root')
        exit(1)

    config['url'] = url

    passwd = getpass.getpass('NTLM password ({}): '.format(user))
    session.auth = requests_ntlm.HttpNtlmAuth(user, passwd)

    # Serve
    waitress.serve(app, threads=10)
