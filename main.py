import logging
import os
import sys
import urllib.request

import yaml
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension, PreferencesUpdateEvent
from ulauncher.api.shared.action.CopyToClipboardAction import \
    CopyToClipboardAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

LOOKS_YML_URL = "https://raw.githubusercontent.com/leighmcculloch/looks.wtf/master/looks.yml"


logger = logging.getLogger(__name__)


class LooksWtfExtension(Extension):
    def __init__(self):
        super(LooksWtfExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(
            PreferencesUpdateEvent, PreferencesUpdateEventListener()
        )


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []

        data = download_looks(False)

        query = str(event.get_argument()).lower()
        if len(query) < 2:
            return None

        for item in data:
            if query in str(item.get("title")).lower():
                items.append(
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=str(item.get("title")),
                        description=item.get("plain"),
                        on_enter=CopyToClipboardAction(
                            item.get("plain"),
                        ),
                    )
                )

        return RenderResultListAction(items)


# If file does not exist on disk download it
def download_looks(force: bool):
    # check if file exists
    if os.path.isfile(os.path.join(sys.path[0], "looks.yml")) and not force:
        logger.info("Load looks from file")
        with open(os.path.join(sys.path[0], "looks.yml"), "r") as stream:
            return yaml.safe_load(stream)

    logger.info("Load looks from github")
    urllib.request.urlretrieve(
        LOOKS_YML_URL, os.path.join(sys.path[0], "looks.yml")
    )
    with open(os.path.join(sys.path[0], "looks.yml"), "r") as stream:
        return yaml.safe_load(stream)


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "reset" and event.new_value == "yes":
            download_looks(True)
            extension.preferences["reset"] = "-"


if __name__ == "__main__":
    LooksWtfExtension().run()
