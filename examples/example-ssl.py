#!/usr/bin/env python3

from grole import Grole
import ssl

# Create an SSL context from keys created through e.g. Let's Encrypt or self signing:
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('fullchain.pem', keyfile='privkey.pem')
ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

app = Grole()

@app.route('/(.*)?')
def index(env, req):
  return 'Is it secret? Is it safe?'

app.run('0.0.0.0', port=443, ssl_context=ssl_context)
