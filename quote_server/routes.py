import json
from aiohttp import web

from quote_bot.database import quotes

routes = web.RouteTableDef()


@routes.get('/api/quotes/{id}')
async def hello(request):
    id = int(request.match_info['id'])
    quote = quotes.get_quote_by_id(int(id))
    if not quote:
        raise web.HTTPNotFound()

    del quote["_id"]
    return web.json_response(quote, dumps=dump)

def dump(*args, **kwargs):
    return json.dumps(*args, ensure_ascii=False, **kwargs)