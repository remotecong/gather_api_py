from sanic import Sanic
from sanic.response import json

app = Sanic()

@app.route('/')
async def test(req):
    return json({'test':'test'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
