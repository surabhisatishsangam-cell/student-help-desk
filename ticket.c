#include "ticket.h"
#include <string.h>
#include <stdio.h>

void ticket_init(Ticket *ticket, int id, const char *student_id,
                 const char *student_name, const char *category,
                 const char *description, const char *timestamp) {
    if (!ticket) return;

    ticket->id = id;

    if (student_id) {
        strncpy(ticket->student_id, student_id, sizeof(ticket->student_id) - 1);
        ticket->student_id[sizeof(ticket->student_id) - 1] = '\0';
    } else {
        ticket->student_id[0] = '\0';
    }

    if (student_name) {
        strncpy(ticket->student_name, student_name, sizeof(ticket->student_name) - 1);
        ticket->student_name[sizeof(ticket->student_name) - 1] = '\0';
    } else {
        ticket->student_name[0] = '\0';
    }

    if (category) {
        strncpy(ticket->category, category, sizeof(ticket->category) - 1);
        ticket->category[sizeof(ticket->category) - 1] = '\0';
    } else {
        ticket->category[0] = '\0';
    }

    if (description) {
        strncpy(ticket->description, description, sizeof(ticket->description) - 1);
        ticket->description[sizeof(ticket->description) - 1] = '\0';
    } else {
        ticket->description[0] = '\0';
    }

    if (timestamp) {
        strncpy(ticket->timestamp, timestamp, sizeof(ticket->timestamp) - 1);
        ticket->timestamp[sizeof(ticket->timestamp) - 1] = '\0';
    } else {
        ticket->timestamp[0] = '\0';
    }
}

void ticket_print_card(const Ticket *ticket, const char *status_label, int position) {
    if (!ticket) return;

    printf("+------------------------------------------------------------------------------+\n");
    printf("| TICKET #%-6d %-40s ", ticket->id, status_label ? status_label : "");
    if (position > 0) {
        printf("[Pos: %2d] |\n", position);
    } else {
        printf("           |\n");
    }
    printf("+------------------------------------------------------------------------------+\n");
    printf("| Student ID   : %-61s |\n", ticket->student_id);
    printf("| Student Name : %-61s |\n", ticket->student_name);
    printf("| Category     : %-61s |\n", ticket->category);
    printf("| Submitted At : %-61s |\n", ticket->timestamp);
    printf("| Description  : %-61.61s |\n", ticket->description);

    /* If description is longer than 61 characters, print subsequent lines */
    size_t len = strlen(ticket->description);
    if (len > 61) {
        size_t offset = 61;
        while (offset < len) {
            printf("|                %-61.61s |\n", ticket->description + offset);
            offset += 61;
        }
    }
    printf("+------------------------------------------------------------------------------+\n");
}

void ticket_print_compact(const Ticket *ticket, int index) {
    if (!ticket) return;
    char short_desc[28];
    strncpy(short_desc, ticket->description, sizeof(short_desc) - 1);
    short_desc[sizeof(short_desc) - 1] = '\0';

    /* Truncate with ellipsis if needed */
    if (strlen(ticket->description) >= sizeof(short_desc) - 1) {
        short_desc[24] = '.';
        short_desc[25] = '.';
        short_desc[26] = '.';
        short_desc[27] = '\0';
    }

    printf("| %4d | #%-5d | %-10s | %-16s | %-12s | %-20s |\n",
           index,
           ticket->id,
           ticket->student_id,
           ticket->student_name,
           ticket->category,
           ticket->timestamp);
}
