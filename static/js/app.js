// QuickBite JavaScript Application
// Handles dynamic interactions and form validation

document.addEventListener('DOMContentLoaded', function() {
    console.log('QuickBite app initialized');
    
    // Initialize form handlers
    initializeOrderForm();
    initializeRegistrationForm();
    initializeMealSelection();
    initializeAdminDashboard();
    initializeGPSFeatures();
});

/**
 * Initialize order form functionality
 */
function initializeOrderForm() {
    const orderForm = document.getElementById('orderForm');
    if (!orderForm) return;
    
    const mealRadios = document.querySelectorAll('input[name="meal_id"]');
    const pickupTimeSelect = document.getElementById('pickup_time');
    const pickupLocationSelect = document.getElementById('pickup_location');
    const placeOrderBtn = document.getElementById('place-order-btn');
    const orderSummary = document.getElementById('order-summary');
    
    // Add event listeners for form validation
    if (mealRadios.length > 0) {
        mealRadios.forEach(radio => {
            radio.addEventListener('change', updateOrderSummary);
        });
    }
    
    if (pickupTimeSelect) {
        pickupTimeSelect.addEventListener('change', updateOrderSummary);
    }
    
    if (pickupLocationSelect) {
        pickupLocationSelect.addEventListener('change', updateOrderSummary);
    }
    
    /**
     * Update order summary and enable/disable order button
     */
    function updateOrderSummary() {
        const selectedMeal = document.querySelector('input[name="meal_id"]:checked');
        const selectedTime = pickupTimeSelect?.value;
        const selectedLocation = pickupLocationSelect?.value;
        
        // Check if all required fields are selected
        const canPlaceOrder = selectedMeal && selectedTime && selectedLocation;
        
        if (placeOrderBtn) {
            placeOrderBtn.disabled = !canPlaceOrder;
        }
        
        // Show/hide order summary
        if (orderSummary) {
            if (canPlaceOrder) {
                orderSummary.style.display = 'block';
                
                // Get meal details
                const mealCard = selectedMeal.closest('.meal-card');
                const mealName = mealCard.querySelector('.card-title').textContent.trim();
                const mealPrice = mealCard.querySelector('.badge').textContent;
                
                // Update summary content
                document.getElementById('selected-meal').innerHTML = 
                    `<strong>Meal:</strong> ${mealName}`;
                document.getElementById('selected-time').innerHTML = 
                    `<strong>Time:</strong> ${selectedTime}`;
                document.getElementById('selected-location').innerHTML = 
                    `<strong>Location:</strong> ${selectedLocation}`;
                document.getElementById('total-price').innerHTML = 
                    `<strong>Total:</strong> ${mealPrice}`;
            } else {
                orderSummary.style.display = 'none';
            }
        }
        
        // Update meal card selection styling
        document.querySelectorAll('.meal-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        if (selectedMeal) {
            selectedMeal.closest('.meal-card').classList.add('selected');
        }
    }
    
    // Form submission handler
    orderForm.addEventListener('submit', function(e) {
        const selectedMeal = document.querySelector('input[name="meal_id"]:checked');
        const selectedTime = pickupTimeSelect?.value;
        const selectedLocation = pickupLocationSelect?.value;
        
        if (!selectedMeal || !selectedTime || !selectedLocation) {
            e.preventDefault();
            showAlert('Please complete all order details before submitting.', 'warning');
            return false;
        }
        
        // Show loading state
        if (placeOrderBtn) {
            placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            placeOrderBtn.disabled = true;
        }
    });
}

/**
 * Initialize meal selection functionality
 */
function initializeMealSelection() {
    const mealCards = document.querySelectorAll('.meal-card');
    
    mealCards.forEach(card => {
        card.addEventListener('click', function() {
            const radio = this.querySelector('input[name="meal_id"]');
            if (radio) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change'));
            }
        });
    });
}

/**
 * Initialize registration form validation
 */
function initializeRegistrationForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;
    
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    
    function validatePasswords() {
        const password = passwordField?.value;
        const confirmPassword = confirmPasswordField?.value;
        
        if (password && confirmPassword) {
            if (password !== confirmPassword) {
                confirmPasswordField.setCustomValidity('Passwords do not match');
                confirmPasswordField.classList.add('is-invalid');
            } else {
                confirmPasswordField.setCustomValidity('');
                confirmPasswordField.classList.remove('is-invalid');
                confirmPasswordField.classList.add('is-valid');
            }
        }
    }
    
    if (passwordField && confirmPasswordField) {
        passwordField.addEventListener('input', validatePasswords);
        confirmPasswordField.addEventListener('input', validatePasswords);
    }
    
    registerForm.addEventListener('submit', function(e) {
        validatePasswords();
        
        // Check if form is valid
        if (!registerForm.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        registerForm.classList.add('was-validated');
    });
}

/**
 * Initialize admin dashboard functionality
 */
function initializeAdminDashboard() {
    // Auto-refresh functionality for admin dashboard
    if (window.location.pathname.includes('/admin')) {
        console.log('Admin dashboard loaded');
        
        // Add auto-refresh every 30 seconds
        setInterval(function() {
            const refreshBtn = document.querySelector('button[onclick="window.location.reload()"]');
            if (refreshBtn && !document.hidden) {
                // Only refresh if page is visible
                console.log('Auto-refreshing admin dashboard...');
                window.location.reload();
            }
        }, 30000); // 30 seconds
    }
}

/**
 * Show alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, warning, danger, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alertContainer, main.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
}

/**
 * Get appropriate icon for alert type
 * @param {string} type - Alert type
 * @returns {string} Icon class
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'danger': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

/**
 * Validate time slot capacity
 * @param {string} timeSlot - Selected time slot
 * @returns {boolean} Whether time slot is available
 */
function validateTimeSlotCapacity(timeSlot) {
    const timeSlotOption = document.querySelector(`option[value="${timeSlot}"]`);
    return timeSlotOption && !timeSlotOption.disabled;
}

/**
 * Handle form loading states
 * @param {HTMLFormElement} form - Form element
 * @param {boolean} loading - Loading state
 */
function setFormLoading(form, loading) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const inputs = form.querySelectorAll('input, select, textarea');
    
    if (loading) {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');
        }
        inputs.forEach(input => input.disabled = true);
    } else {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
        inputs.forEach(input => input.disabled = false);
    }
}

// Utility functions for better UX
window.QuickBite = {
    showAlert,
    formatCurrency,
    validateTimeSlotCapacity,
    setFormLoading
};

// Global functions for map integration
window.openLocationMap = openLocationMap;
window.getDirectionsToPickup = getDirectionsToPickup;

/**
 * Open location on map (for confirmation page)
 * @param {string} locationName - Name of pickup location
 */
function openLocationMap(locationName) {
    const locations = {
        "Main Cafeteria": { lat: 28.6139, lng: 77.2090 },
        "Food Court": { lat: 28.6145, lng: 77.2095 },
        "Outdoor Station": { lat: 28.6135, lng: 77.2085 }
    };
    
    const location = locations[locationName];
    if (location) {
        const mapUrl = `https://www.google.com/maps?q=${location.lat},${location.lng}&t=m&z=16`;
        window.open(mapUrl, '_blank');
        showAlert(`Opening ${locationName} on map...`, 'success');
    }
}

/**
 * Get directions to pickup location (for confirmation page)
 * @param {string} locationName - Name of pickup location
 */
function getDirectionsToPickup(locationName) {
    const locations = {
        "Main Cafeteria": { lat: 28.6139, lng: 77.2090 },
        "Food Court": { lat: 28.6145, lng: 77.2095 },
        "Outdoor Station": { lat: 28.6135, lng: 77.2085 }
    };
    
    const location = locations[locationName];
    if (location) {
        const directionsUrl = `https://www.google.com/maps/dir//${location.lat},${location.lng}`;
        window.open(directionsUrl, '_blank');
        showAlert(`Getting directions to ${locationName}...`, 'success');
    }
}

// Handle page navigation loading states
window.addEventListener('beforeunload', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => setFormLoading(form, true));
});

// Handle responsive table scrolling
function makeTablesResponsive() {
    const tables = document.querySelectorAll('table:not(.table-responsive table)');
    tables.forEach(table => {
        if (!table.closest('.table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Initialize responsive tables on load
document.addEventListener('DOMContentLoaded', makeTablesResponsive);

/**
 * Initialize GPS and location features
 */
function initializeGPSFeatures() {
    const pickupLocationSelect = document.getElementById('pickup_location');
    const showMapBtn = document.getElementById('show-map-btn');
    const getDirectionsBtn = document.getElementById('get-directions-btn');
    
    if (!pickupLocationSelect) return;
    
    let userLocation = null;
    
    // Get user's current location on page load
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                console.log('User location obtained:', userLocation);
                updateLocationDistances();
            },
            function(error) {
                console.log('Location access denied or failed:', error.message);
                showAlert('Location access denied. You can still use the app without GPS features.', 'info');
            }
        );
    }
    
    // Handle location selection
    pickupLocationSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const hasLocation = selectedOption.value && selectedOption.dataset.lat;
        
        if (showMapBtn) showMapBtn.disabled = !hasLocation;
        if (getDirectionsBtn) getDirectionsBtn.disabled = !hasLocation;
        
        if (hasLocation) {
            updateLocationDistance(selectedOption);
        }
    });
    
    // Show map functionality
    if (showMapBtn) {
        showMapBtn.addEventListener('click', function() {
            const selectedOption = pickupLocationSelect.options[pickupLocationSelect.selectedIndex];
            if (selectedOption.dataset.lat) {
                showLocationOnMap(selectedOption);
            }
        });
    }
    
    // Get directions functionality
    if (getDirectionsBtn) {
        getDirectionsBtn.addEventListener('click', function() {
            const selectedOption = pickupLocationSelect.options[pickupLocationSelect.selectedIndex];
            if (selectedOption.dataset.lat) {
                getDirectionsToLocation(selectedOption, userLocation);
            }
        });
    }
    
    /**
     * Update distances for all locations
     */
    function updateLocationDistances() {
        if (!userLocation) return;
        
        Array.from(pickupLocationSelect.options).forEach(option => {
            if (option.dataset.lat) {
                const distance = calculateDistance(
                    userLocation.lat, userLocation.lng,
                    parseFloat(option.dataset.lat), parseFloat(option.dataset.lng)
                );
                
                const originalText = option.textContent.split(' (')[0];
                option.textContent = `${originalText} (${distance.toFixed(1)} km away)`;
            }
        });
    }
    
    /**
     * Update distance for selected location
     */
    function updateLocationDistance(option) {
        if (!userLocation || !option.dataset.lat) return;
        
        const distance = calculateDistance(
            userLocation.lat, userLocation.lng,
            parseFloat(option.dataset.lat), parseFloat(option.dataset.lng)
        );
        
        showAlert(`Selected location is ${distance.toFixed(1)} km away from your current position.`, 'info');
    }
}

/**
 * Calculate distance between two GPS coordinates using Haversine formula
 * @param {number} lat1 - Latitude of first point
 * @param {number} lon1 - Longitude of first point
 * @param {number} lat2 - Latitude of second point
 * @param {number} lon2 - Longitude of second point
 * @returns {number} Distance in kilometers
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of Earth in kilometers
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

/**
 * Convert degrees to radians
 * @param {number} deg - Degrees
 * @returns {number} Radians
 */
function toRad(deg) {
    return deg * (Math.PI / 180);
}

/**
 * Show location on map (opens Google Maps)
 * @param {HTMLOptionElement} locationOption - Selected location option
 */
function showLocationOnMap(locationOption) {
    const lat = locationOption.dataset.lat;
    const lng = locationOption.dataset.lng;
    const name = locationOption.value;
    
    const mapUrl = `https://www.google.com/maps?q=${lat},${lng}&t=m&z=16`;
    window.open(mapUrl, '_blank');
    
    showAlert(`Opening ${name} on map...`, 'success');
}

/**
 * Get directions to location
 * @param {HTMLOptionElement} locationOption - Selected location option
 * @param {Object} userLocation - User's current location
 */
function getDirectionsToLocation(locationOption, userLocation) {
    const lat = locationOption.dataset.lat;
    const lng = locationOption.dataset.lng;
    const name = locationOption.value;
    
    let directionsUrl;
    
    if (userLocation) {
        // From user's location to destination
        directionsUrl = `https://www.google.com/maps/dir/${userLocation.lat},${userLocation.lng}/${lat},${lng}`;
    } else {
        // Just show destination (user can set their own starting point)
        directionsUrl = `https://www.google.com/maps/dir//${lat},${lng}`;
    }
    
    window.open(directionsUrl, '_blank');
    showAlert(`Getting directions to ${name}...`, 'success');
}

/**
 * Request location permission and get user coordinates
 * @returns {Promise} Promise that resolves with user location
 */
function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by this browser'));
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => resolve({
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                accuracy: position.coords.accuracy
            }),
            error => reject(error),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            }
        );
    });
}
