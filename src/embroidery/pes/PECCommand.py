from .PECOpCode import PECOpCode
from src.embroidery.dst import DSTOpCode


class PECCommand:
    commands = {
        PECOpCode.STITCH: "STC",
        PECOpCode.JUMP: "JMP",
        PECOpCode.TRIM: "TRM",
    }

    def __init__(self, arg0: int | bytes, *args, **kwargs):
        self.x = 0
        self.y = 0
        self.op = 0
        self.color = 0

        if isinstance(arg0, bytes):
            self._init_from_bytecode(arg0)
        else:
            self._init_from_args(arg0, *args, **kwargs)

    def _init_from_bytecode(self, bytecode: bytes) -> None:
        if bytecode == b"\xff":
            self.op = PECOpCode.END
            return
        elif bytecode.startswith(b"\xfe\xb0"):
            self.op = PECOpCode.COLOR_CHANGE
            self.color = bytecode[2]
            return

        is_short = bytecode[0] >> 7 == 0
        byte_count = 1 if is_short else 2
        coord_len = 7 if is_short else 12
        print(
            int.from_bytes(bytecode[:byte_count], "big"),
            int.from_bytes(bytecode[byte_count:byte_count*2], "big"),
            coord_len,
        )
        self.x = self._decode_twos_complement(
            int.from_bytes(bytecode[:byte_count], "big") & (2**coord_len - 1),
            coord_len
        )
        self.y = self._decode_twos_complement(
            int.from_bytes(bytecode[byte_count:byte_count*2], "big") & (2**coord_len - 1),
            coord_len
        )
        self.op = 0 if is_short else ((bytecode[0] >> 4) & 0b111)

    def _init_from_args(
            self,
            x: int,
            y: int,
            op: int,
            color_change: int | None = None,
            is_end: bool = False
    ) -> None:
        if is_end:
            self.op = PECOpCode.END
            return

        if color_change is not None:
            self.op = PECOpCode.COLOR_CHANGE
            self.color = color_change
            return

        self.x = x
        self.y = y
        self.op = op

    @classmethod
    def from_dst(cls, dst: "src.dst.DSTCommand") -> "PECCommand":
        if dst.is_end:
            return cls(0, 0, 0, is_end=True)
        if dst.op == DSTOpCode.COLOR_CHANGE:
            return cls(0, 0, 0, color_change=2)

        op_switch = {
            DSTOpCode.STITCH: PECOpCode.STITCH,
            DSTOpCode.JUMP: PECOpCode.JUMP,
            DSTOpCode.SEQUIN: PECOpCode.TRIM,  # Unsure but what else could it be
        }
        return cls(dst.x, -dst.y, op_switch[dst.op])

    def to_bytes(self) -> bytes:
        if self.op == PECOpCode.END:
            return b"\xff"
        elif self.op == PECOpCode.COLOR_CHANGE:
            return b"\xfe\xb0" + self.color.to_bytes(1, "little")

        if self.op > 0 or \
                self.x > 2**6 - 1 or self.x < -(2**6) or \
                self.y > 2**6 - 1 or self.y < -(2**6):
            opcode = ((1 << 3) + self.op) << 4
            command_x = (opcode << 8) + self._encode_twos_complement(self.x, 12)
            command_y = (opcode << 8) + self._encode_twos_complement(self.y, 12)
            return command_x.to_bytes(2, "big") + command_y.to_bytes(2, "big")

        return \
            self._encode_twos_complement(self.x, 7).to_bytes(1, "big") \
            + self._encode_twos_complement(self.y, 7).to_bytes(1, "big")

    def __str__(self) -> str:
        if self.op == PECOpCode.END:
            return "[END]"
        if self.op == PECOpCode.COLOR_CHANGE:
            return "[CLR]"

        cmd_str = PECCommand.commands[self.op]
        return f"[{cmd_str}] {self.x},{self.y}"

    def __repr__(self) -> str:
        if self.op == PECOpCode.END:
            return "<PECCommand END>"
        if self.op == PECOpCode.COLOR_CHANGE:
            return f"<PECCommand CLR {self.color}>"

        cmd_str = PECCommand.commands[self.op]
        return f"<PECCommand {cmd_str} {self.x},{self.y}>"

    @staticmethod
    def _encode_twos_complement(num: int, bits: int) -> int:
        if num >= 0:
            return num
        return (2 ** bits - abs(num)) % (2 ** bits)

    @staticmethod
    def _decode_twos_complement(num: int, bits: int) -> int:
        if num >> (bits-1) == 0:
            return num
        return -(2 ** bits - (num - 1) - 1)
