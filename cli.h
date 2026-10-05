#ifndef CLI_H
#define CLI_H

#include "desk_manager.h"

/* Starts the interactive CLI application loop */
void cli_run(ServiceDesk *desk);

/* Robust input helpers */
void clean_newline(char *str);
int  get_input_string(const char *prompt, char *buffer, size_t size, int allow_empty);
int  get_input_int(const char *prompt, int *out_val, int min, int max);
void pause_prompt(void);

#endif /* CLI_H */
