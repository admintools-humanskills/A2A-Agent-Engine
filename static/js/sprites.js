/**
 * sprites.js - Pixel art character drawing functions
 *
 * Each agent is drawn as a 32x32 sprite (concierge 40x40) using fillRect calls.
 * No external image assets needed.
 */

const PALETTES = {
    concierge: {
        skin: '#f5c6a0',
        hair: '#4a3728',
        body: '#e8b830',
        bodyDark: '#c49a20',
        accent: '#1a1a2e',
        bow: '#ef5350',
        clipboard: '#e0e0e0',
        clipboardDark: '#9e9e9e',
    },
    hotel: {
        skin: '#f5c6a0',
        hair: '#2c1810',
        body: '#1565c0',
        bodyDark: '#0d47a1',
        accent: '#e8b830',
        key: '#fdd835',
        keyDark: '#c6a700',
    },
    flight: {
        skin: '#d4a574',
        hair: '#1a1a1a',
        body: '#4fc3f7',
        bodyDark: '#0288d1',
        accent: '#ffffff',
        cap: '#0d47a1',
        capBrim: '#1565c0',
    },
    train: {
        skin: '#f5c6a0',
        hair: '#5d4037',
        body: '#388e3c',
        bodyDark: '#2e7d32',
        accent: '#fdd835',
        cap: '#1b5e20',
        capBrim: '#2e7d32',
    },
    ticket: {
        skin: '#8d6e63',
        hair: '#1a1a1a',
        body: '#e65100',
        bodyDark: '#bf360c',
        accent: '#ffffff',
        ticket: '#fff9c4',
        ticketStripe: '#ef5350',
    },
    restaurant: {
        skin: '#f5c6a0',
        hair: '#4a3728',
        body: '#d32f2f',
        bodyDark: '#b71c1c',
        accent: '#ffffff',
        toque: '#ffffff',
        toqueDark: '#e0e0e0',
    },
};

/**
 * Draw a single pixel (scaled) on the canvas
 */
function px(ctx, x, y, size, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, size, size);
}

/**
 * Draw a row of pixels starting at (startX, y) with a color map
 * Each character in the pattern maps to a color in the colorMap
 * '.' = transparent (skip)
 */
function drawRow(ctx, startX, y, pixelSize, pattern, colorMap) {
    for (let i = 0; i < pattern.length; i++) {
        const ch = pattern[i];
        if (ch !== '.' && colorMap[ch]) {
            px(ctx, startX + i * pixelSize, y, pixelSize, colorMap[ch]);
        }
    }
}

/**
 * Draw a sprite from a pattern array
 */
function drawSprite(ctx, x, y, pixelSize, patterns, colorMap) {
    for (let row = 0; row < patterns.length; row++) {
        drawRow(ctx, x, y + row * pixelSize, pixelSize, patterns[row], colorMap);
    }
}

// ==================== Character Sprites ====================

function drawConcierge(ctx, cx, cy, frame) {
    const s = 2.5; // pixel size for 40x40 sprite area
    const ox = cx - 20;
    const oy = cy - 20;
    const p = PALETTES.concierge;
    const cm = {
        'H': p.hair, 'S': p.skin, 'B': p.body, 'D': p.bodyDark,
        'R': p.bow, 'C': p.clipboard, 'G': p.clipboardDark, 'A': p.accent,
        'E': '#2c1810', // eyes
    };

    const sprite = [
        '......HHHHHH......',
        '.....HHHHHHHH.....',
        '....HHHHHHHHH.....',
        '....HSSSSSSSSH....',
        '...HSSSSSSSSSH....',
        '...SSSESSSESSS....',
        '...SSSSSSSSSSSS...',
        '....SSSSSSSSSS....',
        '....SSSSMMSSS.....',
        '.....SSSSSSSS.....',
        '......RRRRRR......',
        '.....RRRRRRRR.....',
        '....DBBBBBBBBDD...',
        '...DBBBBBBBBBBDD..',
        '..SDBBBBBBBBBDS...',
        '..SSBBBBBBBBBBSS..',
        '..SSBBBBBBBBBBS...',
        '...SBBBBBBBBBBS...',
        '...SBBBBBBBBBB....',
        '....BBBBBBBBBB....',
        '....AAAAAAAAA.....',
        '....AA......AA....',
        '...AA........AA...',
    ];

    // Subtle bounce animation
    const bounce = Math.sin(frame * 0.05) * 1;
    drawSprite(ctx, ox, oy + bounce, s, sprite, cm);

    // Clipboard in hand
    ctx.fillStyle = p.clipboard;
    ctx.fillRect(ox + 36, oy + bounce + 28, 6, 8);
    ctx.fillStyle = p.clipboardDark;
    ctx.fillRect(ox + 37, oy + bounce + 30, 4, 1);
    ctx.fillRect(ox + 37, oy + bounce + 33, 4, 1);

    // 'M' = mouth
    cm['M'] = '#c0392b';
    drawSprite(ctx, ox, oy + bounce, s, sprite, cm);
}

function drawHotelAgent(ctx, cx, cy, frame) {
    const s = 2;
    const ox = cx - 16;
    const oy = cy - 16;
    const p = PALETTES.hotel;
    const cm = {
        'H': p.hair, 'S': p.skin, 'B': p.body, 'D': p.bodyDark,
        'A': p.accent, 'K': p.key, 'L': p.keyDark, 'E': '#1a1a1a',
    };

    const sprite = [
        '.....HHHHHH.....',
        '....HHHHHHHH....',
        '....HSSSSSSH....',
        '...HSSESSEHS....',
        '...SSSSSSSSS....',
        '....SSSSSSSS....',
        '.....SSSSSS.....',
        '....DBBBBBD.....',
        '...DBBABBBBD....',
        '..SDBBBBBBBBDS..',
        '..SSBBBBBBBBSS..',
        '..SSBBBBBBBBS...',
        '...SBBBBBBBB....',
        '....BBBBBBBB....',
        '....BB....BB....',
        '...BB......BB...',
    ];

    const bounce = Math.sin(frame * 0.06 + 1) * 1;
    drawSprite(ctx, ox, oy + bounce, s, sprite, cm);

    // Key accessory
    ctx.fillStyle = p.key;
    ctx.fillRect(ox - 2, oy + bounce + 18, 6, 3);
    ctx.fillRect(ox - 2, oy + bounce + 16, 3, 2);
    ctx.fillStyle = p.keyDark;
    ctx.fillRect(ox + 1, oy + bounce + 19, 2, 1);
}

function drawFlightAgent(ctx, cx, cy, frame) {
    const s = 2;
    const ox = cx - 16;
    const oy = cy - 16;
    const p = PALETTES.flight;
    const cm = {
        'H': p.hair, 'S': p.skin, 'B': p.body, 'D': p.bodyDark,
        'A': p.accent, 'C': p.cap, 'P': p.capBrim, 'E': '#1a1a1a',
    };

    const sprite = [
        '....CCCCCCCC....',
        '...CCCCCCCCCC...',
        '...PPPPPPPPPP...',
        '....SSSSSSSS....',
        '...SSSESSEHS....',
        '...SSSSSSSSS....',
        '....SSSSSSSS....',
        '.....SSSSSS.....',
        '....DBBBBBD.....',
        '...DBBBBBBBBD...',
        '..ADBBBBBBBBDA..',
        '..AABBBBBBBBAA..',
        '..SSBBBBBBBBSS..',
        '...SBBBBBBBB....',
        '....BB....BB....',
        '...BB......BB...',
    ];

    const bounce = Math.sin(frame * 0.06 + 2) * 1;
    drawSprite(ctx, ox, oy + bounce, s, sprite, cm);

    // Wings emblem on chest
    ctx.fillStyle = p.accent;
    ctx.fillRect(ox + 12, oy + bounce + 20, 8, 1);
    ctx.fillRect(ox + 15, oy + bounce + 19, 2, 1);
}

function drawTrainAgent(ctx, cx, cy, frame) {
    const s = 2;
    const ox = cx - 16;
    const oy = cy - 16;
    const p = PALETTES.train;
    const cm = {
        'H': p.hair, 'S': p.skin, 'B': p.body, 'D': p.bodyDark,
        'A': p.accent, 'C': p.cap, 'P': p.capBrim, 'E': '#1a1a1a',
    };

    const sprite = [
        '....CCCCCCCC....',
        '...CCCCCCCCCC...',
        '...PPPPPPPPPP...',
        '....SSSSSSSS....',
        '...HSSESSEHS....',
        '...SSSSSSSSS....',
        '....SSSSSSSS....',
        '.....SSSSSS.....',
        '....DBBBBBD.....',
        '...DBBBABBBBD...',
        '..SDBBBBBBBBDS..',
        '..SSBBBBBBBBSS..',
        '..SSBBBBBBBBS...',
        '...SBBBBBBBB....',
        '....BB....BB....',
        '...BB......BB...',
    ];

    const bounce = Math.sin(frame * 0.06 + 3) * 1;
    drawSprite(ctx, ox, oy + bounce, s, sprite, cm);
}

function drawTicketAgent(ctx, cx, cy, frame) {
    const s = 2;
    const ox = cx - 16;
    const oy = cy - 16;
    const p = PALETTES.ticket;
    const cm = {
        'H': p.hair, 'S': p.skin, 'B': p.body, 'D': p.bodyDark,
        'A': p.accent, 'T': p.ticket, 'R': p.ticketStripe, 'E': '#1a1a1a',
    };

    const sprite = [
        '.....HHHHHH.....',
        '....HHHHHHHH....',
        '....HSSSSSSH....',
        '...HSSESSEHS....',
        '...SSSSSSSSS....',
        '....SSSSSSSS....',
        '.....SSSSSS.....',
        '....DBBBBBD.....',
        '...DBBBBBBBD....',
        '..SDBBBBBBBBDS..',
        '..SSBBBBBBBBSS..',
        '..SSBBBBBBBBS...',
        '...SBBBBBBBB....',
        '....BBBBBBBB....',
        '....BB....BB....',
        '...BB......BB...',
    ];

    const bounce = Math.sin(frame * 0.06 + 4) * 1;
    drawSprite(ctx, ox, oy + bounce, s, sprite, cm);

    // Ticket in hand
    ctx.fillStyle = p.ticket;
    ctx.fillRect(ox + 30, oy + bounce + 18, 8, 5);
    ctx.fillStyle = p.ticketStripe;
    ctx.fillRect(ox + 30, oy + bounce + 19, 8, 1);
    ctx.fillRect(ox + 30, oy + bounce + 21, 8, 1);
}

function drawRestaurantAgent(ctx, cx, cy, frame) {
    const s = 2;
    const ox = cx - 16;
    const oy = cy - 16;
    const p = PALETTES.restaurant;
    const cm = {
        'H': p.hair, 'S': p.skin, 'B': p.body, 'D': p.bodyDark,
        'A': p.accent, 'T': p.toque, 'Q': p.toqueDark, 'E': '#1a1a1a',
    };

    const sprite = [
        '.....TTTTTT.....',
        '....TTTTTTTT....',
        '....TTTTTTTT....',
        '...QTTTTTTTTQ...',
        '...QQQQQQQQQQ...',
        '....SSSSSSSS....',
        '...SSSESSEHS....',
        '...SSSSSSSSS....',
        '....SSSSSSSS....',
        '.....SSSSSS.....',
        '....DBBBBBD.....',
        '...DBBABBBBD....',
        '..SDBBBBBBBBDS..',
        '..SSBBBBBBBBSS..',
        '...SBBBBBBBB....',
        '....BB....BB....',
    ];

    const bounce = Math.sin(frame * 0.06 + 5) * 1;
    drawSprite(ctx, ox, oy + bounce, s, sprite, cm);
}

// ==================== Agent Registry ====================

const AGENTS = {
    concierge: {
        draw: drawConcierge,
        x: 240, y: 240,
        color: '#e8b830',
        label: 'Concierge',
        icon: '\u2606', // star
    },
    hotel: {
        draw: drawHotelAgent,
        x: 100, y: 160,
        color: '#1565c0',
        label: 'Hotel',
        icon: '\u2302', // house
    },
    flight: {
        draw: drawFlightAgent,
        x: 240, y: 80,
        color: '#4fc3f7',
        label: 'Flight',
        icon: '\u2708', // plane
    },
    train: {
        draw: drawTrainAgent,
        x: 380, y: 160,
        color: '#388e3c',
        label: 'Train',
        icon: '\u2634', // train-ish
    },
    ticket: {
        draw: drawTicketAgent,
        x: 380, y: 320,
        color: '#e65100',
        label: 'Ticket',
        icon: '\u2660', // ticket-ish
    },
    restaurant: {
        draw: drawRestaurantAgent,
        x: 100, y: 320,
        color: '#d32f2f',
        label: 'Restaurant',
        icon: '\u2615', // cup
    },
};

/**
 * Draw a label under an agent
 */
function drawAgentLabel(ctx, agent) {
    ctx.fillStyle = agent.color;
    ctx.font = '7px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText(agent.label, agent.x, agent.y + 30);
}

/**
 * Draw connection lines between concierge and all agents
 */
function drawConnectionLines(ctx, activeAgents, frame) {
    const c = AGENTS.concierge;
    const agentKeys = ['hotel', 'flight', 'train', 'ticket', 'restaurant'];

    agentKeys.forEach(key => {
        const agent = AGENTS[key];
        const isActive = activeAgents.has(key);

        ctx.save();
        ctx.beginPath();
        ctx.setLineDash([4, 4]);

        if (isActive) {
            // Glowing line
            ctx.strokeStyle = agent.color;
            ctx.lineWidth = 2;
            ctx.shadowColor = agent.color;
            ctx.shadowBlur = 6;
            // Animate dash offset
            ctx.lineDashOffset = -frame * 0.5;
        } else {
            ctx.strokeStyle = '#2a2a4a';
            ctx.lineWidth = 1;
            ctx.lineDashOffset = 0;
        }

        ctx.moveTo(c.x, c.y);
        ctx.lineTo(agent.x, agent.y);
        ctx.stroke();
        ctx.restore();
    });
}
