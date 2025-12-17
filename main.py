import tkinter as tk
from database import Database
from views.login_window import LoginWindow
from views.customer_dashboard import CustomerDashboard
from views.admin_dashboard import AdminDashboard
from views.driver_dashboard import DriverDashboard

class TaxiBookingApp:
    
    def __init__(self):
        self.db = Database()
        self.current_window = None
        self.show_login()
    
    def show_login(self, fullscreen=False, geometry=None):
        """Show login window"""
        if self.current_window:
            try:
                self.current_window.destroy()
            except:
                pass
            self.current_window = None
        
        root = tk.Tk()
        self.current_window = root
        LoginWindow(root, self.db, self.on_login_success, fullscreen, geometry)
        root.update_idletasks()  # Ensure geometry is applied
        root.mainloop()
    
    def on_login_success(self, user_data, fullscreen=False, geometry=None):
        """Handle successful login"""
        user_id, username, role, name = user_data
        
        if self.current_window:
            try:
                self.current_window.destroy()
            except:
                pass
            self.current_window = None
        
        root = tk.Tk()
        self.current_window = root
        
        if role == 'Customer':
            CustomerDashboard(root, self.db, user_data, self.show_login, fullscreen, geometry)
        elif role == 'Admin':
            AdminDashboard(root, self.db, user_data, self.show_login, fullscreen, geometry)
        elif role == 'Driver':
            DriverDashboard(root, self.db, user_data, self.show_login, fullscreen, geometry)
        
        root.update_idletasks()  # Ensure geometry is applied
        root.mainloop()


if __name__ == "__main__":
    app = TaxiBookingApp()
