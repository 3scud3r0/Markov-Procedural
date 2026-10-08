// Generated portable integer functions (inputs within +/-1,000,000).

pub fn proc_000(x: i64, y: i64) -> i64 {
    let mut value = (((-7_i64 * 3_i64) + (y - x)) * 2_i64);
    for iteration in 0_i64..5_i64 {
        if (value > (x + 10_i64)) {
            value = (value + (iteration + 3_i64));
        } else {
            value = (value - 2_i64);
        }
        value = (value + y);
    }
    value
}

pub fn proc_001(x: i64, y: i64) -> i64 {
    let mut value = (((y - 5_i64) - (y + x)) + ((x * 8_i64) - (y + x)));
    for iteration in 0_i64..5_i64 {
        if (value == (x + 12_i64)) {
            value = (value + (iteration + 4_i64));
        } else {
            value = (value - 3_i64);
        }
        value = (value + y);
    }
    value
}

pub fn proc_002(x: i64, y: i64) -> i64 {
    let mut value = (((y - -3_i64) + (y * 2_i64)) - ((y * 5_i64) * 3_i64));
    for iteration in 0_i64..5_i64 {
        if (value > (x + 3_i64)) {
            value = (value + (iteration + 1_i64));
        } else {
            value = (value - 6_i64);
        }
        value = (value + y);
    }
    value
}

pub fn proc_003(x: i64, y: i64) -> i64 {
    let mut value = (((-4_i64 + x) - (x * 9_i64)) * 3_i64);
    for iteration in 0_i64..5_i64 {
        if (value < (x + -9_i64)) {
            value = (value + (iteration + 4_i64));
        } else {
            value = (value - 4_i64);
        }
        value = (value + y);
    }
    value
}

