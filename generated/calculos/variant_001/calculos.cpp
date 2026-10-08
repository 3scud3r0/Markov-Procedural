// Generated portable integer functions.
#include <cstdint>

std::int64_t proc_000(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((x - std::int64_t(1)) - (std::int64_t(8) - x)) - ((y - x) * std::int64_t(3)));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + std::int64_t(20))) {
            value = (value + (iteration + std::int64_t(8)));
        } else {
            value = (value - std::int64_t(7));
        }
        value = (value + y);
    }
    return value;
}

std::int64_t proc_001(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((y - x) + (x - x)) * std::int64_t(2));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + std::int64_t(-11))) {
            value = (value + (iteration + std::int64_t(9)));
        } else {
            value = (value - std::int64_t(2));
        }
        value = (value + y);
    }
    return value;
}

std::int64_t proc_002(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((y + std::int64_t(9)) + (x * std::int64_t(3))) * std::int64_t(1));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + std::int64_t(7))) {
            value = (value + (iteration + std::int64_t(9)));
        } else {
            value = (value - std::int64_t(4));
        }
        value = (value + y);
    }
    return value;
}

std::int64_t proc_003(std::int64_t x, std::int64_t y) {
    std::int64_t value = (((x + x) - (y * std::int64_t(9))) * std::int64_t(9));
    for (std::int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value < (x + std::int64_t(-8))) {
            value = (value + (iteration + std::int64_t(2)));
        } else {
            value = (value - std::int64_t(4));
        }
        value = (value + y);
    }
    return value;
}

