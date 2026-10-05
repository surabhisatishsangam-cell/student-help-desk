#include "desk_manager.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void desk_init(ServiceDesk *desk) {
    if (!desk) return;
    init_queue(&desk->pending_queue);
    init_stack(&desk->resolved_stack);
    desk->next_ticket_id = 1001;
}

void desk_cleanup(ServiceDesk *desk) {
    if (!desk) return;
    free_queue(&desk->pending_queue);
    free_stack(&desk->resolved_stack);
    desk->next_ticket_id = 1001;
}

int desk_submit_ticket(ServiceDesk *desk,
                        const char *student_id,
                        const char *student_name,
                        const char *category,
                        const char *description,
                        Ticket *out_ticket) {
    if (!desk) return 0;

    int id = desk->next_ticket_id++;

    /* Format current timestamp */
    char timestamp[TIMESTAMP_LEN];
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    if (tm_info) {
        strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_info);
    } else {
        strncpy(timestamp, "N/A", sizeof(timestamp) - 1);
        timestamp[sizeof(timestamp) - 1] = '\0';
    }

    Ticket t;
    ticket_init(&t, id, student_id, student_name, category, description, timestamp);

    if (!enqueue(&desk->pending_queue, &t)) {
        /* Rollback ID increment if enqueue fails */
        desk->next_ticket_id--;
        return 0;
    }

    if (out_ticket) {
        *out_ticket = t;
    }

    return 1;
}

int desk_process_next(ServiceDesk *desk, Ticket *out_processed) {
    if (!desk || is_queue_empty(&desk->pending_queue)) {
        return 0;
    }

    Ticket t;
    if (!dequeue(&desk->pending_queue, &t)) {
        return 0;
    }

    /* Push the processed ticket to the resolved stack */
    if (!push(&desk->resolved_stack, &t)) {
        /* Safety: push failed (out of memory), restore to front of queue */
        enqueue_front(&desk->pending_queue, &t);
        return 0;
    }

    if (out_processed) {
        *out_processed = t;
    }

    return 1;
}

int desk_undo_resolution(ServiceDesk *desk, Ticket *out_undone) {
    if (!desk || is_stack_empty(&desk->resolved_stack)) {
        return 0;
    }

    Ticket t;
    if (!pop(&desk->resolved_stack, &t)) {
        return 0;
    }

    /* Restore ticket to the front of the pending queue */
    if (!enqueue_front(&desk->pending_queue, &t)) {
        /* Safety: enqueue failed, restore to stack */
        push(&desk->resolved_stack, &t);
        return 0;
    }

    if (out_undone) {
        *out_undone = t;
    }

    return 1;
}

int desk_find_ticket(const ServiceDesk *desk, int id,
                      Ticket *out_ticket, char *out_status, size_t status_buf_size) {
    if (!desk) return 0;

    int pos = 0;
    Ticket t;

    /* Check pending queue first */
    if (find_in_queue(&desk->pending_queue, id, &t, &pos)) {
        if (out_ticket) *out_ticket = t;
        if (out_status && status_buf_size > 0) {
            snprintf(out_status, status_buf_size, "PENDING (Queue Position: %d)", pos);
        }
        return 1;
    }

    /* Check resolved stack */
    if (find_in_stack(&desk->resolved_stack, id, &t)) {
        if (out_ticket) *out_ticket = t;
        if (out_status && status_buf_size > 0) {
            snprintf(out_status, status_buf_size, "RESOLVED (In History)");
        }
        return 1;
    }

    return 0;
}

int desk_count_student_tickets(const ServiceDesk *desk, const char *student_id) {
    if (!desk || !student_id) return 0;
    int count = 0;

    const QueueNode *q_curr = desk->pending_queue.front;
    while (q_curr) {
        if (strcmp(q_curr->ticket.student_id, student_id) == 0) {
            count++;
        }
        q_curr = q_curr->next;
    }

    const StackNode *s_curr = desk->resolved_stack.top;
    while (s_curr) {
        if (strcmp(s_curr->ticket.student_id, student_id) == 0) {
            count++;
        }
        s_curr = s_curr->next;
    }

    return count;
}

void desk_print_student_tickets(const ServiceDesk *desk, const char *student_id) {
    if (!desk || !student_id) return;

    printf("\n======================== TICKETS FOR STUDENT ID: %-12s ========================\n", student_id);

    int total_found = 0;
    int pending_count = 0;
    int resolved_count = 0;

    /* Pending tickets */
    const QueueNode *q_curr = desk->pending_queue.front;
    int pos = 1;
    while (q_curr) {
        if (strcmp(q_curr->ticket.student_id, student_id) == 0) {
            char status[32];
            snprintf(status, sizeof(status), "PENDING [Queue Pos: %d]", pos);
            ticket_print_card(&q_curr->ticket, status, pos);
            pending_count++;
            total_found++;
        }
        q_curr = q_curr->next;
        pos++;
    }

    /* Resolved tickets */
    const StackNode *s_curr = desk->resolved_stack.top;
    while (s_curr) {
        if (strcmp(s_curr->ticket.student_id, student_id) == 0) {
            ticket_print_card(&s_curr->ticket, "RESOLVED", 0);
            resolved_count++;
            total_found++;
        }
        s_curr = s_curr->next;
    }

    if (total_found == 0) {
        printf("  No tickets found for student ID '%s'.\n", student_id);
    } else {
        printf("  Summary: %d Total (%d Pending, %d Resolved)\n",
               total_found, pending_count, resolved_count);
    }
    printf("=================================================================================\n\n");
}

/* Helper to write a CSV field safely escaping commas, quotes, and newlines */
static void write_csv_field(FILE *fp, const char *str, int is_last) {
    int needs_quotes = 0;
    const char *p = str;

    while (*p) {
        if (*p == ',' || *p == '"' || *p == '\n' || *p == '\r') {
            needs_quotes = 1;
            break;
        }
        p++;
    }

    if (!needs_quotes) {
        fputs(str, fp);
    } else {
        fputc('"', fp);
        p = str;
        while (*p) {
            if (*p == '"') {
                fputc('"', fp);
                fputc('"', fp);
            } else {
                fputc(*p, fp);
            }
            p++;
        }
        fputc('"', fp);
    }

    if (is_last) {
        fputc('\n', fp);
    } else {
        fputc(',', fp);
    }
}

int desk_save_to_file(const ServiceDesk *desk, const char *filename) {
    if (!desk || !filename) return 0;

    FILE *fp = fopen(filename, "w");
    if (!fp) {
        perror("Error opening file for saving");
        return 0;
    }

    /* Write CSV Header */
    fprintf(fp, "Type,ID,StudentID,StudentName,Category,Description,Timestamp\n");

    /* 1. Write Pending Queue (from front to rear) */
    const QueueNode *q_curr = desk->pending_queue.front;
    while (q_curr) {
        char id_str[16];
        snprintf(id_str, sizeof(id_str), "%d", q_curr->ticket.id);

        write_csv_field(fp, "PENDING", 0);
        write_csv_field(fp, id_str, 0);
        write_csv_field(fp, q_curr->ticket.student_id, 0);
        write_csv_field(fp, q_curr->ticket.student_name, 0);
        write_csv_field(fp, q_curr->ticket.category, 0);
        write_csv_field(fp, q_curr->ticket.description, 0);
        write_csv_field(fp, q_curr->ticket.timestamp, 1);

        q_curr = q_curr->next;
    }

    /* 2. Write Resolved Stack (from bottom to top so reloading preserves exact LIFO order) */
    int resolved_count = desk->resolved_stack.count;
    if (resolved_count > 0) {
        Ticket *temp_arr = (Ticket *)malloc(sizeof(Ticket) * resolved_count);
        if (temp_arr) {
            const StackNode *s_curr = desk->resolved_stack.top;
            int idx = 0;
            while (s_curr && idx < resolved_count) {
                temp_arr[idx++] = s_curr->ticket;
                s_curr = s_curr->next;
            }

            /* Write from bottom (oldest resolved) to top (most recently resolved) */
            for (int i = resolved_count - 1; i >= 0; i--) {
                char id_str[16];
                snprintf(id_str, sizeof(id_str), "%d", temp_arr[i].id);

                write_csv_field(fp, "RESOLVED", 0);
                write_csv_field(fp, id_str, 0);
                write_csv_field(fp, temp_arr[i].student_id, 0);
                write_csv_field(fp, temp_arr[i].student_name, 0);
                write_csv_field(fp, temp_arr[i].category, 0);
                write_csv_field(fp, temp_arr[i].description, 0);
                write_csv_field(fp, temp_arr[i].timestamp, 1);
            }

            free(temp_arr);
        }
    }

    fclose(fp);
    return 1;
}

/* Helper to parse a single CSV line into up to max_fields tokens */
static int parse_csv_line(char *line, char **fields, int max_fields) {
    int field_count = 0;
    char *p = line;

    while (*p && field_count < max_fields) {
        if (*p == '"') {
            p++; /* Skip opening quote */
            fields[field_count++] = p;
            char *write_p = p;
            while (*p) {
                if (*p == '"') {
                    if (*(p + 1) == '"') {
                        *write_p++ = '"';
                        p += 2;
                    } else {
                        p++; /* End of quoted field */
                        break;
                    }
                } else {
                    *write_p++ = *p++;
                }
            }
            *write_p = '\0';
            while (*p && *p != ',') p++;
            if (*p == ',') p++;
        } else {
            fields[field_count++] = p;
            while (*p && *p != ',' && *p != '\r' && *p != '\n') {
                p++;
            }
            if (*p == ',') {
                *p = '\0';
                p++;
            } else if (*p == '\r' || *p == '\n') {
                *p = '\0';
                break;
            }
        }
    }
    return field_count;
}

int desk_load_from_file(ServiceDesk *desk, const char *filename) {
    if (!desk || !filename) return 0;

    FILE *fp = fopen(filename, "r");
    if (!fp) {
        return 0;
    }

    /* Reset existing state */
    desk_cleanup(desk);
    desk_init(desk);

    char line[1024];
    int line_num = 0;
    int max_id_found = 1000;

    while (fgets(line, sizeof(line), fp)) {
        line_num++;
        if (line_num == 1) {
            /* Skip CSV header line if present */
            if (strncmp(line, "Type,", 5) == 0) {
                continue;
            }
        }

        /* Strip trailing newlines */
        size_t len = strlen(line);
        while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
            line[--len] = '\0';
        }
        if (len == 0) continue;

        char *fields[7];
        int field_count = parse_csv_line(line, fields, 7);
        if (field_count < 7) {
            continue; /* Skip invalid line */
        }

        const char *type        = fields[0];
        int id                  = atoi(fields[1]);
        const char *student_id  = fields[2];
        const char *student_name= fields[3];
        const char *category    = fields[4];
        const char *description = fields[5];
        const char *timestamp   = fields[6];

        Ticket t;
        ticket_init(&t, id, student_id, student_name, category, description, timestamp);

        if (strcmp(type, "PENDING") == 0) {
            enqueue(&desk->pending_queue, &t);
        } else if (strcmp(type, "RESOLVED") == 0) {
            push(&desk->resolved_stack, &t);
        }

        if (id > max_id_found) {
            max_id_found = id;
        }
    }

    desk->next_ticket_id = max_id_found + 1;
    fclose(fp);
    return 1;
}
