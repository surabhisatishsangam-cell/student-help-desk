#include "queue.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void init_queue(Queue *q) {
    if (!q) return;
    q->front = NULL;
    q->rear = NULL;
    q->size = 0;
}

int enqueue(Queue *q, const Ticket *ticket) {
    if (!q || !ticket) return 0;

    QueueNode *new_node = (QueueNode *)malloc(sizeof(QueueNode));
    if (!new_node) {
        perror("Failed to allocate memory for QueueNode");
        return 0;
    }

    new_node->ticket = *ticket;
    new_node->next = NULL;

    if (q->rear == NULL) {
        /* Queue is currently empty */
        q->front = new_node;
        q->rear = new_node;
    } else {
        q->rear->next = new_node;
        q->rear = new_node;
    }

    q->size++;
    return 1;
}

int enqueue_front(Queue *q, const Ticket *ticket) {
    if (!q || !ticket) return 0;

    QueueNode *new_node = (QueueNode *)malloc(sizeof(QueueNode));
    if (!new_node) {
        perror("Failed to allocate memory for QueueNode");
        return 0;
    }

    new_node->ticket = *ticket;
    new_node->next = q->front;
    q->front = new_node;

    if (q->rear == NULL) {
        q->rear = new_node;
    }

    q->size++;
    return 1;
}

int dequeue(Queue *q, Ticket *out_ticket) {
    if (!q || is_queue_empty(q)) {
        return 0;
    }

    QueueNode *temp = q->front;
    if (out_ticket) {
        *out_ticket = temp->ticket;
    }

    q->front = q->front->next;
    if (q->front == NULL) {
        q->rear = NULL;
    }

    free(temp);
    q->size--;
    return 1;
}

int is_queue_empty(const Queue *q) {
    return (q == NULL || q->front == NULL);
}

int queue_size(const Queue *q) {
    return q ? q->size : 0;
}

void print_queue(const Queue *q) {
    if (!q || is_queue_empty(q)) {
        printf("\n  [Empty: No pending tickets in queue]\n\n");
        return;
    }

    printf("\n============================= PENDING TICKETS QUEUE (FIFO) =============================\n");
    printf("+------+--------+------------+------------------+--------------+----------------------+\n");
    printf("| Pos  | Ticket | Student ID | Student Name     | Category     | Submitted At         |\n");
    printf("+------+--------+------------+------------------+--------------+----------------------+\n");

    const QueueNode *curr = q->front;
    int pos = 1;
    while (curr) {
        ticket_print_compact(&curr->ticket, pos);
        curr = curr->next;
        pos++;
    }

    printf("+------+--------+------------+------------------+--------------+----------------------+\n");
    printf("  Total Pending Tickets in Queue: %d\n\n", q->size);
}

int find_in_queue(const Queue *q, int id, Ticket *out_ticket, int *out_position) {
    if (!q) return 0;

    const QueueNode *curr = q->front;
    int pos = 1;
    while (curr) {
        if (curr->ticket.id == id) {
            if (out_ticket) {
                *out_ticket = curr->ticket;
            }
            if (out_position) {
                *out_position = pos;
            }
            return 1;
        }
        curr = curr->next;
        pos++;
    }
    return 0;
}

void free_queue(Queue *q) {
    if (!q) return;

    QueueNode *curr = q->front;
    while (curr) {
        QueueNode *next = curr->next;
        free(curr);
        curr = next;
    }

    q->front = NULL;
    q->rear = NULL;
    q->size = 0;
}
