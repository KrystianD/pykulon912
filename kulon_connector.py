import enum
import re
from dataclasses import dataclass
from io import StringIO
from typing import Optional, Any

import requests
from lxml import etree


class KulonMode(enum.Enum):
    Idle = 0
    Charging = 1
    Discharging = 2


@dataclass
class KulonState:
    mode: KulonMode
    voltage: Optional[float] = None
    current: Optional[float] = None
    energy: Optional[float] = None


class InvalidDataException(Exception):
    pass


class NotAccessibleException(Exception):
    pass


def parse_kulon_state(data: Any) -> KulonState:
    display_html = data["pda"]
    doc_root = etree.parse(StringIO(display_html), etree.HTMLParser())

    voltage_str: str = doc_root.xpath("//strong")[0].text
    voltage = float(voltage_str[:-1])

    if "prs" in data:
        prs = data["prs"]
        if prs == "Battery connected.":
            return KulonState(KulonMode.Idle, voltage=voltage)

    if voltage_str[-1] != "V":
        raise InvalidDataException()

    current_str: str = doc_root.xpath("//strong")[1].text
    current = float(current_str[:-1])

    if current_str[-1] != "A":
        raise InvalidDataException()

    pnf = data["pnf"]

    m = re.match(r".*time:(\d\d)h(\d\d)m\s+Charge:\s*([\d.]+)Ah", pnf)
    if m is not None:
        time_hours = int(m.group(1))
        time_minutes = int(m.group(2))
        total_energy = float(m.group(3))
        return KulonState(KulonMode.Charging, voltage=voltage, current=current, energy=total_energy)
    else:
        m = re.match(r".*time:(\d\d)h(\d\d)m\s+Capacity:\s*([\d.]+)Ah", pnf)
        if m is not None:
            time_hours = int(m.group(1))
            time_minutes = int(m.group(2))
            total_energy = float(m.group(3))
            return KulonState(KulonMode.Discharging, voltage=voltage, current=current, energy=total_energy)
        else:
            raise InvalidDataException()


class KulonConnector:
    def __init__(self, host: str, port: int = 80):
        self.host = host
        self.port = port

    def fetch(self) -> KulonState:
        try:
            d = requests.get(f"http://{self.host}:{self.port}/data.jsn")
        except:
            raise NotAccessibleException()

        d.encoding = d.apparent_encoding
        data = d.json()

        return parse_kulon_state(data)


__all__ = [
    "KulonMode",
    "KulonState",
    "InvalidDataException",
    "NotAccessibleException",
    "KulonConnector",
]
