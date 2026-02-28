/**
 * animation.js - Canvas animation engine
 *
 * Manages the pixel art visualization: agent states, traveling packets,
 * speech bubbles, particles, and the main render loop.
 */

// ==================== Agent State Machine ====================

const AgentState = {
    IDLE: 'idle',
    RECEIVING: 'receiving',
    WORKING: 'working',
    RESPONDING: 'responding',
    DONE: 'done',
};

class AgentStateManager {
    constructor() {
        this.states = {};
        // Initialize all agents as IDLE
        Object.keys(AGENTS).forEach(key => {
            this.states[key] = AgentState.IDLE;
        });
    }

    setState(agentKey, state) {
        this.states[agentKey] = state;
    }

    getState(agentKey) {
        return this.states[agentKey] || AgentState.IDLE;
    }

    getActiveAgents() {
        const active = new Set();
        Object.entries(this.states).forEach(([key, state]) => {
            if (state !== AgentState.IDLE) {
                active.add(key);
            }
        });
        return active;
    }

    resetAll() {
        Object.keys(this.states).forEach(key => {
            this.states[key] = AgentState.IDLE;
        });
    }
}

// ==================== Traveling Packet ====================

class TravelingPacket {
    /**
     * @param {number} fromX - Start X
     * @param {number} fromY - Start Y
     * @param {number} toX - End X
     * @param {number} toY - End Y
     * @param {string} color - Packet color
     * @param {string} type - 'envelope' or 'document'
     * @param {function} onArrive - Callback when packet arrives
     */
    constructor(fromX, fromY, toX, toY, color, type, onArrive) {
        this.fromX = fromX;
        this.fromY = fromY;
        this.toX = toX;
        this.toY = toY;
        this.color = color;
        this.type = type || 'envelope';
        this.onArrive = onArrive;
        this.progress = 0;
        this.speed = 0.02;
        this.done = false;
        this.arrived = false;
    }

    update() {
        if (this.done) return;
        this.progress += this.speed;
        if (this.progress >= 1) {
            this.progress = 1;
            this.done = true;
            this.arrived = true;
            if (this.onArrive) this.onArrive();
        }
    }

    draw(ctx, frame) {
        if (this.done) return;

        const t = this.progress;
        const x = this.fromX + (this.toX - this.fromX) * t;
        const y = this.fromY + (this.toY - this.fromY) * t;

        // Sinusoidal wobble perpendicular to travel direction
        const dx = this.toX - this.fromX;
        const dy = this.toY - this.fromY;
        const len = Math.sqrt(dx * dx + dy * dy);
        const nx = -dy / len;
        const ny = dx / len;
        const wobble = Math.sin(t * Math.PI * 4 + frame * 0.1) * 4;
        const drawX = x + nx * wobble;
        const drawY = y + ny * wobble;

        ctx.save();
        if (this.type === 'envelope') {
            // Envelope: 10x7 px rectangle
            ctx.fillStyle = '#fff9c4';
            ctx.fillRect(drawX - 5, drawY - 3, 10, 7);
            ctx.fillStyle = this.color;
            // Flap triangle
            ctx.beginPath();
            ctx.moveTo(drawX - 5, drawY - 3);
            ctx.lineTo(drawX, drawY + 1);
            ctx.lineTo(drawX + 5, drawY - 3);
            ctx.closePath();
            ctx.fill();
            // Border
            ctx.strokeStyle = '#bdbdbd';
            ctx.lineWidth = 0.5;
            ctx.strokeRect(drawX - 5, drawY - 3, 10, 7);
        } else {
            // Document: 8x10 px
            ctx.fillStyle = '#e0e0e0';
            ctx.fillRect(drawX - 4, drawY - 5, 8, 10);
            ctx.fillStyle = this.color;
            ctx.fillRect(drawX - 3, drawY - 3, 6, 1);
            ctx.fillRect(drawX - 3, drawY - 1, 6, 1);
            ctx.fillRect(drawX - 3, drawY + 1, 4, 1);
            // Border
            ctx.strokeStyle = '#9e9e9e';
            ctx.lineWidth = 0.5;
            ctx.strokeRect(drawX - 4, drawY - 5, 8, 10);
        }
        ctx.restore();

        // Trailing sparkle
        if (frame % 3 === 0) {
            ctx.fillStyle = this.color;
            ctx.globalAlpha = 0.5;
            ctx.fillRect(drawX - 1 + (Math.random() - 0.5) * 6, drawY - 1 + (Math.random() - 0.5) * 6, 2, 2);
            ctx.globalAlpha = 1;
        }
    }
}

// ==================== Speech Bubble ====================

class SpeechBubble {
    /**
     * @param {number} x - Position X (agent center)
     * @param {number} y - Position Y (agent center)
     * @param {string} text - Display text
     * @param {string} color - Border/accent color
     * @param {number} duration - Total duration in frames (default ~180 = 3s at 60fps)
     */
    constructor(x, y, text, color, duration) {
        this.x = x;
        this.y = y - 40; // Above the agent
        this.text = text.length > 40 ? text.substring(0, 37) + '...' : text;
        this.color = color || '#e0e0e0';
        this.duration = duration || 180;
        this.age = 0;
        this.done = false;

        // Fade phases: 15 frames in, hold, 15 frames out
        this.fadeIn = 15;
        this.fadeOut = 15;
    }

    update() {
        if (this.done) return;
        this.age++;
        if (this.age >= this.duration) {
            this.done = true;
        }
    }

    draw(ctx) {
        if (this.done) return;

        // Calculate opacity
        let alpha = 1;
        if (this.age < this.fadeIn) {
            alpha = this.age / this.fadeIn;
        } else if (this.age > this.duration - this.fadeOut) {
            alpha = (this.duration - this.age) / this.fadeOut;
        }

        ctx.save();
        ctx.globalAlpha = Math.max(0, alpha);

        // Measure text
        ctx.font = '6px "Press Start 2P", monospace';
        const metrics = ctx.measureText(this.text);
        const textWidth = Math.min(metrics.width, 160);
        const padding = 6;
        const bubbleW = textWidth + padding * 2;
        const bubbleH = 18;
        const bx = this.x - bubbleW / 2;
        const by = this.y - bubbleH;

        // Bubble background
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(bx, by, bubbleW, bubbleH);

        // Bubble border (pixel style - no rounded corners)
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 1;
        ctx.strokeRect(bx, by, bubbleW, bubbleH);

        // Pointer triangle
        ctx.fillStyle = '#1a1a2e';
        ctx.beginPath();
        ctx.moveTo(this.x - 4, by + bubbleH);
        ctx.lineTo(this.x, by + bubbleH + 5);
        ctx.lineTo(this.x + 4, by + bubbleH);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = this.color;
        ctx.beginPath();
        ctx.moveTo(this.x - 4, by + bubbleH);
        ctx.lineTo(this.x, by + bubbleH + 5);
        ctx.lineTo(this.x + 4, by + bubbleH);
        ctx.stroke();

        // Text
        ctx.fillStyle = '#e0e0e0';
        ctx.font = '6px "Press Start 2P", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.text, this.x, by + bubbleH / 2, 160);

        ctx.restore();
    }
}

// ==================== Particle System ====================

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.vx = (Math.random() - 0.5) * 3;
        this.vy = (Math.random() - 0.5) * 3 - 1;
        this.life = 1;
        this.decay = 0.02 + Math.random() * 0.02;
        this.size = 2;
        this.done = false;
    }

    update() {
        if (this.done) return;
        this.x += this.vx;
        this.y += this.vy;
        this.vy += 0.05; // gravity
        this.life -= this.decay;
        if (this.life <= 0) {
            this.done = true;
        }
    }

    draw(ctx) {
        if (this.done) return;
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.fillRect(Math.floor(this.x), Math.floor(this.y), this.size, this.size);
        ctx.restore();
    }
}

function emitParticles(particles, x, y, color, count) {
    count = count || 10;
    for (let i = 0; i < count; i++) {
        particles.push(new Particle(x, y, color));
    }
}

// ==================== Main Visualization ====================

class AgentVisualization {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.frame = 0;
        this.stateManager = new AgentStateManager();
        this.packets = [];
        this.bubbles = [];
        this.particles = [];
        this.running = true;

        // Done flash effect
        this.flashAlpha = 0;

        this.initStatusBar();
        this.startRenderLoop();
    }

    initStatusBar() {
        const statusBar = document.getElementById('status-bar');
        const agentKeys = ['concierge', 'hotel', 'flight', 'train', 'ticket', 'restaurant'];
        agentKeys.forEach(key => {
            const item = document.createElement('div');
            item.className = 'status-item';
            item.innerHTML = `<span class="status-dot idle" id="status-${key}"></span><span>${AGENTS[key].label}</span>`;
            statusBar.appendChild(item);
        });
    }

    updateStatusDot(agentKey, state) {
        const dot = document.getElementById(`status-${agentKey}`);
        if (dot) {
            dot.className = `status-dot ${state}`;
        }
    }

    // ---- Event handlers (called from app.js) ----

    onAgentThinking() {
        this.stateManager.setState('concierge', AgentState.WORKING);
        this.updateStatusDot('concierge', 'working');
        this.addBubble('concierge', 'Thinking...', AGENTS.concierge.color);
    }

    onAgentCall(agentName, taskSummary) {
        const agentKey = this.resolveAgentKey(agentName);
        if (!agentKey) return;

        // Concierge sends to agent
        this.stateManager.setState(agentKey, AgentState.RECEIVING);
        this.updateStatusDot(agentKey, 'receiving');

        const c = AGENTS.concierge;
        const a = AGENTS[agentKey];

        // Send envelope from concierge to agent
        this.packets.push(new TravelingPacket(
            c.x, c.y, a.x, a.y,
            a.color, 'envelope',
            () => {
                // Agent starts working
                this.stateManager.setState(agentKey, AgentState.WORKING);
                this.updateStatusDot(agentKey, 'working');
                emitParticles(this.particles, a.x, a.y, a.color, 10);
                this.addBubble(agentKey, taskSummary, a.color);
            }
        ));
    }

    onAgentResponse(agentName, responseSummary) {
        const agentKey = this.resolveAgentKey(agentName);
        if (!agentKey) return;

        this.stateManager.setState(agentKey, AgentState.RESPONDING);
        this.updateStatusDot(agentKey, 'responding');

        const c = AGENTS.concierge;
        const a = AGENTS[agentKey];

        // Send document from agent back to concierge
        this.packets.push(new TravelingPacket(
            a.x, a.y, c.x, c.y,
            a.color, 'document',
            () => {
                this.stateManager.setState(agentKey, AgentState.DONE);
                this.updateStatusDot(agentKey, 'done');
                emitParticles(this.particles, c.x, c.y, a.color, 8);

                // Return to idle after 2 seconds
                setTimeout(() => {
                    this.stateManager.setState(agentKey, AgentState.IDLE);
                    this.updateStatusDot(agentKey, 'idle');
                }, 2000);
            }
        ));

        this.addBubble(agentKey, responseSummary, a.color);
    }

    onFinalResponse() {
        this.stateManager.setState('concierge', AgentState.DONE);
        this.updateStatusDot('concierge', 'done');
        this.flashAlpha = 0.4;

        // Flash green effect
        setTimeout(() => {
            this.stateManager.setState('concierge', AgentState.IDLE);
            this.updateStatusDot('concierge', 'idle');
        }, 2000);
    }

    resolveAgentKey(agentName) {
        // Try exact match first
        const name = agentName.toLowerCase().replace(/[^a-z]/g, '');
        const keys = ['hotel', 'flight', 'train', 'ticket', 'restaurant'];
        for (const key of keys) {
            if (name.includes(key)) return key;
        }
        // Fallback: check known patterns
        if (name.includes('accomod') || name.includes('room') || name.includes('lodg')) return 'hotel';
        if (name.includes('air') || name.includes('plane') || name.includes('avion')) return 'flight';
        if (name.includes('rail') || name.includes('tgv') || name.includes('sncf')) return 'train';
        if (name.includes('event') || name.includes('match') || name.includes('concert') || name.includes('billet')) return 'ticket';
        if (name.includes('food') || name.includes('dine') || name.includes('dining') || name.includes('bistro')) return 'restaurant';
        return null;
    }

    addBubble(agentKey, text, color) {
        const agent = AGENTS[agentKey];
        if (!agent) return;
        // Remove old bubbles for this agent
        this.bubbles = this.bubbles.filter(b => !(b.x === agent.x && b.y === agent.y - 40));
        this.bubbles.push(new SpeechBubble(agent.x, agent.y, text, color));
    }

    // ---- Render Loop ----

    startRenderLoop() {
        const loop = () => {
            if (!this.running) return;
            this.update();
            this.render();
            this.frame++;
            requestAnimationFrame(loop);
        };
        loop();
    }

    update() {
        // Update packets
        this.packets.forEach(p => p.update());
        this.packets = this.packets.filter(p => !p.done);

        // Update bubbles
        this.bubbles.forEach(b => b.update());
        this.bubbles = this.bubbles.filter(b => !b.done);

        // Update particles
        this.particles.forEach(p => p.update());
        this.particles = this.particles.filter(p => !p.done);

        // Decay flash
        if (this.flashAlpha > 0) {
            this.flashAlpha -= 0.005;
        }
    }

    render() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // Clear
        ctx.fillStyle = '#0a0a1a';
        ctx.fillRect(0, 0, w, h);

        // Background grid (subtle)
        ctx.fillStyle = '#111130';
        for (let x = 0; x < w; x += 20) {
            for (let y = 0; y < h; y += 20) {
                ctx.fillRect(x, y, 1, 1);
            }
        }

        // Draw connection lines
        const activeAgents = this.stateManager.getActiveAgents();
        drawConnectionLines(ctx, activeAgents, this.frame);

        // Draw agents
        Object.entries(AGENTS).forEach(([key, agent]) => {
            const state = this.stateManager.getState(key);

            // State-based glow
            if (state === AgentState.WORKING) {
                ctx.save();
                ctx.shadowColor = agent.color;
                ctx.shadowBlur = 8 + Math.sin(this.frame * 0.1) * 4;
                ctx.fillStyle = agent.color;
                ctx.globalAlpha = 0.1;
                ctx.beginPath();
                ctx.arc(agent.x, agent.y, 24, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }

            if (state === AgentState.DONE) {
                ctx.save();
                ctx.shadowColor = '#66bb6a';
                ctx.shadowBlur = 12;
                ctx.fillStyle = '#66bb6a';
                ctx.globalAlpha = 0.15;
                ctx.beginPath();
                ctx.arc(agent.x, agent.y, 24, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }

            // Draw the character sprite
            agent.draw(ctx, agent.x, agent.y, this.frame);

            // Draw label
            drawAgentLabel(ctx, agent);
        });

        // Draw packets
        this.packets.forEach(p => p.draw(ctx, this.frame));

        // Draw bubbles
        this.bubbles.forEach(b => b.draw(ctx));

        // Draw particles
        this.particles.forEach(p => p.draw(ctx));

        // Green flash overlay
        if (this.flashAlpha > 0) {
            ctx.save();
            ctx.fillStyle = '#66bb6a';
            ctx.globalAlpha = this.flashAlpha;
            ctx.fillRect(0, 0, w, h);
            ctx.restore();
        }
    }

    destroy() {
        this.running = false;
    }
}
