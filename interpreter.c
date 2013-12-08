#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdlib.h>

/* #define TRACE */

int32_t code[] = {
	420, 420, 11, 103, 111, 111, 100, 95, 109, 115,
	103, 3, 3, 14, -1, 3, 17, 420, 420, 21,
	88, 20, 3, 24, 420, 3, 30, 420, 420, 408,
	3, 420, 36, 420, 420, 408, 420, 420, 40, 206,
	411, 411, 43, -1, 411, 46, 420, 420, 50, 90,
	49, 411, 53, 420, 411, 59, 420, 420, 408, 411,
	420, 65, 420, 420, 408, 411, 411, 68, -1, 411,
	71, 420, 420, 75, 2, 420, 420, 80, 0, 0,
	78, 78, 83, 74, 420, 86, 420, 78, 89, 420,
	420, 92, 79, 79, 95, 411, 420, 98, 420, 79,
	101, 420, 420, 104, 411, 411, 107, 420, 78, 113,
	420, 420, 119, 78, 420, 138, 420, 420, 119, 79,
	420, 122, 420, 411, 125, 420, 420, 128, 420, 420,
	132, 1, 131, 78, 135, 420, 420, 107, 420, 420,
	141, 39, 411, 144, 420, 411, 150, 420, 420, 408,
	411, 420, 156, 420, 420, 408, 411, 411, 159, -1,
	411, 162, 420, 420, 166, 118, 165, 411, 169, 420,
	411, 175, 420, 420, 408, 411, 420, 181, 420, 420,
	408, 420, 420, 206, 420, 420, 188, 83, 187, 411,
	191, 420, 411, 197, 420, 420, 408, 411, 420, 203,
	420, 420, 408, 420, 420, 215, 411, 411, 209, -1,
	411, 212, 420, 420, 184, 3, 3, 218, -1, 3,
	221, 420, 420, 225, 89, 224, 3, 228, 420, 411,
	234, 420, 420, 408, 411, 420, 240, 420, 420, 408,
	420, 420, 244, 9, 411, 411, 247, -1, 411, 250,
	420, 420, 254, 104, 253, 411, 257, 420, 411, 263,
	420, 420, 408, 411, 420, 269, 420, 420, 408, 420,
	420, 273, 8, 272, 243, 276, 420, 243, 282, 420,
	420, 244, 243, 420, 288, 420, 420, 288, 411, 411,
	291, -1, 411, 294, 420, 420, 298, 55, 297, 411,
	301, 420, 411, 307, 420, 420, 408, 411, 420, 313,
	420, 420, 408, 411, 411, 316, -1, 411, 319, 420,
	420, 323, -67, 322, 420, 326, 420, 411, 329, 420,
	420, 332, 420, 411, 338, 420, 420, 408, 411, 420,
	344, 420, 420, 408, 411, 411, 347, -1, 411, 350,
	420, 411, 356, 420, 420, 408, 411, 420, 408, 420,
	420, 362, 411, 411, 365, 414, 420, 368, 420, 411,
	371, 420, 420, 374, 420, 411, 380, 420, 420, 386,
	411, 420, 405, 420, 420, 386, 411, -1, 389, 420,
	420, 393, 1, 392, 420, 396, 420, 365, 399, 420,
	420, 402, 420, 420, 362, 420, 420, 408, 420, 420,
	-1, 0, 0, 31, 71, 111, 111, 100, 10, 0,
	0,
};

int32_t start = 0;



#define MEMORY_SIZE  ((int32_t)(sizeof(code) / sizeof(code[0])))


void die(const char * format, ...)
{
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);

    fprintf(stderr, "\n");
    fflush(stderr);
    exit(1);
}

int main(void) {
    int32_t ip = start;
    int32_t a, b, c;
    int32_t existing, new;
#ifdef TRACE
    uint32_t count = 0;
#endif

    while( ip >= 0 ) {
        /* Bounds check.  It might overflow ... but if you're
         * doing that much emulation, there are bigger problems.
         */
        if( (ip + 2) >= MEMORY_SIZE ) {
            die("IP ran past end of array (%d)", ip);
        }

        /* Read instruction. */
        a = code[ip + 0];
        b = code[ip + 1];
        c = code[ip + 2];

#ifdef TRACE
        fprintf(stderr, "[vm] %d: %d %d %d\n", ip, a, b, c);
#endif

        /* Bounds check. */
        if( b >= MEMORY_SIZE ) {
            die("Bad operand %d at %d", b, ip);
        }
        if( c >= MEMORY_SIZE ) {
            die("Bad operand %d at %d", c, ip);
        }

        /* Perform subtraction.  Note that a read of -1 here should read a
         * single character from stdin, and a write to -1 should write that
         * character to stdout.  For the initial read, we just have negative
         * reads return 0.
         */
        if( b < 0 ) {
            existing = 0;
        } else {
            existing = code[b];
        }

        if( a < 0 ) {
            new = -getchar();
        } else {
            new = code[a];
        }
        new = existing - new;

        if( b < 0 ) {
            putchar(-new);
        } else {
            code[b] = new;
        }

#ifdef TRACE
        fprintf(stderr, "[vm]     mem[%d] = %d --> %d\n", b, existing, new);
#endif

        /* Branch. */
        if( new <= 0 ) {
            ip = c;
        } else {
            ip += 3;
        }

#ifdef TRACE
        count++;
#endif
    }

#ifdef TRACE
    fprintf(stderr, "[vm] Ran %d instructions\n", count);
#endif

    return 0;
}
