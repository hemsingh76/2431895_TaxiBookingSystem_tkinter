import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLORS, FONTS, BOOKING_STATUS

class DriverDashboard:
    """Driver dashboard for viewing assigned trips"""
    
    def __init__(self, root, db, user_data, logout_callback, fullscreen=False, geometry=None):
        self.root = root
        self.db = db
        self.user_id, self.username, self.role, self.name = user_data
        self.logout_callback = logout_callback
        
        self.root.title(f"Driver Dashboard - {self.name}")
        # Set window state BEFORE setting up UI - fullscreen takes priority
        if fullscreen:
            self.root.attributes('-fullscreen', True)
            self.root.update_idletasks()  # Ensure fullscreen is applied
        elif geometry and geometry.strip():
            self.root.geometry(geometry)
            self.root.update_idletasks()  # Ensure geometry is applied
        else:
            self.root.geometry("900x600")
        
        self.setup_ui()
        self.load_trips()
    
    def setup_ui(self):
        """Setup driver UI"""
        # Header
        header = tk.Frame(self.root, bg=COLORS['driver_header'], height=60)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text=f"Driver Dashboard - {self.name}",
            font=FONTS['header'],
            bg=COLORS['driver_header'],
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
        
        # Control frame
        control_frame = tk.Frame(container)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Button(
            control_frame,
            text="Refresh Trips",
            bg=COLORS['info'],
            fg=COLORS['white'],
            font=FONTS['button'],
            width=15,
            cursor="hand2",
            command=self.load_trips
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="Complete Trip",
            bg=COLORS['success'],
            fg=COLORS['white'],
            font=FONTS['button'],
            width=15,
            cursor="hand2",
            command=self.complete_trip
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="Cancel Trip",
            bg=COLORS['danger'],
            fg=COLORS['white'],
            font=FONTS['button'],
            width=15,
            cursor="hand2",
            command=self.cancel_trip
        ).pack(side=tk.LEFT, padx=5)
        
        # Trips list
        list_frame = tk.LabelFrame(
            container,
            text="Assigned Trips",
            font=FONTS['subheader'],
            padx=10,
            pady=10
        )
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ("ID", "Customer", "Phone", "Pickup", "Dropoff", "Date", "Time", "Status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 60 if col == "ID" else 110
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_trips(self):
        """Load assigned trips"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.db.cursor.execute('''
            SELECT b.booking_id, u.name, u.phone,
                   b.pickup_location, b.dropoff_location, 
                   b.booking_date, b.booking_time, b.status
            FROM bookings b
            JOIN users u ON b.customer_id = u.user_id
            WHERE b.driver_id = ?
            ORDER BY b.booking_date DESC, b.booking_time DESC
        ''', (self.user_id,))
        
        for row in self.db.cursor.fetchall():
            self.tree.insert('', tk.END, values=row)
    
    def complete_trip(self):
        """Mark trip as completed"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a trip")
            return
        
        booking_id = self.tree.item(selected[0])['values'][0]
        status = self.tree.item(selected[0])['values'][7]
        
        if status == BOOKING_STATUS['COMPLETED']:
            messagebox.showinfo("Info", "Trip is already completed")
            return
        
        if status == BOOKING_STATUS['CANCELLED']:
            messagebox.showerror("Error", "Cannot complete cancelled trip")
            return
        
        if messagebox.askyesno("Confirm", "Mark this trip as completed?"):
            self.db.cursor.execute('''
                UPDATE bookings SET status = ? WHERE booking_id = ?
            ''', (BOOKING_STATUS['COMPLETED'], booking_id))
            self.db.conn.commit()
            
            messagebox.showinfo("Success", "Trip completed successfully!")
            self.load_trips()
    
    def cancel_trip(self):
        """Cancel trip"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a trip")
            return
        
        booking_id = self.tree.item(selected[0])['values'][0]
        status = self.tree.item(selected[0])['values'][7]
        
        if status in [BOOKING_STATUS['COMPLETED'], BOOKING_STATUS['CANCELLED']]:
            messagebox.showerror("Error", f"Cannot cancel {status.lower()} trip")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this trip?"):
            self.db.cursor.execute('''
                UPDATE bookings SET status = ?, driver_id = NULL 
                WHERE booking_id = ?
            ''', (BOOKING_STATUS['CANCELLED'], booking_id))
            self.db.conn.commit()
            
            messagebox.showinfo("Success", "Trip cancelled successfully!")
            self.load_trips()
    
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
