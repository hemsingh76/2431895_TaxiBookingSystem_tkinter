import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.constants import COLORS, FONTS, BOOKING_STATUS

class CustomerDashboard:
    """Customer dashboard for booking management"""
    
    def __init__(self, root, db, user_data, logout_callback, fullscreen=False, geometry=None):
        self.root = root
        self.db = db
        self.user_id, self.username, self.role, self.name = user_data
        self.logout_callback = logout_callback
        self.root.title(f"Customer Dashboard - {self.name}")
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
        self.load_bookings()
    
    def setup_ui(self):
        """Setup customer UI"""
        header = tk.Frame(self.root, bg=COLORS['customer_header'], height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"Welcome, {self.name}", font=FONTS['header'],
                bg=COLORS['customer_header'], fg=COLORS['white']).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Button(header, text="Logout", bg=COLORS['danger'], fg=COLORS['white'],
                 font=FONTS['button'], command=self.logout).pack(side=tk.RIGHT, padx=20, pady=15)
        
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        form_frame = tk.LabelFrame(container, text="New Booking", font=FONTS['subheader'], padx=10, pady=10)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        fields_frame = tk.Frame(form_frame)
        fields_frame.pack(fill=tk.X)
        
        fields = [("Pickup Location:", 0, 0), ("Dropoff Location:", 0, 2), 
                  ("Date (YYYY-MM-DD):", 1, 0), ("Time (HH:MM):", 1, 2)]
        self.pickup_entry = tk.Entry(fields_frame, font=FONTS['normal'], width=25)
        self.dropoff_entry = tk.Entry(fields_frame, font=FONTS['normal'], width=25)
        self.date_entry = tk.Entry(fields_frame, font=FONTS['normal'], width=25)
        self.time_entry = tk.Entry(fields_frame, font=FONTS['normal'], width=25)
        
        for label, row, col in fields:
            tk.Label(fields_frame, text=label, font=FONTS['normal']).grid(row=row, column=col, sticky=tk.W, pady=5)
        
        self.pickup_entry.grid(row=0, column=1, padx=10, pady=5)
        self.dropoff_entry.grid(row=0, column=3, padx=10, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=10, pady=5)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.grid(row=1, column=3, padx=10, pady=5)
        
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(pady=10)
        for text, cmd, color in [("Book Taxi", self.book_taxi, COLORS['success']),
                                 ("Update Booking", self.update_booking, COLORS['warning']),
                                 ("Cancel Booking", self.cancel_booking, COLORS['danger'])]:
            tk.Button(btn_frame, text=text, bg=color, fg=COLORS['white'], font=FONTS['button'],
                     width=15, cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=5)
        
        list_frame = tk.LabelFrame(container, text="My Bookings", font=FONTS['subheader'], padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Pickup", "Dropoff", "Date", "Time", "Driver", "Status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col == "ID" else 120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind('<ButtonRelease-1>', self.on_booking_select)
    
    def get_form_data(self):
        """Get and validate form data"""
        data = [e.get().strip() for e in [self.pickup_entry, self.dropoff_entry, self.date_entry, self.time_entry]]
        if not all(data):
            messagebox.showerror("Error", "Please fill all fields")
            return None
        try:
            datetime.strptime(data[2], "%Y-%m-%d")
            datetime.strptime(data[3], "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid date or time format")
            return None
        return data
    
    def book_taxi(self):
        """Book a new taxi"""
        data = self.get_form_data()
        if not data: return
        self.db.cursor.execute('''INSERT INTO bookings (customer_id, pickup_location, dropoff_location, 
                                booking_date, booking_time, status) VALUES (?, ?, ?, ?, ?, ?)''',
                              (self.user_id, *data, BOOKING_STATUS['PENDING']))
        self.db.conn.commit()
        messagebox.showinfo("Success", "Taxi booked successfully!")
        self.clear_form()
        self.load_bookings()
    
    def update_booking(self):
        """Update selected booking"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a booking to update")
            return
        booking_id = self.tree.item(selected[0])['values'][0]
        self.db.cursor.execute('SELECT status FROM bookings WHERE booking_id = ?', (booking_id,))
        status = self.db.cursor.fetchone()[0]
        if status in [BOOKING_STATUS['COMPLETED'], BOOKING_STATUS['CANCELLED']]:
            messagebox.showerror("Error", f"Cannot update {status.lower()} booking")
            return
        data = self.get_form_data()
        if not data: return
        self.db.cursor.execute('''UPDATE bookings SET pickup_location = ?, dropoff_location = ?, 
                                booking_date = ?, booking_time = ? WHERE booking_id = ?''',
                              (*data, booking_id))
        self.db.conn.commit()
        messagebox.showinfo("Success", "Booking updated successfully!")
        self.load_bookings()
    
    def cancel_booking(self):
        """Cancel selected booking"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a booking to cancel")
            return
        booking_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
            self.db.cursor.execute('UPDATE bookings SET status = ? WHERE booking_id = ?',
                                  (BOOKING_STATUS['CANCELLED'], booking_id))
            self.db.conn.commit()
            messagebox.showinfo("Success", "Booking cancelled successfully!")
            self.load_bookings()
    
    def load_bookings(self):
        """Load customer bookings"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.db.cursor.execute('''SELECT b.booking_id, b.pickup_location, b.dropoff_location, 
                                 b.booking_date, b.booking_time, COALESCE(u.name, 'Not Assigned') as driver_name, b.status
                                 FROM bookings b LEFT JOIN users u ON b.driver_id = u.user_id
                                 WHERE b.customer_id = ? ORDER BY b.booking_date DESC, b.booking_time DESC''',
                              (self.user_id,))
        for row in self.db.cursor.fetchall():
            self.tree.insert('', tk.END, values=row)
    
    def on_booking_select(self, event):
        """Handle booking selection"""
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            entries = [self.pickup_entry, self.dropoff_entry, self.date_entry, self.time_entry]
            for entry, idx in zip(entries, [1, 2, 3, 4]):
                entry.delete(0, tk.END)
                entry.insert(0, values[idx])
    
    def clear_form(self):
        """Clear form fields"""
        self.pickup_entry.delete(0, tk.END)
        self.dropoff_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
    
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

