from sanic import Sanic
from sanic.response import json
from sanic.exceptions import ServerError
from .owner_info import get_owner_data
from .thatsthem import get_phone_numbers

app = Sanic()

@app.route('/')
async def lookup(req):
    if 'address' in req.raw_args:
        a = req.raw_args['address']
        owner_data = get_owner_data(a)
        owner_data['phones'] = get_phone_numbers(a)
        return json(owner_data)
    else:
        raise ServerError("No address query", status_code=400)
