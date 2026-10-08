"""Procedurally generated functions; integer inputs within ±1,000,000."""

def proc_000(x: int, y: int) -> int:
    value = (((-7 * 3) + (y - x)) * 2)
    for iteration in range(5):
        if (value > (x + 10)):
            value = (value + (iteration + 3))
        else:
            value = (value - 2)
        value = (value + y)
    return value

def proc_001(x: int, y: int) -> int:
    value = (((y - 5) - (y + x)) + ((x * 8) - (y + x)))
    for iteration in range(5):
        if (value == (x + 12)):
            value = (value + (iteration + 4))
        else:
            value = (value - 3)
        value = (value + y)
    return value

def proc_002(x: int, y: int) -> int:
    value = (((y - -3) + (y * 2)) - ((y * 5) * 3))
    for iteration in range(5):
        if (value > (x + 3)):
            value = (value + (iteration + 1))
        else:
            value = (value - 6)
        value = (value + y)
    return value

def proc_003(x: int, y: int) -> int:
    value = (((-4 + x) - (x * 9)) * 3)
    for iteration in range(5):
        if (value < (x + -9)):
            value = (value + (iteration + 4))
        else:
            value = (value - 4)
        value = (value + y)
    return value

