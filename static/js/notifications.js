// Notification handling for SPAS

var NotificationSystem = {
    init: function() {
        this.checkPermission();
        this.loadNotifications();
        this.setupEventListeners();
        this.startPolling();
    },
    
    checkPermission: function() {
        if (!("Notification" in window)) {
            console.log("This browser does not support desktop notification");
            return;
        }
        
        if (Notification.permission !== "granted" && Notification.permission !== "denied") {
            Notification.requestPermission();
        }
    },
    
    showNotification: function(title, options = {}) {
        if (Notification.permission === "granted") {
            var notification = new Notification(title, {
                icon: '/static/images/logo.png',
                badge: '/static/images/logo.png',
                ...options
            });
            
            notification.onclick = function() {
                window.focus();
                if (options.url) {
                    window.location.href = options.url;
                }
            };
        }
    },
    
    loadNotifications: function() {
        $.get('/api/notifications', function(data) {
            NotificationSystem.updateNotificationBadge(data.unread_count);
            NotificationSystem.renderNotifications(data.notifications);
        });
    },
    
    updateNotificationBadge: function(count) {
        var badge = $('#notification-badge');
        if (count > 0) {
            badge.text(count).show();
        } else {
            badge.hide();
        }
    },
    
    renderNotifications: function(notifications) {
        var container = $('#notification-list');
        container.empty();
        
        if (notifications.length === 0) {
            container.html('<li class="dropdown-item text-muted">No notifications</li>');
            return;
        }
        
        notifications.forEach(function(notif) {
            var item = `
                <li>
                    <a class="dropdown-item ${notif.is_read ? '' : 'unread'}" href="${notif.url || '#'}">
                        <div class="d-flex align-items-center">
                            <div class="flex-shrink-0">
                                <i class="fas fa-${notif.icon || 'bell'} text-purple"></i>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <h6 class="mb-1">${notif.title}</h6>
                                <small class="text-muted">${notif.message}</small>
                                <small class="text-muted d-block">${notif.time}</small>
                            </div>
                        </div>
                    </a>
                </li>
            `;
            container.append(item);
        });
    },
    
    setupEventListeners: function() {
        $('#mark-all-read').click(function() {
            $.post('/api/notifications/mark-all-read', function() {
                NotificationSystem.loadNotifications();
            });
        });
        
        $('#notification-bell').click(function() {
            NotificationSystem.loadNotifications();
        });
    },
    
    startPolling: function() {
        setInterval(function() {
            NotificationSystem.loadNotifications();
        }, 30000); // Poll every 30 seconds
    },
    
    sendNotification: function(userId, title, message, type = 'info') {
        $.post('/api/notifications/send', {
            user_id: userId,
            title: title,
            message: message,
            type: type
        });
    },
    
    broadcastNotification: function(title, message, role = null, departmentId = null) {
        $.post('/api/notifications/broadcast', {
            title: title,
            message: message,
            role: role,
            department_id: departmentId
        });
    }
};

// Initialize notification system when document is ready
$(document).ready(function() {
    if ($('#notification-system').length) {
        NotificationSystem.init();
    }
});

// WebSocket connection for real-time notifications (if using Socket.IO)
function initWebSocket() {
    var socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to notification server');
    });
    
    socket.on('notification', function(data) {
        NotificationSystem.showNotification(data.title, {
            body: data.message,
            url: data.url
        });
        NotificationSystem.loadNotifications();
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from notification server');
    });
}