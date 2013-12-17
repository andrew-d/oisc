all: run test/hacknight.bc

test/hacknight.bc: test/hacknight.asm
	./assemble.py < $< > $@

code.gen.h: test/hacknight.asm
	./assemble.py -c < $< > $@

run: interpreter.c code.gen.h
	$(CC) -Wall -Wextra -pedantic -ansi -o $@ $<

clean:
	$(RM) run
