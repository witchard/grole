#!/usr/bin/env python3

import asyncio
from grole import Grole

app = Grole()

@app.route('/(\d+)')
async def index(env, req):
    await asyncio.sleep( int(req.match.group(1)) )
app.run()
