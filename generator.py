from dataclasses import dataclass
import struct
# https://edutechwiki.unige.ch/en/Embroidery_format_DST


@dataclass
class DSTHeader:
  label: str
  stitches: int
  color_changes: int
  extend_x: tuple[int, int]
  extend_y: tuple[int, int]
  start_coords: tuple[int, int]
  multi_design_start: tuple[int, int]
  previous_design: str
  author: str | None = None
  copyright: str | None = None
  colors: list[tuple[str, str, str]] | None = None
  
  def to_bytes(self) -> bytes:
    def getsign(num: int) -> str:
      s = sign(num)
      return "+" if s >= 0 else "-"
      
    return (
      "LA:" + self.label.ljust(16) + "\r"
      "ST:" + str(self.stitches).rjust(7) + "\r"
      "CO:" + str(self.color_changes).rjust(3) + "\r"
      "+X:" + str(self.extend_x[0]).rjust(5) + "\r"
      "-X:" + str(abs(self.extend_x[1])).rjust(5) + "\r"
      "+Y:" + str(self.extend_y[0]).rjust(5) + "\r"
      "-Y:" + str(abs(self.extend_y[1])).rjust(5) + "\r"
      "AX:" + getsign(self.start_coords[0]) + str(abs(self.start_coords[0])).rjust(5) + "\r"
      "AY:" + getsign(self.start_coords[1]) + str(abs(self.start_coords[1])).rjust(5) + "\r"
      "MX:" + getsign(self.multi_design_start[0]) + str(abs(self.multi_design_start[0])).rjust(5) + "\r"
      "MY:" + getsign(self.multi_design_start[1]) + str(abs(self.multi_design_start[1])).rjust(5) + "\r"
      "PD:" + self.previous_design + "\r\x1a"
    ).ljust(512).encode()


class DSTOpCode:
  STITCH = 0b00
  JUMP = 0b10
  SEQUIN = 0b01
  COLOR_CHANGE = 0b11
  END = 0b11


class DSTCommand:
  commands = {
    0b00: "STC",
    0b10: "JMP",
    0b01: "SQN",
    0b11: "CLR",
  }

  def __init__(self, arg0: bytes | int, y: int = None, op: int = None, is_end: bool = False):
    if op is y is None:
      if len(arg0) != 3:
        raise ValueError("DST commands must be exactly 3 bytes long.")
      self.x, self.y = cmd_to_coords(arg0)
      self.op = int(arg0[2]/0b01000000)
      self.is_end = int(arg0[2]/0b00010000) == 0b1111
    else:
      if abs(arg0) > 121 or abs(y) > 121:
        raise ValueError(f"X and Y must be between -121 and 121 included. Given: ({arg0}, {y}).")
      self.x = arg0
      self.y = y
      self.op = op
      self.is_end = is_end
  
  @staticmethod
  def from_bytes() -> DSTCommand:
    

  def __str__(self) -> str:
    cmd_str = DSTCommand.commands[self.op]
    if self.is_end:
      cmd_str = "END"
    return f"[{cmd_str}] {self.x},{self.y}"
  
  def to_bytes(self) -> bytes:
    cmd = coords_to_cmd((self.x, self.y), self.op)
    if self.is_end:
      cmd = cmd[:2] + (cmd[2]+0b00110000).to_bytes(1, "little")
    return cmd


def sign(num: int) -> int:
  if num == 0:
    return 0
  return -1 if num < 0 else 1


def dst_load(fname) -> tuple[DSTHeader, list[DSTCommand]]:
  with open(fname, "rb") as fin:
  	header_raw = fin.read(512)
  	embroidery_raw = fin.read()
  
  header = DSTHeader(
    header_raw[3:19].decode(),
    int(header_raw[23:30]),
    int(header_raw[34:37]),
    (int(header_raw[41:46]), int(header_raw[50:55])*-1),
    (int(header_raw[59:64]), int(header_raw[68:73])*-1),
    (int(header_raw[77:83].replace(b" ", b"")), int(header_raw[87:93].replace(b" ", b""))),
    (int(header_raw[97:103].replace(b" ", b"")), int(header_raw[107:113].replace(b" ", b""))),
    header_raw[117:123].decode(),
  )
  
  embroidery = [DSTCommand(embroidery_raw[i:i+3]) for i in range(0, len(embroidery_raw), 3)]
  
  return header, embroidery
  

coords_matrix = [
  [1, -1,  9,  -9,  -9,  9, -1, 1],
  [3, -3, 27, -27, -27, 27, -3, 3],
  [0,  0, 81, -81, -81, 81,  0, 0],
]
def cmd_to_coords(cmd: bytes) -> tuple[int, int]:
  x, y = 0, 0
  for i in range(len(cmd)):
    for j in range(8):
      bit = int(cmd[i]/(2**j)) % 2
      if j < 4:
        x += bit * coords_matrix[i][j]
      else:
        y += bit * coords_matrix[i][j]
  return x, y


num_to_operations = {}
operators = [3**4, 3**3, 3**2, 3**1, 3**0]
def populate_nto(ops=None):
  if ops is None:
    return populate_nto([])
  if len(ops) == 5:
    num_to_operations[sum(ops)] = [sign(op) for op in ops]
    return
  populate_nto(ops + [3**len(ops)])
  populate_nto(ops + [0])
  populate_nto(ops + [-(3**len(ops))])
populate_nto()


# First number in the tuple is the byte to sum to, the second is the amount to sum (bit to change)
command_sums = {
  "y": {
     1: [(0, 0b10000000), (1, 0b10000000), (0, 0b00100000), (1, 0b00100000), (2, 0b00100000)],
    -1: [(0, 0b01000000), (1, 0b01000000), (0, 0b00010000), (1, 0b00010000), (2, 0b00010000)],
  },
  "x": {
     1: [(0, 0b00000001), (1, 0b00000001), (0, 0b00000100), (1, 0b00000100), (2, 0b00000100)],
    -1: [(0, 0b00000010), (1, 0b00000010), (0, 0b00001000), (1, 0b00001000), (2, 0b00001000)],
  },
}
def operations_to_cmd(op_x, op_y, op_code) -> bytes:
  byte_3 = 0b00000011 + op_code * 0b01000000
  command = [0, 0, byte_3]
  for i, op in enumerate(op_y):
    if op != 0:
      byte_no, sum_amount = command_sums["y"][op][i]
      command[byte_no] += sum_amount
  for i, op in enumerate(op_x):
    if op != 0:
      byte_no, sum_amount = command_sums["x"][op][i]
      command[byte_no] += sum_amount
  return b"".join([x.to_bytes(1, "little") for x in command])


def coords_to_cmd(coords: tuple[int, int], op_code: int = 0b10) -> bytes:
  x, y = coords
  ops_x, ops_y = [], []
  while abs(x) >= 121:
    ops_x.append(num_to_operations[121 * sign(x)])
    x -= 121 * sign(x)
  ops_x.append(num_to_operations[x])

  while abs(y) >= 121:
    ops_y.append(num_to_operations[121 * sign(y)])
    y -= 121 * sign(y)
  ops_y.append(num_to_operations[y])
  
  for i in range(max(len(ops_y), len(ops_x))):
    op_x = ops_x[i] if i < len(ops_x) else [0]*5
    op_y = ops_y[i] if i < len(ops_y) else [0]*5
    return operations_to_cmd(op_x, op_y, op_code)


def main(fname):
  header, commands = dst_load(fname)
  insert_stop_at = -1
  for i, cmd in enumerate(commands):
    if cmd.op == DSTOpCode.JUMP and insert_stop_at == -1:
        continue
    insert_stop_at = i
    if cmd.op == DSTOpCode.JUMP:
      break
    
  print(header.stitches, len(commands))
  
  header.color_changes += 1
  header.stitches += 1
  commands.insert(insert_stop_at, DSTCommand(0, 0, DSTOpCode.COLOR_CHANGE))