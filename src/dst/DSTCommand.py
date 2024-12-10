from src.utils import cmd_to_coords, coords_to_cmd


class DSTCommand:
    commands = {
        0b00: "STC",
        0b10: "JMP",
        0b01: "SQN",
        0b11: "CLR",
    }

    def __init__(self, arg0: bytes | int, y: int = None, op: int = None, is_end: bool = False):
        """
        :param arg0: Can either be the X shift value or the complete 3-byte command.
        :param y: The Y shift value
        :param op: The command operation
        :param is_end: if True, it represents the end of the file instead of another CLR.
            It's recommended to set X and Y to 0.
        """
        if op is y is None:
            if len(arg0) != 3:
                raise ValueError("DST commands must be exactly 3 bytes long.")
            self.x, self.y = cmd_to_coords(arg0)
            self.op = int(arg0[2] / 0b01000000)
            self.is_end = int(arg0[2] / 0b00010000) == 0b1111
        else:
            if abs(arg0) > 121 or abs(y) > 121:
                raise ValueError(f"X and Y must be between -121 and 121 included. Given: ({arg0}, {y}).")
            self.x = arg0
            self.y = y if y else 0
            self.op = op
            self.is_end = is_end

    def __str__(self) -> str:
        cmd_str = DSTCommand.commands[self.op]
        if self.is_end:
            cmd_str = "END"
        return f"[{cmd_str}] {self.x},{self.y}"

    def __repr__(self) -> str:
        cmd_str = DSTCommand.commands[self.op]
        if self.is_end:
            cmd_str = "END"
        return f"<DSTCommand {cmd_str} {self.x},{self.y}>"

    def to_bytes(self) -> bytes:
        cmd = coords_to_cmd((self.x, self.y), self.op)
        if self.is_end:
            cmd = cmd[:2] + (cmd[2] + 0b00110000).to_bytes(1, "little")
        return cmd
