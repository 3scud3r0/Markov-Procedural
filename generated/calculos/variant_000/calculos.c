/* Generated portable integer functions. */
#include <stdint.h>

int64_t proc_000(int64_t x, int64_t y) {
    int64_t value = (((INT64_C(-7) * INT64_C(3)) + (y - x)) * INT64_C(2));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + INT64_C(10))) {
            value = (value + (iteration + INT64_C(3)));
        } else {
            value = (value - INT64_C(2));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_001(int64_t x, int64_t y) {
    int64_t value = (((y - INT64_C(5)) - (y + x)) + ((x * INT64_C(8)) - (y + x)));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value == (x + INT64_C(12))) {
            value = (value + (iteration + INT64_C(4)));
        } else {
            value = (value - INT64_C(3));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_002(int64_t x, int64_t y) {
    int64_t value = (((y - INT64_C(-3)) + (y * INT64_C(2))) - ((y * INT64_C(5)) * INT64_C(3)));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value > (x + INT64_C(3))) {
            value = (value + (iteration + INT64_C(1)));
        } else {
            value = (value - INT64_C(6));
        }
        value = (value + y);
    }
    return value;
}

int64_t proc_003(int64_t x, int64_t y) {
    int64_t value = (((INT64_C(-4) + x) - (x * INT64_C(9))) * INT64_C(3));
    for (int64_t iteration = 0; iteration < 5; ++iteration) {
        if (value < (x + INT64_C(-9))) {
            value = (value + (iteration + INT64_C(4)));
        } else {
            value = (value - INT64_C(4));
        }
        value = (value + y);
    }
    return value;
}

