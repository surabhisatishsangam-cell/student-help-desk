#ifndef TICKET_H
#define TICKET_H

#include <stdio.h>

#define STUDENT_ID_LEN   16
#define STUDENT_NAME_LEN 64
#define CATEGORY_LEN     32
#define DESCRIPTION_LEN  256
#define TIMESTAMP_LEN    32

/**
 * Ticket represents an individual help desk request.
 */
typedef struct {
    int  id;
    char student_id[STUDENT_ID_LEN];
    char student_name[STUDENT_NAME_LEN];
    char category[CATEGORY_LEN];
    char description[DESCRIPTION_LEN];
    char timestamp[TIMESTAMP_LEN];
} Ticket;

/**
 * Utility functions for Ticket
 */
void ticket_init(Ticket *ticket, int id, const char *student_id,
                 const char *student_name, const char *category,
                 const char *description, const char *timestamp);

void ticket_print_card(const Ticket *ticket, const char *status_label, int position);
void ticket_print_compact(const Ticket *ticket, int index);

#endif /* TICKET_H */
