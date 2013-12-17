all: run test/hacknight.bc

test/hacknight.bc: test/hacknight.asm
	./assemble.py < $< > $@

code.gen.h: test/hacknight.asm
	./assemble.py -c < $< > $@

run: interpreter.c code.gen.h
	$(CC) -Wall -Wextra -pedantic -ansi -o $@ $<

PASSWORD := XZgvSYhh7C
test: run
	@echo 'Testing (should print "Good"):'
	@printf $(PASSWORD) | ./run

itest: test/hacknight.bc
	@echo 'Testing (should print "Good"):'
	@printf $(PASSWORD) | ./interpreter.py test/hacknight.bc

clean:
	$(RM) run
