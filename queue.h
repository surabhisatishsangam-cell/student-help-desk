#ifndef QUEUE_H
#define QUEUE_H

#include "ticket.h"

/**
 * Singly-linked list node for dynamic FIFO queue.
 */
typedef struct QueueNode {
    Ticket ticket;
    struct QueueNode *next;
} QueueNode;

/**
 * Queue structure keeping pointers to front and rear for O(1) operations.
 */
typedef struct {
    QueueNode *front;
    QueueNode *rear;
    int size;
} Queue;

/* Core Queue operations required */
void init_queue(Queue *q);
int  enqueue(Queue *q, const Ticket *ticket);
int  dequeue(Queue *q, Ticket *out_ticket);
int  is_queue_empty(const Queue *q);
void print_queue(const Queue *q);
void free_queue(Queue *q);

/* Additional helper operations */
int  enqueue_front(Queue *q, const Ticket *ticket);
int  queue_size(const Queue *q);
int  find_in_queue(const Queue *q, int id, Ticket *out_ticket, int *out_position);

#endif /* QUEUE_H */
