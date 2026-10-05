#include "stack.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void init_stack(Stack *s) {
    if (!s) return;
    s->top = NULL;
    s->count = 0;
}

int push(Stack *s, const Ticket *ticket) {
    if (!s || !ticket) return 0;

    StackNode *new_node = (StackNode *)malloc(sizeof(StackNode));
    if (!new_node) {
        perror("Failed to allocate memory for StackNode");
        return 0;
    }

    new_node->ticket = *ticket;
    new_node->next = s->top;
    s->top = new_node;
    s->count++;

    return 1;
}

int pop(Stack *s, Ticket *out_ticket) {
    if (!s || is_stack_empty(s)) {
        return 0;
    }

    StackNode *temp = s->top;
    if (out_ticket) {
        *out_ticket = temp->ticket;
    }

    s->top = s->top->next;
    free(temp);
    s->count--;

    return 1;
}

int peek(const Stack *s, Ticket *out_ticket) {
    if (!s || is_stack_empty(s)) {
        return 0;
    }

    if (out_ticket) {
        *out_ticket = s->top->ticket;
    }

    return 1;
}

int is_stack_empty(const Stack *s) {
    return (s == NULL || s->top == NULL);
}

int stack_count(const Stack *s) {
    return s ? s->count : 0;
}

void print_stack(const Stack *s) {
    if (!s || is_stack_empty(s)) {
        printf("\n  [Empty: No resolved tickets in history]\n\n");
        return;
    }

    printf("\n======================== RESOLUTION HISTORY STACK (LIFO) ========================\n");
    printf("+------+--------+------------+------------------+--------------+----------------------+\n");
    printf("| Item | Ticket | Student ID | Student Name     | Category     | Resolved Timestamp   |\n");
    printf("+------+--------+------------+------------------+--------------+----------------------+\n");

    const StackNode *curr = s->top;
    int idx = 1;
    while (curr) {
        ticket_print_compact(&curr->ticket, idx);
        curr = curr->next;
        idx++;
    }

    printf("+------+--------+------------+------------------+--------------+----------------------+\n");
    printf("  Total Resolved Tickets in History (Top = Most Recent): %d\n\n", s->count);
}

int find_in_stack(const Stack *s, int id, Ticket *out_ticket) {
    if (!s) return 0;

    const StackNode *curr = s->top;
    while (curr) {
        if (curr->ticket.id == id) {
            if (out_ticket) {
                *out_ticket = curr->ticket;
            }
            return 1;
        }
        curr = curr->next;
    }

    return 0;
}

void free_stack(Stack *s) {
    if (!s) return;

    StackNode *curr = s->top;
    while (curr) {
        StackNode *next = curr->next;
        free(curr);
        curr = next;
    }

    s->top = NULL;
    s->count = 0;
}
