#!/usr/bin/env python3
"""
Student Help Desk Management System - Reference Python Runner
Matches the C99 Linked-List Dynamic Queue & Dynamic Stack Implementation.
Can be executed immediately in environments without a C compiler:
    python helpdesk.py [optional_data.csv]
"""

import sys
import os
import csv
from datetime import datetime

# =========================================================================
#                          1. TICKET ENTITY
# =========================================================================

class Ticket:
    def __init__(self, ticket_id, student_id, student_name, category, description, timestamp=None):
        self.id = int(ticket_id)
        self.student_id = str(student_id)
        self.student_name = str(student_name)
        self.category = str(category)
        self.description = str(description)
        self.timestamp = timestamp if timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def print_card(self, status_label="", position=0):
        pos_str = f"[Pos: {position:2d}] |" if position > 0 else "           |"
        print("+------------------------------------------------------------------------------+")
        print(f"| TICKET #{self.id:<6d} {status_label:<40s} {pos_str}")
        print("+------------------------------------------------------------------------------+")
        print(f"| Student ID   : {self.student_id:<61s} |")
        print(f"| Student Name : {self.student_name:<61s} |")
        print(f"| Category     : {self.category:<61s} |")
        print(f"| Submitted At : {self.timestamp:<61s} |")
        
        # Multi-line word-wrapped description
        desc = self.description
        if len(desc) <= 61:
            print(f"| Description  : {desc:<61s} |")
        else:
            print(f"| Description  : {desc[:61]:<61s} |")
            offset = 61
            while offset < len(desc):
                chunk = desc[offset:offset+61]
                print(f"|                {chunk:<61s} |")
                offset += 61
        print("+------------------------------------------------------------------------------+")

    def print_compact(self, index):
        print(f"| {index:4d} | #{self.id:<5d} | {self.student_id:<10s} | {self.student_name:<16.16s} | {self.category:<12.12s} | {self.timestamp:<20s} |")

# =========================================================================
#                 2. DYNAMIC QUEUE (LINKED LIST - FIFO)
# =========================================================================

class QueueNode:
    def __init__(self, ticket):
        self.ticket = ticket
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self.size = 0

    def is_empty(self):
        return self.front is None

    def enqueue(self, ticket):
        node = QueueNode(ticket)
        if self.rear is None:
            self.front = node
            self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def enqueue_front(self, ticket):
        node = QueueNode(ticket)
        node.next = self.front
        self.front = node
        if self.rear is None:
            self.rear = node
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            return None
        temp = self.front
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self.size -= 1
        return temp.ticket

    def print_queue(self):
        if self.is_empty():
            print("\n  [Empty: No pending tickets in queue]\n")
            return
        print("\n============================= PENDING TICKETS QUEUE (FIFO) =============================")
        print("+------+--------+------------+------------------+--------------+----------------------+")
        print("| Pos  | Ticket | Student ID | Student Name     | Category     | Submitted At         |")
        print("+------+--------+------------+------------------+--------------+----------------------+")
        curr = self.front
        pos = 1
        while curr:
            curr.ticket.print_compact(pos)
            curr = curr.next
            pos += 1
        print("+------+--------+------------+------------------+--------------+----------------------+")
        print(f"  Total Pending Tickets in Queue: {self.size}\n")

    def find(self, ticket_id):
        curr = self.front
        pos = 1
        while curr:
            if curr.ticket.id == ticket_id:
                return curr.ticket, pos
            curr = curr.next
            pos += 1
        return None, 0

    def clear(self):
        self.front = None
        self.rear = None
        self.size = 0

# =========================================================================
#                 3. DYNAMIC STACK (LINKED LIST - LIFO)
# =========================================================================

class StackNode:
    def __init__(self, ticket):
        self.ticket = ticket
        self.next = None

class Stack:
    def __init__(self):
        self.top = None
        self.count = 0

    def is_empty(self):
        return self.top is None

    def push(self, ticket):
        node = StackNode(ticket)
        node.next = self.top
        self.top = node
        self.count += 1

    def pop(self):
        if self.is_empty():
            return None
        temp = self.top
        self.top = self.top.next
        self.count -= 1
        return temp.ticket

    def peek(self):
        return self.top.ticket if self.top else None

    def print_stack(self):
        if self.is_empty():
            print("\n  [Empty: No resolved tickets in history]\n")
            return
        print("\n======================== RESOLUTION HISTORY STACK (LIFO) ========================")
        print("+------+--------+------------+------------------+--------------+----------------------+")
        print("| Item | Ticket | Student ID | Student Name     | Category     | Resolved Timestamp   |")
        print("+------+--------+------------+------------------+--------------+----------------------+")
        curr = self.top
        idx = 1
        while curr:
            curr.ticket.print_compact(idx)
            curr = curr.next
            idx += 1
        print("+------+--------+------------+------------------+--------------+----------------------+")
        print(f"  Total Resolved Tickets in History (Top = Most Recent): {self.count}\n")

    def find(self, ticket_id):
        curr = self.top
        while curr:
            if curr.ticket.id == ticket_id:
                return curr.ticket
            curr = curr.next
        return None

    def clear(self):
        self.top = None
        self.count = 0

# =========================================================================
#                     4. SERVICE DESK COORDINATOR
# =========================================================================

class ServiceDesk:
    DEFAULT_CSV = "helpdesk_data.csv"

    def __init__(self):
        self.pending_queue = Queue()
        self.resolved_stack = Stack()
        self.next_ticket_id = 1001

    def submit_ticket(self, student_id, student_name, category, description):
        tid = self.next_ticket_id
        self.next_ticket_id += 1
        t = Ticket(tid, student_id, student_name, category, description)
        self.pending_queue.enqueue(t)
        return t

    def process_next(self):
        t = self.pending_queue.dequeue()
        if t:
            self.resolved_stack.push(t)
        return t

    def undo_resolution(self):
        t = self.resolved_stack.pop()
        if t:
            self.pending_queue.enqueue_front(t)
        return t

    def find_ticket(self, ticket_id):
        t, pos = self.pending_queue.find(ticket_id)
        if t:
            return t, f"PENDING (Queue Position: {pos})", pos
        t = self.resolved_stack.find(ticket_id)
        if t:
            return t, "RESOLVED (In History)", 0
        return None, None, 0

    def print_student_tickets(self, student_id):
        print(f"\n======================== TICKETS FOR STUDENT ID: {student_id:<12s} ========================")
        total, pending_count, resolved_count = 0, 0, 0
        
        curr = self.pending_queue.front
        pos = 1
        while curr:
            if curr.ticket.student_id == student_id:
                curr.ticket.print_card(f"PENDING [Queue Pos: {pos}]", pos)
                pending_count += 1
                total += 1
            curr = curr.next
            pos += 1

        curr = self.resolved_stack.top
        while curr:
            if curr.ticket.student_id == student_id:
                curr.ticket.print_card("RESOLVED", 0)
                resolved_count += 1
                total += 1
            curr = curr.next

        if total == 0:
            print(f"  No tickets found for student ID '{student_id}'.")
        else:
            print(f"  Summary: {total} Total ({pending_count} Pending, {resolved_count} Resolved)")
        print("=================================================================================\n")

    def save_to_file(self, filename):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "ID", "StudentID", "StudentName", "Category", "Description", "Timestamp"])
            
            # 1. Pending Queue (front to rear)
            curr = self.pending_queue.front
            while curr:
                t = curr.ticket
                writer.writerow(["PENDING", t.id, t.student_id, t.student_name, t.category, t.description, t.timestamp])
                curr = curr.next

            # 2. Resolved Stack (bottom to top so reload preserves exact order)
            arr = []
            curr = self.resolved_stack.top
            while curr:
                arr.append(curr.ticket)
                curr = curr.next
            for t in reversed(arr):
                writer.writerow(["RESOLVED", t.id, t.student_id, t.student_name, t.category, t.description, t.timestamp])
        return True

    def load_from_file(self, filename):
        if not os.path.exists(filename):
            return False
        self.pending_queue.clear()
        self.resolved_stack.clear()
        max_id = 1000

        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) < 7:
                    continue
                req_type, tid, sid, sname, cat, desc, tstamp = row[:7]
                t = Ticket(tid, sid, sname, cat, desc, tstamp)
                if req_type == "PENDING":
                    self.pending_queue.enqueue(t)
                elif req_type == "RESOLVED":
                    self.resolved_stack.push(t)
                if t.id > max_id:
                    max_id = t.id
        self.next_ticket_id = max_id + 1
        return True

# =========================================================================
#                       5. CLI MENU INTERACTION
# =========================================================================

def get_int(prompt, min_val, max_val):
    while True:
        val_str = input(prompt).strip()
        try:
            val = int(val_str)
            if min_val <= val <= max_val:
                return val
            print(f"  [!] Selection out of range ({min_val} to {max_val}).")
        except ValueError:
            print("  [!] Please enter numbers only.")

def pause():
    input("\nPress [Enter] to continue...")

def student_portal(desk):
    while True:
        print("\n==================================================================")
        print("                         STUDENT PORTAL                           ")
        print("==================================================================")
        print("  [1] Submit a Help Request (Create Ticket)")
        print("  [2] Check Ticket Status (by Ticket ID)")
        print("  [3] View All My Tickets (by Student ID)")
        print("  [0] Return to Main Menu")
        print("------------------------------------------------------------------")
        choice = get_int("Select an option (0-3): ", 0, 3)
        if choice == 0:
            break
        elif choice == 1:
            print("\n------------------- SUBMIT A NEW HELP DESK TICKET -------------------")
            sid = input("Enter Student ID (e.g. S10243): ").strip()
            sname = input("Enter Student Full Name       : ").strip()
            print("\nSelect Issue Category:")
            print("  [1] Academic Support\n  [2] IT & Campus WiFi\n  [3] Course Registration\n  [4] Hostel & Accommodation\n  [5] Financial & Billing\n  [6] Custom / Other")
            cat_choice = get_int("Choice (1-6): ", 1, 6)
            categories = {
                1: "Academic Support", 2: "IT & Campus WiFi",
                3: "Course Registration", 4: "Hostel & Housing",
                5: "Financial & Billing"
            }
            cat = categories.get(cat_choice) or input("Enter Custom Category: ").strip()
            desc = input("Describe the issue in detail: ").strip()
            created = desk.submit_ticket(sid, sname, cat, desc)
            print("\n>>> TICKET SUBMITTED SUCCESSFULLY! <<<")
            created.print_card("PENDING", desk.pending_queue.size)
            print(f"Please take note of your Ticket ID #{created.id} to check your status later.")
            pause()
        elif choice == 2:
            print("\n----------------------- CHECK TICKET STATUS -------------------------")
            tid = get_int("Enter Ticket ID to query: ", 1, 9999999)
            t, status, pos = desk.find_ticket(tid)
            if t:
                print("\n>>> TICKET RECORD FOUND <<<")
                t.print_card(status, pos)
            else:
                print(f"\n[!] No ticket found with ID #{tid}.")
            pause()
        elif choice == 3:
            print("\n--------------------- VIEW ALL STUDENT TICKETS ----------------------")
            sid = input("Enter your Student ID: ").strip()
            desk.print_student_tickets(sid)
            pause()

def admin_portal(desk):
    while True:
        print("\n==================================================================")
        print("                          ADMIN PORTAL                            ")
        print(f"  [Pending Queue: {desk.pending_queue.size:2d} tickets] | [Resolved Stack: {desk.resolved_stack.count:2d} tickets]")
        print("==================================================================")
        print("  [1] View Pending Queue (FIFO Order)")
        print("  [2] Process Next Ticket (Dequeue -> Push to Resolved Stack)")
        print("  [3] Undo Last Resolution (Pop Resolved Stack -> Re-enqueue)")
        print("  [4] View Resolution History Stack (LIFO Order)")
        print("  [5] Search Ticket Details (by Ticket ID)")
        print("  [6] Save System State to CSV File")
        print("  [7] Load System State from CSV File")
        print("  [0] Return to Main Menu")
        print("------------------------------------------------------------------")
        choice = get_int("Select an option (0-7): ", 0, 7)
        if choice == 0:
            break
        elif choice == 1:
            desk.pending_queue.print_queue()
            pause()
        elif choice == 2:
            print("\n----------------------- PROCESS NEXT TICKET -------------------------")
            t = desk.process_next()
            if t:
                print("\n>>> TICKET PROCESSED SUCCESSFULLY <<<")
                print("Dequeued from Pending FIFO Queue and pushed to Resolved LIFO Stack.")
                t.print_card("STATUS: RESOLVED", 0)
            else:
                print("  [Notice] The pending queue is empty! No requests to process.")
            pause()
        elif choice == 3:
            print("\n--------------------- UNDO LAST RESOLUTION --------------------------")
            t = desk.undo_resolution()
            if t:
                print("\n>>> LAST RESOLUTION SUCCESSFULLY UNDONE <<<")
                print("Popped from Resolved Stack and restored to head of Pending Queue.")
                t.print_card("RESTORED: PENDING", 1)
            else:
                print("  [Notice] The resolution history stack is empty. Nothing to undo!")
            pause()
        elif choice == 4:
            desk.resolved_stack.print_stack()
            pause()
        elif choice == 5:
            tid = get_int("Enter Ticket ID to search: ", 1, 9999999)
            t, status, pos = desk.find_ticket(tid)
            if t:
                t.print_card(status, pos)
            else:
                print(f"\n[!] No ticket found with ID #{tid}.")
            pause()
        elif choice == 6:
            fname = input(f"Enter filename to save [{desk.DEFAULT_CSV}]: ").strip() or desk.DEFAULT_CSV
            desk.save_to_file(fname)
            print(f"\n>>> System state successfully saved to '{fname}' <<<")
            pause()
        elif choice == 7:
            fname = input(f"Enter filename to load [{desk.DEFAULT_CSV}]: ").strip() or desk.DEFAULT_CSV
            if desk.load_from_file(fname):
                print(f"\n>>> Successfully loaded data from '{fname}' <<<")
            else:
                print(f"\n[ERROR] Failed to load '{fname}'.")
            pause()

def main():
    desk = ServiceDesk()
    if len(sys.argv) > 1:
        if desk.load_from_file(sys.argv[1]):
            print(f"[Startup] Loaded initial state from '{sys.argv[1]}'.")
    elif os.path.exists("sample_helpdesk_data.csv"):
        desk.load_from_file("sample_helpdesk_data.csv")

    while True:
        print("\n==================================================================")
        print("               STUDENT HELP DESK MANAGEMENT SYSTEM                ")
        print("        Powered by Dynamic Queue (FIFO) & Dynamic Stack (LIFO)    ")
        print("==================================================================")
        print("  [1] Student Portal (Submit Request, Check Ticket Status)")
        print("  [2] Admin Portal   (Queue & History, Process, Undo, Disk I/O)")
        print("  [0] Exit Application")
        print("------------------------------------------------------------------")
        choice = get_int("Select Portal (0-2): ", 0, 2)
        if choice == 1:
            student_portal(desk)
        elif choice == 2:
            admin_portal(desk)
        elif choice == 0:
            print("\nThank you for using the Student Help Desk System. Goodbye!\n")
            break

if __name__ == "__main__":
    main()
