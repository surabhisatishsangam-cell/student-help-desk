#ifndef STACK_H
#define STACK_H

#include "ticket.h"

/**
 * Singly-linked list node for dynamic LIFO stack.
 */
typedef struct StackNode {
    Ticket ticket;
    struct StackNode *next;
} StackNode;

/**
 * Stack structure tracking the top node and element count.
 */
typedef struct {
    StackNode *top;
    int count;
} Stack;

/* Core Stack operations required */
void init_stack(Stack *s);
int  push(Stack *s, const Ticket *ticket);
int  pop(Stack *s, Ticket *out_ticket);
int  peek(const Stack *s, Ticket *out_ticket);
int  is_stack_empty(const Stack *s);
void print_stack(const Stack *s);
void free_stack(Stack *s);

/* Additional helper operations */
int  stack_count(const Stack *s);
int  find_in_stack(const Stack *s, int id, Ticket *out_ticket);

#endif /* STACK_H */
