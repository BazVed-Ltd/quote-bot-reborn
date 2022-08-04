from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle.dispatch.rules.base import RegexRule


def command_regex(command: str) -> RegexRule:
    return RegexRule(fr"^/{command}(?!\S)")


class NameArguments(ABCRule[Message]):
    def __init__(self, *args) -> None:
        self.variables = [*args]

    async def check(self, event: Message) -> dict:
        result = {}
        words = event.text.split(" ")
        for word_index in range(len(words)):
            word = words[word_index]
            word = word.removeprefix("-").removeprefix("—")
            if word in self.variables:
                result[word] = words[word_index + 1] if word_index + 1 < len(words) else None
        for var in self.variables:
            if var not in result:
                result[var] = None
        return result
