from sanic import Sanic
from sanic.response import json
from sanic.exceptions import ServerError
from .owner_info import get_owner_data

app = Sanic()

@app.route('/')
async def lookup(req):
    if 'address' in req.raw_args:
        return json(get_owner_data(req.raw_args['address']))
    else:
        raise ServerError("No address query", status_code=400)
