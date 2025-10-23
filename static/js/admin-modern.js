// TRINARY MLM - Modern Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize modern admin panel
    initAdminPanel();
    initSidebar();
    initDashboard();
    initTables();
    initForms();
    initAnimations();
});

// Admin Panel Initialization
function initAdminPanel() {
    // Add loading states
    addLoadingStates();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize notifications
    initNotifications();
    
    // Initialize search
    initSearch();
}

// Sidebar Management
function initSidebar() {
    const sidebar = document.querySelector('.admin-sidebar');
    const main = document.querySelector('.admin-main');
    const toggle = document.querySelector('.sidebar-toggle');
    
    if (toggle) {
        toggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            main.classList.toggle('sidebar-collapsed');
            
            // Save state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed);
        });
    }
    
    // Restore sidebar state
    const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
        main.classList.add('sidebar-collapsed');
    }
    
    // Mobile sidebar
    const mobileToggle = document.querySelector('.mobile-sidebar-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
    }
    
    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });
}

// Dashboard Enhancements
function initDashboard() {
    // Animate dashboard cards
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Real-time updates for dashboard
    updateDashboardStats();
    
    // Auto-refresh dashboard data
    setInterval(updateDashboardStats, 30000); // 30 seconds
}

// Update Dashboard Statistics
function updateDashboardStats() {
    // This would typically fetch data from your API
    // For now, we'll simulate with random updates
    const statElements = document.querySelectorAll('.dashboard-card-value');
    
    statElements.forEach(element => {
        const currentValue = parseInt(element.textContent);
        const change = Math.floor(Math.random() * 10) - 5; // -5 to +5
        const newValue = Math.max(0, currentValue + change);
        
        // Animate the change
        animateNumber(element, currentValue, newValue);
    });
}

// Animate Number Changes
function animateNumber(element, start, end) {
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// Table Enhancements
function initTables() {
    const tables = document.querySelectorAll('.admin-table');
    
    tables.forEach(table => {
        // Add sorting functionality
        addTableSorting(table);
        
        // Add row selection
        addRowSelection(table);
        
        // Add inline editing
        addInlineEditing(table);
    });
}

// Add Table Sorting
function addTableSorting(table) {
    const headers = table.querySelectorAll('th[data-sortable]');
    
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const column = this.dataset.column;
            const isAscending = this.classList.contains('sort-asc');
            
            // Remove sort classes from all headers
            headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            
            // Add sort class to current header
            this.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
            
            // Sort table rows
            sortTable(table, column, !isAscending);
        });
    });
}

// Sort Table Function
function sortTable(table, column, ascending) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`[data-column="${column}"]`)?.textContent || '';
        const bValue = b.querySelector(`[data-column="${column}"]`)?.textContent || '';
        
        if (ascending) {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Add Row Selection
function addRowSelection(table) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        row.addEventListener('click', function(e) {
            if (e.target.type !== 'checkbox' && e.target.type !== 'button') {
                this.classList.toggle('selected');
            }
        });
    });
}

// Add Inline Editing
function addInlineEditing(table) {
    const editableCells = table.querySelectorAll('[data-editable]');
    
    editableCells.forEach(cell => {
        cell.addEventListener('dblclick', function() {
            const currentValue = this.textContent;
            const input = document.createElement('input');
            input.value = currentValue;
            input.className = 'admin-form-input';
            input.style.width = '100%';
            input.style.border = '2px solid var(--primary-color)';
            
            this.innerHTML = '';
            this.appendChild(input);
            input.focus();
            input.select();
            
            input.addEventListener('blur', function() {
                const newValue = this.value;
                cell.textContent = newValue;
                
                // Save changes (you would typically send to server)
                saveCellValue(cell, newValue);
            });
            
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    this.blur();
                }
            });
        });
    });
}

// Save Cell Value
function saveCellValue(cell, value) {
    // This would typically send data to your server
    console.log('Saving value:', value, 'for cell:', cell);
    
    // Show success notification
    showNotification('Value saved successfully!', 'success');
}

// Form Enhancements
function initForms() {
    const forms = document.querySelectorAll('.admin-form');
    
    forms.forEach(form => {
        // Add form validation
        addFormValidation(form);
        
        // Add auto-save
        addAutoSave(form);
        
        // Add file upload preview
        addFileUploadPreview(form);
    });
}

// Add Form Validation
function addFormValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
    
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showNotification('Please fix the errors before submitting.', 'danger');
        }
    });
}

// Validate Field
function validateField(field) {
    const value = field.value.trim();
    const required = field.hasAttribute('required');
    const minLength = field.getAttribute('minlength');
    const maxLength = field.getAttribute('maxlength');
    const pattern = field.getAttribute('pattern');
    
    let isValid = true;
    let errorMessage = '';
    
    if (required && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    } else if (minLength && value.length < parseInt(minLength)) {
        isValid = false;
        errorMessage = `Minimum length is ${minLength} characters.`;
    } else if (maxLength && value.length > parseInt(maxLength)) {
        isValid = false;
        errorMessage = `Maximum length is ${maxLength} characters.`;
    } else if (pattern && !new RegExp(pattern).test(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid format.';
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

// Show Field Error
function showFieldError(field, message) {
    field.classList.add('error');
    
    let errorElement = field.parentNode.querySelector('.field-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.style.color = 'var(--danger-color)';
        errorElement.style.fontSize = '0.8rem';
        errorElement.style.marginTop = '0.25rem';
        field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

// Clear Field Error
function clearFieldError(field) {
    field.classList.remove('error');
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
}

// Add Auto Save
function addAutoSave(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let saveTimeout;
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                autoSaveForm(form);
            }, 2000); // Save after 2 seconds of inactivity
        });
    });
}

// Auto Save Form
function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // This would typically send data to your server
    console.log('Auto-saving form data:', data);
    
    showNotification('Changes saved automatically', 'info');
}

// Add File Upload Preview
function addFileUploadPreview(form) {
    const fileInputs = form.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = this.files;
            const preview = this.parentNode.querySelector('.file-preview');
            
            if (preview) {
                preview.innerHTML = '';
                
                Array.from(files).forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <div class="file-icon">📄</div>
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${formatFileSize(file.size)}</div>
                        </div>
                    `;
                    preview.appendChild(fileItem);
                });
            }
        });
    });
}

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Search Functionality
function initSearch() {
    const searchInput = document.querySelector('.admin-search input');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
    }
}

// Perform Search
function performSearch(query) {
    if (query.length < 2) return;
    
    // This would typically search your data
    console.log('Searching for:', query);
    
    // Highlight search results
    highlightSearchResults(query);
}

// Highlight Search Results
function highlightSearchResults(query) {
    const elements = document.querySelectorAll('[data-searchable]');
    
    elements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const queryLower = query.toLowerCase();
        
        if (text.includes(queryLower)) {
            element.classList.add('search-highlight');
        } else {
            element.classList.remove('search-highlight');
        }
    });
}

// Tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.dataset.tooltip);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

// Show Tooltip
function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'admin-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: var(--dark-color);
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        font-size: 0.8rem;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.2s;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    
    setTimeout(() => tooltip.style.opacity = '1', 10);
}

// Hide Tooltip
function hideTooltip() {
    const tooltip = document.querySelector('.admin-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Notifications
function initNotifications() {
    // Create notification container
    const container = document.createElement('div');
    container.className = 'admin-notifications';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        pointer-events: none;
    `;
    document.body.appendChild(container);
}

// Show Notification
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.admin-notifications');
    const notification = document.createElement('div');
    
    notification.className = `admin-notification admin-notification-${type}`;
    notification.style.cssText = `
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.5rem;
        box-shadow: var(--shadow-soft);
        border-left: 4px solid var(--${type}-color);
        pointer-events: auto;
        cursor: pointer;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div class="notification-icon">${getNotificationIcon(type)}</div>
            <div class="notification-message">${message}</div>
            <button class="notification-close" style="background: none; border: none; font-size: 1.2rem; cursor: pointer;">×</button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove
    setTimeout(() => {
        removeNotification(notification);
    }, duration);
    
    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', () => {
        removeNotification(notification);
    });
}

// Remove Notification
function removeNotification(notification) {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Get Notification Icon
function getNotificationIcon(type) {
    const icons = {
        success: '✅',
        warning: '⚠️',
        danger: '❌',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

// Loading States
function addLoadingStates() {
    const buttons = document.querySelectorAll('.admin-btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.type === 'submit' || this.classList.contains('loading-trigger')) {
                showButtonLoading(this);
            }
        });
    });
}

// Show Button Loading
function showButtonLoading(button) {
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    button.style.opacity = '0.7';
    
    // Simulate loading (replace with actual async operation)
    setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
        button.style.opacity = '1';
    }, 2000);
}

// Animations
function initAnimations() {
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.dashboard-card, .admin-table-container, .admin-form');
    animatedElements.forEach(el => observer.observe(el));
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for global use
window.AdminPanel = {
    showNotification,
    showButtonLoading,
    performSearch,
    updateDashboardStats
};
