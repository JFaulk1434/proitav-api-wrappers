"""IPD970 wrapper built on the shared IP970 family base."""

import importlib
from pathlib import Path
import sys


CURRENT_DIR = Path(__file__).resolve().parent
FAMILY_ROOT = CURRENT_DIR.parent

if str(FAMILY_ROOT) not in sys.path:
    sys.path.insert(0, str(FAMILY_ROOT))

IP970BaseDevice = importlib.import_module("base").IP970BaseDevice


class IPD970Device(IP970BaseDevice):
    """IPD970 model wrapper.

    Add IPD970-specific commands here while keeping shared behavior in
    `apiwrappers/IP970_Family/base.py`.
    """

    MODEL_NAME = "IPD970"
    COMMAND_TEMPLATES = {
        **IP970BaseDevice.COMMAND_TEMPLATES,
        # Add IPD970-specific command templates here.
    }
