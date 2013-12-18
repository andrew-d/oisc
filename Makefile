PASSWORD := XZgvSYhh7C
CFLAGS := -Wall -Wextra -pedantic -ansi -O3
OS := $(shell uname | tr '[:upper:]' '[:lower:]')
PLATFORM := $(shell uname -p)
TARGET := hacknight/hacknight_$(OS)_$(PLATFORM)
SOURCE_FILE ?= test/hacknight.asm
BYTECODE_FILE := $(SOURCE_FILE:asm=bc)


all: $(TARGET) $(BYTECODE_FILE)

$(BYTECODE_FILE): $(SOURCE_FILE)
	./assemble.py < $< > $@

code.gen.h: $(SOURCE_FILE)
	./assemble.py -c < $< > $@

$(TARGET): interpreter.c code.gen.h
	$(CC) $(CFLAGS) -o $@ $<
	strip $@

.PHONY: test
test: $(TARGET)
	@echo 'Testing (should print "Good"):'
	@printf $(PASSWORD) | ./$(TARGET)
	@echo
	@echo 'Testing (should print nothing):'
	@printf "bad" | ./$(TARGET)

itest: $(BYTECODE_FILE)
	@echo 'Testing (should print "Good"):'
	@printf $(PASSWORD) | ./interpreter.py $(BYTECODE_FILE)
	@echo
	@echo 'Testing (should print nothing):'
	@printf "bad" | ./interpreter.py $(BYTECODE_FILE)

hacknight.tar.gz: hacknight_*
	@tar cvzf $@ $^

archive: hacknight.tar.gz

clean:
	$(RM) $(TARGET) code.gen.h
