// ============================================
// BuyReal - Main JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            try {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                // Alert might already be closed
            }
        });
    }, 5000);
    
    // Quantity buttons for cart
    setupQuantityButtons();
    
    // Image preview for file uploads
    setupImagePreview();
    
    // Confirm delete dialogs
    setupDeleteConfirmations();
    
    // Get location button
    setupLocationButton();
});

// Quantity increment/decrement buttons
function setupQuantityButtons() {
    document.querySelectorAll('.quantity-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var input = this.closest('.input-group').querySelector('.quantity-input');
            if (!input) return;
            
            var currentValue = parseInt(input.value) || 1;
            var maxValue = parseInt(input.getAttribute('max')) || 99;
            var minValue = parseInt(input.getAttribute('min')) || 1;
            
            if (this.classList.contains('btn-plus')) {
                if (currentValue < maxValue) {
                    input.value = currentValue + 1;
                }
            } else if (this.classList.contains('btn-minus')) {
                if (currentValue > minValue) {
                    input.value = currentValue - 1;
                }
            }
            
            // Trigger change event
            input.dispatchEvent(new Event('change'));
        });
    });
}

// Get user's geolocation
function setupLocationButton() {
    var btn = document.getElementById('getLocationBtn');
    if (!btn) return;
    
    btn.addEventListener('click', function() {
        var latInput = document.getElementById('id_latitude');
        var lngInput = document.getElementById('id_longitude');
        
        if (!latInput || !lngInput) return;
        
        if (navigator.geolocation) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    latInput.value = position.coords.latitude.toFixed(6);
                    lngInput.value = position.coords.longitude.toFixed(6);
                    
                    btn.innerHTML = '<i class="bi bi-check"></i> Done';
                    btn.classList.remove('btn-outline-secondary');
                    btn.classList.add('btn-success');
                    btn.disabled = false;
                    
                    setTimeout(function() {
                        btn.innerHTML = '<i class="bi bi-geo-alt"></i> Get';
                        btn.classList.remove('btn-success');
                        btn.classList.add('btn-outline-secondary');
                    }, 2000);
                },
                function(error) {
                    btn.innerHTML = '<i class="bi bi-geo-alt"></i> Get';
                    btn.disabled = false;
                    alert('Unable to get location: ' + error.message);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        } else {
            alert('Geolocation is not supported by your browser.');
        }
    });
}

// Image preview before upload
function setupImagePreview() {
    var imageInput = document.getElementById('id_image');
    var previewContainer = document.getElementById('imagePreview');
    
    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', function(e) {
            var file = e.target.files[0];
            if (file) {
                // Validate file size (5MB max)
                if (file.size > 5 * 1024 * 1024) {
                    alert('File is too large. Maximum size is 5MB.');
                    e.target.value = '';
                    previewContainer.innerHTML = '';
                    return;
                }
                
                var reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = '<img src="' + e.target.result + '" class="img-fluid rounded" style="max-height: 200px;">';
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = '';
            }
        });
    }
}

// Confirm delete dialogs
function setupDeleteConfirmations() {
    document.querySelectorAll('.delete-btn, [data-confirm]').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Toast notification function
function showToast(message, type) {
    type = type || 'info';
    
    var toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }
    
    var bgClass = 'bg-primary';
    if (type === 'success') bgClass = 'bg-success';
    if (type === 'error' || type === 'danger') bgClass = 'bg-danger';
    if (type === 'warning') bgClass = 'bg-warning text-dark';
    
    var toastId = 'toast_' + Date.now();
    var toastHtml = 
        '<div id="' + toastId + '" class="toast align-items-center text-white ' + bgClass + ' border-0 show mb-2" role="alert">' +
            '<div class="d-flex">' +
                '<div class="toast-body">' + message + '</div>' +
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
            '</div>' +
        '</div>';
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Remove toast after 4 seconds
    setTimeout(function() {
        var toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.remove('show');
            setTimeout(function() {
                toast.remove();
            }, 300);
        }
    }, 4000);
}

// Format currency
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

// CSRF token for AJAX requests
function getCsrfToken() {
    var cookieValue = null;
    var name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}