// Generated portable integer functions (inputs within +/-1,000,000).

export function proc_000(x: number, y: number): number {
    let value = (((-7 * 3) + (y - x)) * 2);
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value > (x + 10)) {
            value = (value + (iteration + 3));
        } else {
            value = (value - 2);
        }
        value = (value + y);
    }
    return value;
}

export function proc_001(x: number, y: number): number {
    let value = (((y - 5) - (y + x)) + ((x * 8) - (y + x)));
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value == (x + 12)) {
            value = (value + (iteration + 4));
        } else {
            value = (value - 3);
        }
        value = (value + y);
    }
    return value;
}

export function proc_002(x: number, y: number): number {
    let value = (((y - -3) + (y * 2)) - ((y * 5) * 3));
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value > (x + 3)) {
            value = (value + (iteration + 1));
        } else {
            value = (value - 6);
        }
        value = (value + y);
    }
    return value;
}

export function proc_003(x: number, y: number): number {
    let value = (((-4 + x) - (x * 9)) * 3);
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value < (x + -9)) {
            value = (value + (iteration + 4));
        } else {
            value = (value - 4);
        }
        value = (value + y);
    }
    return value;
}

