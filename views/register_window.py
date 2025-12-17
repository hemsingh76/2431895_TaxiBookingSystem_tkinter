import tkinter as tk
from tkinter import messagebox
from utils.constants import COLORS, FONTS

class RegisterWindow:
    """Customer Registration window (designed to be used as a Toplevel)"""

    def __init__(self, root, db, on_register_success):
        """
        root: a Toplevel or Tk instance passed by caller
        db: Database instance
        on_register_success: callback to call when registration succeeds (no args)
        """
        self.root = root
        self.db = db
        self.on_register_success = on_register_success

        # If this is a Toplevel, don't reconfigure app-level geometry too aggressively
        self.root.title("Register - Customer")
        self.root.resizable(False, False)
        # Geometry will be set by the parent window for centering

        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root, bg=COLORS["white"])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Create Customer Account", font=FONTS["header"]).pack(pady=10)

        self.entry_name = self.create_entry(frame, "Full Name")
        self.entry_username = self.create_entry(frame, "Username")
        self.entry_phone = self.create_entry(frame, "Phone")
        self.entry_password = self.create_entry(frame, "Password", show="*")

        btn_frame = tk.Frame(frame, bg=COLORS["white"])
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Register",
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=FONTS["button"],
            width=15,
            command=self.register
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Back",
            bg=COLORS["warning"],
            fg=COLORS["white"],
            font=FONTS["button"],
            width=12,
            command=self.go_back
        ).pack(side=tk.LEFT, padx=5)

        # Optional: bind Enter to register
        self.entry_password.bind('<Return>', lambda e: self.register())

    def create_entry(self, parent, label, show=None):
        tk.Label(parent, text=label, font=FONTS["normal"], bg=COLORS["white"]).pack(anchor="w")
        entry = tk.Entry(parent, font=FONTS["normal"], show=show)
        entry.pack(fill=tk.X, pady=5)
        return entry

    def register(self):
        name = self.entry_name.get().strip()
        username = self.entry_username.get().strip()
        phone = self.entry_phone.get().strip()
        password = self.entry_password.get().strip()

        if not all([name, username, phone, password]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Invalid password!")
            return
        
        if len(phone) < 10 or len(phone)>10 or not phone.isdigit():
            messagebox.showerror("Error", "Invalid phone number!")
            return

        # Use the Database.create_user method (make sure it's implemented)
        success = self.db.create_user(username, password, "Customer", name, phone)

        if success:
            # call parent's success callback (e.g., show info + close)
            if callable(self.on_register_success):
                self.on_register_success()
        else:
            messagebox.showerror("Error", "Username already exists!")

    def go_back(self):
        """Close this Toplevel and return to the login window"""
        self.root.destroy()
