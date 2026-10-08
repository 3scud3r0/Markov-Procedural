-- Generated portable integer functions (inputs within +/-1,000,000).

local function proc_000(x, y)
    local value = (((4 - -4) + (1 - x)) + ((x * 3) + (3 - 0)))
    for iteration = 0, 4 do
        if (value > (x + -14)) then
            value = (value + (iteration + 5))
        else
            value = (value - 9)
        end
        value = (value + y)
    end
    return value
end

local function proc_001(x, y)
    local value = (((-8 - y) * 9) * 1)
    for iteration = 0, 4 do
        if (value > (x + -16)) then
            value = (value + (iteration + 7))
        else
            value = (value - 9)
        end
        value = (value + y)
    end
    return value
end

local function proc_002(x, y)
    local value = (((x - 3) + (y + x)) + ((x * 4) + (y + y)))
    for iteration = 0, 4 do
        if (value == (x + 16)) then
            value = (value + (iteration + 1))
        else
            value = (value - 7)
        end
        value = (value + y)
    end
    return value
end

local function proc_003(x, y)
    local value = (((4 + y) - (-2 + y)) - ((y * 9) * 4))
    for iteration = 0, 4 do
        if (value < (x + 0)) then
            value = (value + (iteration + 1))
        else
            value = (value - 5)
        end
        value = (value + y)
    end
    return value
end

return { proc_000 = proc_000, proc_001 = proc_001, proc_002 = proc_002, proc_003 = proc_003 }
