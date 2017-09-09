#!/usr/bin/env python3

import asyncio
from jinja2 import Template
from grole import Grole

tpl = Template('Hello {{ name }}', enable_async=True)
app = Grole(tpl)

@app.route('/(.*)')
async def index(env, req):
    return await env.render_async(name=req.match.group(1))
app.run()
