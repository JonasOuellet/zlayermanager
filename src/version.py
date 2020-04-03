import requests
import re


current_version = 1.2


def get_version():
    page = requests.get("https://jonasouellet.github.io/zlayermanager/")
    version = re.findall('<div\\s*class="version">\\s*(.*)\\s*<\\/div>',
                         page.text)
    version = float(version[0])
    return version


def is_version_valid():
    try:
        version = get_version()
        return current_version >= version
    except:
        raise Exception('Could not retrieve version')
