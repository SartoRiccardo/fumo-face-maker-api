

def sign(num: int) -> int:
    if num == 0:
        return 0
    return -1 if num < 0 else 1


coords_matrix = [
    [1, -1,    9,    -9,    -9,    9, -1, 1],
    [3, -3, 27, -27, -27, 27, -3, 3],
    [0,    0, 81, -81, -81, 81,    0, 0],
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
operators = [3 ** 4, 3 ** 3, 3 ** 2, 3 ** 1, 3 ** 0]


def populate_nto(ops=None):
    if ops is None:
        return populate_nto([])
    if len(ops) == 5:
        num_to_operations[sum(ops)] = [sign(op) for op in ops]
        return
    populate_nto(ops + [3 ** len(ops)])
    populate_nto(ops + [0])
    populate_nto(ops + [-(3 ** len(ops))])


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
        op_x = ops_x[i] if i < len(ops_x) else [0] * 5
        op_y = ops_y[i] if i < len(ops_y) else [0] * 5
        return operations_to_cmd(op_x, op_y, op_code)