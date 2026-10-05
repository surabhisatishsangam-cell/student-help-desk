#!/usr/bin/env python3
"""
Student Help Desk Management System - Graphical User Interface (Tkinter)
Provides an interactive GUI with buttons, forms, and live queue/stack visualizations
replacing the terminal interface.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# Import core DSA structures from existing helpdesk.py
import helpdesk
from helpdesk import Ticket, Queue, Stack, ServiceDesk


class HelpDeskGUI:
    """
    Tkinter Graphical Frontend for the Student Help Desk System.
    Visualizes the FIFO Pending Queue and LIFO Resolution Stack with button-driven controls.
    """
    
    CATEGORIES = [
        "Academic Support",
        "IT & Campus WiFi",
        "Course Registration",
        "Hostel & Housing",
        "Financial & Billing",
        "Custom / Other"
    ]

    def __init__(self, root, initial_csv=None):
        self.root = root
        self.root.title("Student Help Desk Management System (DSA - Queue & Stack)")
        self.root.geometry("1100x750")
        self.root.minsize(920, 620)

        # Initialize the DSA ServiceDesk backend
        self.desk = ServiceDesk()
        self.current_csv_file = "helpdesk_data.csv"

        # Load initial data if available
        if initial_csv and os.path.exists(initial_csv):
            self.desk.load_from_file(initial_csv)
            self.current_csv_file = initial_csv
        elif os.path.exists("sample_helpdesk_data.csv"):
            self.desk.load_from_file("sample_helpdesk_data.csv")
            self.current_csv_file = "sample_helpdesk_data.csv"
        elif os.path.exists("helpdesk_data.csv"):
            self.desk.load_from_file("helpdesk_data.csv")
            self.current_csv_file = "helpdesk_data.csv"

        # Setup styling and widgets
        self._setup_styles()
        self._build_ui()
        self.refresh_all()

    def _setup_styles(self):
        """Configure ttk theme and clean styles for buttons, tables, and frames."""
        self.style = ttk.Style()
        
        # Use clam theme for cross-platform color customization
        available_themes = self.style.theme_names()
        if "clam" in available_themes:
            self.style.theme_use("clam")

        # Color Palette
        self.COLOR_BG = "#F1F5F9"         # Slate 100
        self.COLOR_PANEL = "#FFFFFF"      # White
        self.COLOR_PRIMARY = "#2563EB"    # Blue 600
        self.COLOR_PRIMARY_HOVER = "#1D4ED8"
        self.COLOR_SUCCESS = "#16A34A"    # Green 600
        self.COLOR_WARNING = "#D97706"    # Amber 600
        self.COLOR_DANGER = "#DC2626"     # Red 600
        self.COLOR_TEXT = "#0F172A"       # Slate 900
        self.COLOR_MUTED = "#64748B"      # Slate 500
        self.COLOR_BORDER = "#CBD5E1"     # Slate 300

        self.root.configure(bg=self.COLOR_BG)

        # Standard Ttk styles
        self.style.configure(".", background=self.COLOR_BG, foreground=self.COLOR_TEXT, font=("Segoe UI", 10))
        self.style.configure("TFrame", background=self.COLOR_BG)
        self.style.configure("Card.TFrame", background=self.COLOR_PANEL, relief="flat")
        self.style.configure("White.TFrame", background=self.COLOR_PANEL)
        
        # Notebook styles
        self.style.configure("TNotebook", background=self.COLOR_BG, borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[16, 8], background="#E2E8F0")
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.COLOR_PANEL)],
                       foreground=[("selected", self.COLOR_PRIMARY)])

        # Label styles
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#1E293B", foreground="#FFFFFF")
        self.style.configure("HeaderSub.TLabel", font=("Segoe UI", 9), background="#1E293B", foreground="#94A3B8")
        self.style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), background=self.COLOR_PANEL, foreground=self.COLOR_TEXT)
        self.style.configure("Muted.TLabel", font=("Segoe UI", 9), foreground=self.COLOR_MUTED, background=self.COLOR_PANEL)
        self.style.configure("Badge.TLabel", font=("Segoe UI", 10, "bold"), padding=[8, 4])

        # Treeview (Tables)
        self.style.configure("Treeview",
                             font=("Segoe UI", 9),
                             rowheight=26,
                             background=self.COLOR_PANEL,
                             fieldbackground=self.COLOR_PANEL,
                             foreground=self.COLOR_TEXT,
                             borderwidth=1)
        self.style.configure("Treeview.Heading",
                             font=("Segoe UI", 9, "bold"),
                             background="#E2E8F0",
                             foreground=self.COLOR_TEXT,
                             relief="flat")
        self.style.map("Treeview",
                       background=[("selected", "#DBEAFE")],
                       foreground=[("selected", "#1E3A8A")])

        # Button Styles
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=[10, 6], borderwidth=1)
        
        # Action Buttons
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=self.COLOR_PRIMARY, foreground="#FFFFFF")
        self.style.map("Primary.TButton", background=[("active", self.COLOR_PRIMARY_HOVER)])

        self.style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), background=self.COLOR_SUCCESS, foreground="#FFFFFF")
        self.style.map("Success.TButton", background=[("active", "#15803D")])

        self.style.configure("Warning.TButton", font=("Segoe UI", 10, "bold"), background=self.COLOR_WARNING, foreground="#FFFFFF")
        self.style.map("Warning.TButton", background=[("active", "#B45309")])

    def _build_ui(self):
        """Construct the top header, tabbed portals, and bottom status bar."""
        # 1. Top Header Banner
        self._build_header()

        # 2. Main Tabbed Notebook (Admin Dashboard & Student Portal)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # Tab 1: Admin & Queues Dashboard
        self.tab_admin = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_admin, text="  🖥️  Admin Dashboard & Live Queues  ")
        self._build_admin_tab(self.tab_admin)

        # Tab 2: Student Portal
        self.tab_student = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_student, text="  🎓  Student Portal  ")
        self._build_student_tab(self.tab_student)

        # 3. Bottom Status Bar
        self._build_status_bar()

    def _build_header(self):
        """Top banner with system branding and real-time DSA metric counters."""
        header_frame = tk.Frame(self.root, bg="#1E293B", height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        # Left title info
        title_box = tk.Frame(header_frame, bg="#1E293B")
        title_box.pack(side=tk.LEFT, padx=16, pady=10)

        title_lbl = ttk.Label(title_box, text="🎓 Student Help Desk Management System", style="Header.TLabel")
        title_lbl.pack(anchor="w")

        sub_lbl = ttk.Label(title_box, text="Core DSA Implementation: Dynamic FIFO Queue (Pending) & Dynamic LIFO Stack (Resolved)", style="HeaderSub.TLabel")
        sub_lbl.pack(anchor="w")

        # Right KPI metric badges
        kpi_box = tk.Frame(header_frame, bg="#1E293B")
        kpi_box.pack(side=tk.RIGHT, padx=16, pady=10)

        self.lbl_kpi_pending = tk.Label(kpi_box, text="⏳ Pending: 0", font=("Segoe UI", 10, "bold"),
                                        bg="#FEF3C7", fg="#92400E", padx=10, pady=4, relief="flat", bd=0)
        self.lbl_kpi_pending.pack(side=tk.LEFT, padx=5)

        self.lbl_kpi_resolved = tk.Label(kpi_box, text="✅ Resolved: 0", font=("Segoe UI", 10, "bold"),
                                         bg="#DCFCE7", fg="#166534", padx=10, pady=4, relief="flat", bd=0)
        self.lbl_kpi_resolved.pack(side=tk.LEFT, padx=5)

        self.lbl_kpi_next_id = tk.Label(kpi_box, text="🏷️ Next ID: #1001", font=("Segoe UI", 10, "bold"),
                                        bg="#E0E7FF", fg="#3730A3", padx=10, pady=4, relief="flat", bd=0)
        self.lbl_kpi_next_id.pack(side=tk.LEFT, padx=5)

    def _build_status_bar(self):
        """Bottom status bar displaying feedback messages and active file name."""
        status_bar = tk.Frame(self.root, bg="#CBD5E1", height=24)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Ready. System loaded.")
        status_label = tk.Label(status_bar, textvariable=self.status_var, font=("Segoe UI", 9),
                                bg="#CBD5E1", fg="#334155", anchor="w")
        status_label.pack(side=tk.LEFT, padx=12, pady=2)

        self.file_status_var = tk.StringVar(value=f"Active File: {self.current_csv_file}")
        file_label = tk.Label(status_bar, textvariable=self.file_status_var, font=("Segoe UI", 9, "italic"),
                              bg="#CBD5E1", fg="#475569", anchor="e")
        file_label.pack(side=tk.RIGHT, padx=12, pady=2)

    # =========================================================================
    #                           ADMIN & QUEUES TAB
    # =========================================================================

    def _build_admin_tab(self, parent):
        """Build the button-driven Admin Dashboard with side-by-side Queue and Stack views."""
        # Top Action Button Toolbar
        toolbar = tk.Frame(parent, bg=self.COLOR_PANEL, relief="groove", bd=1)
        toolbar.pack(fill=tk.X, padx=4, pady=(4, 8), ipady=6)

        btn_process = tk.Button(toolbar, text="▶  Process Next Ticket (Dequeue FIFO)",
                                font=("Segoe UI", 10, "bold"), bg=self.COLOR_SUCCESS, fg="#FFFFFF",
                                activebackground="#15803D", activeforeground="#FFFFFF",
                                relief="flat", padx=12, pady=5, cursor="hand2",
                                command=self.on_process_next)
        btn_process.pack(side=tk.LEFT, padx=8)

        btn_undo = tk.Button(toolbar, text="↶  Undo Last Resolution (Pop LIFO)",
                             font=("Segoe UI", 10, "bold"), bg=self.COLOR_WARNING, fg="#FFFFFF",
                             activebackground="#B45309", activeforeground="#FFFFFF",
                             relief="flat", padx=12, pady=5, cursor="hand2",
                             command=self.on_undo_resolution)
        btn_undo.pack(side=tk.LEFT, padx=8)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, fill="y", padx=8, pady=4)

        btn_save = tk.Button(toolbar, text="💾  Save to CSV",
                             font=("Segoe UI", 9, "bold"), bg="#475569", fg="#FFFFFF",
                             activebackground="#334155", activeforeground="#FFFFFF",
                             relief="flat", padx=10, pady=5, cursor="hand2",
                             command=self.on_save_csv)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_load = tk.Button(toolbar, text="📂  Load CSV",
                             font=("Segoe UI", 9, "bold"), bg="#475569", fg="#FFFFFF",
                             activebackground="#334155", activeforeground="#FFFFFF",
                             relief="flat", padx=10, pady=5, cursor="hand2",
                             command=self.on_load_csv)
        btn_load.pack(side=tk.LEFT, padx=5)

        btn_refresh = tk.Button(toolbar, text="🔄  Refresh Tables",
                                font=("Segoe UI", 9), bg="#E2E8F0", fg=self.COLOR_TEXT,
                                activebackground="#CBD5E1",
                                relief="flat", padx=10, pady=5, cursor="hand2",
                                command=self.refresh_all)
        btn_refresh.pack(side=tk.LEFT, padx=5)

        btn_quick_new = tk.Button(toolbar, text="➕  New Ticket Form",
                                  font=("Segoe UI", 9, "bold"), bg=self.COLOR_PRIMARY, fg="#FFFFFF",
                                  activebackground=self.COLOR_PRIMARY_HOVER, activeforeground="#FFFFFF",
                                  relief="flat", padx=10, pady=5, cursor="hand2",
                                  command=lambda: self.notebook.select(self.tab_student))
        btn_quick_new.pack(side=tk.RIGHT, padx=8)

        # Main Paned Area: Split into Left (Queue), Right (Stack)
        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, bg=self.COLOR_BG, sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # LEFT PANE: Dynamic FIFO Queue
        left_frame = tk.Frame(paned, bg=self.COLOR_PANEL, relief="groove", bd=1)
        paned.add(left_frame, minsize=420)

        left_header = tk.Frame(left_frame, bg="#EFF6FF", relief="flat")
        left_header.pack(fill=tk.X, padx=1, pady=1)

        tk.Label(left_header, text="⏳  Pending Tickets Queue (FIFO)",
                 font=("Segoe UI", 11, "bold"), bg="#EFF6FF", fg="#1E40AF").pack(anchor="w", padx=10, pady=(6, 2))
        self.lbl_queue_sub = tk.Label(left_header, text="Head of queue is served first. Size: 0",
                                      font=("Segoe UI", 8), bg="#EFF6FF", fg="#64748B")
        self.lbl_queue_sub.pack(anchor="w", padx=10, pady=(0, 6))

        # Queue Treeview Table
        tree_q_frame = tk.Frame(left_frame, bg=self.COLOR_PANEL)
        tree_q_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        q_cols = ("pos", "id", "sid", "name", "cat", "time")
        self.tree_queue = ttk.Treeview(tree_q_frame, columns=q_cols, show="headings", selectmode="browse")
        self.tree_queue.heading("pos", text="Pos")
        self.tree_queue.heading("id", text="ID")
        self.tree_queue.heading("sid", text="Student ID")
        self.tree_queue.heading("name", text="Student Name")
        self.tree_queue.heading("cat", text="Category")
        self.tree_queue.heading("time", text="Submitted At")

        self.tree_queue.column("pos", width=42, anchor="center")
        self.tree_queue.column("id", width=55, anchor="center")
        self.tree_queue.column("sid", width=80, anchor="w")
        self.tree_queue.column("name", width=110, anchor="w")
        self.tree_queue.column("cat", width=120, anchor="w")
        self.tree_queue.column("time", width=125, anchor="w")

        q_scroll_y = ttk.Scrollbar(tree_q_frame, orient="vertical", command=self.tree_queue.yview)
        self.tree_queue.configure(yscrollcommand=q_scroll_y.set)

        self.tree_queue.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        q_scroll_y.pack(side=tk.RIGHT, fill="y")
        self.tree_queue.bind("<<TreeviewSelect>>", self._on_queue_item_select)

        # RIGHT PANE: Dynamic LIFO Stack
        right_frame = tk.Frame(paned, bg=self.COLOR_PANEL, relief="groove", bd=1)
        paned.add(right_frame, minsize=420)

        right_header = tk.Frame(right_frame, bg="#F0FDF4", relief="flat")
        right_header.pack(fill=tk.X, padx=1, pady=1)

        tk.Label(right_header, text="✅  Resolution History Stack (LIFO)",
                 font=("Segoe UI", 11, "bold"), bg="#F0FDF4", fg="#166534").pack(anchor="w", padx=10, pady=(6, 2))
        self.lbl_stack_sub = tk.Label(right_header, text="Top of stack can be undone. Count: 0",
                                      font=("Segoe UI", 8), bg="#F0FDF4", fg="#64748B")
        self.lbl_stack_sub.pack(anchor="w", padx=10, pady=(0, 6))

        # Stack Treeview Table
        tree_s_frame = tk.Frame(right_frame, bg=self.COLOR_PANEL)
        tree_s_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        s_cols = ("order", "id", "sid", "name", "cat", "time")
        self.tree_stack = ttk.Treeview(tree_s_frame, columns=s_cols, show="headings", selectmode="browse")
        self.tree_stack.heading("order", text="Order")
        self.tree_stack.heading("id", text="ID")
        self.tree_stack.heading("sid", text="Student ID")
        self.tree_stack.heading("name", text="Student Name")
        self.tree_stack.heading("cat", text="Category")
        self.tree_stack.heading("time", text="Resolved At")

        self.tree_stack.column("order", width=48, anchor="center")
        self.tree_stack.column("id", width=55, anchor="center")
        self.tree_stack.column("sid", width=80, anchor="w")
        self.tree_stack.column("name", width=110, anchor="w")
        self.tree_stack.column("cat", width=120, anchor="w")
        self.tree_stack.column("time", width=125, anchor="w")

        s_scroll_y = ttk.Scrollbar(tree_s_frame, orient="vertical", command=self.tree_stack.yview)
        self.tree_stack.configure(yscrollcommand=s_scroll_y.set)

        self.tree_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s_scroll_y.pack(side=tk.RIGHT, fill="y")
        self.tree_stack.bind("<<TreeviewSelect>>", self._on_stack_item_select)

        # BOTTOM INSPECTOR: Selected Ticket Details Card
        detail_frame = tk.Frame(parent, bg=self.COLOR_PANEL, relief="groove", bd=1)
        detail_frame.pack(fill=tk.X, padx=4, pady=(6, 2))

        d_head = tk.Frame(detail_frame, bg="#F8FAFC")
        d_head.pack(fill=tk.X, padx=2, pady=2)
        tk.Label(d_head, text="🔍  Selected Ticket Inspector", font=("Segoe UI", 10, "bold"),
                 bg="#F8FAFC", fg=self.COLOR_TEXT).pack(side=tk.LEFT, padx=10, pady=4)

        self.lbl_detail_status = tk.Label(d_head, text="Select any ticket above to view details",
                                          font=("Segoe UI", 9, "bold"), bg="#E2E8F0", fg="#475569", padx=8, pady=2)
        self.lbl_detail_status.pack(side=tk.RIGHT, padx=10, pady=4)

        body_grid = tk.Frame(detail_frame, bg=self.COLOR_PANEL)
        body_grid.pack(fill=tk.X, padx=12, pady=6)

        # Meta attributes
        self.var_det_id = tk.StringVar(value="--")
        self.var_det_sid = tk.StringVar(value="--")
        self.var_det_name = tk.StringVar(value="--")
        self.var_det_cat = tk.StringVar(value="--")
        self.var_det_time = tk.StringVar(value="--")

        tk.Label(body_grid, text="Ticket ID:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg="#475569").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        tk.Label(body_grid, textvariable=self.var_det_id, font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg=self.COLOR_PRIMARY).grid(row=0, column=1, sticky="w", padx=6, pady=2)

        tk.Label(body_grid, text="Student ID:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg="#475569").grid(row=0, column=2, sticky="w", padx=10, pady=2)
        tk.Label(body_grid, textvariable=self.var_det_sid, font=("Segoe UI", 9), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).grid(row=0, column=3, sticky="w", padx=6, pady=2)

        tk.Label(body_grid, text="Student Name:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg="#475569").grid(row=0, column=4, sticky="w", padx=10, pady=2)
        tk.Label(body_grid, textvariable=self.var_det_name, font=("Segoe UI", 9), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).grid(row=0, column=5, sticky="w", padx=6, pady=2)

        tk.Label(body_grid, text="Category:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg="#475569").grid(row=0, column=6, sticky="w", padx=10, pady=2)
        tk.Label(body_grid, textvariable=self.var_det_cat, font=("Segoe UI", 9), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).grid(row=0, column=7, sticky="w", padx=6, pady=2)

        tk.Label(body_grid, text="Timestamp:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg="#475569").grid(row=0, column=8, sticky="w", padx=10, pady=2)
        tk.Label(body_grid, textvariable=self.var_det_time, font=("Segoe UI", 9), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).grid(row=0, column=9, sticky="w", padx=6, pady=2)

        # Description view
        tk.Label(body_grid, text="Description:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg="#475569").grid(row=1, column=0, sticky="nw", padx=4, pady=4)
        self.txt_det_desc = tk.Text(body_grid, height=3, wrap="word", font=("Segoe UI", 9),
                                    bg="#F8FAFC", relief="solid", bd=1, padx=6, pady=4)
        self.txt_det_desc.grid(row=1, column=1, columnspan=9, sticky="ew", padx=6, pady=4)
        self.txt_det_desc.insert("1.0", "Click on any row in the Pending Queue or Resolution Stack above to inspect its contents.")
        self.txt_det_desc.configure(state="disabled")

    # =========================================================================
    #                           STUDENT PORTAL TAB
    # =========================================================================

    def _build_student_tab(self, parent):
        """Build the Student Portal with Ticket Submission and Status / History queries."""
        paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, bg=self.COLOR_BG, sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # LEFT COLUMN: Submit a Help Request
        submit_card = tk.Frame(paned, bg=self.COLOR_PANEL, relief="groove", bd=1)
        paned.add(submit_card, minsize=420)

        header_sub = tk.Frame(submit_card, bg="#EFF6FF")
        header_sub.pack(fill=tk.X, padx=1, pady=1)
        tk.Label(header_sub, text="📝  Submit a New Help Request", font=("Segoe UI", 12, "bold"),
                 bg="#EFF6FF", fg="#1E40AF").pack(anchor="w", padx=12, pady=(8, 2))
        tk.Label(header_sub, text="Your ticket will be enqueued into the FIFO Pending Queue.",
                 font=("Segoe UI", 9), bg="#EFF6FF", fg="#64748B").pack(anchor="w", padx=12, pady=(0, 8))

        form = tk.Frame(submit_card, bg=self.COLOR_PANEL)
        form.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Student ID
        tk.Label(form, text="Student ID *", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL).pack(anchor="w", pady=(4, 2))
        self.entry_stu_id = ttk.Entry(form, font=("Segoe UI", 10))
        self.entry_stu_id.pack(fill=tk.X, pady=(0, 8))
        self.entry_stu_id.insert(0, "S10245")

        # Student Name
        tk.Label(form, text="Student Full Name *", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL).pack(anchor="w", pady=(4, 2))
        self.entry_stu_name = ttk.Entry(form, font=("Segoe UI", 10))
        self.entry_stu_name.pack(fill=tk.X, pady=(0, 8))

        # Category
        tk.Label(form, text="Issue Category *", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL).pack(anchor="w", pady=(4, 2))
        self.combo_cat = ttk.Combobox(form, values=self.CATEGORIES, state="readonly", font=("Segoe UI", 9))
        self.combo_cat.pack(fill=tk.X, pady=(0, 8))
        self.combo_cat.set(self.CATEGORIES[1])  # Default: IT & Campus WiFi

        # Custom Category Entry (visible if Custom is chosen)
        self.lbl_custom_cat = tk.Label(form, text="Custom Category Name", font=("Segoe UI", 9), bg=self.COLOR_PANEL, fg="#475569")
        self.entry_custom_cat = ttk.Entry(form, font=("Segoe UI", 10))
        self.combo_cat.bind("<<ComboboxSelected>>", self._on_category_change)

        # Description
        tk.Label(form, text="Issue Description *", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL).pack(anchor="w", pady=(4, 2))
        self.txt_desc = tk.Text(form, height=6, font=("Segoe UI", 10), wrap="word", relief="solid", bd=1, padx=6, pady=4)
        self.txt_desc.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Button row
        btn_box = tk.Frame(form, bg=self.COLOR_PANEL)
        btn_box.pack(fill=tk.X, pady=(4, 8))

        btn_submit = tk.Button(btn_box, text="🚀  Submit Help Request", font=("Segoe UI", 10, "bold"),
                               bg=self.COLOR_PRIMARY, fg="#FFFFFF", activebackground=self.COLOR_PRIMARY_HOVER,
                               relief="flat", padx=16, pady=8, cursor="hand2", command=self.on_submit_ticket)
        btn_submit.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear = tk.Button(btn_box, text="✕  Clear Form", font=("Segoe UI", 9),
                              bg="#E2E8F0", fg=self.COLOR_TEXT, activebackground="#CBD5E1",
                              relief="flat", padx=12, pady=8, cursor="hand2", command=self.clear_student_form)
        btn_clear.pack(side=tk.LEFT)

        # Success announcement card
        self.receipt_frame = tk.Frame(form, bg="#DCFCE7", relief="solid", bd=1)
        self.lbl_receipt = tk.Label(self.receipt_frame, text="", font=("Segoe UI", 9),
                                    bg="#DCFCE7", fg="#166534", justify="left", padx=10, pady=8)
        self.lbl_receipt.pack(fill=tk.X)

        # RIGHT COLUMN: Check Ticket Status & View All Student Tickets
        right_col = tk.Frame(paned, bg=self.COLOR_BG)
        paned.add(right_col, minsize=420)

        # 1. Query Card: Check Ticket Status by ID
        query_card = tk.Frame(right_col, bg=self.COLOR_PANEL, relief="groove", bd=1)
        query_card.pack(fill=tk.X, pady=(0, 6))

        q_head = tk.Frame(query_card, bg="#F8FAFC")
        q_head.pack(fill=tk.X, padx=1, pady=1)
        tk.Label(q_head, text="🔍  Check Ticket Status (by Ticket ID)", font=("Segoe UI", 11, "bold"),
                 bg="#F8FAFC", fg=self.COLOR_TEXT).pack(anchor="w", padx=10, pady=6)

        q_body = tk.Frame(query_card, bg=self.COLOR_PANEL)
        q_body.pack(fill=tk.X, padx=12, pady=8)

        input_row = tk.Frame(q_body, bg=self.COLOR_PANEL)
        input_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(input_row, text="Ticket ID:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL).pack(side=tk.LEFT, padx=(0, 6))
        self.entry_query_id = ttk.Entry(input_row, width=14, font=("Segoe UI", 10))
        self.entry_query_id.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_query_id.bind("<Return>", lambda event: self.on_check_status())

        btn_query = tk.Button(input_row, text="🔎  Check Status", font=("Segoe UI", 9, "bold"),
                              bg="#334155", fg="#FFFFFF", activebackground="#1E293B",
                              relief="flat", padx=10, pady=4, cursor="hand2", command=self.on_check_status)
        btn_query.pack(side=tk.LEFT)

        # Query Result Card
        self.status_result_card = tk.Frame(q_body, bg="#F1F5F9", relief="solid", bd=1)
        self.status_result_card.pack(fill=tk.X, pady=4)

        self.lbl_status_header = tk.Label(self.status_result_card, text="Enter a Ticket ID above to check progress.",
                                          font=("Segoe UI", 9, "italic"), bg="#F1F5F9", fg="#64748B", padx=8, pady=8)
        self.lbl_status_header.pack(anchor="w")

        # 2. Query Card: View All Tickets for a Student ID
        student_list_card = tk.Frame(right_col, bg=self.COLOR_PANEL, relief="groove", bd=1)
        student_list_card.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        s_head = tk.Frame(student_list_card, bg="#F8FAFC")
        s_head.pack(fill=tk.X, padx=1, pady=1)
        tk.Label(s_head, text="📋  My Tickets History (by Student ID)", font=("Segoe UI", 11, "bold"),
                 bg="#F8FAFC", fg=self.COLOR_TEXT).pack(anchor="w", padx=10, pady=6)

        s_body = tk.Frame(student_list_card, bg=self.COLOR_PANEL)
        s_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        s_input_row = tk.Frame(s_body, bg=self.COLOR_PANEL)
        s_input_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(s_input_row, text="Student ID:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL).pack(side=tk.LEFT, padx=(0, 6))
        self.entry_filter_sid = ttk.Entry(s_input_row, width=16, font=("Segoe UI", 10))
        self.entry_filter_sid.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_filter_sid.bind("<Return>", lambda event: self.on_find_student_tickets())

        btn_find_stu = tk.Button(s_input_row, text="🔍  Find My Tickets", font=("Segoe UI", 9, "bold"),
                                 bg=self.COLOR_PRIMARY, fg="#FFFFFF", activebackground=self.COLOR_PRIMARY_HOVER,
                                 relief="flat", padx=10, pady=4, cursor="hand2", command=self.on_find_student_tickets)
        btn_find_stu.pack(side=tk.LEFT)

        self.lbl_stu_summary = tk.Label(s_body, text="Showing all tickets matching entered Student ID.",
                                        font=("Segoe UI", 8), bg=self.COLOR_PANEL, fg=self.COLOR_MUTED)
        self.lbl_stu_summary.pack(anchor="w", pady=(0, 4))

        # Student Tickets Treeview
        tree_st_frame = tk.Frame(s_body, bg=self.COLOR_PANEL)
        tree_st_frame.pack(fill=tk.BOTH, expand=True)

        st_cols = ("status", "id", "cat", "desc", "time")
        self.tree_student = ttk.Treeview(tree_st_frame, columns=st_cols, show="headings", selectmode="browse")
        self.tree_student.heading("status", text="Status")
        self.tree_student.heading("id", text="Ticket #")
        self.tree_student.heading("cat", text="Category")
        self.tree_student.heading("desc", text="Description")
        self.tree_student.heading("time", text="Submitted")

        self.tree_student.column("status", width=90, anchor="center")
        self.tree_student.column("id", width=60, anchor="center")
        self.tree_student.column("cat", width=110, anchor="w")
        self.tree_student.column("desc", width=170, anchor="w")
        self.tree_student.column("time", width=120, anchor="w")

        st_scroll_y = ttk.Scrollbar(tree_st_frame, orient="vertical", command=self.tree_student.yview)
        self.tree_student.configure(yscrollcommand=st_scroll_y.set)

        self.tree_student.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        st_scroll_y.pack(side=tk.RIGHT, fill="y")
        self.tree_student.bind("<<TreeviewSelect>>", self._on_student_tree_select)

    def _on_category_change(self, event=None):
        """Show or hide custom category entry based on dropdown selection."""
        if self.combo_cat.get() == "Custom / Other":
            self.lbl_custom_cat.pack(anchor="w", pady=(2, 2))
            self.entry_custom_cat.pack(fill=tk.X, pady=(0, 8))
        else:
            self.lbl_custom_cat.pack_forget()
            self.entry_custom_cat.pack_forget()

    # =========================================================================
    #                             ACTIONS & EVENTS
    # =========================================================================

    def refresh_all(self):
        """Refresh queue treeview, stack treeview, and header metric badges."""
        # 1. Update KPI Badges
        q_size = self.desk.pending_queue.size
        s_count = self.desk.resolved_stack.count
        next_id = self.desk.next_ticket_id

        self.lbl_kpi_pending.config(text=f"⏳ Pending Queue: {q_size}")
        self.lbl_kpi_resolved.config(text=f"✅ Resolved Stack: {s_count}")
        self.lbl_kpi_next_id.config(text=f"🏷️ Next ID: #{next_id}")

        self.lbl_queue_sub.config(text=f"Head of FIFO queue is processed next. Total: {q_size} ticket(s)")
        self.lbl_stack_sub.config(text=f"Top of LIFO stack is most recently resolved. Total: {s_count} ticket(s)")

        # 2. Populate Pending Queue Treeview (FIFO: front to rear)
        for row in self.tree_queue.get_children():
            self.tree_queue.delete(row)

        curr = self.desk.pending_queue.front
        pos = 1
        while curr:
            t = curr.ticket
            self.tree_queue.insert("", "end", iid=f"q_{t.id}", values=(
                f"#{pos}", f"#{t.id}", t.student_id, t.student_name, t.category, t.timestamp
            ))
            curr = curr.next
            pos += 1

        # 3. Populate Resolution Stack Treeview (LIFO: top to bottom)
        for row in self.tree_stack.get_children():
            self.tree_stack.delete(row)

        curr = self.desk.resolved_stack.top
        idx = 1
        while curr:
            t = curr.ticket
            self.tree_stack.insert("", "end", iid=f"s_{t.id}", values=(
                f"#{idx}", f"#{t.id}", t.student_id, t.student_name, t.category, t.timestamp
            ))
            curr = curr.next
            idx += 1

    def on_process_next(self):
        """Admin Action: Dequeue front ticket from Pending Queue and Push onto Resolved Stack."""
        if self.desk.pending_queue.is_empty():
            messagebox.showinfo("Queue Empty", "There are no pending tickets in the queue to process!")
            self.status_var.set("Notice: Pending queue is empty.")
            return

        ticket = self.desk.process_next()
        if ticket:
            self.refresh_all()
            self._display_ticket_in_inspector(ticket, "RESOLVED", 0)
            self.status_var.set(f"Processed Ticket #{ticket.id} ({ticket.student_name}) -> Pushed to Resolved Stack.")
            messagebox.showinfo("Ticket Processed",
                                f"Successfully processed Ticket #{ticket.id}!\n\n"
                                f"Student: {ticket.student_name} ({ticket.student_id})\n"
                                f"Category: {ticket.category}\n\n"
                                f"Dequeued from Pending FIFO Queue and pushed onto Resolution LIFO Stack.")

    def on_undo_resolution(self):
        """Admin Action: Pop top ticket from Resolved Stack and re-enqueue to Front of Pending Queue."""
        if self.desk.resolved_stack.is_empty():
            messagebox.showinfo("Stack Empty", "The resolution history stack is empty. There is nothing to undo!")
            self.status_var.set("Notice: Resolution stack is empty.")
            return

        ticket = self.desk.undo_resolution()
        if ticket:
            self.refresh_all()
            self._display_ticket_in_inspector(ticket, "RESTORED: PENDING", 1)
            self.status_var.set(f"Undone Ticket #{ticket.id} ({ticket.student_name}) -> Restored to Front of Pending Queue.")
            messagebox.showinfo("Resolution Undone",
                                f"Resolution for Ticket #{ticket.id} has been undone!\n\n"
                                f"Student: {ticket.student_name} ({ticket.student_id})\n\n"
                                f"Popped from Resolved Stack and restored to Position #1 in Pending Queue.")

    def on_submit_ticket(self):
        """Student Action: Validate input and enqueue new ticket."""
        sid = self.entry_stu_id.get().strip()
        sname = self.entry_stu_name.get().strip()
        cat_choice = self.combo_cat.get().strip()
        desc = self.txt_desc.get("1.0", tk.END).strip()

        if not sid or not sname:
            messagebox.showwarning("Incomplete Form", "Please provide both Student ID and Full Name.")
            return

        if cat_choice == "Custom / Other":
            cat = self.entry_custom_cat.get().strip()
            if not cat:
                messagebox.showwarning("Incomplete Form", "Please specify the custom category name.")
                return
        else:
            cat = cat_choice

        if not desc:
            messagebox.showwarning("Incomplete Form", "Please describe your issue in the description box.")
            return

        # Enqueue new ticket
        new_ticket = self.desk.submit_ticket(sid, sname, cat, desc)
        self.refresh_all()

        # Update receipt card
        receipt_text = (
            f"🎉  TICKET SUBMITTED SUCCESSFULLY!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• Ticket ID      : #{new_ticket.id}\n"
            f"• Student        : {new_ticket.student_name} ({new_ticket.student_id})\n"
            f"• Category       : {new_ticket.category}\n"
            f"• Queue Position : #{self.desk.pending_queue.size} (FIFO Order)\n"
            f"• Timestamp      : {new_ticket.timestamp}\n\n"
            f"Please save your Ticket ID #{new_ticket.id} to track progress."
        )
        self.lbl_receipt.config(text=receipt_text)
        self.receipt_frame.pack(fill=tk.X, pady=(4, 0))

        self.status_var.set(f"Ticket #{new_ticket.id} submitted by {new_ticket.student_name}. Enqueued at Pos #{self.desk.pending_queue.size}.")
        
        # Reset form fields
        self.txt_desc.delete("1.0", tk.END)
        self.entry_custom_cat.delete(0, tk.END)

        messagebox.showinfo("Ticket Submitted",
                            f"Ticket #{new_ticket.id} created successfully!\n\n"
                            f"Current Position in Queue: #{self.desk.pending_queue.size}")

    def clear_student_form(self):
        """Reset the student ticket submission form."""
        self.entry_stu_id.delete(0, tk.END)
        self.entry_stu_name.delete(0, tk.END)
        self.txt_desc.delete("1.0", tk.END)
        self.combo_cat.set(self.CATEGORIES[0])
        self._on_category_change()
        self.receipt_frame.pack_forget()
        self.status_var.set("Student form cleared.")

    def on_check_status(self):
        """Query ticket by ID and display status card."""
        tid_str = self.entry_query_id.get().strip()
        if not tid_str:
            messagebox.showwarning("Input Required", "Please enter a Ticket ID to query.")
            return

        try:
            tid = int(tid_str.replace("#", ""))
        except ValueError:
            messagebox.showerror("Invalid Input", "Ticket ID must be an integer (e.g. 1001).")
            return

        ticket, status_str, pos = self.desk.find_ticket(tid)
        if ticket:
            bg_color = "#FEF3C7" if "PENDING" in status_str else "#DCFCE7"
            fg_color = "#92400E" if "PENDING" in status_str else "#166534"
            pos_info = f" | Position in Queue: #{pos}" if pos > 0 else ""

            msg = (
                f"TICKET #{ticket.id} — {status_str}{pos_info}\n"
                f"Student    : {ticket.student_name} ({ticket.student_id})\n"
                f"Category   : {ticket.category}\n"
                f"Submitted  : {ticket.timestamp}\n"
                f"Description: {ticket.description}"
            )
            self.lbl_status_header.config(text=msg, font=("Segoe UI", 9), bg=bg_color, fg=fg_color)
            self.status_result_card.config(bg=bg_color)
            self.status_var.set(f"Found Ticket #{ticket.id} [{status_str}].")
        else:
            self.lbl_status_header.config(text=f"❌ No ticket found with ID #{tid}.",
                                          font=("Segoe UI", 9, "bold"), bg="#FEE2E2", fg="#991B1B")
            self.status_result_card.config(bg="#FEE2E2")
            self.status_var.set(f"Ticket #{tid} not found.")

    def on_find_student_tickets(self):
        """Find and display all tickets associated with a given Student ID."""
        sid = self.entry_filter_sid.get().strip()
        if not sid:
            messagebox.showwarning("Input Required", "Please enter a Student ID to search.")
            return

        for row in self.tree_student.get_children():
            self.tree_student.delete(row)

        total, pending_cnt, resolved_cnt = 0, 0, 0

        # Scan Pending Queue
        curr = self.desk.pending_queue.front
        pos = 1
        while curr:
            if curr.ticket.student_id.lower() == sid.lower():
                t = curr.ticket
                self.tree_student.insert("", "end", iid=f"st_p_{t.id}", values=(
                    f"⏳ PENDING (#{pos})", f"#{t.id}", t.category, t.description, t.timestamp
                ))
                pending_cnt += 1
                total += 1
            curr = curr.next
            pos += 1

        # Scan Resolved Stack
        curr = self.desk.resolved_stack.top
        while curr:
            if curr.ticket.student_id.lower() == sid.lower():
                t = curr.ticket
                self.tree_student.insert("", "end", iid=f"st_r_{t.id}", values=(
                    "✅ RESOLVED", f"#{t.id}", t.category, t.description, t.timestamp
                ))
                resolved_cnt += 1
                total += 1
            curr = curr.next

        summary = f"Student '{sid}': {total} Total Ticket(s) ({pending_cnt} Pending, {resolved_cnt} Resolved)"
        self.lbl_stu_summary.config(text=summary, fg=self.COLOR_TEXT if total > 0 else self.COLOR_MUTED)
        self.status_var.set(summary)

    def on_save_csv(self):
        """Save current system state to CSV file."""
        filename = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            initialfile=self.current_csv_file or "helpdesk_data.csv",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            success = self.desk.save_to_file(filename)
            if success:
                self.current_csv_file = os.path.basename(filename)
                self.file_status_var.set(f"Active File: {self.current_csv_file}")
                self.status_var.set(f"System state successfully saved to '{filename}'.")
                messagebox.showinfo("Saved", f"System state successfully saved to:\n{filename}")
            else:
                messagebox.showerror("Save Error", f"Failed to save data to '{filename}'.")

    def on_load_csv(self):
        """Load system state from a CSV file."""
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            success = self.desk.load_from_file(filename)
            if success:
                self.current_csv_file = os.path.basename(filename)
                self.file_status_var.set(f"Active File: {self.current_csv_file}")
                self.refresh_all()
                self.status_var.set(f"Successfully loaded {self.desk.pending_queue.size} pending and {self.desk.resolved_stack.count} resolved tickets.")
                messagebox.showinfo("Loaded", f"Data loaded successfully from:\n{filename}\n\n"
                                              f"Pending Queue: {self.desk.pending_queue.size}\n"
                                              f"Resolved Stack: {self.desk.resolved_stack.count}")
            else:
                messagebox.showerror("Load Error", f"Could not load or parse '{filename}'.")

    # =========================================================================
    #                       SELECTION & INSPECTION HANDLERS
    # =========================================================================

    def _on_queue_item_select(self, event):
        """Handler when a row in the Pending Queue treeview is selected."""
        selected = self.tree_queue.selection()
        if not selected:
            return
        item_id = selected[0]
        tid = int(item_id.split("_")[1])
        ticket, pos = self.desk.pending_queue.find(tid)
        if ticket:
            self._display_ticket_in_inspector(ticket, f"PENDING (Queue Pos: #{pos})", pos)

    def _on_stack_item_select(self, event):
        """Handler when a row in the Resolution Stack treeview is selected."""
        selected = self.tree_stack.selection()
        if not selected:
            return
        item_id = selected[0]
        tid = int(item_id.split("_")[1])
        ticket = self.desk.resolved_stack.find(tid)
        if ticket:
            self._display_ticket_in_inspector(ticket, "RESOLVED (In Stack)", 0)

    def _on_student_tree_select(self, event):
        """Handler when a ticket is clicked in the Student My-Tickets table."""
        selected = self.tree_student.selection()
        if not selected:
            return
        item_id = selected[0]
        tid = int(item_id.split("_")[2])
        ticket, status_str, pos = self.desk.find_ticket(tid)
        if ticket:
            self._display_ticket_in_inspector(ticket, status_str, pos)

    def _display_ticket_in_inspector(self, ticket, status_str, pos):
        """Populate the bottom inspector panel with full ticket details."""
        self.var_det_id.set(f"#{ticket.id}")
        self.var_det_sid.set(ticket.student_id)
        self.var_det_name.set(ticket.student_name)
        self.var_det_cat.set(ticket.category)
        self.var_det_time.set(ticket.timestamp)

        # Status badge color
        if "PENDING" in status_str:
            self.lbl_detail_status.config(text=f"⏳ {status_str}", bg="#FEF3C7", fg="#92400E")
        else:
            self.lbl_detail_status.config(text=f"✅ {status_str}", bg="#DCFCE7", fg="#166534")

        self.txt_det_desc.configure(state="normal")
        self.txt_det_desc.delete("1.0", tk.END)
        self.txt_det_desc.insert("1.0", ticket.description)
        self.txt_det_desc.configure(state="disabled")


def launch_gui(initial_csv=None):
    """Entry point to launch the Tkinter GUI window."""
    root = tk.Tk()
    app = HelpDeskGUI(root, initial_csv)
    root.mainloop()


if __name__ == "__main__":
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    launch_gui(csv_arg)
