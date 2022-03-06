import wsgiref.simple_server as wsgi_server
import cgi
import colorsys

from . import message
from . import db
from . import config

html = """
<html>
<head>
<title>{title}</title>
</head>
<body>
<h3>Leave me a message</h3>
<form method="post" action="">
<input type="text" name="message">
<input type="color" value="#FFFFFF" name="color">
<input type="submit" value="Send">
<span style="color:red">{thanks}</span>
</form>
<br/><br/>
<a href="https://github.com/ianmtaylor1/pimsgboard">
View the code on GitHub
</a>
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
    message_color_hex = post_data.get(b"color",[b"#FFFFFF"])[0].decode(errors='ignore')
    
    # Create a Message and save to db
    if len(message_text) > 0:
        try:
            rgb = tuple(int(message_color_hex[x:(x+2)], 16)/255 for x in [1,3,5])
        except:
            # If anything at all doesn't work, just use white
            rgb = (1.0, 1.0, 1.0)
        hsv = colorsys.rgb_to_hsv(*rgb)
        msg = message.Message(id_=0, text=message_text, hue=hsv[0], sat=hsv[1])
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

def start_server():
    global _web_db
    
    _web_db = config.getstr('dbfile')
    host = config.getstr('webhost')
    port = config.getint('webport')

    with wsgi_server.make_server(host, port, msg_app) as server:
        server.serve_forever()

