/**
 * AI Financial Coach - Frontend Logic
 * Handles all chat interactions, animations, and UI state
 */

// ===================================
// STATE MANAGEMENT
// ===================================

const state = {
    sessionId: generateSessionId(),
    userContext: {},
    settings: {
        personality: 'friendly',
        useEmojis: true,
        showSuggestions: true,
        typingIndicators: true,
        soundEffects: false
    },
    isTyping: false,
    messageHistory: []
};

// ===================================
// INITIALIZATION
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    loadSettings();
    setupEventListeners();
    checkForCalculatorContext();
});

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function initializeApp() {
    console.log('FinBot AI Coach initialized');
    console.log('Session ID:', state.sessionId);
    
    // Auto-resize textarea
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('input', autoResizeTextarea);
    
    // Show welcome screen initially
    document.getElementById('welcomeScreen').style.display = 'flex';
}

// ===================================
// EVENT LISTENERS
// ===================================

function setupEventListeners() {
    // Header actions
    document.getElementById('contextBtn').addEventListener('click', toggleSidebar);
    document.getElementById('settingsBtn').addEventListener('click', openSettingsModal);
    document.getElementById('clearBtn').addEventListener('click', clearConversation);
    
    // Sidebar
    document.getElementById('closeSidebar').addEventListener('click', toggleSidebar);
    document.getElementById('contextForm').addEventListener('submit', saveContext);
    document.getElementById('editContext')?.addEventListener('click', editContext);
    
    // Input area
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('messageInput').addEventListener('input', handleInputChange);
    document.getElementById('messageInput').addEventListener('keydown', handleKeyDown);
    document.getElementById('attachBtn').addEventListener('click', attachCalculatorContext);
    
    // Settings modal
    document.getElementById('closeSettingsModal').addEventListener('click', closeSettingsModal);
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
    document.getElementById('resetSettings').addEventListener('click', resetSettings);
    
    // Welcome suggestions
    document.querySelectorAll('#welcomeSuggestions .suggestion-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            sendSuggestedQuestion(e.target.textContent);
        });
    });
    
    // Click outside modal to close
    document.getElementById('settingsModal').addEventListener('click', (e) => {
        if (e.target.id === 'settingsModal') {
            closeSettingsModal();
        }
    });
}

// ===================================
// SIDEBAR MANAGEMENT
// ===================================

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

function saveContext(e) {
    e.preventDefault();
    
    const context = {
        total_capital: parseFloat(document.getElementById('totalCapital').value) || 0,
        monthly_income: parseFloat(document.getElementById('monthlyIncome').value) || 0,
        monthly_expenses: parseFloat(document.getElementById('monthlyExpenses').value) || 0,
        age: parseInt(document.getElementById('age').value) || 0,
        investment_goal: document.getElementById('investmentGoal').value || '',
        risk_tolerance: document.getElementById('riskTolerance').value || '',
        investment_allocation: parseFloat(document.getElementById('investmentAllocation').value) || 0,
        years: parseInt(document.getElementById('planningYears').value) || 0
    };
    
    // Remove zero/empty values
    Object.keys(context).forEach(key => {
        if (!context[key]) delete context[key];
    });
    
    state.userContext = context;
    updateContextBadge();
    showContextSummary();
    toggleSidebar();
    
    // Send context to backend
    updateBackendContext();
    
    showNotification('Financial context saved successfully!', 'success');
}

function showContextSummary() {
    const form = document.getElementById('contextForm');
    const summary = document.querySelector('.context-summary');
    const summaryContent = document.getElementById('contextSummaryContent');
    
    form.style.display = 'none';
    summary.style.display = 'block';
    
    let html = '';
    const labels = {
        total_capital: 'Total Capital',
        monthly_income: 'Monthly Income',
        monthly_expenses: 'Monthly Expenses',
        age: 'Age',
        investment_goal: 'Primary Goal',
        risk_tolerance: 'Risk Tolerance',
        investment_allocation: 'Investment %',
        years: 'Planning Years'
    };
    
    Object.entries(state.userContext).forEach(([key, value]) => {
        const label = labels[key] || key;
        let displayValue = value;
        
        if (['total_capital', 'monthly_income', 'monthly_expenses'].includes(key)) {
            displayValue = '$' + value.toLocaleString();
        }
        
        html += `<div><span>${label}:</span><strong>${displayValue}</strong></div>`;
    });
    
    summaryContent.innerHTML = html;
}

function editContext() {
    document.getElementById('contextForm').style.display = 'flex';
    document.querySelector('.context-summary').style.display = 'none';
}

function updateContextBadge() {
    const badge = document.getElementById('contextBadge');
    const count = Object.keys(state.userContext).length;
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
}

async function updateBackendContext() {
    try {
        const response = await fetch('/api/coach/context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                context: state.userContext
            })
        });
        
        if (!response.ok) {
            console.error('Failed to update backend context');
        }
    } catch (error) {
        console.error('Error updating context:', error);
    }
}

function checkForCalculatorContext() {
    // Check if there's calculation data from main calculator
    const calculatorData = sessionStorage.getItem('calculatorResults');
    if (calculatorData) {
        try {
            const data = JSON.parse(calculatorData);
            
            // Show import notification
            showImportNotification(data);
            
        } catch (error) {
            console.error('Error parsing calculator data:', error);
        }
    }
}

function showImportNotification(data) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.5);
        z-index: 10000;
        max-width: 350px;
        animation: slideInRight 0.3s ease;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <i class="fas fa-calculator" style="font-size: 2rem;"></i>
            <div>
                <h3 style="margin: 0; font-size: 1.1rem;">Calculation Detected!</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
                    Import your results for personalized advice?
                </p>
            </div>
        </div>
        <div style="display: flex; gap: 0.5rem;">
            <button id="importCalcBtn" style="flex: 1; padding: 0.75rem; background: white; color: #667eea; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
                Import Results
            </button>
            <button id="dismissCalcBtn" style="padding: 0.75rem; background: rgba(255,255,255,0.2); color: white; border: none; border-radius: 8px; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Event listeners
    document.getElementById('importCalcBtn').addEventListener('click', async () => {
        await importCalculationResults(data);
        notification.remove();
    });
    
    document.getElementById('dismissCalcBtn').addEventListener('click', () => {
        notification.remove();
        sessionStorage.removeItem('calculatorResults');
    });
}

async function importCalculationResults(data) {
    try {
        const response = await fetch('/api/coach/import-calculation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                calculation_data: data
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update UI context
            populateContextFromCalculator(data);
            
            // Update state
            state.userContext = {
                ...state.userContext,
                total_capital: data.total_capital,
                monthly_income: data.monthly_income,
                monthly_expenses: data.monthly_expense_allocation,
                investment_allocation: data.investment_allocation,
                years: data.years,
                calculation_results: {
                    results: data.results,
                    summary: data.summary
                }
            };
            
            updateContextBadge();
            
            showNotification(`Imported ${result.context_fields} data points! 🎉`, 'success');
            
            // Auto-suggest questions about their results
            setTimeout(() => {
                addMessage(
                    "I've imported your calculation results! I can now give you specific advice based on your projections. Try asking me:\n\n" +
                    "• \"Analyze my calculation results\"\n" +
                    "• \"Is my plan sustainable?\"\n" +
                    "• \"How can I improve my financial projections?\"\n" +
                    "• \"Explain my coverage ratio\"",
                    'bot'
                );
            }, 500);
            
            // Clear from session storage
            sessionStorage.removeItem('calculatorResults');
            
        } else {
            showNotification('Failed to import calculation results', 'error');
        }
        
    } catch (error) {
        console.error('Error importing calculation:', error);
        showNotification('Error importing calculation results', 'error');
    }
}

function populateContextFromCalculator(data) {
    if (data.total_capital) document.getElementById('totalCapital').value = data.total_capital;
    if (data.monthly_income) document.getElementById('monthlyIncome').value = data.monthly_income;
    if (data.monthly_expenses) document.getElementById('monthlyExpenses').value = data.monthly_expenses;
    if (data.investment_allocation) document.getElementById('investmentAllocation').value = data.investment_allocation;
    if (data.years) document.getElementById('planningYears').value = data.years;
    if (data.investment_goal) document.getElementById('investmentGoal').value = data.investment_goal;
}

function attachCalculatorContext() {
    // Open sidebar to add calculator context
    toggleSidebar();
    showNotification('Import your calculation data to get personalized advice', 'info');
}

// ===================================
// CHAT FUNCTIONALITY
// ===================================

function handleInputChange(e) {
    const input = e.target;
    const sendBtn = document.getElementById('sendBtn');
    const charCount = document.getElementById('charCount');
    
    const length = input.value.length;
    charCount.textContent = `${length}/2000`;
    
    sendBtn.disabled = length === 0 || length > 2000;
    
    if (length > 2000) {
        charCount.style.color = '#f5576c';
    } else {
        charCount.style.color = 'var(--text-muted)';
    }
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResizeTextarea(e) {
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message || state.isTyping) return;
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    document.getElementById('sendBtn').disabled = true;
    document.getElementById('charCount').textContent = '0/2000';
    
    // Hide welcome screen, show messages
    hideWelcomeScreen();
    
    // Add user message
    addMessage(message, 'user');
    
    // Show typing indicator
    if (state.settings.typingIndicators) {
        showTypingIndicator();
    }
    
    // Send to backend
    try {
        const response = await fetch('/api/coach/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                message: message
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (data.success) {
            // Add bot response
            addMessage(data.response, 'bot');
            
            // Update suggestions
            if (state.settings.showSuggestions) {
                updateSuggestions();
            }
            
            // Play sound
            if (state.settings.soundEffects) {
                playNotificationSound();
            }
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot', true);
            console.error('Chat error:', data.error);
        }
    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, I couldn\'t connect to the server. Please check your connection.', 'bot', true);
        console.error('Network error:', error);
    }
}

function sendSuggestedQuestion(question) {
    const input = document.getElementById('messageInput');
    input.value = question;
    input.focus();
    sendMessage();
}

function addMessage(content, role, isError = false) {
    const container = document.getElementById('messagesContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    if (isError) {
        bubble.style.background = 'linear-gradient(135deg, #f5576c 0%, #f093fb 100%)';
    }
    
    // Format message content (convert markdown-like syntax)
    bubble.innerHTML = formatMessage(content);
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    contentDiv.appendChild(bubble);
    contentDiv.appendChild(time);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    container.appendChild(messageDiv);
    
    // Scroll to bottom
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 100);
    
    // Store in history
    state.messageHistory.push({ role, content, timestamp: Date.now() });
}

function formatMessage(text) {
    // Convert markdown-like formatting to HTML
    let formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    // Convert bullet points
    formatted = formatted.replace(/^[-•]\s+(.+)/gm, '<li>$1</li>');
    if (formatted.includes('<li>')) {
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
    
    // Convert numbered lists
    formatted = formatted.replace(/^\d+\.\s+(.+)/gm, '<li>$1</li>');
    
    return '<p>' + formatted + '</p>';
}

function showTypingIndicator() {
    state.isTyping = true;
    
    const container = document.getElementById('messagesContainer');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    state.isTyping = false;
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function hideWelcomeScreen() {
    const welcome = document.getElementById('welcomeScreen');
    const messages = document.getElementById('messagesContainer');
    
    if (welcome.style.display !== 'none') {
        welcome.style.display = 'none';
        messages.classList.add('active');
    }
}

async function updateSuggestions() {
    try {
        const response = await fetch('/api/coach/suggestions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.suggestions.length > 0) {
            showSuggestionsBar(data.suggestions);
        }
    } catch (error) {
        console.error('Error fetching suggestions:', error);
    }
}

function showSuggestionsBar(suggestions) {
    const bar = document.getElementById('suggestionsBar');
    const scroll = document.getElementById('suggestionsScroll');
    
    scroll.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.addEventListener('click', () => sendSuggestedQuestion(suggestion));
        scroll.appendChild(chip);
    });
    
    bar.style.display = 'block';
}

async function clearConversation() {
    if (!confirm('Are you sure you want to clear the conversation? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/coach/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId
            })
        });
        
        if (response.ok) {
            // Clear UI
            document.getElementById('messagesContainer').innerHTML = '';
            document.getElementById('messagesContainer').classList.remove('active');
            document.getElementById('welcomeScreen').style.display = 'flex';
            document.getElementById('suggestionsBar').style.display = 'none';
            
            // Reset state
            state.messageHistory = [];
            state.sessionId = generateSessionId();
            
            showNotification('Conversation cleared successfully', 'success');
        }
    } catch (error) {
        console.error('Error clearing conversation:', error);
        showNotification('Failed to clear conversation', 'error');
    }
}

// ===================================
// SETTINGS MANAGEMENT
// ===================================

function openSettingsModal() {
    document.getElementById('settingsModal').classList.add('active');
}

function closeSettingsModal() {
    document.getElementById('settingsModal').classList.remove('active');
}

function loadSettings() {
    const saved = localStorage.getItem('finbotSettings');
    if (saved) {
        state.settings = { ...state.settings, ...JSON.parse(saved) };
    }
    
    // Apply settings to UI
    document.getElementById('personalitySelect').value = state.settings.personality;
    document.getElementById('emojiToggle').checked = state.settings.useEmojis;
    document.getElementById('suggestionsToggle').checked = state.settings.showSuggestions;
    document.getElementById('typingToggle').checked = state.settings.typingIndicators;
    document.getElementById('soundToggle').checked = state.settings.soundEffects;
}

function saveSettings() {
    state.settings = {
        personality: document.getElementById('personalitySelect').value,
        useEmojis: document.getElementById('emojiToggle').checked,
        showSuggestions: document.getElementById('suggestionsToggle').checked,
        typingIndicators: document.getElementById('typingToggle').checked,
        soundEffects: document.getElementById('soundToggle').checked
    };
    
    localStorage.setItem('finbotSettings', JSON.stringify(state.settings));
    closeSettingsModal();
    showNotification('Settings saved successfully', 'success');
}

function resetSettings() {
    state.settings = {
        personality: 'friendly',
        useEmojis: true,
        showSuggestions: true,
        typingIndicators: true,
        soundEffects: false
    };
    
    loadSettings();
    showNotification('Settings reset to defaults', 'info');
}

// ===================================
// UTILITY FUNCTIONS
// ===================================

function showNotification(message, type = 'info') {
    const colors = {
        success: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        error: 'linear-gradient(135deg, #f5576c 0%, #f093fb 100%)',
        info: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${colors[type]};
        color: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function playNotificationSound() {
    // Create a simple notification beep
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}

// ===================================
// ANIMATIONS
// ===================================

const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);

// ===================================
// EXPORT FOR DEBUGGING
// ===================================

window.FinBotState = state;
console.log('FinBot ready! Type window.FinBotState to inspect state.');
