import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLORS, FONTS, BOOKING_STATUS

class AdminDashboard:
    """Admin dashboard for managing bookings and drivers"""
    
    def __init__(self, root, db, user_data, logout_callback, fullscreen=False, geometry=None):
        self.root = root
        self.db = db
        self.user_id, self.username, self.role, self.name = user_data
        self.logout_callback = logout_callback
        
        self.root.title(f"Admin Dashboard - {self.name}")
        # Set window state BEFORE setting up UI - fullscreen takes priority
        if fullscreen:
            self.root.attributes('-fullscreen', True)
            self.root.update_idletasks()  # Ensure fullscreen is applied
        elif geometry and geometry.strip():
            self.root.geometry(geometry)
            self.root.update_idletasks()  # Ensure geometry is applied
        else:
            self.root.geometry("1000x650")
        
        self.setup_ui()
        self.load_bookings()
        self.load_drivers()
    
    def setup_ui(self):
        """Setup admin UI"""
        # Header
        header = tk.Frame(self.root, bg=COLORS['admin_header'], height=60)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="Admin Dashboard",
            font=FONTS['title'],
            bg=COLORS['admin_header'],
            fg=COLORS['white']
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Button(
            header,
            text="Logout",
            bg=COLORS['danger'],
            fg=COLORS['white'],
            font=FONTS['button'],
            command=self.logout
        ).pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Main container
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Assignment frame
        assign_frame = tk.LabelFrame(
            container,
            text="Assign Driver",
            font=FONTS['subheader'],
            padx=10,
            pady=10
        )
        assign_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            assign_frame,
            text="Select Booking ID:",
            font=FONTS['normal']
        ).pack(side=tk.LEFT, padx=5)
        
        self.booking_id_entry = tk.Entry(assign_frame, font=FONTS['normal'], width=10)
        self.booking_id_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            assign_frame,
            text="Select Driver:",
            font=FONTS['normal']
        ).pack(side=tk.LEFT, padx=5)
        
        self.driver_combo = ttk.Combobox(
            assign_frame,
            font=FONTS['normal'],
            width=20,
            state='readonly'
        )
        self.driver_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            assign_frame,
            text="Assign Driver",
            bg=COLORS['success'],
            fg=COLORS['white'],
            font=FONTS['button'],
            cursor="hand2",
            command=self.assign_driver
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            assign_frame,
            text="Refresh",
            bg=COLORS['info'],
            fg=COLORS['white'],
            font=FONTS['button'],
            cursor="hand2",
            command=self.load_bookings
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            header,
            text="Register Driver",
            bg=COLORS['info'],
            fg="white",
            font=FONTS["button"],
            command=self.open_driver_registration
        ).pack(side=tk.LEFT, padx=10)
        
        # Bookings list
        list_frame = tk.LabelFrame(
            container,
            text="All Bookings",
            font=FONTS['subheader'],
            padx=10,
            pady=10
        )
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ("ID", "Customer", "Pickup", "Dropoff", "Date", "Time", "Driver", "Status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 60 if col == "ID" else 120
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<ButtonRelease-1>', self.on_booking_select)
    
    def load_drivers(self):
        """Load available drivers"""
        drivers = self.db.get_all_drivers()
        self.drivers = {name: user_id for user_id, name in drivers}
        self.driver_combo['values'] = list(self.drivers.keys())
    
    def load_bookings(self):
        """Load all bookings"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.db.cursor.execute('''
            SELECT b.booking_id, c.name as customer_name, 
                   b.pickup_location, b.dropoff_location, 
                   b.booking_date, b.booking_time, 
                   COALESCE(d.name, 'Not Assigned') as driver_name, b.status
            FROM bookings b
            JOIN users c ON b.customer_id = c.user_id
            LEFT JOIN users d ON b.driver_id = d.user_id
            ORDER BY b.booking_date DESC, b.booking_time DESC
        ''')
        
        for row in self.db.cursor.fetchall():
            self.tree.insert('', tk.END, values=row)
    
    def assign_driver(self):
        """Assign driver to booking"""
        booking_id = self.booking_id_entry.get().strip()
        driver_name = self.driver_combo.get()
        
        if not booking_id or not driver_name:
            messagebox.showerror("Error", "Please select booking ID and driver")
            return
        
        driver_id = self.drivers[driver_name]
        
        # Get booking details
        self.db.cursor.execute('''
            SELECT booking_date, booking_time, status 
            FROM bookings WHERE booking_id = ?
        ''', (booking_id,))
        
        result = self.db.cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Invalid booking ID")
            return
        
        booking_date, booking_time, status = result
        
        if status in [BOOKING_STATUS['CANCELLED'], BOOKING_STATUS['COMPLETED']]:
            messagebox.showerror("Error", f"Cannot assign driver to {status.lower()} booking")
            return
        
        # Check for overlapping bookings
        if not self.db.check_driver_availability(driver_id, booking_date, booking_time):
            messagebox.showerror("Error", 
                               "Driver has overlapping booking at this time!")
            return
        
        # Assign driver
        self.db.cursor.execute('''
            UPDATE bookings 
            SET driver_id = ?, status = ?
            WHERE booking_id = ?
        ''', (driver_id, BOOKING_STATUS['ASSIGNED'], booking_id))
        self.db.conn.commit()
        
        messagebox.showinfo("Success", "Driver assigned successfully!")
        self.booking_id_entry.delete(0, tk.END)
        self.driver_combo.set('')
        self.load_bookings()
    
    def on_booking_select(self, event):
        """Handle booking selection"""
        selected = self.tree.selection()
        if selected:
            booking_id = self.tree.item(selected[0])['values'][0]
            self.booking_id_entry.delete(0, tk.END)
            self.booking_id_entry.insert(0, str(booking_id))
    
    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            self.root.update_idletasks()  # Ensure window state is current
            is_fullscreen = bool(self.root.attributes('-fullscreen'))
            if is_fullscreen:
                geometry = None
            else:
                geometry = self.root.geometry()
            self.root.quit()
            self.logout_callback(fullscreen=is_fullscreen, geometry=geometry)

    def open_driver_registration(self):
        """Open the driver registration window"""
        win = tk.Toplevel(self.root)
        
        # Center the window relative to the admin dashboard
        win.update_idletasks()  # Update to get accurate window dimensions
        admin_x = self.root.winfo_x()
        admin_y = self.root.winfo_y()
        admin_width = self.root.winfo_width()
        admin_height = self.root.winfo_height()
        
        register_width = 400
        register_height = 550
        
        # Calculate center position
        center_x = admin_x + (admin_width // 2) - (register_width // 2)
        center_y = admin_y + (admin_height // 2) - (register_height // 2)
        
        win.geometry(f"{register_width}x{register_height}+{center_x}+{center_y}")
        
        from views.register_driver_window import RegisterDriverWindow
        # Pass load_drivers as the callback to refresh the driver list
        RegisterDriverWindow(win, self.db, self.load_drivers)

