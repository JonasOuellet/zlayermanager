from typing import Tuple
import requests
import re


current_version = "1.10.0"


def get_version() -> Tuple[int, int, int]:
    page = requests.get("https://jonasouellet.github.io/zlayermanager/")
    version = re.finditer(r'<title>.*([0-9]+\.[0-9]+\.[0-9]+).*<\/title>', page.text)
    version = next(version)
    return toTupleV(version.group(1))


def is_version_valid():
    try:
        version = get_version()
        curVer = toTupleV(current_version)
        return curVer >= version
    except:
        raise Exception('Could not retrieve version')


def toTupleV(ver: str):
    return tuple(map(int, ver.split('.')))
