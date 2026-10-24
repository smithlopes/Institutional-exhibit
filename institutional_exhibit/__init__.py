from .fonts import register_inter

register_inter()          # must run before Frame is used

from .frame import Frame
from .spec import SPEC
from .theme import THEME, inr, usd_bn

__all__ = ["Frame", "SPEC", "THEME", "usd_bn", "inr"]