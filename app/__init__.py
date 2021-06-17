""" main server app router """
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
from .lookup import lookup

app = Sanic()
CORS(app)

@app.route('/')
async def root(req):
    """ main route just looks up address """
    return json(lookup(req.raw_args.get("address")))
