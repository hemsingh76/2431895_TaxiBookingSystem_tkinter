import sqlite3
import hashlib
import os

class Database:
    """Database handler for taxi booking system"""
    
    def __init__(self, db_name='taxi_booking.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_default_users()
    
    def create_tables(self):
        """Create necessary tables"""
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT
            )
        ''')
        
        # Bookings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                driver_id INTEGER,
                pickup_location TEXT NOT NULL,
                dropoff_location TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES users(user_id),
                FOREIGN KEY (driver_id) REFERENCES users(user_id)
            )
        ''')
        
        self.conn.commit()
    
    def create_default_users(self):
        """Create default users if they don't exist"""
        default_user = [
            ('admin', 'admin123', 'Admin', 'System Admin', '1234567890')
        ]
        
        for username, password, role, name, phone in default_user:
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            try:
                self.cursor.execute('''
                    INSERT INTO users (username, password, role, name, phone)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, hashed_pw, role, name, phone))
            except sqlite3.IntegrityError:
                pass
        
        self.conn.commit()
    
    def authenticate(self, username, password):
        """Authenticate user"""
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''
            SELECT user_id, username, role, name FROM users
            WHERE username = ? AND password = ?
        ''', (username, hashed_pw))
        return self.cursor.fetchone()
    
    def get_all_drivers(self):
        """Get all drivers"""
        self.cursor.execute('''
            SELECT user_id, name FROM users WHERE role = 'Driver'
        ''')
        return self.cursor.fetchall()
    
    def check_driver_availability(self, driver_id, booking_date, booking_time):
        """Check if driver has overlapping bookings"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM bookings 
            WHERE driver_id = ? 
            AND booking_date = ? 
            AND booking_time = ?
            AND status NOT IN ('Cancelled', 'Completed')
        ''', (driver_id, booking_date, booking_time))
        
        return self.cursor.fetchone()[0] == 0
    
    def create_user(self, username, password, role, name, phone):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, role, name, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_pw, role, name, phone))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        
    def create_driver(self, username, password, full_name, phone, vehicle_no, license_no):
        """Create a new driver user"""
        return self.create_user(username, password, 'Driver', full_name, phone)

    
    def close(self):
        """Close database connection"""
        self.conn.close()