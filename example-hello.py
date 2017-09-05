#!/usr/bin/env python3

from grole import Grole

app = Grole()
app.env = {'message': 'Hello, World!'}

@app.route('/(\d+)')
def index(req):
    times = int(req.match.group(1))
    return req.env.get('message', '')*times

@app.route('/message', methods=['POST'])
def update(req):
    req.env['message'] = req.body()

app.run()
