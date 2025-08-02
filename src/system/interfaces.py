
from enum import StrEnum

class OpModes(StrEnum):
    NA = "N/A"
    LIVE = "live"
    SIM = "sim"

class Status(StrEnum):
    NONE = "none"
    STANDBY = "standby"
    ACTIVE = "active"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"