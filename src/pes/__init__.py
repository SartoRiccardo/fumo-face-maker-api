# https://edutechwiki.unige.ch/en/Embroidery_format_PES
# https://edutechwiki.unige.ch/en/Embroidery_format_PEC
from .PESv1Header import PESv1Header
from .PECOpCode import PECOpCode
from .PECCommand import PECCommand


def pes_generate_header(_e) -> PESv1Header:
    return PESv1Header(
        PESv1Header.length(),
        False,
        False,
        0,
    )
