// Generated portable integer functions (inputs within +/-1,000,000).

export function proc_000(x: number, y: number): number {
    let value = (((x - 1) - (8 - x)) - ((y - x) * 3));
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value > (x + 20)) {
            value = (value + (iteration + 8));
        } else {
            value = (value - 7);
        }
        value = (value + y);
    }
    return value;
}

export function proc_001(x: number, y: number): number {
    let value = (((y - x) + (x - x)) * 2);
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value > (x + -11)) {
            value = (value + (iteration + 9));
        } else {
            value = (value - 2);
        }
        value = (value + y);
    }
    return value;
}

export function proc_002(x: number, y: number): number {
    let value = (((y + 9) + (x * 3)) * 1);
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value > (x + 7)) {
            value = (value + (iteration + 9));
        } else {
            value = (value - 4);
        }
        value = (value + y);
    }
    return value;
}

export function proc_003(x: number, y: number): number {
    let value = (((x + x) - (y * 9)) * 9);
    for (let iteration = 0; iteration < 5; iteration++) {
        if (value < (x + -8)) {
            value = (value + (iteration + 2));
        } else {
            value = (value - 4);
        }
        value = (value + y);
    }
    return value;
}

