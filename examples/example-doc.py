#!/usr/bin/env python3

from grole import Grole, serve_doc

app = Grole()

serve_doc(app, '/')

@app.route('/hex/(\d+)')
def hexify(env, req):
    """
    Convert integer parameter to hex
    """
    return str(hex(int(req.match.group(1))))

@app.route('/bin/(\d+)')
def hexify(env, req):
    """
    Convert integer parameter to binary
    """
    return str(bin(int(req.match.group(1))))
app.run()
