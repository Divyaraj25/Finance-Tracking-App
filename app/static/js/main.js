// app/static/js/main.js
/**
 * Expense Tracker System - Main JavaScript
 * Version: 1.1.0
 */

// Global user preferences (will be loaded from API)
let userPreferences = {
  dateFormat: 'YYYY-MM-DD',
  timeFormat: '24h',
  timezone: 'local',
  weekStart: 'monday',
  numberFormat: '1,234.56',
  currency: 'USD'
};

// Load user preferences on page load
async function loadUserPreferences() {
  try {
    const response = await fetch('/api/v1/profile/settings');
    const data = await response.json();
    if (data.success) {
      userPreferences = {
        ...userPreferences,
        ...data.data
      };
      console.log('User preferences loaded:', userPreferences);

      // Dispatch event for other scripts that need preferences
      window.dispatchEvent(new CustomEvent('preferencesLoaded', { detail: userPreferences }));
    }
  } catch (error) {
    console.error('Failed to load user preferences:', error);
  }
}

// Enhanced formatDate with user preferences
window.formatDate = function (dateString) {
  if (!dateString) return 'N/A';

  try {
    // Handle MongoDB ISODate format (object with $date)
    if (typeof dateString === 'object' && dateString !== null) {
      if (dateString.$date) {
        dateString = dateString.$date;
      } else {
        return 'Invalid Date';
      }
    }

    // Handle string dates
    const date = new Date(dateString);

    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.warn('Invalid date:', dateString);
      return 'Invalid Date';
    }

    // Format based on user preference
    const format = userPreferences.dateFormat || 'YYYY-MM-DD';

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const shortMonth = date.toLocaleString('default', { month: 'short' });
    const shortYear = String(year).slice(-2);

    switch (format) {
      case 'MM/DD/YYYY':
        return `${month}/${day}/${year}`;
      case 'DD/MM/YYYY':
        return `${day}/${month}/${year}`;
      case 'MM-DD-YYYY':
        return `${month}-${day}-${year}`;
      case 'DD-MM-YYYY':
        return `${day}-${month}-${year}`;
      case 'MMM D, YYYY':
        return `${shortMonth} ${parseInt(day)}, ${year}`;
      case 'D MMM YYYY':
        return `${parseInt(day)} ${shortMonth} ${year}`;
      case 'YYYY-MM-DD':
      default:
        return `${year}-${month}-${day}`;
    }
  } catch (e) {
    console.error('Date formatting error:', e);
    return 'Invalid Date';
  }
};

// Enhanced formatDateTime with user preferences
window.formatDateTime = function (dateString) {
  if (!dateString) return 'N/A';

  try {
    // Handle MongoDB ISODate format (object with $date)
    if (typeof dateString === 'object' && dateString !== null) {
      if (dateString.$date) {
        dateString = dateString.$date;
      } else {
        return 'Invalid Date';
      }
    }

    // Handle string dates
    const date = new Date(dateString);

    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.warn('Invalid date:', dateString);
      return 'Invalid Date';
    }

    const datePart = window.formatDate(dateString);

    // Format time based on user preference
    const timeFormat = userPreferences.timeFormat || '24h';

    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');

    if (timeFormat === '12h') {
      const ampm = hours >= 12 ? 'PM' : 'AM';
      hours = hours % 12 || 12;
      return `${datePart} ${hours}:${minutes} ${ampm}`;
    } else {
      // 24h format
      hours = String(hours).padStart(2, '0');
      return `${datePart} ${hours}:${minutes}`;
    }
  } catch (e) {
    console.error('DateTime formatting error:', e);
    return 'Invalid Date';
  }
};

// Enhanced formatCurrency with user preferences
window.formatCurrency = function (amount, currency = null) {
  try {
    const currencyCode = currency || userPreferences.currency || 'USD';

    // Handle number format preference
    const numberFormat = userPreferences.numberFormat || '1,234.56';
    let options = {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    };

    // Apply number format preferences
    if (numberFormat === '1.234,56') {
      // European format
      return new Intl.NumberFormat('de-DE', options).format(amount);
    } else if (numberFormat === '1 234,56') {
      // French format
      return new Intl.NumberFormat('fr-FR', options).format(amount);
    } else if (numberFormat === "1'234.56") {
      // Swiss format - custom handling
      const formatted = new Intl.NumberFormat('de-CH', options).format(amount);
      return formatted.replace("'", '’');
    } else {
      // US/UK format (default)
      return new Intl.NumberFormat('en-US', options).format(amount);
    }
  } catch (e) {
    console.error('Currency formatting error:', e);
    return `$${parseFloat(amount).toFixed(2)}`;
  }
};

// Enhanced formatNumber with user preferences
window.formatNumber = function (number, decimals = 2) {
  try {
    const numberFormat = userPreferences.numberFormat || '1,234.56';

    if (numberFormat === '1.234,56') {
      // European format
      return new Intl.NumberFormat('de-DE', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(number);
    } else if (numberFormat === '1 234,56') {
      // French format
      return new Intl.NumberFormat('fr-FR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(number);
    } else if (numberFormat === "1'234.56") {
      // Swiss format
      const formatted = new Intl.NumberFormat('de-CH', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(number);
      return formatted.replace("'", '’');
    } else {
      // US/UK format (default)
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(number);
    }
  } catch (e) {
    return parseFloat(number).toFixed(decimals);
  }
};

// Get week start based on user preference
window.getWeekStart = function () {
  return userPreferences.weekStart || 'monday';
};

// Get first day of week as number (0=Sunday, 1=Monday, 6=Saturday)
window.getFirstDayOfWeek = function () {
  const weekStart = userPreferences.weekStart || 'monday';
  const firstDayMap = {
    sunday: 0,
    monday: 1,
    saturday: 6
  };
  return firstDayMap[weekStart] || 1;
};

// Global utility functions
window.escapeHtml = function (unsafe) {
  if (!unsafe) return '';
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};

window.getInitials = function (name) {
  if (!name) return '?';
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

window.generateColor = function (string) {
  if (!string) return '#4361ee';
  let hash = 0;
  for (let i = 0; i < string.length; i++) {
    hash = string.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = '#';
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    color += ('00' + value.toString(16)).substr(-2);
  }
  return color;
};

window.downloadFile = function (content, fileName, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.click();
  URL.revokeObjectURL(url);
};

window.copyToClipboard = function (text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      Swal.fire({
        icon: 'success',
        title: 'Copied!',
        text: 'Text copied to clipboard',
        timer: 1500,
        showConfirmButton: false
      });
    })
    .catch(() => {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Failed to copy to clipboard'
      });
    });
};

window.debounce = function (func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

window.throttle = function (func, limit) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// API Service
const ApiService = {
  baseUrl: '/api/v1',
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }
    return data;
  },
  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  },
  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },
  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};

// Notification Service
const NotificationService = {
  show(message, type = 'info') {
    Swal.fire({
      icon: type,
      title: message,
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true
    });
  },
  success(message) {
    this.show(message, 'success');
  },
  error(message) {
    this.show(message, 'error');
  },
  warning(message) {
    this.show(message, 'warning');
  },
  info(message) {
    this.show(message, 'info');
  },
  confirm(message) {
    return Swal.fire({
      title: 'Are you sure?',
      text: message,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes',
      cancelButtonText: 'No'
    });
  }
};

// Cache Service
const CacheService = {
  set(key, value, ttl = 3600) {
    const item = { value, expiry: Date.now() + ttl * 1000 };
    localStorage.setItem(key, JSON.stringify(item));
  },
  get(key) {
    const itemStr = localStorage.getItem(key);
    if (!itemStr) return null;
    try {
      const item = JSON.parse(itemStr);
      if (Date.now() > item.expiry) {
        localStorage.removeItem(key);
        return null;
      }
      return item.value;
    } catch {
      return null;
    }
  },
  remove(key) {
    localStorage.removeItem(key);
  },
  clear() {
    localStorage.clear();
  }
};

// Chart Theme with dynamic colors based on theme
const ChartTheme = {
  light: {
    background: '#ffffff',
    textColor: '#212529',
    gridColor: '#e9ecef',
    colors: ['#4361ee', '#4cc9f0', '#f72585', '#f8961e', '#4895ef', '#3f37c9']
  },
  dark: {
    background: '#252b33',
    textColor: '#ffffff',
    gridColor: '#3a414a',
    colors: ['#6d8eff', '#4cc9f0', '#ff5e7d', '#ff9f43', '#5cabff', '#5f5cf0']
  }
};

// Initialize everything on DOM load
document.addEventListener('DOMContentLoaded', async function () {
  // Load user preferences first
  await loadUserPreferences();

  // Initialize theme
  initTheme();

  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Initialize select2
  if (typeof $.fn.select2 !== 'undefined') {
    $('.select2').select2({
      theme: 'bootstrap-5',
      width: '100%'
    });
  }

  // Handle flash messages
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
      alert.classList.add('fade');
      setTimeout(() => alert.remove(), 3000);
    });
  }, 5000);

  // Add loading state to buttons
  document.querySelectorAll('button[type="submit"]').forEach(button => {
    button.addEventListener('click', function () {
      if (this.form) {
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
      }
    });
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + N: New transaction
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault();
      const modal = document.getElementById('addTransactionModal');
      if (modal) new bootstrap.Modal(modal).show();
    }
    // /: Focus search
    if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      const searchInput = document.getElementById('searchFilter');
      if (searchInput) searchInput.focus();
    }
    // Esc: Close modals
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal.show').forEach(modal => {
        bootstrap.Modal.getInstance(modal)?.hide();
      });
    }
  });
});

// Theme functions
function initTheme() {
  const theme = userPreferences.theme || localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon(theme);
  // Save to localStorage for backward compatibility
  localStorage.setItem('theme', theme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  document.documentElement.setAttribute('data-theme', newTheme);
  updateThemeIcon(newTheme);
  localStorage.setItem('theme', newTheme);

  // Update user preferences if needed
  if (userPreferences) {
    userPreferences.theme = newTheme;
  }

  // Reload charts if they exist
  if (typeof refreshCharts === 'function') {
    refreshCharts();
  }
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.className = theme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
  }
}

// Export data function
window.exportData = function (format) {
  const params = new URLSearchParams(window.location.search);
  const startDate = params.get('start_date') || '';
  const endDate = params.get('end_date') || '';

  let url = `/api/v1/export/${format}?type=all`;
  if (startDate) url += `&start_date=${startDate}`;
  if (endDate) url += `&end_date=${endDate}`;

  window.location.href = url;
};

// Export to global scope
window.ApiService = ApiService;
window.NotificationService = NotificationService;
window.CacheService = CacheService;
window.userPreferences = userPreferences;
