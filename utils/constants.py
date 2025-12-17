"""Constants and configuration for the application"""
# Colors
COLORS = {
    'customer_header': '#3498db',
    'admin_header': '#8e44ad',
    'driver_header': '#16a085',
    'login_bg': '#2c3e50',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    'white': 'white',
    'light_gray': '#ecf0f1'
}

# Booking statuses
BOOKING_STATUS = {
    'PENDING': 'Pending',
    'ASSIGNED': 'Assigned',
    'COMPLETED': 'Completed',
    'CANCELLED': 'Cancelled'
}

# User roles
USER_ROLES = {
    'ADMIN': 'Admin',
    'CUSTOMER': 'Customer',
    'DRIVER': 'Driver'
}

# Font settings
FONTS = {
    'title': ('Arial', 18, 'bold'),
    'header': ('Arial', 16, 'bold'),
    'subheader': ('Arial', 12, 'bold'),
    'normal': ('Arial', 10),
    'button': ('Arial', 10, 'bold'),
    'small': ('Arial', 8)
}
