#!/usr/bin/env python3

from grole import Grole

app = Grole({'message': 'Hello, World!'})

@app.route('/(\d+)')
def index(env, req):
    times = int(req.match.group(1))
    return env.get('message', '')*times

@app.route('/message', methods=['POST'])
def update(env, req):
    env['message'] = req.body()

app.run()
