from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app
from models import (
    load_menu, get_time_slots, get_pickup_locations, 
    create_user, authenticate_user, create_order, create_order_from_cart,
    get_orders_by_time_and_location, get_orders_count_by_time_slot,
    get_or_create_cart, add_to_cart, remove_from_cart, update_cart_quantity, clear_cart,
    users_db, orders_db, carts_db
)

@app.route('/')
def home():
    """Public home page - accessible to everyone"""
    if 'user' in session:
        user = users_db.get(session['user'])
        # If admin is already logged in, redirect to dashboard
        if user and user.is_admin:
            return redirect(url_for('admin_dashboard'))
        
        # Get cart info for logged in users
        cart = get_or_create_cart(session['user'])
        cart_items = cart.get_total_items()
        return render_template('index.html', user=user, cart_items=cart_items)
    else:
        return render_template('index.html', user=None, cart_items=0)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Student login page"""
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        password = request.form.get('password')
        
        if not student_id or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        user = authenticate_user(student_id, password)
        if user:
            session['user'] = user.student_id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.name}!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        else:
            flash('Invalid student ID or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration page"""
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([student_id, name, email, password, confirm_password]):
            flash('Please fill in all fields', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if password and len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        success, message = create_user(student_id, name, email, password)
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')

@app.route('/menu')
def menu():
    """Display menu and allow meal selection (login required for ordering)"""
    menu_data = load_menu()
    time_slots = get_time_slots()
    locations = get_pickup_locations()
    
    # Get current order counts to show capacity
    order_counts = get_orders_count_by_time_slot()
    
    # Check if user is logged in
    user_logged_in = 'user' in session
    
    # Get user's cart
    cart = None
    if user_logged_in:
        cart = get_or_create_cart(session['user'])
    
    return render_template('menu.html', 
                         menu=menu_data, 
                         time_slots=time_slots,
                         locations=locations,
                         order_counts=order_counts,
                         max_capacity=125,  # 500 total / 4 time slots
                         user_logged_in=user_logged_in,
                         cart=cart)

@app.route('/order', methods=['POST'])
def place_order():
    """Process order placement"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get form data
    meal_id = request.form.get('meal_id')
    pickup_time = request.form.get('pickup_time')
    pickup_location = request.form.get('pickup_location')
    
    if not all([meal_id, pickup_time, pickup_location]):
        flash('Please complete all order details', 'error')
        return redirect(url_for('menu'))
    
    # Check capacity for selected time slot
    order_counts = get_orders_count_by_time_slot()
    if pickup_time and order_counts.get(pickup_time, 0) >= 125:
        flash('Sorry, this time slot is full. Please select another time.', 'error')
        return redirect(url_for('menu'))
    
    # Load menu to get meal details
    menu_data = load_menu()
    selected_meal = None
    for meal in menu_data.get('meals', []):
        if str(meal['id']) == meal_id:
            selected_meal = meal
            break
    
    if not selected_meal:
        flash('Invalid meal selection', 'error')
        return redirect(url_for('menu'))
    
    # Create order
    order = create_order(
        session['user'],
        session['user_name'],
        selected_meal['name'],
        selected_meal['price'],
        pickup_time,
        pickup_location
    )
    
    # Store order in session for confirmation page
    session['last_order_id'] = order.order_id
    
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_confirmation'))

# Cart Routes
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    """Add item to cart"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Login required'}), 401
    
    meal_id = request.form.get('meal_id')
    quantity = int(request.form.get('quantity', 1))
    
    if not meal_id:
        return jsonify({'success': False, 'message': 'Meal ID required'}), 400
    
    # Load menu to get meal details
    menu_data = load_menu()
    selected_meal = None
    for meal in menu_data.get('meals', []):
        if str(meal['id']) == meal_id:
            selected_meal = meal
            break
    
    if not selected_meal:
        return jsonify({'success': False, 'message': 'Invalid meal selection'}), 400
    
    # Add to cart
    cart = add_to_cart(session['user'], meal_id, selected_meal['name'], 
                       selected_meal['price'], quantity)
    
    return jsonify({
        'success': True, 
        'message': f'{selected_meal["name"]} added to cart',
        'cart_count': cart.get_total_items(),
        'cart_total': cart.get_total_price()
    })

@app.route('/cart')
def view_cart():
    """View cart page"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    cart = get_or_create_cart(session['user'])
    time_slots = get_time_slots()
    locations = get_pickup_locations()
    order_counts = get_orders_count_by_time_slot()
    
    return render_template('cart.html', 
                         cart=cart,
                         time_slots=time_slots,
                         locations=locations,
                         order_counts=order_counts,
                         max_capacity=125)

@app.route('/update_cart', methods=['POST'])
def update_cart_route():
    """Update cart item quantity"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Login required'}), 401
    
    meal_id = request.form.get('meal_id')
    quantity = int(request.form.get('quantity', 0))
    
    update_cart_quantity(session['user'], meal_id, quantity)
    cart = get_or_create_cart(session['user'])
    
    return jsonify({
        'success': True,
        'cart_count': cart.get_total_items(),
        'cart_total': cart.get_total_price()
    })

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart_route():
    """Remove item from cart"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Login required'}), 401
    
    meal_id = request.form.get('meal_id')
    remove_from_cart(session['user'], meal_id)
    cart = get_or_create_cart(session['user'])
    
    return jsonify({
        'success': True,
        'cart_count': cart.get_total_items(),
        'cart_total': cart.get_total_price()
    })

@app.route('/place_cart_order', methods=['POST'])
def place_cart_order():
    """Place order from cart items"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    pickup_time = request.form.get('pickup_time')
    pickup_location = request.form.get('pickup_location')
    
    if not all([pickup_time, pickup_location]):
        flash('Please complete all order details', 'error')
        return redirect(url_for('view_cart'))
    
    # Check capacity for selected time slot
    order_counts = get_orders_count_by_time_slot()
    if pickup_time and order_counts.get(pickup_time, 0) >= 125:
        flash('Sorry, this time slot is full. Please select another time.', 'error')
        return redirect(url_for('view_cart'))
    
    # Create order from cart
    order, message = create_order_from_cart(
        session['user'],
        session['user_name'],
        pickup_time,
        pickup_location
    )
    
    if order:
        # Store order in session for confirmation page
        session['last_order_id'] = order.order_id
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_confirmation'))
    else:
        flash(message, 'error')
        return redirect(url_for('view_cart'))

@app.route('/confirmation')
def order_confirmation():
    """Order confirmation page"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    order_id = session.get('last_order_id')
    if not order_id or order_id not in orders_db:
        flash('No recent order found', 'error')
        return redirect(url_for('menu'))
    
    order = orders_db[order_id]
    return render_template('confirmation.html', order=order)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard showing orders by time and location"""
    if 'user' not in session or not session.get('is_admin'):
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    orders_summary = get_orders_by_time_and_location()
    order_counts = get_orders_count_by_time_slot()
    total_orders = len(orders_db)
    
    return render_template('admin.html', 
                         orders_summary=orders_summary,
                         order_counts=order_counts,
                         total_orders=total_orders)

@app.route('/admin/update_order_status', methods=['POST'])
def update_order_status():
    """Admin route to update order status for testing delivery tracking"""
    if 'user' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')
    
    if not order_id or not new_status:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
    
    order = orders_db.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    # Valid status transitions
    valid_statuses = ['received', 'preparing', 'ready', 'delivered']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    # Update order status
    order.update_status(new_status)
    
    return jsonify({
        'success': True, 
        'message': f'Order {order_id} status updated to {new_status}',
        'order_id': order_id,
        'new_status': new_status,
        'progress': order.get_delivery_progress()
    })

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/orders')
def user_orders():
    """View user's order history"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get user's orders
    user_orders = [order for order in orders_db.values() 
                   if order.student_id == session['user']]
    
    # Sort by order time (newest first)
    user_orders.sort(key=lambda x: x.order_time, reverse=True)
    
    return render_template('orders.html', orders=user_orders)

@app.route('/track_order/<order_id>')
def track_order(order_id):
    """Track a specific order with delivery time estimation"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    order = orders_db.get(order_id)
    
    # Check if order exists and belongs to current user
    if not order or order.student_id != session['user']:
        flash('Order not found or access denied', 'error')
        return redirect(url_for('user_orders'))
    
    return render_template('order_tracking.html', order=order)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('base.html'), 500
