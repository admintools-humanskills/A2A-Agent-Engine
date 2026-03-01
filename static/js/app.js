/**
 * app.js - WebSocket connection and event routing
 *
 * Bridges the WebSocket events from the FastAPI backend to the
 * ChatPanel and AgentVisualization modules.
 */

(function () {
    'use strict';

    let ws = null;
    let chat = null;
    let viz = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT = 5;

    function init() {
        // Initialize chat panel
        chat = new ChatPanel();
        chat.onSendMessage = sendMessage;

        // Initialize pixel art visualization
        const canvas = document.getElementById('pixel-canvas');
        viz = new AgentVisualization(canvas);

        // Welcome message
        chat.addSystemMessage('Welcome! Ask me to book flights, hotels, trains, event tickets, restaurants or fan shop merchandise across Europe.');

        // Connect WebSocket
        connectWebSocket();

        // Handle window resize for canvas
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
    }

    function resizeCanvas() {
        const canvas = document.getElementById('pixel-canvas');
        const panel = document.getElementById('canvas-panel');
        const size = Math.min(panel.clientWidth - 20, panel.clientHeight - 60);
        canvas.style.width = size + 'px';
        canvas.style.height = size + 'px';
    }

    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            reconnectAttempts = 0;
            updateConnectionStatus(true);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            routeEvent(data);
        };

        ws.onclose = () => {
            updateConnectionStatus(false);
            // Auto-reconnect
            if (reconnectAttempts < MAX_RECONNECT) {
                reconnectAttempts++;
                const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
                setTimeout(connectWebSocket, delay);
            }
        };

        ws.onerror = () => {
            updateConnectionStatus(false);
        };
    }

    function updateConnectionStatus(connected) {
        const dot = document.getElementById('connection-dot');
        const label = document.getElementById('connection-status');
        if (connected) {
            dot.className = 'dot dot-connected';
            label.textContent = 'Connected';
        } else {
            dot.className = 'dot dot-disconnected';
            label.textContent = 'Disconnected';
        }
    }

    function sendMessage(text) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            chat.addErrorMessage('Not connected to server. Please refresh the page.');
            chat.setProcessing(false);
            return;
        }

        ws.send(JSON.stringify({
            type: 'user_message',
            text: text,
        }));
    }

    function routeEvent(data) {
        switch (data.type) {
            case 'connected':
                // Connection confirmed by server
                break;

            case 'agent_thinking':
                chat.showTyping('Agent is thinking...');
                viz.onAgentThinking();
                break;

            case 'agent_call':
                chat.showTyping(`Calling ${data.agent_name}...`);
                chat.addToolCallMessage(data.agent_name, data.task_summary);
                viz.onAgentCall(data.agent_name, data.task_summary);
                break;

            case 'agent_response':
                chat.showTyping('Processing response...');
                chat.addToolResponseMessage(data.agent_name, data.response_summary);
                viz.onAgentResponse(data.agent_name, data.response_summary);
                break;

            case 'final_response':
                chat.hideTyping();
                chat.addAgentMessage(data.text);
                chat.setProcessing(false);
                viz.onFinalResponse();
                break;

            case 'error':
                chat.hideTyping();
                chat.addErrorMessage(data.message);
                chat.setProcessing(false);
                break;

            default:
                console.warn('Unknown event type:', data.type);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
