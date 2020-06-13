#!/usr/bin/env python3

from grole import Grole
import ssl

# Create an SSL context from keys created through e.g. Let's Encrypt or self signing:
# Generate a self signed cert with:
#   openssl genrsa -out rootCA.key 4096
#   openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt -subj "/CN=root"
#   openssl genrsa -out cert.key 2048
#   openssl req -new -sha256 -key cert.key -subj "/CN=localhost" -out cert.csr
#   openssl x509 -req -in cert.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out cert.crt -days 500 -sha256
# If using a self signed cert, you can access the server using: curl --cacert rootCA.crt https://localhost:8443
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.crt', keyfile='cert.key')
ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

app = Grole()

@app.route('/(.*)?')
def index(env, req):
  return 'Is it secret? Is it safe?'

app.run('0.0.0.0', port=8443, ssl_context=ssl_context)
