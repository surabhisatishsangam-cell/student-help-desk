#ifndef DESK_MANAGER_H
#define DESK_MANAGER_H

#include "ticket.h"
#include "queue.h"
#include "stack.h"

#define DEFAULT_CSV_FILE "helpdesk_data.csv"

/**
 * ServiceDesk encapsulates:
 * - pending_queue: FIFO queue of incoming student requests
 * - resolved_stack: LIFO stack of processed tickets (enabling undo and history)
 * - next_ticket_id: Auto-incrementing unique ticket identifier
 */
typedef struct {
    Queue pending_queue;
    Stack resolved_stack;
    int   next_ticket_id;
} ServiceDesk;

/* Lifecycle */
void desk_init(ServiceDesk *desk);
void desk_cleanup(ServiceDesk *desk);

/* Core Desk Operations */
int  desk_submit_ticket(ServiceDesk *desk,
                        const char *student_id,
                        const char *student_name,
                        const char *category,
                        const char *description,
                        Ticket *out_ticket);

int  desk_process_next(ServiceDesk *desk, Ticket *out_processed);
int  desk_undo_resolution(ServiceDesk *desk, Ticket *out_undone);

/* Search / Query Operations */
int  desk_find_ticket(const ServiceDesk *desk, int id,
                      Ticket *out_ticket, char *out_status, size_t status_buf_size);

int  desk_count_student_tickets(const ServiceDesk *desk, const char *student_id);
void desk_print_student_tickets(const ServiceDesk *desk, const char *student_id);

/* Persistence */
int  desk_save_to_file(const ServiceDesk *desk, const char *filename);
int  desk_load_from_file(ServiceDesk *desk, const char *filename);

#endif /* DESK_MANAGER_H */
