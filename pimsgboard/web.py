import wsgiref.simple_server as wsgi_server
import cgi

def msg_app(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b"Hello world!", bytes(_web_db, 'utf8'), bytes(repr(env), 'utf8')]

def start_server(host, port, db_file):
    global _web_db
    _web_db = db_file
    with wsgi_server.make_server(host, port, msg_app) as server:
        server.serve_forever()

