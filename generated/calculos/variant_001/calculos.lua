-- Generated portable integer functions (inputs within +/-1,000,000).

local function proc_000(x, y)
    local value = (((x - 1) - (8 - x)) - ((y - x) * 3))
    for iteration = 0, 4 do
        if (value > (x + 20)) then
            value = (value + (iteration + 8))
        else
            value = (value - 7)
        end
        value = (value + y)
    end
    return value
end

local function proc_001(x, y)
    local value = (((y - x) + (x - x)) * 2)
    for iteration = 0, 4 do
        if (value > (x + -11)) then
            value = (value + (iteration + 9))
        else
            value = (value - 2)
        end
        value = (value + y)
    end
    return value
end

local function proc_002(x, y)
    local value = (((y + 9) + (x * 3)) * 1)
    for iteration = 0, 4 do
        if (value > (x + 7)) then
            value = (value + (iteration + 9))
        else
            value = (value - 4)
        end
        value = (value + y)
    end
    return value
end

local function proc_003(x, y)
    local value = (((x + x) - (y * 9)) * 9)
    for iteration = 0, 4 do
        if (value < (x + -8)) then
            value = (value + (iteration + 2))
        else
            value = (value - 4)
        end
        value = (value + y)
    end
    return value
end

return { proc_000 = proc_000, proc_001 = proc_001, proc_002 = proc_002, proc_003 = proc_003 }
