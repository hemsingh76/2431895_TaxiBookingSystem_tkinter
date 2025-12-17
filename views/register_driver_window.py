import tkinter as tk
from tkinter import messagebox
from utils.constants import COLORS, FONTS

class RegisterDriverWindow:
    """Driver Registration for Admin"""

    def __init__(self, root, db, refresh_callback):
        self.root = root
        self.db = db
        self.refresh_callback = refresh_callback

        self.root.title("Register Driver")
        self.root.resizable(False, False)
        # Geometry will be set by the parent window for centering

        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root, bg=COLORS["white"])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Register New Driver", font=FONTS["header"], bg=COLORS["white"]).pack(pady=10)

        self.entry_name = self.create_input(frame, "Driver Name")
        self.entry_username = self.create_input(frame, "Username")
        self.entry_phone = self.create_input(frame, "Phone Number")
        self.entry_vehicle = self.create_input(frame, "Vehicle Number")
        self.entry_license = self.create_input(frame, "License Number")
        self.entry_password = self.create_input(frame, "Password", show="*")

        btn_frame = tk.Frame(frame, bg=COLORS["white"])
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Register",
            bg=COLORS["success"],
            fg="white",
            font=FONTS["button"],
            width=12,
            command=self.register_driver
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Back",
            bg=COLORS["warning"],
            fg="white",
            font=FONTS["button"],
            width=10,
            command=self.root.destroy
        ).pack(side=tk.LEFT)

    def create_input(self, parent, label, show=None):
        tk.Label(parent, text=label, font=FONTS["normal"], bg=COLORS["white"]).pack(anchor="w")
        entry = tk.Entry(parent, font=FONTS["normal"], show=show)
        entry.pack(fill=tk.X, pady=5)
        return entry

    def register_driver(self):
        name = self.entry_name.get().strip()
        username = self.entry_username.get().strip()
        phone = self.entry_phone.get().strip()
        vehicle = self.entry_vehicle.get().strip()
        license_no = self.entry_license.get().strip()
        password = self.entry_password.get().strip()

        if not all([name, username, phone, vehicle, license_no, password]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if len(phone) < 10 or len(phone)>10 or not phone.isdigit():
            messagebox.showerror("Error", "Invalid phone number!")
            return      

        success = self.db.create_driver(username, password, name, phone, vehicle, license_no)

        if success:
            messagebox.showinfo("Success", "Driver Registered Successfully!")
            self.refresh_callback()
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Username already exists!")
