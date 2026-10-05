#include <stdio.h>
#include <stdlib.h>
#include "desk_manager.h"
#include "cli.h"

int main(int argc, char *argv[]) {
    ServiceDesk desk;
    desk_init(&desk);

    /* If a CSV file argument is passed, attempt to load it on startup */
    if (argc > 1) {
        printf("[Startup] Loading tickets from '%s'...\n", argv[1]);
        if (desk_load_from_file(&desk, argv[1])) {
            printf("[Startup] Successfully loaded initial state from '%s'.\n", argv[1]);
        } else {
            printf("[Startup] Could not load '%s'. Starting with empty desk.\n", argv[1]);
        }
    }

    /* Run interactive CLI menu loop */
    cli_run(&desk);

    /* Graceful cleanup: free all dynamically allocated queue and stack nodes */
    desk_cleanup(&desk);

    return EXIT_SUCCESS;
}
