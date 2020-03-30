from sanic import Sanic
from sanic.response import json
from sanic.exceptions import ServerError
from .lookup import lookup

app = Sanic()

@app.route('/')
async def root(req):
    if 'address' in req.raw_args:
        return json(lookup(req.raw_args['address']))
    else:
        raise ServerError("No address query", status_code=400)
