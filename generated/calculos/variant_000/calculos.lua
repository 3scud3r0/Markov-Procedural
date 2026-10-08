-- Generated portable integer functions (inputs within +/-1,000,000).

local function proc_000(x, y)
    local value = (((-7 * 3) + (y - x)) * 2)
    for iteration = 0, 4 do
        if (value > (x + 10)) then
            value = (value + (iteration + 3))
        else
            value = (value - 2)
        end
        value = (value + y)
    end
    return value
end

local function proc_001(x, y)
    local value = (((y - 5) - (y + x)) + ((x * 8) - (y + x)))
    for iteration = 0, 4 do
        if (value == (x + 12)) then
            value = (value + (iteration + 4))
        else
            value = (value - 3)
        end
        value = (value + y)
    end
    return value
end

local function proc_002(x, y)
    local value = (((y - -3) + (y * 2)) - ((y * 5) * 3))
    for iteration = 0, 4 do
        if (value > (x + 3)) then
            value = (value + (iteration + 1))
        else
            value = (value - 6)
        end
        value = (value + y)
    end
    return value
end

local function proc_003(x, y)
    local value = (((-4 + x) - (x * 9)) * 3)
    for iteration = 0, 4 do
        if (value < (x + -9)) then
            value = (value + (iteration + 4))
        else
            value = (value - 4)
        end
        value = (value + y)
    end
    return value
end

return { proc_000 = proc_000, proc_001 = proc_001, proc_002 = proc_002, proc_003 = proc_003 }
