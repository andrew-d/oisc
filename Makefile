run: interpreter.c
	$(CC) -Wall -Wextra -pedantic -ansi -o $@ $<

clean:
	$(RM) run
