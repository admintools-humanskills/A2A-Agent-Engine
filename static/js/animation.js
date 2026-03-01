/**
 * animation.js - Canvas animation engine for RPG Village
 *
 * ConciergeWalker, NPC patrols, offscreen canvas, depth-sorted rendering.
 * Public API unchanged: onAgentThinking, onAgentCall, onAgentResponse, onFinalResponse.
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
        Object.keys(AGENTS).forEach(key => { this.states[key] = AgentState.IDLE; });
    }
    setState(k, s) { this.states[k] = s; }
    getState(k) { return this.states[k] || AgentState.IDLE; }
    getActiveAgents() {
        const active = new Set();
        Object.entries(this.states).forEach(([k, s]) => { if (s !== AgentState.IDLE) active.add(k); });
        return active;
    }
    resetAll() { Object.keys(this.states).forEach(k => { this.states[k] = AgentState.IDLE; }); }
}

// ==================== Concierge Walker ====================

class ConciergeWalker {
    constructor() {
        this.homeX = AGENTS.concierge.x;
        this.homeY = AGENTS.concierge.y;
        this.x = this.homeX;
        this.y = this.homeY;
        this.waypoints = [];
        this.wpIndex = 0;
        this.walking = false;
        this.walkFrame = 0;
        this.walkTimer = 0;
        this.direction = 0; // 0=down,1=left,2=right,3=up
        this.speed = 2.5;
        this.onArrive = null;
        this.queue = [];
    }

    _pathTo(agentKey) {
        const paths = {
            hotel:      [{ x: 240, y: 112 }, { x: 64, y: 112 },  { x: 64, y: 100 }],
            flight:     [{ x: 240, y: 100 }],
            train:      [{ x: 240, y: 112 }, { x: 400, y: 112 }, { x: 400, y: 100 }],
            ticket:     [{ x: 240, y: 352 }, { x: 80, y: 352 },  { x: 80, y: 380 }],
            restaurant: [{ x: 240, y: 352 }, { x: 400, y: 352 }, { x: 400, y: 380 }],
            merchandise:[{ x: 240, y: 352 }, { x: 240, y: 400 }],
        };
        return paths[agentKey] || [];
    }

    walkTo(agentKey, onArrive) {
        if (this.walking) {
            this.queue.push({ type: 'to', agentKey, onArrive });
            return;
        }
        this._start(this._pathTo(agentKey), onArrive);
    }

    returnToPlaza(onArrive) {
        if (this.walking) {
            this.queue.push({ type: 'home', onArrive });
            return;
        }
        const wp = [];
        if (this.y < 200) {
            wp.push({ x: this.x, y: 112 });
            wp.push({ x: 240, y: 112 });
        } else if (this.y > 280) {
            wp.push({ x: this.x, y: 352 });
            wp.push({ x: 240, y: 352 });
        }
        wp.push({ x: this.homeX, y: this.homeY });
        this._start(wp, onArrive);
    }

    _start(waypoints, onArrive) {
        this.waypoints = waypoints;
        this.wpIndex = 0;
        this.walking = true;
        this.onArrive = onArrive;
    }

    _processQueue() {
        if (this.queue.length === 0) return;
        const next = this.queue.shift();
        if (next.type === 'home') this.returnToPlaza(next.onArrive);
        else this.walkTo(next.agentKey, next.onArrive);
    }

    update() {
        if (!this.walking || this.waypoints.length === 0) {
            this.walkFrame = 0;
            return;
        }
        const target = this.waypoints[this.wpIndex];
        const dx = target.x - this.x;
        const dy = target.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < this.speed) {
            this.x = target.x;
            this.y = target.y;
            this.wpIndex++;
            if (this.wpIndex >= this.waypoints.length) {
                this.walking = false;
                this.walkFrame = 0;
                AGENTS.concierge.x = this.x;
                AGENTS.concierge.y = this.y;
                if (this.onArrive) this.onArrive();
                this._processQueue();
                return;
            }
        } else {
            this.x += (dx / dist) * this.speed;
            this.y += (dy / dist) * this.speed;
            if (Math.abs(dx) > Math.abs(dy)) this.direction = dx > 0 ? 2 : 1;
            else this.direction = dy > 0 ? 0 : 3;
        }

        this.walkTimer++;
        if (this.walkTimer >= 8) {
            this.walkTimer = 0;
            this.walkFrame = this.walkFrame === 1 ? 2 : 1;
        }
        AGENTS.concierge.x = this.x;
        AGENTS.concierge.y = this.y;
    }
}

// ==================== NPC Animator ====================

class NPCAnimator {
    constructor(agentKey) {
        this.key = agentKey;
        this.baseX = AGENTS[agentKey].x;
        this.baseY = AGENTS[agentKey].y;
        this.x = this.baseX;
        this.y = this.baseY;
        this.walkFrame = 0;
        this.walkTimer = 0;
        this.dir = 1;
        this.patrolDist = 0;
        this.patrolMax = 16;
        this.paused = false;
        this.pauseTimer = 0;
        this.exclamation = false;
        this.exclTimer = 0;
        this.checkmark = false;
        this.checkTimer = 0;
    }

    react() {
        this.exclamation = true;
        this.exclTimer = 60;
        this.paused = true;
        this.pauseTimer = 90;
    }

    showDone() {
        this.checkmark = true;
        this.checkTimer = 60;
    }

    update() {
        if (this.exclTimer > 0) { this.exclTimer--; if (this.exclTimer === 0) this.exclamation = false; }
        if (this.checkTimer > 0) { this.checkTimer--; if (this.checkTimer === 0) this.checkmark = false; }

        if (this.pauseTimer > 0) {
            this.pauseTimer--;
            if (this.pauseTimer === 0) this.paused = false;
            this.walkFrame = 0;
            return;
        }

        this.x += this.dir * 0.3;
        this.patrolDist += 0.3;
        if (this.patrolDist >= this.patrolMax) {
            this.patrolDist = 0;
            this.dir *= -1;
            this.paused = true;
            this.pauseTimer = 40;
        }

        this.walkTimer++;
        if (this.walkTimer >= 12) {
            this.walkTimer = 0;
            this.walkFrame = this.walkFrame === 1 ? 2 : 1;
        }
    }
}

// ==================== Speech Bubble ====================

class SpeechBubble {
    constructor(x, y, text, color, duration) {
        this.x = x;
        this.y = y - 44;
        this.text = text.length > 40 ? text.substring(0, 37) + '...' : text;
        this.color = color || '#e0e0e0';
        this.duration = duration || 180;
        this.age = 0;
        this.done = false;
    }

    update() {
        if (this.done) return;
        this.age++;
        if (this.age >= this.duration) this.done = true;
    }

    draw(ctx) {
        if (this.done) return;
        let alpha = 1;
        if (this.age < 15) alpha = this.age / 15;
        else if (this.age > this.duration - 15) alpha = (this.duration - this.age) / 15;

        ctx.save();
        ctx.globalAlpha = Math.max(0, alpha);
        ctx.font = '6px "Press Start 2P", monospace';
        const tw = Math.min(ctx.measureText(this.text).width, 160);
        const pad = 6, bw = tw + pad * 2, bh = 18;
        const bx = this.x - bw / 2, by = this.y - bh;

        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(bx, by, bw, bh);
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 1;
        ctx.strokeRect(bx, by, bw, bh);

        // Pointer
        ctx.fillStyle = '#1a1a2e';
        ctx.beginPath();
        ctx.moveTo(this.x - 4, by + bh);
        ctx.lineTo(this.x, by + bh + 5);
        ctx.lineTo(this.x + 4, by + bh);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = this.color;
        ctx.beginPath();
        ctx.moveTo(this.x - 4, by + bh);
        ctx.lineTo(this.x, by + bh + 5);
        ctx.lineTo(this.x + 4, by + bh);
        ctx.stroke();

        ctx.fillStyle = '#e0e0e0';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.text, this.x, by + bh / 2, 160);
        ctx.restore();
    }
}

// ==================== Particle System ====================

class Particle {
    constructor(x, y, color) {
        this.x = x; this.y = y; this.color = color;
        this.vx = (Math.random() - 0.5) * 3;
        this.vy = (Math.random() - 0.5) * 3 - 1;
        this.life = 1;
        this.decay = 0.02 + Math.random() * 0.02;
        this.size = 2;
        this.done = false;
    }
    update() {
        if (this.done) return;
        this.x += this.vx; this.y += this.vy;
        this.vy += 0.05;
        this.life -= this.decay;
        if (this.life <= 0) this.done = true;
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

function emitParticles(arr, x, y, color, count) {
    for (let i = 0; i < (count || 10); i++) arr.push(new Particle(x, y, color));
}

// ==================== Main Visualization ====================

class AgentVisualization {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.frame = 0;
        this.stateManager = new AgentStateManager();
        this.bubbles = [];
        this.particles = [];
        this.running = true;
        this.flashAlpha = 0;

        // Concierge walker
        this.walker = new ConciergeWalker();

        // NPC animators
        this.npcs = {};
        ['hotel', 'flight', 'train', 'ticket', 'restaurant', 'merchandise'].forEach(k => {
            this.npcs[k] = new NPCAnimator(k);
        });

        // Pre-render static scene
        this.staticCanvas = document.createElement('canvas');
        this.staticCanvas.width = 480;
        this.staticCanvas.height = 480;
        renderStaticScene(this.staticCanvas.getContext('2d'));

        this.initStatusBar();
        this.startRenderLoop();
    }

    initStatusBar() {
        const bar = document.getElementById('status-bar');
        ['concierge', 'hotel', 'flight', 'train', 'ticket', 'restaurant', 'merchandise'].forEach(k => {
            const item = document.createElement('div');
            item.className = 'status-item';
            item.innerHTML = `<span class="status-dot idle" id="status-${k}"></span><span>${AGENTS[k].label}</span>`;
            bar.appendChild(item);
        });
    }

    updateStatusDot(k, state) {
        const dot = document.getElementById(`status-${k}`);
        if (dot) dot.className = `status-dot ${state}`;
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

        this.stateManager.setState(agentKey, AgentState.RECEIVING);
        this.updateStatusDot(agentKey, 'receiving');
        const a = AGENTS[agentKey];

        // Walk concierge to agent's building
        this.walker.walkTo(agentKey, () => {
            this.stateManager.setState(agentKey, AgentState.WORKING);
            this.updateStatusDot(agentKey, 'working');
            this.npcs[agentKey].react();
            emitParticles(this.particles, a.x, a.y, a.color, 10);
            this.addBubble(agentKey, taskSummary, a.color);
        });
    }

    onAgentResponse(agentName, responseSummary) {
        const agentKey = this.resolveAgentKey(agentName);
        if (!agentKey) return;

        this.stateManager.setState(agentKey, AgentState.DONE);
        this.updateStatusDot(agentKey, 'done');
        this.npcs[agentKey].showDone();
        this.addBubble(agentKey, responseSummary, AGENTS[agentKey].color);
        emitParticles(this.particles, AGENTS[agentKey].x, AGENTS[agentKey].y, '#66bb6a', 8);

        // Walk concierge back to plaza
        this.walker.returnToPlaza(() => {
            emitParticles(this.particles, this.walker.x, this.walker.y, '#e8b830', 6);
        });

        setTimeout(() => {
            this.stateManager.setState(agentKey, AgentState.IDLE);
            this.updateStatusDot(agentKey, 'idle');
        }, 3000);
    }

    onFinalResponse() {
        this.stateManager.setState('concierge', AgentState.DONE);
        this.updateStatusDot('concierge', 'done');
        this.flashAlpha = 0.3;
        emitParticles(this.particles, this.walker.x, this.walker.y, '#e8b830', 20);

        setTimeout(() => {
            this.stateManager.setState('concierge', AgentState.IDLE);
            this.updateStatusDot('concierge', 'idle');
        }, 2000);
    }

    resolveAgentKey(agentName) {
        const name = agentName.toLowerCase().replace(/[^a-z]/g, '');
        const keys = ['hotel', 'flight', 'train', 'ticket', 'restaurant', 'merchandise'];
        for (const key of keys) {
            if (name.includes(key)) return key;
        }
        if (name.includes('accomod') || name.includes('room') || name.includes('lodg')) return 'hotel';
        if (name.includes('air') || name.includes('plane') || name.includes('avion')) return 'flight';
        if (name.includes('rail') || name.includes('tgv') || name.includes('sncf')) return 'train';
        if (name.includes('event') || name.includes('match') || name.includes('concert') || name.includes('billet')) return 'ticket';
        if (name.includes('food') || name.includes('dine') || name.includes('dining') || name.includes('bistro')) return 'restaurant';
        if (name.includes('merch') || name.includes('jersey') || name.includes('shop') || name.includes('scarf') || name.includes('fan') || name.includes('souvenir')) return 'merchandise';
        return null;
    }

    addBubble(agentKey, text, color) {
        const a = AGENTS[agentKey];
        if (!a) return;
        this.bubbles = this.bubbles.filter(b => !(Math.abs(b.x - a.x) < 2 && Math.abs(b.y - a.y + 44) < 2));
        this.bubbles.push(new SpeechBubble(a.x, a.y, text, color));
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
        this.walker.update();
        Object.values(this.npcs).forEach(n => n.update());
        this.bubbles.forEach(b => b.update());
        this.bubbles = this.bubbles.filter(b => !b.done);
        this.particles.forEach(p => p.update());
        this.particles = this.particles.filter(p => !p.done);
        if (this.flashAlpha > 0) this.flashAlpha -= 0.005;
    }

    render() {
        const ctx = this.ctx;

        // 1. Static background
        ctx.drawImage(this.staticCanvas, 0, 0);

        // 2. Animated decorations
        drawFountainAnim(ctx, DECORATIONS.fountain.x, DECORATIONS.fountain.y, this.frame);
        this._drawLampGlow(ctx);
        this._drawChimneySmoke(ctx);

        // 3. Collect & sort characters by Y
        const chars = this._getSortedChars();
        chars.forEach(ch => {
            const state = this.stateManager.getState(ch.key);

            // Working glow
            if (state === AgentState.WORKING) {
                ctx.save();
                ctx.shadowColor = AGENTS[ch.key].color;
                ctx.shadowBlur = 8 + Math.sin(this.frame * 0.1) * 4;
                ctx.fillStyle = AGENTS[ch.key].color;
                ctx.globalAlpha = 0.12;
                ctx.beginPath();
                ctx.arc(ch.x, ch.y - 16, 22, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            if (state === AgentState.DONE) {
                ctx.save();
                ctx.shadowColor = '#66bb6a';
                ctx.shadowBlur = 10;
                ctx.fillStyle = '#66bb6a';
                ctx.globalAlpha = 0.12;
                ctx.beginPath();
                ctx.arc(ch.x, ch.y - 16, 22, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }

            drawCharacter(ctx, ch.x, ch.y, ch.key, ch.walkFrame, ch.dir);
            drawAgentLabel(ctx, ch.x, ch.y, AGENTS[ch.key].label, AGENTS[ch.key].color);

            // Exclamation / checkmark
            if (ch.npc && ch.npc.exclamation) drawExclamation(ctx, ch.x, ch.y - 38);
            if (ch.npc && ch.npc.checkmark) drawCheckmark(ctx, ch.x, ch.y - 38);
        });

        // 4. Overlays
        this.bubbles.forEach(b => b.draw(ctx));
        this.particles.forEach(p => p.draw(ctx));

        // Flash
        if (this.flashAlpha > 0) {
            ctx.save();
            ctx.fillStyle = '#e8b830';
            ctx.globalAlpha = this.flashAlpha;
            ctx.fillRect(0, 0, 480, 480);
            ctx.restore();
        }
    }

    _getSortedChars() {
        const chars = [];
        // Concierge
        chars.push({
            key: 'concierge',
            x: this.walker.x,
            y: this.walker.y,
            walkFrame: this.walker.walkFrame,
            dir: this.walker.direction,
            npc: null,
        });
        // NPCs
        Object.entries(this.npcs).forEach(([k, npc]) => {
            chars.push({
                key: k,
                x: npc.x,
                y: npc.y,
                walkFrame: npc.walkFrame,
                dir: npc.dir > 0 ? 2 : 1,
                npc: npc,
            });
        });
        chars.sort((a, b) => a.y - b.y);
        return chars;
    }

    _drawLampGlow(ctx) {
        const pulse = 0.15 + Math.sin(this.frame * 0.04) * 0.05;
        ctx.save();
        ctx.globalAlpha = pulse;
        ctx.fillStyle = '#fff9c4';
        DECORATIONS.lampposts.forEach(l => {
            ctx.beginPath();
            ctx.arc(l.x + 2, l.y + 5, 10, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.restore();
    }

    _drawChimneySmoke(ctx) {
        // Small smoke particles from restaurant chimney
        const r = BUILDINGS.restaurant;
        if (this.frame % 15 === 0) {
            emitParticles(this.particles, r.x + 80, r.y - 4, '#9e9e9e', 2);
        }
    }

    destroy() {
        this.running = false;
    }
}
