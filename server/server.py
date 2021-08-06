from aiohttp import web
import sys
sys.path.append('../talked')
import talked

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def test_handle(aiohttp_client, loop):
    app = web.Application()
    app.add_routes([web.get('/', handle), web.get('/{name}', handle)])
    client = await aiohttp_client(app)
    resp = await client.get('/test')
    assert resp.status == 200
    text = await resp.text()
    assert "Hello, test" in text

app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{name}', handle)])

if __name__ == '__main__':
    web.run_app(app)
