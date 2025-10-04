from io import StringIO

import yaml

from oatlas.config import Config


def load_yaml(filename):
    return yaml.load(StringIO(open(filename, "r").read()), Loader=yaml.FullLoader)


class load_message:
    def __init__(self):
        self.language = (
            "en"  # This is always going to be english only because I don't care for languages
        )
        self.messages = load_yaml(
            "{messages_path}/en.yaml".format(messages_path=Config.path.nettacker_locale_dir)
        )


message_cache = load_message().messages


def messages(msg_id):
    """
    load a message from message library with specified language

    Args:
        msg_id: message id

    Returns:
        the message content in the selected language if
        message found otherwise return message in English
    """
    return message_cache[str(msg_id)]
