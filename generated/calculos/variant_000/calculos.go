// Generated portable integer functions (inputs within +/-1,000,000).
package generated

func proc_000(x int64, y int64) int64 {
    value := (((int64(-7) * int64(3)) + (y - x)) * int64(2))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value > (x + int64(10))) {
            value = (value + (iteration + int64(3)))
        } else {
            value = (value - int64(2))
        }
        value = (value + y)
    }
    return value
}

func proc_001(x int64, y int64) int64 {
    value := (((y - int64(5)) - (y + x)) + ((x * int64(8)) - (y + x)))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value == (x + int64(12))) {
            value = (value + (iteration + int64(4)))
        } else {
            value = (value - int64(3))
        }
        value = (value + y)
    }
    return value
}

func proc_002(x int64, y int64) int64 {
    value := (((y - int64(-3)) + (y * int64(2))) - ((y * int64(5)) * int64(3)))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value > (x + int64(3))) {
            value = (value + (iteration + int64(1)))
        } else {
            value = (value - int64(6))
        }
        value = (value + y)
    }
    return value
}

func proc_003(x int64, y int64) int64 {
    value := (((int64(-4) + x) - (x * int64(9))) * int64(3))
    for iteration := int64(0); iteration < int64(5); iteration++ {
        if (value < (x + int64(-9))) {
            value = (value + (iteration + int64(4)))
        } else {
            value = (value - int64(4))
        }
        value = (value + y)
    }
    return value
}

