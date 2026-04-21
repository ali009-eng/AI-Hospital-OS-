/**
 * AI Triage Assistant Dashboard
 * Real-time patient queue management and monitoring
 */
class TriageDashboard {
    constructor() {
        this.apiBaseUrl = window.location.origin || 'http://localhost:8000';
        this.wsUrl = this.apiBaseUrl.replace('http', 'ws') + '/ws';
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }
    
    init() {
        this.updateCurrentTime();
        setInterval(() => this.updateCurrentTime(), 1000);
        
        this.connectWebSocket();
        this.loadData();
        this.initializeCharts();
        this.setupChatInterface();
        
        // Set up auto-refresh
        const refreshInterval = parseInt(this.getConfig('DASHBOARD_REFRESH_INTERVAL', '30')) * 1000;
        this.refreshInterval = setInterval(() => this.loadData(), refreshInterval);
    }
    
    getConfig(key, defaultValue) {
        // Get config from meta tags or use default
        const meta = document.querySelector(`meta[name="${key}"]`);
        return meta ? meta.content : defaultValue;
    }
    
    updateCurrentTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        const dateStr = now.toLocaleDateString();
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = `${dateStr} ${timeStr}`;
        }
    }
    
    connectWebSocket() {
        try {
            this.ws = new WebSocket(this.wsUrl);
            this.updateWebSocketStatus('connecting');
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateWebSocketStatus('connected');
                this.reconnectAttempts = 0;
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateWebSocketStatus('disconnected');
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateWebSocketStatus('disconnected');
                this.attemptReconnect();
            };
            
        } catch (e) {
            console.error('Error connecting WebSocket:', e);
            this.updateWebSocketStatus('disconnected');
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
                this.connectWebSocket();
            }, this.reconnectDelay);
        }
    }
    
    updateWebSocketStatus(status) {
        const statusElement = document.getElementById('websocketStatus');
        if (!statusElement) return;
        
        statusElement.className = `websocket-status ${status}`;
        const icons = {
            'connected': '🟢',
            'disconnected': '🔴',
            'connecting': '🟡'
        };
        const texts = {
            'connected': 'Connected',
            'disconnected': 'Disconnected',
            'connecting': 'Connecting...'
        };
        
        statusElement.innerHTML = `<i class="fas fa-circle me-1"></i> ${texts[status]}`;
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'patient_classified':
                this.loadData(); // Refresh dashboard
                this.showNotification('New patient classified', 'success');
                break;
            case 'connection':
                console.log('WebSocket connection confirmed');
                break;
            default:
                console.log('Unknown WebSocket message:', data);
        }
    }
    
    async loadData() {
        try {
            // Load dashboard data
            const dashboardResponse = await fetch(`${this.apiBaseUrl}/dashboard`);
            const dashboardData = await dashboardResponse.json();
            this.updateDashboard(dashboardData);
            
            // Load surveillance data
            const surveillanceResponse = await fetch(`${this.apiBaseUrl}/surveillance`);
            const surveillanceData = await surveillanceResponse.json();
            this.updateSurveillance(surveillanceData);
            
        } catch (e) {
            console.error('Error loading data:', e);
            this.showNotification('Error loading data', 'error');
        }
    }
    
    updateDashboard(data) {
        // Update statistics
        document.getElementById('total-patients').textContent = data.total_patients || 0;
        document.getElementById('high-priority').textContent = data.high_priority_patients || 0;
        document.getElementById('active-alerts').textContent = data.active_alerts || 0;
        document.getElementById('avg-wait-time').textContent = 
            data.average_wait_time ? `${data.average_wait_time.toFixed(1)}` : '0';
        
        // Update patient queue
        this.updatePatientQueue(data.queue || []);
        
        // Update triage distribution chart
        if (data.triage_distribution) {
            this.updateTriageChart(data.triage_distribution);
        }
    }
    
    updatePatientQueue(queue) {
        const queueContainer = document.getElementById('patient-queue');
        if (!queueContainer) return;
        
        // Hide loading
        const loading = queueContainer.parentElement.querySelector('.loading');
        if (loading) loading.classList.remove('show');
        
        if (!queue || queue.length === 0) {
            queueContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No patients in queue
                </div>
            `;
            return;
        }
        
        queueContainer.innerHTML = queue.map((patient, index) => {
            const level = patient.triage_level || 3;
            const esiLevels = window.Config?.ESI_LEVELS || {
                1: "Immediate - Life-threatening",
                2: "High Risk - Urgent",
                3: "Medium - Stable but needs evaluation",
                4: "Lower Medium - Stable with minor issues",
                5: "Minor - Non-urgent"
            };
            const esiLevel = patient.esi_level || esiLevels[level] || 'Unknown';
            const arrivalTime = this.formatTime(patient.arrival_time || patient.timestamp);
            
            return `
                <div class="card mb-2 patient-row level-${level} fade-in" style="animation-delay: ${index * 0.1}s">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-1">
                                <div class="queue-position ${level <= 2 ? 'high-priority' : level <= 3 ? 'medium-priority' : 'low-priority'}">
                                    ${index + 1}
                                </div>
                            </div>
                            <div class="col-md-2">
                                <strong>${patient.patient_id || 'N/A'}</strong>
                                <div class="text-muted small">${arrivalTime}</div>
                            </div>
                            <div class="col-md-2">
                                <span class="badge bg-danger triage-level-${level}">
                                    ESI ${level}: ${esiLevel.split(' - ')[0]}
                                </span>
                            </div>
                            <div class="col-md-4">
                                <div><strong>${patient.chief_complaint || 'No complaint'}</strong></div>
                                <div class="text-muted small">${patient.reasoning || ''}</div>
                            </div>
                            <div class="col-md-3 text-end">
                                <button class="btn btn-sm btn-primary" onclick="viewPatientDetails('${patient.patient_id}')">
                                    <i class="fas fa-eye"></i> View
                                </button>
                                <button class="btn btn-sm btn-warning" onclick="replacePatient('${patient.patient_id}')">
                                    <i class="fas fa-exchange-alt"></i> Replace
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deletePatient('${patient.patient_id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    updateSurveillance(data) {
        const alertsContainer = document.getElementById('surveillance-alerts');
        if (!alertsContainer) return;
        
        // Hide loading
        const loading = alertsContainer.parentElement.querySelector('.loading');
        if (loading) loading.classList.remove('show');
        
        const alerts = data.alerts || [];
        if (alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    No active alerts
                </div>
            `;
            return;
        }
        
        alertsContainer.innerHTML = alerts.map(alert => {
            const severity = alert.severity?.toLowerCase() || 'medium';
            return `
                <div class="alert alert-${severity} alert-card alert-${severity} mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="alert-heading">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                ${alert.alert_type || 'Alert'}
                            </h5>
                            <p class="mb-1">${alert.description || ''}</p>
                            ${alert.recommendations ? `
                                <ul class="mb-0 mt-2">
                                    ${alert.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                                </ul>
                            ` : ''}
                        </div>
                        <div class="text-end">
                            <div class="badge bg-${severity === 'high' ? 'danger' : 'warning'}">
                                ${alert.affected_patients || 0} patients
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Update trends chart
        if (data.trends) {
            this.updateTrendsChart(data.trends);
        }
    }
    
    initializeCharts() {
        // Triage Distribution Chart
        const triageCtx = document.getElementById('triageChart');
        if (triageCtx) {
            this.charts.triage = new Chart(triageCtx, {
                type: 'pie',
                data: {
                    labels: ['ESI 1', 'ESI 2', 'ESI 3', 'ESI 4', 'ESI 5'],
                    datasets: [{
                        data: [0, 0, 0, 0, 0],
                        backgroundColor: [
                            '#e74c3c',
                            '#f39c12',
                            '#17a2b8',
                            '#27ae60',
                            '#6c757d'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // Trends Chart
        const trendsCtx = document.getElementById('trendsChart');
        if (trendsCtx) {
            this.charts.trends = new Chart(trendsCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Total Cases',
                            data: [],
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'High Priority',
                            data: [],
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
    
    updateTriageChart(distribution) {
        if (!this.charts.triage) return;
        
        this.charts.triage.data.datasets[0].data = [
            distribution.level_1 || 0,
            distribution.level_2 || 0,
            distribution.level_3 || 0,
            distribution.level_4 || 0,
            distribution.level_5 || 0
        ];
        this.charts.triage.update();
    }
    
    updateTrendsChart(trends) {
        if (!this.charts.trends || !trends) return;
        
        const sortedTrends = [...trends].reverse(); // Reverse to show oldest first
        
        this.charts.trends.data.labels = sortedTrends.map(t => {
            const date = new Date(t.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        
        this.charts.trends.data.datasets[0].data = sortedTrends.map(t => t.daily_cases || 0);
        this.charts.trends.data.datasets[1].data = sortedTrends.map(t => t.high_priority_cases || 0);
        
        this.charts.trends.update();
    }
    
    setupChatInterface() {
        const chatInput = document.getElementById('chat-input');
        const chatSendBtn = document.getElementById('chat-send-btn');
        
        if (chatInput && chatSendBtn) {
            chatSendBtn.addEventListener('click', () => this.sendChatMessage());
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendChatMessage();
                }
            });
            
            // Auto-resize textarea
            chatInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 150) + 'px';
            });
        }
    }
    
    async sendChatMessage() {
        const chatInput = document.getElementById('chat-input');
        const chatMessages = document.getElementById('chat-messages');
        
        if (!chatInput || !chatMessages) return;
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addChatMessage('user', message);
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator(true);
        
        try {
            // In a real implementation, this would call an API endpoint
            // For now, simulate a response
            await this.simulateChatResponse(message);
        } catch (e) {
            console.error('Error sending chat message:', e);
            this.addChatMessage('agent', 'Sorry, I encountered an error. Please try again.');
        } finally {
            this.showTypingIndicator(false);
        }
    }
    
    async simulateChatResponse(message) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simple response logic (in production, this would call an AI endpoint)
        let response = "I can help you with triage classification, ESI levels, and patient information. ";
        
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('esi') || lowerMessage.includes('triage')) {
            response += "ESI (Emergency Severity Index) levels range from 1 (Immediate/Life-threatening) to 5 (Minor/Non-urgent). ";
        }
        if (lowerMessage.includes('patient') || lowerMessage.includes('queue')) {
            response += "Check the patient queue above for current cases. ";
        }
        
        response += "For specific questions about a patient, please provide the patient ID.";
        
        this.addChatMessage('agent', response);
    }
    
    addChatMessage(sender, message) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${sender}`;
        bubble.textContent = message;
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString();
        
        bubble.appendChild(time);
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    showTypingIndicator(show) {
        const typingIndicator = document.getElementById('chat-typing');
        if (typingIndicator) {
            if (show) {
                typingIndicator.classList.add('show');
            } else {
                typingIndicator.classList.remove('show');
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show notification-toast`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    formatTime(timestamp) {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
}

// Global functions
function refreshDashboard() {
    if (window.dashboard) {
        window.dashboard.loadData();
        window.dashboard.showNotification('Dashboard refreshed', 'success');
    }
}

function viewPatientDetails(patientId) {
    alert(`View details for patient: ${patientId}\n\nThis would open a detailed patient view in a production system.`);
}

function deletePatient(patientId) {
    if (confirm(`Are you sure you want to remove patient ${patientId} from the queue?`)) {
        console.log('Deleting patient:', patientId);
        // In production, this would call an API endpoint
        if (window.dashboard) {
            window.dashboard.showNotification(`Patient ${patientId} removed`, 'success');
            window.dashboard.loadData();
        }
    }
}

function replacePatient(patientId) {
    document.getElementById('currentPatientId').value = patientId;
    const modal = new bootstrap.Modal(document.getElementById('replacePatientModal'));
    modal.show();
}

function submitPatientReplacement() {
    const form = document.getElementById('replacePatientForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const patientData = {
        patient_id: document.getElementById('newPatientId').value,
        age: parseInt(document.getElementById('newPatientAge').value) || null,
        gender: document.getElementById('newPatientGender').value || null,
        chief_complaint: document.getElementById('newPatientComplaint').value || null,
        heart_rate: parseInt(document.getElementById('newPatientHeartRate').value) || null,
        respiratory_rate: parseInt(document.getElementById('newPatientRespRate').value) || null,
        oxygen_saturation: parseFloat(document.getElementById('newPatientO2Sat').value) || null,
        temperature: parseFloat(document.getElementById('newPatientTemp').value) || null,
        blood_pressure: document.getElementById('newPatientBP').value || null,
        pain_level: parseInt(document.getElementById('newPatientPain').value) || null
    };
    
    // Submit to API
    fetch(`${window.dashboard?.apiBaseUrl || 'http://localhost:8000'}/triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
    })
    .then(response => response.json())
    .then(data => {
        window.dashboard?.showNotification('Patient replaced successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('replacePatientModal')).hide();
        window.dashboard?.loadData();
        form.reset();
    })
    .catch(error => {
        console.error('Error:', error);
        window.dashboard?.showNotification('Error replacing patient', 'error');
    });
}

function addSamplePatients() {
    const samplePatients = [
        {
            patient_id: 'SAMPLE_001',
            age: 45,
            gender: 'M',
            chief_complaint: 'Chest pain and shortness of breath',
            heart_rate: 110,
            respiratory_rate: 24,
            oxygen_saturation: 92,
            temperature: 37.2,
            blood_pressure: '140/90',
            pain_level: 7
        },
        {
            patient_id: 'SAMPLE_002',
            age: 28,
            gender: 'F',
            chief_complaint: 'Fever and body aches',
            heart_rate: 95,
            respiratory_rate: 20,
            oxygen_saturation: 98,
            temperature: 38.5,
            blood_pressure: '120/80',
            pain_level: 5
        }
    ];
    
    samplePatients.forEach((patient, index) => {
        setTimeout(() => {
            fetch(`${window.dashboard?.apiBaseUrl || 'http://localhost:8000'}/triage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(patient)
            })
            .then(response => response.json())
            .then(data => {
                if (index === samplePatients.length - 1) {
                    window.dashboard?.showNotification(`${samplePatients.length} sample patients added`, 'success');
                    window.dashboard?.loadData();
                }
            })
            .catch(error => console.error('Error:', error));
        }, index * 500); // Stagger requests
    });
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (window.dashboard) {
            window.dashboard.sendChatMessage();
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new TriageDashboard();
    
    // Global Config (from server or defaults)
    window.Config = window.Config || {
        ESI_LEVELS: {
            1: "Immediate - Life-threatening",
            2: "High Risk - Urgent",
            3: "Medium - Stable but needs evaluation",
            4: "Lower Medium - Stable with minor issues",
            5: "Minor - Non-urgent"
        }
    };
});