/* Generated portable integer functions. */
#include <stdint.h>

int64_t proc_000(int64_t x, int64_t y) {
    int64_t value = (((INT64_C(4) - INT64_C(-4)) + (INT64_C(1) - x)) + ((x * INT64_C(3)) + (INT64_C(3) - INT64_C(0))));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + INT64_C(-14))) {
            value = (value + (iteration + INT64_C(5)));
        } else {
            value = (value - INT64_C(9));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_001(int64_t x, int64_t y) {
    int64_t value = (((INT64_C(-8) - y) * INT64_C(9)) * INT64_C(1));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + INT64_C(-16))) {
            value = (value + (iteration + INT64_C(7)));
        } else {
            value = (value - INT64_C(9));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_002(int64_t x, int64_t y) {
    int64_t value = (((x - INT64_C(3)) + (y + x)) + ((x * INT64_C(4)) + (y + y)));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value == (x + INT64_C(16))) {
            value = (value + (iteration + INT64_C(1)));
        } else {
            value = (value - INT64_C(7));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_003(int64_t x, int64_t y) {
    int64_t value = (((INT64_C(4) + y) - (INT64_C(-2) + y)) - ((y * INT64_C(9)) * INT64_C(4)));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value < (x + INT64_C(0))) {
            value = (value + (iteration + INT64_C(1)));
        } else {
            value = (value - INT64_C(5));
        }
        value = (value + y);
    }
    return value;
}

