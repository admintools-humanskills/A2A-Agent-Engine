/**
 * chat.js - Chat panel management
 *
 * Handles displaying messages, typing indicator, and auto-scrolling.
 */

class ChatPanel {
    constructor() {
        this.messagesEl = document.getElementById('chat-messages');
        this.typingEl = document.getElementById('typing-indicator');
        this.inputEl = document.getElementById('chat-input');
        this.formEl = document.getElementById('chat-form');
        this.sendBtn = document.getElementById('chat-send');
        this.onSendMessage = null; // callback set by app.js
        this.isProcessing = false;

        this.formEl.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSend();
        });
    }

    handleSend() {
        const text = this.inputEl.value.trim();
        if (!text || this.isProcessing) return;

        this.addUserMessage(text);
        this.inputEl.value = '';
        this.setProcessing(true);

        if (this.onSendMessage) {
            this.onSendMessage(text);
        }
    }

    setProcessing(processing) {
        this.isProcessing = processing;
        this.sendBtn.disabled = processing;
        this.inputEl.disabled = processing;
        if (!processing) {
            this.inputEl.focus();
        }
    }

    showTyping(label) {
        const typingLabel = this.typingEl.querySelector('.typing-label');
        if (typingLabel && label) {
            typingLabel.textContent = label;
        }
        this.typingEl.classList.remove('hidden');
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingEl.classList.add('hidden');
    }

    addUserMessage(text) {
        const el = document.createElement('div');
        el.className = 'chat-message user';
        el.innerHTML = `<div class="msg-role">You</div><div class="msg-text">${this.escapeHtml(text)}</div>`;
        this.messagesEl.appendChild(el);
        this.scrollToBottom();
    }

    addAgentMessage(text) {
        this.hideTyping();
        const el = document.createElement('div');
        el.className = 'chat-message agent';
        el.innerHTML = `<div class="msg-role">Concierge</div><div class="msg-text">${this.formatText(text)}</div>`;
        this.messagesEl.appendChild(el);
        this.scrollToBottom();
    }

    addToolCallMessage(agentName, summary) {
        const el = document.createElement('div');
        el.className = 'chat-message tool-call';
        el.innerHTML = `
            <div class="msg-role">Calling ${this.escapeHtml(agentName)} <span class="expand-hint">[click to expand]</span></div>
            <div class="msg-text">${this.escapeHtml(this.truncate(summary, 80))}</div>
            <div class="tool-details">${this.escapeHtml(summary)}</div>
        `;
        el.addEventListener('click', () => el.classList.toggle('expanded'));
        this.messagesEl.appendChild(el);
        this.scrollToBottom();
    }

    addToolResponseMessage(agentName, summary) {
        const el = document.createElement('div');
        el.className = 'chat-message tool-response';
        el.innerHTML = `
            <div class="msg-role">Response from ${this.escapeHtml(agentName)} <span class="expand-hint">[click to expand]</span></div>
            <div class="msg-text">${this.escapeHtml(this.truncate(summary, 80))}</div>
            <div class="tool-details">${this.escapeHtml(summary)}</div>
        `;
        el.addEventListener('click', () => el.classList.toggle('expanded'));
        this.messagesEl.appendChild(el);
        this.scrollToBottom();
    }

    addErrorMessage(message) {
        this.hideTyping();
        const el = document.createElement('div');
        el.className = 'chat-message agent';
        el.style.borderColor = '#ef5350';
        el.style.background = '#3e0000';
        el.innerHTML = `<div class="msg-role" style="color:#ef5350">Error</div><div class="msg-text">${this.escapeHtml(message)}</div>`;
        this.messagesEl.appendChild(el);
        this.scrollToBottom();
    }

    addSystemMessage(text) {
        const el = document.createElement('div');
        el.className = 'chat-message agent';
        el.style.opacity = '0.6';
        el.style.borderColor = '#616161';
        el.innerHTML = `<div class="msg-role" style="color:#9e9e9e">System</div><div class="msg-text">${this.escapeHtml(text)}</div>`;
        this.messagesEl.appendChild(el);
        this.scrollToBottom();
    }

    scrollToBottom() {
        requestAnimationFrame(() => {
            this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatText(text) {
        // Basic markdown-like formatting
        let html = this.escapeHtml(text);
        // Bold: **text**
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Newlines
        html = html.replace(/\n/g, '<br>');
        return html;
    }

    truncate(text, maxLen) {
        if (text.length <= maxLen) return text;
        return text.substring(0, maxLen) + '...';
    }
}
