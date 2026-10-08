// Generated portable integer functions (inputs within +/-1,000,000).
package generated

func proc_000(x int64, y int64) int64 {
    value := (((x - int64(1)) - (int64(8) - x)) - ((y - x) * int64(3)))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value > (x + int64(20))) {
            value = (value + (iteration + int64(8)))
        } else {
            value = (value - int64(7))
        }
        value = (value + y)
    }
    return value
}

func proc_001(x int64, y int64) int64 {
    value := (((y - x) + (x - x)) * int64(2))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value > (x + int64(-11))) {
            value = (value + (iteration + int64(9)))
        } else {
            value = (value - int64(2))
        }
        value = (value + y)
    }
    return value
}

func proc_002(x int64, y int64) int64 {
    value := (((y + int64(9)) + (x * int64(3))) * int64(1))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value > (x + int64(7))) {
            value = (value + (iteration + int64(9)))
        } else {
            value = (value - int64(4))
        }
        value = (value + y)
    }
    return value
}

func proc_003(x int64, y int64) int64 {
    value := (((x + x) - (y * int64(9))) * int64(9))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value < (x + int64(-8))) {
            value = (value + (iteration + int64(2)))
        } else {
            value = (value - int64(4))
        }
        value = (value + y)
    }
    return value
}

