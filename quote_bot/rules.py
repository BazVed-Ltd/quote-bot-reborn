from typing import Union
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle.dispatch.rules import base


class CommandRule(base.CommandRule):
    """Копия правила `vkbottle.dispatch.rules.base.CommandRule` но если `args_count < 0`, то длину сообщения игнорируем
    """
    async def check(self, event: Message) -> Union[dict, bool]:
        for prefix in self.prefixes:
            if self.args_count < 0 and event.text.startswith(prefix + self.command_text + " "):
                return True
            if self.args_count == 0 and event.text == prefix + self.command_text:
                return True
            if self.args_count > 0 and event.text.startswith(prefix + self.command_text + " "):
                args = event.text[len(prefix + self.command_text) + 1:].split(self.sep)
                if len(args) != self.args_count:
                    return False
                elif any(len(arg) == 0 for arg in args):
                    return False
                return {"args": tuple(args)}
        return False


class NameArguments(ABCRule[Message]):
    def __init__(self, *args) -> None:
        self.variables = [*args]

    async def check(self, event: Message) -> bool:
        result = {}
        words = event.text.split(" ")
        for word_index in range(len(words)):
            word = words[word_index]
            word = word.removeprefix("-").removeprefix("—")
            if word in self.variables:
                result[word] = words[word_index+1] if word_index+1 < len(words) else None
        for var in self.variables:
            if var not in result:
                result[var] = None
        return result
