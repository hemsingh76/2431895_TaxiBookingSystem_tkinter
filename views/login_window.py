import tkinter as tk
from tkinter import messagebox
import sys
import os

# Ensure parent directory is in path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.constants import COLORS, FONTS

class LoginWindow:
    """Login window for user authentication"""    
    def __init__(self, root, db, on_login_success, fullscreen=False, geometry=None):
        self.root = root
        self.db = db
        self.on_login_success = on_login_success
        
        self.root.title("Taxi Booking System - Login")
        self.root.resizable(True, True)
        
        # Set geometry or fullscreen - preserve state BEFORE setting up UI - fullscreen takes priority
        if fullscreen:
            self.root.attributes('-fullscreen', True)
            self.root.update_idletasks()  # Ensure fullscreen is applied
        elif geometry and geometry.strip():
            self.root.geometry(geometry)
            self.root.update_idletasks()  # Ensure geometry is applied
        else:
            self.root.geometry("1000x900")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup login UI"""
        # ---------- Main background ----------
        main_frame = tk.Frame(self.root, bg=COLORS['login_bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="🚕 Taxi Booking System",
            font=('Arial', 24, 'bold'),
            bg=COLORS['login_bg'],
            fg=COLORS['white']
        )
        title_label.pack(pady=(25, 10))

        # ---------- Center container (does NOT stretch) ----------
        container = tk.Frame(main_frame, bg=COLORS['login_bg'])
        container.pack(expand=True)

        # ---------- Login Box ----------
        login_frame = tk.Frame(
            container,
            bg=COLORS['white'],
            relief=tk.RAISED,
            bd=2
        )
        login_frame.pack()

        tk.Label(
            login_frame,
            text="LOGIN",
            font=('Arial', 18, 'bold'),
            bg=COLORS['white']
        ).pack(pady=(15, 10))

        # Username Label
        tk.Label(
            login_frame,
            text="Username:",
            bg=COLORS['white'],
            font=('Arial', 12)
        ).pack(anchor=tk.W, padx=30, pady=(5, 2))

        # Username Entry
        self.username_entry = tk.Entry(
            login_frame,
            font=('Arial', 13),
            width=28,
            relief=tk.GROOVE,
            bd=2
        )
        self.username_entry.pack(padx=30, pady=(0, 12), ipady=4)

        # Password Label
        tk.Label(
            login_frame,
            text="Password:",
            bg=COLORS['white'],
            font=('Arial', 12)
        ).pack(anchor=tk.W, padx=30, pady=(5, 2))

        # Password Entry
        self.password_entry = tk.Entry(
            login_frame,
            font=('Arial', 13),
            width=28,
            show="*",
            relief=tk.GROOVE,
            bd=2
        )
        self.password_entry.pack(padx=30, pady=(0, 15), ipady=4)

        # Login button
        login_btn = tk.Button(
            login_frame,
            text="Login",
            bg=COLORS['success'],
            fg=COLORS['white'],
            font=('Arial', 12, 'bold'),
            width=18,
            cursor="hand2",
            command=self.login
        )
        login_btn.pack(pady=(5, 8))

        # Register button
        register_btn = tk.Button(
            login_frame,
            text="Register as Customer",
            bg=COLORS['info'],
            fg=COLORS['white'],
            font=('Arial', 12, 'bold'),
            width=18,
            cursor="hand2",
            command=self.open_register
        )
        register_btn.pack(pady=(0, 15))

        # ENTER key triggers login
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Return>", lambda e: self.login())
        
        # ESC key exits fullscreen
        self.root.bind("<Escape>", lambda e: self.root.attributes('-fullscreen', False))

    
    def open_register(self):
        """Open registration window without closing login window"""
        top = tk.Toplevel(self.root)
        top.grab_set()  # keep focus on register window
        
        # Center the window relative to the login window
        top.update_idletasks()  # Update to get accurate window dimensions
        login_x = self.root.winfo_x()
        login_y = self.root.winfo_y()
        login_width = self.root.winfo_width()
        login_height = self.root.winfo_height()
        
        register_width = 400
        register_height = 420
        
        # Calculate center position
        center_x = login_x + (login_width // 2) - (register_width // 2)
        center_y = login_y + (login_height // 2) - (register_height // 2)
        
        top.geometry(f"{register_width}x{register_height}+{center_x}+{center_y}")

        from views.register_window import RegisterWindow

        def on_success():
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            top.destroy()

        RegisterWindow(top, self.db, on_register_success=on_success)
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        user = self.db.authenticate(username, password)
        
        if user:
            # Preserve window state - ensure we get accurate state
            self.root.update_idletasks()  # Ensure window state is current
            is_fullscreen = bool(self.root.attributes('-fullscreen'))
            if is_fullscreen:
                geometry = None
            else:
                geometry = self.root.geometry()
            self.on_login_success(user, fullscreen=is_fullscreen, geometry=geometry)
        else:
            messagebox.showerror("Error", "Invalid username or password")
