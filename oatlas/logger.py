import datetime
import sys
from enum import Enum
from functools import cached_property

from oatlas.config import date_time_format


class TerminalCodes(Enum):
    RESET = "\033[0m"

    # Foreground colors (bright)
    GREY = "\033[1;30m"
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    PURPLE = "\033[1;35m"
    CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"

    # Styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    INVERT = "\033[7m"

    # Backgrounds
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_PURPLE = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class Logger:
    ICONS = {
        "INFO": "ℹ️ ",
        "VERBOSE": "🔎 ",
        "STATE": "📍",
        "WARN": "⚠️ ",
        "ERROR": "❗",
        "EXCITED": "✨",
        "NORMAL": "• ",
    }

    COLORS = {
        "INFO": TerminalCodes.BLUE.value,
        "VERBOSE": TerminalCodes.CYAN.value,
        "STATE": TerminalCodes.PURPLE.value,
        "WARN": TerminalCodes.YELLOW.value,
        "ERROR": TerminalCodes.RED.value,
        "EXCITED": TerminalCodes.GREEN.value,
        "NORMAL": TerminalCodes.WHITE.value,
    }

    @staticmethod
    def log(text):
        print(text, end="", flush=True)

    @cached_property
    def verbose_mode_is_enabled(self):
        return "--verbose" in sys.argv or "-v" in sys.argv

    def _format_message(self, level, content, color_main, color_text):
        timestamp = datetime.datetime.now().strftime(date_time_format)
        return (
            TerminalCodes.CYAN.value
            + f"[{timestamp}]"
            + TerminalCodes.RESET.value
            + " "
            + color_main
            + f"{self.ICONS.get(level, '')}{level:<7}"
            + TerminalCodes.RESET.value
            + " "
            + color_text
            + content
            + TerminalCodes.RESET.value
            + "\n"
        )

    def info(self, content):
        self.log(
            self._format_message("INFO", content, TerminalCodes.CYAN.value, self.COLORS["INFO"])
        )

    def verbose_info(self, content):
        if self.verbose_mode_is_enabled:
            self.log(
                self._format_message(
                    "VERBOSE", content, TerminalCodes.CYAN.value, self.COLORS["VERBOSE"]
                )
            )

    def print_state(self, content):
        self.log(
            self._format_message(
                "STATE", content, TerminalCodes.PURPLE.value, self.COLORS["STATE"]
            )
        )

    def warn(self, content):
        self.log(
            self._format_message("WARN", content, TerminalCodes.YELLOW.value, self.COLORS["WARN"])
        )

    def error(self, content):
        self.log(
            self._format_message("ERROR", content, TerminalCodes.RED.value, self.COLORS["ERROR"])
        )

    def excited(self, content):
        self.log(
            self._format_message(
                "EXCITED", content, TerminalCodes.GREEN.value, self.COLORS["EXCITED"]
            )
        )

    def normal(self, content):
        self.log(
            self._format_message(
                "NORMAL", content, TerminalCodes.WHITE.value, self.COLORS["NORMAL"]
            )
        )

    def write(self, content):
        self.log(content)

    def reset_color(self):
        self.log(TerminalCodes.RESET.value)

    def colorful(self, content, color=TerminalCodes.GREEN.value, emoji="👉 "):
        """
        Simple, colorful log without timestamps/levels.
        Example:
            logger.colorful("Task completed!", Logger.COLORS["INFO"], "✅ ")
        """
        self.log(f"{color}{emoji}{content}{TerminalCodes.RESET.value}\n")

    # This is specifically for Nettacker ...

    def verbose_event_info(
        self, content, color=TerminalCodes.BLUE.value, emoji="🦈"
    ):  # Fix the emojis
        """
        build the info message, log the message in database if requested,
        rewrite the thread temporary file

        Args:
            content: content of the message

        Returns:
            None
        """
        if self.verbose_mode_is_enabled:  # prevent to stdout if run from API
            self.log(f"{color}{emoji}{content}{TerminalCodes.RESET.value}\n")

    def success_event_info(self, content, color=TerminalCodes.GREEN.value, emoji="✅"):
        """
        build the info message, log the message in database if requested,
        rewrite the thread temporary file

        Args:
            content: content of the message

        Returns:
            None
        """
        self.log(f"{color}{emoji}{content}{TerminalCodes.RESET.value}\n")


def get_logger():
    return Logger()
