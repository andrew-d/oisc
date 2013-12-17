PASSWORD := XZgvSYhh7C
CFLAGS := -Wall -Wextra -pedantic -ansi -O3
OS := $(shell uname | tr '[:upper:]' '[:lower:]')
PLATFORM := $(shell uname -p)
TARGET := hacknight_$(OS)_$(PLATFORM)


all: $(TARGET) test/hacknight.bc

test/hacknight.bc: test/hacknight.asm
	./assemble.py < $< > $@

code.gen.h: test/hacknight.asm
	./assemble.py -c < $< > $@

$(TARGET): interpreter.c code.gen.h
	$(CC) $(CFLAGS) -o $@ $<
	strip $@

test: $(TARGET)
	@echo 'Testing (should print "Good"):'
	@printf $(PASSWORD) | ./$(TARGET)

itest: test/hacknight.bc
	@echo 'Testing (should print "Good"):'
	@printf $(PASSWORD) | ./interpreter.py test/hacknight.bc

clean:
	$(RM) $(TARGET) code.gen.h
