# Makefile for Student Help Desk Management System (C99)

CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -pedantic -O2

# Detect OS for binary name and clean command
ifeq ($(OS),Windows_NT)
    TARGET = helpdesk.exe
    RM = del /Q /F
else
    TARGET = helpdesk
    RM = rm -f
endif

SRCS = main.c cli.c desk_manager.c queue.c stack.c ticket.c
OBJS = $(SRCS:.c=.o)
HEADERS = ticket.h queue.h stack.h desk_manager.h cli.h

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

run: $(TARGET)
	./$(TARGET)

clean:
	$(RM) $(OBJS) $(TARGET)
