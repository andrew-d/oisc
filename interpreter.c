#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdlib.h>

//#define TRACE

int32_t code[] = {
        47, 47, 3, 48, 55, 6, 55, 47, 9, 55,
        55, 12, 47, 55, 18, 55, 55, 24, 55, 55,
        21, 55, 47, 43, 47, -1, 27, 55, 55, 31,
        1, 30, 55, 34, 55, 3, 37, 55, 55, 40,
        55, 55, 0, 55, 55, -1, 0, 0, 72, 101,
        108, 108, 111, 10, 0, 0,
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
        // Bounds check.  It might overflow ... but if you're
        // doing that much emulation, there are bigger problems.
        if( (ip + 2) >= MEMORY_SIZE ) {
            die("IP ran past end of array (%d)", ip);
        }

        // Read instruction.
        a = code[ip + 0];
        b = code[ip + 1];
        c = code[ip + 2];

#ifdef TRACE
        fprintf(stderr, "[vm] %d: %d %d %d\n", ip, a, b, c);
#endif

        // Bounds check.
        if( b >= MEMORY_SIZE ) {
            die("Bad operand %d at %d", b, ip);
        }
        if( c >= MEMORY_SIZE ) {
            die("Bad operand %d at %d", c, ip);
        }

        // Perform subtraction.  Note that a read of -1 here should read a
        // single character from stdin, and a write to -1 should write that
        // character to stdout.  For the initial read, we just have negative
        // reads return 0.
        if( b < 0 ) {
            existing = 0;
        } else {
            existing = code[b];
        }

        if( a < 0 ) {
            new = getchar();
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
        fprintf(stderr, "[vm]     %d --> %d\n", existing, new);
#endif

        // Branch.
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
