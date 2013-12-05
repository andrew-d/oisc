#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdlib.h>

//#define TRACE

int32_t code[] = {
	161, 161, 3, -1, 161, 6, 169, 161, 12, 169,
	169, 18, 161, 169, 97, 169, 169, 97, 169, 169,
	23, 0, 0, 21, 21, 26, 163, 169, 29, 169,
	21, 32, 169, 169, 35, 22, 22, 38, 162, 169,
	41, 169, 22, 44, 169, 169, 47, 162, 162, 50,
	169, 21, 56, 169, 169, 62, 21, 169, 81, 169,
	169, 62, 22, 169, 65, 169, 162, 68, 169, 169,
	71, 169, 169, 75, 1, 74, 21, 78, 169, 169,
	50, 169, 169, 84, 161, 169, 87, 169, 162, 90,
	169, 169, 93, 169, 169, 0, 3026088333, 96, 162, 100,
	169, 162, 106, 169, 169, 158, 162, 169, 112, 169,
	169, 158, 161, 161, 115, 164, 169, 118, 169, 161,
	121, 169, 169, 124, 169, 161, 130, 169, 169, 136,
	161, 169, 155, 169, 169, 136, 161, -1, 139, 169,
	169, 143, 1, 142, 169, 146, 169, 115, 149, 169,
	169, 152, 169, 169, 112, 169, 169, 158, 169, 169,
	-1, 0, 0, 31, 71, 111, 111, 100, 0, 0,
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
