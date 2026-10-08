"""Procedurally generated functions; integer inputs within ±1,000,000."""

def proc_000(x: int, y: int) -> int:
    value = (((x - 1) - (8 - x)) - ((y - x) * 3))
    for iteration in range(5):
        if (value > (x + 20)):
            value = (value + (iteration + 8))
        else:
            value = (value - 7)
        value = (value + y)
    return value

def proc_001(x: int, y: int) -> int:
    value = (((y - x) + (x - x)) * 2)
    for iteration in range(5):
        if (value > (x + -11)):
            value = (value + (iteration + 9))
        else:
            value = (value - 2)
        value = (value + y)
    return value

def proc_002(x: int, y: int) -> int:
    value = (((y + 9) + (x * 3)) * 1)
    for iteration in range(5):
        if (value > (x + 7)):
            value = (value + (iteration + 9))
        else:
            value = (value - 4)
        value = (value + y)
    return value

def proc_003(x: int, y: int) -> int:
    value = (((x + x) - (y * 9)) * 9)
    for iteration in range(5):
        if (value < (x + -8)):
            value = (value + (iteration + 2))
        else:
            value = (value - 4)
        value = (value + y)
    return value

