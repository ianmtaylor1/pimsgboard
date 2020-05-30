import wsgiref.simple_server as wsgi_server
import cgi

from . import message
from . import db

html = """
<html>
<head>
<title>{title}</title>
</head>
<body>
<form method="post" action="">
Leave me a message: <input type="text" name="message">
<input type="submit" value="Send">
<span style="color:red">{thanks}</span>
</form>
</body>
</html>
"""

def msg_app(env, start_response):
    # Look for POST content. First check content length.
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    # Now get POST request data from the wsgi.input variable
    request_body = env['wsgi.input'].read(request_body_size)
    post_data = cgi.parse_qs(request_body)
    
    # Extract the message that was submitted (if any)
    message_text = post_data.get(b"message",[b""])[0].decode(errors='ignore')
    
    # Create a Message and save to db
    if len(message_text) > 0:
        msg = message.Message(id_=0, text=message_text)
        db.write_message(_web_db, msg)

    # Construct response body
    title = "Raspberry Pi Message Board"
    if len(message_text) > 0:
        thanks = "Thanks!"
    else:
        thanks = ""
    response_body = html.format(title=title, thanks=thanks)
    
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response_body.encode(errors='ignore')]

def start_server(host, port, db_file):
    global _web_db
    _web_db = db_file
    with wsgi_server.make_server(host, port, msg_app) as server:
        server.serve_forever()

