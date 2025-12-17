"""User model"""
class User:
    
    def __init__(self, user_id, username, role, name, phone=None):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.name = name
        self.phone = phone
    
    def is_admin(self):
        return self.role == 'Admin'
    
    def is_customer(self):
        return self.role == 'Customer'
    
    def is_driver(self):
        return self.role == 'Driver'
    
    def __repr__(self):
        return f"User({self.username}, {self.role}, {self.name})"
