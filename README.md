# Student Help Desk Management System (C99)

A complete, high-performance, self-contained **Student Help Desk Management System** implemented in standard ANSI C (C99) with an interactive Command Line Interface (CLI).

---

## 🏗️ Architecture & Data Structures

The system is designed around fundamental Data Structures & Algorithms principles:

1. **FIFO Queue (Pending Requests)**:
   - **Data Structure**: Singly-linked list with head (`front`) and tail (`rear`) pointers.
   - **Time Complexity**:
     - Enqueue: $\mathcal{O}(1)$
     - Dequeue: $\mathcal{O}(1)$
     - Peek: $\mathcal{O}(1)$
   - **Purpose**: Ensures fair, first-come-first-served processing of incoming student help requests.

2. **LIFO Stack (Resolution History & Undo)**:
   - **Data Structure**: Singly-linked list with a `top` pointer.
   - **Time Complexity**:
     - Push: $\mathcal{O}(1)$
     - Pop: $\mathcal{O}(1)$
     - Peek: $\mathcal{O}(1)$
   - **Purpose**: Tracks recently resolved tickets in reverse chronological order and enables **instant undo operations** if an administrator resolves a ticket by mistake.

3. **Service Desk Manager**:
   - Encapsulates the Pending Queue, Resolved Stack, and auto-incrementing Ticket ID generator.
   - Provides CSV disk persistence (`helpdesk_data.csv`) that preserves exact Queue and Stack ordering across application restarts.

---

## 📁 Source Code Structure

| File | Description |
|---|---|
| [`ticket.h`](file:///c:/Users/DELL/DSA/ticket.h) | Ticket data structure definition and formatting prototypes. |
| [`ticket.c`](file:///c:/Users/DELL/DSA/ticket.c) | Ticket initialization, visual card layout, and compact table printer. |
| [`queue.h`](file:///c:/Users/DELL/DSA/queue.h) | Dynamic Queue header (FIFO). |
| [`queue.c`](file:///c:/Users/DELL/DSA/queue.c) | Linked-list implementation of Queue (`init_queue`, `enqueue`, `dequeue`, `is_queue_empty`, `print_queue`, `free_queue`). |
| [`stack.h`](file:///c:/Users/DELL/DSA/stack.h) | Dynamic Stack header (LIFO). |
| [`stack.c`](file:///c:/Users/DELL/DSA/stack.c) | Linked-list implementation of Stack (`init_stack`, `push`, `pop`, `peek`, `is_stack_empty`, `print_stack`, `free_stack`). |
| [`desk_manager.h`](file:///c:/Users/DELL/DSA/desk_manager.h) | ServiceDesk coordinator and disk I/O interface. |
| [`desk_manager.c`](file:///c:/Users/DELL/DSA/desk_manager.c) | Business logic for ticket submission, resolution processing, undo, query, and CSV persistence. |
| [`cli.h`](file:///c:/Users/DELL/DSA/cli.h) | Interactive CLI menu and input sanitization prototypes. |
| [`cli.c`](file:///c:/Users/DELL/DSA/cli.c) | Multi-portal CLI loop (Student Portal & Admin Portal) with buffer overflow protection. |
| [`main.c`](file:///c:/Users/DELL/DSA/main.c) | Program entry point and graceful memory teardown. |
| [`Makefile`](file:///c:/Users/DELL/DSA/Makefile) | Cross-platform build script. |
| [`sample_helpdesk_data.csv`](file:///c:/Users/DELL/DSA/sample_helpdesk_data.csv) | Sample initial dataset for demonstration and testing. |

---

## ⚙️ Compilation & Execution

### 1. Using GCC (Standard command)
```bash
gcc -std=c99 -Wall -Wextra -pedantic -O2 *.c -o helpdesk
./helpdesk
```

On Windows (Command Prompt or PowerShell):
```cmd
gcc -std=c99 -Wall -Wextra -pedantic -O2 *.c -o helpdesk.exe
.\helpdesk.exe
```

### 2. Using Make
```bash
make
./helpdesk
```

To clean up build artifacts:
```bash
make clean
```

### 3. Loading with Existing CSV Data
You can pass a CSV file directly as an argument:
```bash
./helpdesk sample_helpdesk_data.csv
```

---

## 🖥️ Portals & Features

### [1] Student Portal
- **Submit a Help Request**:
  - Automatically captures Student ID, Student Name, Issue Category, and Description.
  - Automatically assigns an auto-incrementing Ticket ID and local timestamp.
  - Enqueues into the FIFO queue and displays the student's queue position.
- **Check Ticket Status**:
  - Lookup by Ticket ID to see whether the request is `PENDING` (with current position in queue) or `RESOLVED`.
- **View All My Tickets**:
  - Enter Student ID to display all past and current tickets filed by the student.

### [2] Admin Portal
- **View Pending Queue (FIFO)**:
  - Tabular view of all pending requests in exact arrival sequence.
- **Process Next Ticket**:
  - Dequeues the ticket at the head of the queue and pushes it onto the resolution history stack.
- **Undo Last Resolution**:
  - Pops the most recently resolved ticket from the stack and re-enqueues it back to the **front** of the pending queue, restoring immediate priority.
- **View Resolution History Stack (LIFO)**:
  - Displays all processed tickets in reverse chronological order (most recently resolved at the top).
- **Search Ticket by ID**:
  - Fast search across both pending queue and resolved history.
- **Save System State to CSV**:
  - Persists all queues and stacks into a CSV file.
- **Load System State from CSV**:
  - Reconstructs pending queue and resolved stack from disk while maintaining ID continuity.

---

## 🛡️ Robust Input Handling & Memory Safety
- **No `scanf("%d")` Pitfalls**: Uses `fgets` followed by `strtol` / `sscanf` to prevent infinite loops on invalid input.
- **Buffer Overflow Protection**: All input functions enforce strict buffer bounds and discard trailing excess characters.
- **Zero Memory Leaks**: All dynamically allocated queue nodes (`QueueNode`) and stack nodes (`StackNode`) are freed upon ticket dequeuing/popping, system state resets, and application shutdown.
