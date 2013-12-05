#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdlib.h>

/* #define TRACE */

int32_t code[] = {
	161, 161, 3, -1, 161, 6, 170, 161, 12, 170,
	170, 18, 161, 170, 97, 170, 170, 97, 170, 170,
	23, 0, 0, 21, 21, 26, 163, 170, 29, 170,
	21, 32, 170, 170, 35, 22, 22, 38, 162, 170,
	41, 170, 22, 44, 170, 170, 47, 162, 162, 50,
	170, 21, 56, 170, 170, 62, 21, 170, 81, 170,
	170, 62, 22, 170, 65, 170, 162, 68, 170, 170,
	71, 170, 170, 75, 1, 74, 21, 78, 170, 170,
	50, 170, 170, 84, 161, 170, 87, 170, 162, 90,
	170, 170, 93, 170, 170, 0, 3026088333, 96, 162, 100,
	170, 162, 106, 170, 170, 158, 162, 170, 112, 170,
	170, 158, 161, 161, 115, 164, 170, 118, 170, 161,
	121, 170, 170, 124, 170, 161, 130, 170, 170, 136,
	161, 170, 155, 170, 170, 136, 161, -1, 139, 170,
	170, 143, 1, 142, 170, 146, 170, 115, 149, 170,
	170, 152, 170, 170, 112, 170, 170, 158, 170, 170,
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
    fprintf(stderr, "[vm] Ran %d instructions", count);
#endif
}
