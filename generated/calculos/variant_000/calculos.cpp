// Generated portable integer functions.
#include <cstdint>

std::int64_t proc_000(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((std::int64_t(-7) * std::int64_t(3)) + (y - x)) * std::int64_t(2));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + std::int64_t(10))) {
            value = (value + (iteration + std::int64_t(3)));
        } else {
            value = (value - std::int64_t(2));
        }
        value = (value + y);
    }
    return value;
}

std::int64_t proc_001(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((y - std::int64_t(5)) - (y + x)) + ((x * std::int64_t(8)) - (y + x)));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value == (x + std::int64_t(12))) {
            value = (value + (iteration + std::int64_t(4)));
        } else {
            value = (value - std::int64_t(3));
        }
        value = (value + y);
    }
    return value;
}

std::int64_t proc_002(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((y - std::int64_t(-3)) + (y * std::int64_t(2))) - ((y * std::int64_t(5)) * std::int64_t(3)));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + std::int64_t(3))) {
            value = (value + (iteration + std::int64_t(1)));
        } else {
            value = (value - std::int64_t(6));
        }
        value = (value + y);
    }
    return value;
}

std::int64_t proc_003(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((std::int64_t(-4) + x) - (x * std::int64_t(9))) * std::int64_t(3));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value < (x + std::int64_t(-9))) {
            value = (value + (iteration + std::int64_t(4)));
        } else {
            value = (value - std::int64_t(4));
        }
        value = (value + y);
    }
    return value;
}

