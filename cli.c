#include "cli.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

void clean_newline(char *str) {
    if (!str) return;
    size_t len = strlen(str);
    while (len > 0 && (str[len - 1] == '\n' || str[len - 1] == '\r')) {
        str[--len] = '\0';
    }
}

static void discard_excess_input(void) {
    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF) {
        /* Discard remaining characters on the line */
    }
}

int get_input_string(const char *prompt, char *buffer, size_t size, int allow_empty) {
    if (!buffer || size == 0) return 0;

    while (1) {
        if (prompt) {
            printf("%s", prompt);
            fflush(stdout);
        }

        if (!fgets(buffer, (int)size, stdin)) {
            /* Handled EOF */
            return 0;
        }

        /* Check if newline was included or if input overflowed */
        char *newline_pos = strchr(buffer, '\n');
        if (!newline_pos) {
            /* Input was truncated by buffer size; discard remaining characters */
            discard_excess_input();
        } else {
            *newline_pos = '\0';
        }

        clean_newline(buffer);

        /* Trim leading spaces */
        char *start = buffer;
        while (*start && isspace((unsigned char)*start)) {
            start++;
        }

        if (start != buffer) {
            memmove(buffer, start, strlen(start) + 1);
        }

        /* Check empty condition */
        if (!allow_empty && strlen(buffer) == 0) {
            printf("  [!] Input cannot be empty. Please try again.\n");
            continue;
        }

        return 1;
    }
}

int get_input_int(const char *prompt, int *out_val, int min, int max) {
    char line[64];

    while (1) {
        if (prompt) {
            printf("%s", prompt);
            fflush(stdout);
        }

        if (!fgets(line, sizeof(line), stdin)) {
            return 0;
        }

        /* If input exceeded buffer, discard rest of line */
        if (!strchr(line, '\n')) {
            discard_excess_input();
        }

        clean_newline(line);

        /* Trim leading whitespace */
        char *start = line;
        while (*start && isspace((unsigned char)*start)) {
            start++;
        }

        if (*start == '\0') {
            printf("  [!] Invalid input. Please enter a valid number.\n");
            continue;
        }

        char *endptr = NULL;
        long val = strtol(start, &endptr, 10);

        /* Check trailing whitespace */
        while (*endptr && isspace((unsigned char)*endptr)) {
            endptr++;
        }

        if (*endptr != '\0') {
            printf("  [!] Invalid input. Please enter numbers only.\n");
            continue;
        }

        if (val < min || val > max) {
            printf("  [!] Selection out of range (%d to %d). Please try again.\n", min, max);
            continue;
        }

        if (out_val) {
            *out_val = (int)val;
        }
        return 1;
    }
}

void pause_prompt(void) {
    printf("\nPress [Enter] to continue...");
    fflush(stdout);
    char buf[8];
    if (fgets(buf, sizeof(buf), stdin)) {
        if (!strchr(buf, '\n')) {
            discard_excess_input();
        }
    }
}

/* ========================================================================= */
/*                          STUDENT PORTAL LOGIC                             */
/* ========================================================================= */

static void handle_student_submit(ServiceDesk *desk) {
    char student_id[STUDENT_ID_LEN];
    char student_name[STUDENT_NAME_LEN];
    char category[CATEGORY_LEN];
    char description[DESCRIPTION_LEN];

    printf("\n------------------- SUBMIT A NEW HELP DESK TICKET -------------------\n");

    get_input_string("Enter Student ID (e.g. S10243): ", student_id, sizeof(student_id), 0);
    get_input_string("Enter Student Full Name       : ", student_name, sizeof(student_name), 0);

    /* Category selection menu */
    printf("\nSelect Issue Category:\n");
    printf("  [1] Academic Support\n");
    printf("  [2] IT & Campus WiFi\n");
    printf("  [3] Course Registration\n");
    printf("  [4] Hostel & Accommodation\n");
    printf("  [5] Financial & Billing\n");
    printf("  [6] Custom / Other\n");

    int cat_choice = 1;
    get_input_int("Choice (1-6): ", &cat_choice, 1, 6);

    switch (cat_choice) {
        case 1: strncpy(category, "Academic Support", sizeof(category)); break;
        case 2: strncpy(category, "IT & Campus WiFi", sizeof(category)); break;
        case 3: strncpy(category, "Course Registration", sizeof(category)); break;
        case 4: strncpy(category, "Hostel & Housing", sizeof(category)); break;
        case 5: strncpy(category, "Financial & Billing", sizeof(category)); break;
        case 6:
        default:
            get_input_string("Enter Custom Category: ", category, sizeof(category), 0);
            break;
    }

    get_input_string("Describe the issue in detail: ", description, sizeof(description), 0);

    Ticket created;
    if (desk_submit_ticket(desk, student_id, student_name, category, description, &created)) {
        int queue_pos = queue_size(&desk->pending_queue);
        printf("\n>>> TICKET SUBMITTED SUCCESSFULLY! <<<\n");
        ticket_print_card(&created, "PENDING", queue_pos);
        printf("Please take note of your Ticket ID #%d to check your status later.\n", created.id);
    } else {
        printf("\n[ERROR] Failed to submit ticket due to system memory allocation failure.\n");
    }

    pause_prompt();
}

static void handle_student_check_status(const ServiceDesk *desk) {
    int ticket_id = 0;
    printf("\n----------------------- CHECK TICKET STATUS -------------------------\n");
    get_input_int("Enter Ticket ID to query: ", &ticket_id, 1, 9999999);

    Ticket ticket;
    char status_str[64];
    if (desk_find_ticket(desk, ticket_id, &ticket, status_str, sizeof(status_str))) {
        printf("\n>>> TICKET RECORD FOUND <<<\n");
        int pos = 0;
        find_in_queue(&desk->pending_queue, ticket_id, NULL, &pos);
        ticket_print_card(&ticket, status_str, pos);
    } else {
        printf("\n[!] No ticket found with ID #%d.\n", ticket_id);
    }

    pause_prompt();
}

static void handle_student_view_all(const ServiceDesk *desk) {
    char student_id[STUDENT_ID_LEN];
    printf("\n--------------------- VIEW ALL STUDENT TICKETS ----------------------\n");
    get_input_string("Enter your Student ID: ", student_id, sizeof(student_id), 0);

    desk_print_student_tickets(desk, student_id);
    pause_prompt();
}

static void run_student_portal(ServiceDesk *desk) {
    int choice = -1;

    while (choice != 0) {
        printf("\n==================================================================\n");
        printf("                         STUDENT PORTAL                           \n");
        printf("==================================================================\n");
        printf("  [1] Submit a Help Request (Create Ticket)\n");
        printf("  [2] Check Ticket Status (by Ticket ID)\n");
        printf("  [3] View All My Tickets (by Student ID)\n");
        printf("  [0] Return to Main Menu\n");
        printf("------------------------------------------------------------------\n");

        if (!get_input_int("Select an option (0-3): ", &choice, 0, 3)) {
            break;
        }

        switch (choice) {
            case 1: handle_student_submit(desk); break;
            case 2: handle_student_check_status(desk); break;
            case 3: handle_student_view_all(desk); break;
            case 0:
                printf("\nReturning to Main Menu...\n");
                break;
        }
    }
}

/* ========================================================================= */
/*                           ADMIN PORTAL LOGIC                              */
/* ========================================================================= */

static void handle_admin_process_next(ServiceDesk *desk) {
    printf("\n----------------------- PROCESS NEXT TICKET -------------------------\n");
    if (is_queue_empty(&desk->pending_queue)) {
        printf("  [Notice] The pending queue is empty! No requests to process.\n");
        pause_prompt();
        return;
    }

    Ticket processed;
    if (desk_process_next(desk, &processed)) {
        printf("\n>>> TICKET PROCESSED SUCCESSFULLY <<<\n");
        printf("Dequeued from Pending FIFO Queue and pushed to Resolved LIFO Stack.\n");
        ticket_print_card(&processed, "STATUS: RESOLVED", 0);
    } else {
        printf("\n[ERROR] Failed to process ticket.\n");
    }

    pause_prompt();
}

static void handle_admin_undo(ServiceDesk *desk) {
    printf("\n--------------------- UNDO LAST RESOLUTION --------------------------\n");
    if (is_stack_empty(&desk->resolved_stack)) {
        printf("  [Notice] The resolution history stack is empty. Nothing to undo!\n");
        pause_prompt();
        return;
    }

    Ticket undone;
    if (desk_undo_resolution(desk, &undone)) {
        printf("\n>>> LAST RESOLUTION SUCCESSFULLY UNDONE <<<\n");
        printf("Popped from Resolved Stack and restored to head of Pending Queue.\n");
        ticket_print_card(&undone, "RESTORED: PENDING", 1);
    } else {
        printf("\n[ERROR] Failed to undo ticket resolution.\n");
    }

    pause_prompt();
}

static void handle_admin_search(const ServiceDesk *desk) {
    int ticket_id = 0;
    printf("\n----------------------- SEARCH TICKET BY ID -------------------------\n");
    get_input_int("Enter Ticket ID to search: ", &ticket_id, 1, 9999999);

    Ticket ticket;
    char status_str[64];
    if (desk_find_ticket(desk, ticket_id, &ticket, status_str, sizeof(status_str))) {
        int pos = 0;
        find_in_queue(&desk->pending_queue, ticket_id, NULL, &pos);
        ticket_print_card(&ticket, status_str, pos);
    } else {
        printf("\n[!] No ticket found with ID #%d.\n", ticket_id);
    }

    pause_prompt();
}

static void handle_admin_save(const ServiceDesk *desk) {
    char filename[128];
    printf("\n--------------------- SAVE SYSTEM STATE TO CSV ----------------------\n");
    printf("Default filename: [%s]\n", DEFAULT_CSV_FILE);
    get_input_string("Enter filename to save (or press Enter for default): ",
                     filename, sizeof(filename), 1);

    const char *target_file = (strlen(filename) > 0) ? filename : DEFAULT_CSV_FILE;

    if (desk_save_to_file(desk, target_file)) {
        printf("\n>>> System state successfully saved to '%s' <<<\n", target_file);
        printf("Saved %d pending tickets and %d resolved tickets.\n",
               queue_size(&desk->pending_queue),
               stack_count(&desk->resolved_stack));
    } else {
        printf("\n[ERROR] Failed to write data to file '%s'.\n", target_file);
    }

    pause_prompt();
}

static void handle_admin_load(ServiceDesk *desk) {
    char filename[128];
    printf("\n-------------------- LOAD SYSTEM STATE FROM CSV ---------------------\n");
    printf("Default filename: [%s]\n", DEFAULT_CSV_FILE);
    get_input_string("Enter filename to load (or press Enter for default): ",
                     filename, sizeof(filename), 1);

    const char *target_file = (strlen(filename) > 0) ? filename : DEFAULT_CSV_FILE;

    printf("\n[WARNING] Loading will replace current in-memory tickets!\n");
    int confirm = 0;
    get_input_int("Proceed with load? [1 = Yes, 0 = Cancel]: ", &confirm, 0, 1);
    if (!confirm) {
        printf("Operation cancelled.\n");
        pause_prompt();
        return;
    }

    if (desk_load_from_file(desk, target_file)) {
        printf("\n>>> Successfully loaded data from '%s' <<<\n", target_file);
        printf("Loaded %d pending tickets and %d resolved tickets.\n",
               queue_size(&desk->pending_queue),
               stack_count(&desk->resolved_stack));
    } else {
        printf("\n[ERROR] Failed to read or open file '%s'.\n", target_file);
    }

    pause_prompt();
}

static void run_admin_portal(ServiceDesk *desk) {
    int choice = -1;

    while (choice != 0) {
        printf("\n==================================================================\n");
        printf("                          ADMIN PORTAL                            \n");
        printf("  [Pending Queue: %2d tickets] | [Resolved Stack: %2d tickets]      \n",
               queue_size(&desk->pending_queue),
               stack_count(&desk->resolved_stack));
        printf("==================================================================\n");
        printf("  [1] View Pending Queue (FIFO Order)\n");
        printf("  [2] Process Next Ticket (Dequeue -> Push to Resolved Stack)\n");
        printf("  [3] Undo Last Resolution (Pop Resolved Stack -> Re-enqueue)\n");
        printf("  [4] View Resolution History Stack (LIFO Order)\n");
        printf("  [5] Search Ticket Details (by Ticket ID)\n");
        printf("  [6] Save System State to CSV File\n");
        printf("  [7] Load System State from CSV File\n");
        printf("  [0] Return to Main Menu\n");
        printf("------------------------------------------------------------------\n");

        if (!get_input_int("Select an option (0-7): ", &choice, 0, 7)) {
            break;
        }

        switch (choice) {
            case 1:
                print_queue(&desk->pending_queue);
                pause_prompt();
                break;
            case 2:
                handle_admin_process_next(desk);
                break;
            case 3:
                handle_admin_undo(desk);
                break;
            case 4:
                print_stack(&desk->resolved_stack);
                pause_prompt();
                break;
            case 5:
                handle_admin_search(desk);
                break;
            case 6:
                handle_admin_save(desk);
                break;
            case 7:
                handle_admin_load(desk);
                break;
            case 0:
                printf("\nReturning to Main Menu...\n");
                break;
        }
    }
}

/* ========================================================================= */
/*                          MAIN APPLICATION LOOP                            */
/* ========================================================================= */

void cli_run(ServiceDesk *desk) {
    int main_choice = -1;

    while (main_choice != 0) {
        printf("\n==================================================================\n");
        printf("               STUDENT HELP DESK MANAGEMENT SYSTEM                \n");
        printf("        Powered by Dynamic Queue (FIFO) & Dynamic Stack (LIFO)    \n");
        printf("==================================================================\n");
        printf("  [1] Student Portal (Submit Request, Check Ticket Status)\n");
        printf("  [2] Admin Portal   (Queue & History, Process, Undo, Disk I/O)\n");
        printf("  [0] Exit Application\n");
        printf("------------------------------------------------------------------\n");

        if (!get_input_int("Select Portal (0-2): ", &main_choice, 0, 2)) {
            break;
        }

        switch (main_choice) {
            case 1:
                run_student_portal(desk);
                break;
            case 2:
                run_admin_portal(desk);
                break;
            case 0:
                printf("\nThank you for using the Student Help Desk System. Goodbye!\n\n");
                break;
        }
    }
}
