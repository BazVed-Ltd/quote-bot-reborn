from typing import Any, Optional
from xmlrpc.client import boolean
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle.dispatch.rules.base import RegexRule


def command_regex(command: str) -> RegexRule:
    return RegexRule(fr"^/{command}(?!\S)")


class NamedArguments(ABCRule[Message]):
    def __init__(self, *args: "Argument") -> None:
        self.args = args

    async def check(self, event: Message) -> dict:
        result = {}
        for arg in self.args:
            value = arg.get_value(event.text)
            result = {**result, **value}
        return result


class Argument():
    def __init__(
        self,
        name: str = "",
        shortname: str = "",
        in_command_name: Optional[str] = None,
        is_flag: boolean = False,
        required: boolean = False,
    ) -> None:
        self.name = name
        self.shortname = shortname
        self.in_command_name = in_command_name or name
        self.is_flag = is_flag
        self.required = required

    def _find_flag(self, text: str) -> bool:
        words = text.split(" ")
        for word_index in range(len(words)):
            word = words[word_index]
            if word.startswith("-") and any(self.shortname == letter for letter in word.removeprefix("-")):
                return True
            if word.startswith("—") and word.removeprefix("—") == self.name:
                return True
        return False

    def _find_value(self, text: str) -> Any:
        words = text.split(" ")
        for word_index in range(len(words) - 1):
            word = words[word_index]
            if not word.startswith("-") and not word.startswith("—"):
                continue
            word = word.removeprefix("-").removeprefix("—")
            if word == self.shortname or word == self.name:
                return words[word_index + 1]
        return None

    def get_value(self, text: str) -> dict:
        if self.is_flag:
            result = self._find_flag(text)
        else:
            result = self._find_value(text)
        return {self.in_command_name: result}
