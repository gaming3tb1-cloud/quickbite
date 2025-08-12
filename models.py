import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """Simple user class for mock authentication"""
    def __init__(self, student_id, name, email, password=None):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.is_admin = False
    
    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

class CartItem:
    """Cart item class to store individual items in cart"""
    def __init__(self, meal_id, meal_name, meal_price, quantity=1):
        self.meal_id = meal_id
        self.meal_name = meal_name
        self.meal_price = meal_price
        self.quantity = quantity
    
    def get_total_price(self):
        return self.meal_price * self.quantity

class Cart:
    """Shopping cart class to manage user's cart items"""
    def __init__(self, student_id):
        self.student_id = student_id
        self.items = {}  # meal_id -> CartItem
        self.pickup_time = None
        self.pickup_location = None
        self.created_at = datetime.now()
    
    def add_item(self, meal_id, meal_name, meal_price, quantity=1):
        if meal_id in self.items:
            self.items[meal_id].quantity += quantity
        else:
            self.items[meal_id] = CartItem(meal_id, meal_name, meal_price, quantity)
    
    def remove_item(self, meal_id):
        if meal_id in self.items:
            del self.items[meal_id]
    
    def update_quantity(self, meal_id, quantity):
        if meal_id in self.items:
            if quantity <= 0:
                self.remove_item(meal_id)
            else:
                self.items[meal_id].quantity = quantity
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.values())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.values())
    
    def clear(self):
        self.items.clear()
        self.pickup_time = None
        self.pickup_location = None
    
    def is_empty(self):
        return len(self.items) == 0

class Order:
    """Order class to store order information"""
    def __init__(self, order_id, student_id, student_name, items, total_price,
                 pickup_time, pickup_location, order_time=None):
        self.order_id = order_id
        self.student_id = student_id
        self.student_name = student_name
        self.items = items  # List of CartItem objects
        self.total_price = total_price
        self.pickup_time = pickup_time
        self.pickup_location = pickup_location
        self.order_time = order_time or datetime.now()
        self.status = "confirmed"
        self.preparation_status = "received"  # received, preparing, ready, delivered
        self.estimated_ready_time = None
        self.actual_ready_time = None
        self.delivered_time = None
        
    def calculate_estimated_ready_time(self):
        """Calculate estimated preparation time based on items and current queue"""
        # Base preparation time per item (in minutes)
        base_prep_time = 5
        # Additional time based on number of items
        item_count = sum(item.quantity for item in self.items)
        total_prep_time = base_prep_time + (item_count * 2)
        
        # Add queue delay based on orders in same time slot
        from datetime import timedelta
        queue_delay = self.calculate_queue_delay()
        
        self.estimated_ready_time = self.order_time + timedelta(minutes=total_prep_time + queue_delay)
        return self.estimated_ready_time
    
    def calculate_queue_delay(self):
        """Calculate additional delay based on orders ahead in queue"""
        # Get orders in same time slot placed before this order
        same_slot_orders = [order for order in orders_db.values() 
                           if order.pickup_time == self.pickup_time 
                           and order.order_time < self.order_time
                           and order.status in ['confirmed', 'preparing']]
        
        # Each order ahead adds 2 minutes delay
        return len(same_slot_orders) * 2
    
    def get_delivery_progress(self):
        """Get current delivery progress percentage"""
        status_progress = {
            'received': 25,
            'preparing': 50,
            'ready': 75,
            'delivered': 100
        }
        return status_progress.get(self.preparation_status, 0)
    
    def get_estimated_delivery_time(self):
        """Get estimated delivery/ready time"""
        if not self.estimated_ready_time:
            self.calculate_estimated_ready_time()
        return self.estimated_ready_time
    
    def update_status(self, new_status):
        """Update order status and timestamps"""
        self.preparation_status = new_status
        if new_status == 'ready' and not self.actual_ready_time:
            self.actual_ready_time = datetime.now()
        elif new_status == 'delivered' and not self.delivered_time:
            self.delivered_time = datetime.now()

# In-memory storage for MVP
users_db = {}
orders_db = {}
carts_db = {}  # student_id -> Cart
order_counter = 1

# Create admin user
admin_user = User("admin", "Admin User", "admin@school.edu", "admin123")
admin_user.is_admin = True
users_db["admin"] = admin_user

def load_menu():
    """Load menu data from JSON file"""
    try:
        with open('data/menu.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"meals": []}

def get_time_slots():
    """Get available time slots for pickup"""
    return [
        "11:30 AM - 12:00 PM",
        "12:00 PM - 12:30 PM", 
        "12:30 PM - 1:00 PM",
        "1:00 PM - 1:30 PM"
    ]

def get_pickup_locations():
    """Get available pickup locations with GPS coordinates"""
    return [
        {
            "name": "Main Cafeteria",
            "lat": 28.6139,
            "lng": 77.2090,
            "description": "Main building, ground floor"
        },
        {
            "name": "Food Court", 
            "lat": 28.6145,
            "lng": 77.2095,
            "description": "Student center, first floor"
        },
        {
            "name": "Outdoor Station",
            "lat": 28.6135,
            "lng": 77.2085,
            "description": "Near sports complex"
        }
    ]

def create_user(student_id, name, email, password):
    """Create a new user"""
    if student_id in users_db:
        return False, "Student ID already exists"
    
    user = User(student_id, name, email, password)
    users_db[student_id] = user
    return True, "User created successfully"

def authenticate_user(student_id, password):
    """Authenticate user login"""
    user = users_db.get(student_id)
    if user and user.check_password(password):
        return user
    return None

# Cart management functions
def get_or_create_cart(student_id):
    """Get existing cart or create new one for student"""
    if student_id not in carts_db:
        carts_db[student_id] = Cart(student_id)
    return carts_db[student_id]

def add_to_cart(student_id, meal_id, meal_name, meal_price, quantity=1):
    """Add item to student's cart"""
    cart = get_or_create_cart(student_id)
    cart.add_item(meal_id, meal_name, meal_price, quantity)
    return cart

def remove_from_cart(student_id, meal_id):
    """Remove item from student's cart"""
    if student_id in carts_db:
        carts_db[student_id].remove_item(meal_id)

def update_cart_quantity(student_id, meal_id, quantity):
    """Update quantity of item in cart"""
    if student_id in carts_db:
        carts_db[student_id].update_quantity(meal_id, quantity)

def clear_cart(student_id):
    """Clear student's cart"""
    if student_id in carts_db:
        carts_db[student_id].clear()

def create_order_from_cart(student_id, student_name, pickup_time, pickup_location):
    """Create order from cart items"""
    global order_counter
    
    if student_id not in carts_db or carts_db[student_id].is_empty():
        return None, "Cart is empty"
    
    cart = carts_db[student_id]
    order_id = f"ORD{order_counter:04d}"
    
    # Convert cart items to order items
    order_items = list(cart.items.values())
    total_price = cart.get_total_price()
    
    order = Order(order_id, student_id, student_name, order_items, total_price,
                  pickup_time, pickup_location)
    
    # Calculate estimated ready time
    order.calculate_estimated_ready_time()
    
    orders_db[order_id] = order
    order_counter += 1
    
    # Clear cart after order
    cart.clear()
    
    return order, "Order created successfully"

def create_order(student_id, student_name, meal_name, meal_price, pickup_time, pickup_location):
    """Create a new order (legacy function for single item orders)"""
    global order_counter
    order_id = f"ORD{order_counter:04d}"
    
    # Create single cart item for backward compatibility
    cart_item = CartItem("single", meal_name, meal_price, 1)
    
    order = Order(order_id, student_id, student_name, [cart_item], meal_price,
                  pickup_time, pickup_location)
    
    # Calculate estimated ready time
    order.calculate_estimated_ready_time()
    
    orders_db[order_id] = order
    order_counter += 1
    return order

def get_orders_by_time_and_location():
    """Get orders grouped by time slot and location for admin dashboard"""
    time_slots = get_time_slots()
    locations = get_pickup_locations()
    
    summary = {}
    for time_slot in time_slots:
        summary[time_slot] = {}
        for location in locations:
            location_name = location.get('name') if isinstance(location, dict) else location
            summary[time_slot][location_name] = []
    
    for order in orders_db.values():
        if order.pickup_time in summary and order.pickup_location in summary[order.pickup_time]:
            summary[order.pickup_time][order.pickup_location].append(order)
    
    return summary

def get_orders_count_by_time_slot():
    """Get order counts by time slot to check capacity"""
    time_slots = get_time_slots()
    counts = {slot: 0 for slot in time_slots}
    
    for order in orders_db.values():
        if order.pickup_time in counts:
            counts[order.pickup_time] += 1
    
    return counts
