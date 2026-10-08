// Generated portable integer functions (inputs within +/-1,000,000).

pub fn proc_000(x: i64, y: i64) -> i64 {
    let mut value = (((x - 1_i64) - (8_i64 - x)) - ((y - x) * 3_i64));
    for iteration in 0_i64..5_i64 {
        if (value > (x + 20_i64)) {
            value = (value + (iteration + 8_i64));
        } else {
            value = (value - 7_i64);
        }
        value = (value + y);
    }
    value
}

pub fn proc_001(x: i64, y: i64) -> i64 {
    let mut value = (((y - x) + (x - x)) * 2_i64);
    for iteration in 0_i64..5_i64 {
        if (value > (x + -11_i64)) {
            value = (value + (iteration + 9_i64));
        } else {
            value = (value - 2_i64);
        }
        value = (value + y);
    }
    value
}

pub fn proc_002(x: i64, y: i64) -> i64 {
    let mut value = (((y + 9_i64) + (x * 3_i64)) * 1_i64);
    for iteration in 0_i64..5_i64 {
        if (value > (x + 7_i64)) {
            value = (value + (iteration + 9_i64));
        } else {
            value = (value - 4_i64);
        }
        value = (value + y);
    }
    value
}

pub fn proc_003(x: i64, y: i64) -> i64 {
    let mut value = (((x + x) - (y * 9_i64)) * 9_i64);
    for iteration in 0_i64..5_i64 {
        if (value < (x + -8_i64)) {
            value = (value + (iteration + 2_i64));
        } else {
            value = (value - 4_i64);
        }
        value = (value + y);
    }
    value
}

