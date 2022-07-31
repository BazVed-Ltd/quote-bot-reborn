from aiohttp import web
from quote_server.routes import routes

app = web.Application()
app.add_routes(routes)
