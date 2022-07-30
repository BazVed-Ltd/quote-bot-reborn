"""
Предпочтительный способ создания команд - пакеты, см. `src/commands/_example_command`
"""
from vkbottle.bot import Blueprint

bp = Blueprint("ExampleCommandInModule")


@bp.on.message(text="/helloFromModule")
async def hello_handler(_):
    return "Hi! (from module :q)"
