from . import bp


@bp.on.message(text="/hello")
async def hello_handler(_):
    return "Hi!"
