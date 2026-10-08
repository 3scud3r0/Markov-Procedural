/* Generated portable integer functions. */
#include <stdint.h>

int64_t proc_000(int64_t x, int64_t y) {
    int64_t value = (((x - INT64_C(1)) - (INT64_C(8) - x)) - ((y - x) * INT64_C(3)));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + INT64_C(20))) {
            value = (value + (iteration + INT64_C(8)));
        } else {
            value = (value - INT64_C(7));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_001(int64_t x, int64_t y) {
    int64_t value = (((y - x) + (x - x)) * INT64_C(2));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + INT64_C(-11))) {
            value = (value + (iteration + INT64_C(9)));
        } else {
            value = (value - INT64_C(2));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_002(int64_t x, int64_t y) {
    int64_t value = (((y + INT64_C(9)) + (x * INT64_C(3))) * INT64_C(1));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + INT64_C(7))) {
            value = (value + (iteration + INT64_C(9)));
        } else {
            value = (value - INT64_C(4));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_003(int64_t x, int64_t y) {
    int64_t value = (((x + x) - (y * INT64_C(9))) * INT64_C(9));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value < (x + INT64_C(-8))) {
            value = (value + (iteration + INT64_C(2)));
        } else {
            value = (value - INT64_C(4));
        }
        value = (value + y);
    }
    return value;
}

