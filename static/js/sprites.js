/**
 * sprites.js - RPG Village pixel art: tilemap, buildings, character sprites
 * Style: Final Fantasy 2 / Gather.town
 */

// ==================== Palettes ====================

const ENV = {
    grass: ['#5a8f3c', '#4e7f34', '#6a9f48'],
    grassDark: '#3d6b2a',
    path: ['#c4a56e', '#b09060', '#a08050'],
    pathEdge: '#7a6040',
    wall: '#e8dcc8', wallDark: '#c8b8a0', wallLight: '#f0e8d8',
    treeTrunk: '#5d4037', treeTrunkDark: '#3e2723',
    treeLeaf: ['#2d6b30', '#388e3c', '#4caf50'],
    water: ['#1976d2', '#42a5f5'], waterLight: '#90caf9',
    stone: '#9e9e9e', stoneDark: '#757575', stoneLight: '#bdbdbd',
};

const CHAR_PAL = {
    concierge:  { skin:'#f5c6a0', hair:'#4a3728', body:'#e8b830', bodyDark:'#c49a20', eyes:'#2c1810', acc:'#ef5350' },
    hotel:      { skin:'#f5c6a0', hair:'#2c1810', body:'#1565c0', bodyDark:'#0d47a1', eyes:'#1a1a1a', acc:'#e8b830' },
    flight:     { skin:'#d4a574', hair:'#1a1a1a', body:'#4fc3f7', bodyDark:'#0288d1', eyes:'#1a1a1a', acc:'#ffffff', hat:'#0d47a1', hatBrim:'#1565c0' },
    train:      { skin:'#f5c6a0', hair:'#5d4037', body:'#388e3c', bodyDark:'#2e7d32', eyes:'#1a1a1a', acc:'#fdd835', hat:'#1b5e20', hatBrim:'#2e7d32' },
    ticket:     { skin:'#8d6e63', hair:'#1a1a1a', body:'#e65100', bodyDark:'#bf360c', eyes:'#1a1a1a', acc:'#ffffff' },
    restaurant: { skin:'#f5c6a0', hair:'#4a3728', body:'#d32f2f', bodyDark:'#b71c1c', eyes:'#1a1a1a', acc:'#ffffff', toque:true },
    merchandise: { skin:'#d4a574', hair:'#1a1a1a', body:'#9c27b0', bodyDark:'#7b1fa2', eyes:'#1a1a1a', acc:'#fdd835' },
};

// ==================== Ground ====================

const TS = 16; // tile size
const GW = 30, GH = 30; // grid dimensions

function tileHash(x, y) { return ((x * 7 + y * 13 + x * y * 3) & 0x7fffffff) % 3; }

function isPathTile(tx, ty) {
    const x = tx, y = ty;
    // Top horizontal path (rows 6-7)
    if (y >= 6 && y <= 7 && x >= 1 && x <= 28) return true;
    // Bottom horizontal path (rows 21-22)
    if (y >= 21 && y <= 22 && x >= 1 && x <= 28) return true;
    // Center vertical (cols 14-15)
    if (x >= 14 && x <= 15 && y >= 6 && y <= 22) return true;
    // Hotel side path (cols 3-4, rows 5-6)
    if (x >= 3 && x <= 4 && y >= 4 && y <= 6) return true;
    // Train side path (cols 25-26, rows 5-6)
    if (x >= 25 && x <= 26 && y >= 4 && y <= 6) return true;
    // Theater side path (cols 4-5, rows 22-24)
    if (x >= 4 && x <= 5 && y >= 22 && y <= 24) return true;
    // Restaurant side path (cols 24-25, rows 22-24)
    if (x >= 24 && x <= 25 && y >= 22 && y <= 24) return true;
    // Merchandise shop side path (cols 14-15, rows 22-26)
    if (x >= 14 && x <= 15 && y >= 22 && y <= 26) return true;
    // Plaza (cols 12-17, rows 13-17)
    if (x >= 12 && x <= 17 && y >= 13 && y <= 17) return true;
    return false;
}

function renderGround(ctx) {
    for (let ty = 0; ty < GH; ty++) {
        for (let tx = 0; tx < GW; tx++) {
            const px = tx * TS, py = ty * TS;
            const h = tileHash(tx, ty);
            if (isPathTile(tx, ty)) {
                ctx.fillStyle = ENV.path[h];
                ctx.fillRect(px, py, TS, TS);
                if (h === 1) { ctx.fillStyle = ENV.pathEdge; ctx.fillRect(px + 4, py + 6, 3, 2); }
                if (h === 2) { ctx.fillStyle = ENV.pathEdge; ctx.fillRect(px + 9, py + 11, 2, 2); }
            } else {
                ctx.fillStyle = ENV.grass[h];
                ctx.fillRect(px, py, TS, TS);
                if (h === 0) {
                    ctx.fillStyle = ENV.grassDark;
                    ctx.fillRect(px + 3, py + 10, 2, 3);
                    ctx.fillRect(px + 10, py + 5, 2, 3);
                }
                if (h === 2) {
                    ctx.fillStyle = '#7ab648';
                    ctx.fillRect(px + 7, py + 2, 1, 2);
                }
            }
        }
    }
}

// ==================== Buildings ====================

function drawHotelBuilding(ctx, x, y) {
    // Main wall 80x56
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 16, 80, 48);
    ctx.fillStyle = ENV.wallDark;
    ctx.fillRect(x, y + 16, 80, 2);
    // Roof (red)
    ctx.fillStyle = '#c0392b';
    ctx.fillRect(x - 2, y + 10, 84, 8);
    ctx.fillStyle = '#e74c3c';
    ctx.fillRect(x + 6, y + 2, 68, 10);
    ctx.fillStyle = '#a93226';
    ctx.fillRect(x + 16, y - 2, 48, 6);
    // Windows (3 floors x 3)
    for (let f = 0; f < 3; f++) {
        for (let w = 0; w < 3; w++) {
            const wx = x + 8 + w * 24, wy = y + 22 + f * 12;
            ctx.fillStyle = '#4fc3f7';
            ctx.fillRect(wx, wy, 10, 8);
            ctx.fillStyle = '#0288d1';
            ctx.fillRect(wx + 4, wy, 2, 8);
            ctx.fillRect(wx, wy + 3, 10, 2);
        }
    }
    // Door
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(x + 32, y + 52, 16, 12);
    ctx.fillStyle = '#e8b830';
    ctx.fillRect(x + 44, y + 57, 3, 3);
    // "H" sign
    ctx.fillStyle = '#e8b830';
    ctx.font = 'bold 10px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('H', x + 40, y + 9);
}

function drawAirportBuilding(ctx, x, y) {
    // Terminal 100x48
    ctx.fillStyle = ENV.wallLight;
    ctx.fillRect(x, y + 14, 100, 42);
    // Glass front
    ctx.fillStyle = '#b3e5fc';
    ctx.fillRect(x + 4, y + 22, 88, 26);
    ctx.fillStyle = '#81d4fa';
    for (let i = 0; i < 7; i++) ctx.fillRect(x + 4 + i * 13, y + 22, 2, 26);
    // Blue roof
    ctx.fillStyle = '#2980b9';
    ctx.fillRect(x - 2, y + 8, 104, 8);
    ctx.fillStyle = '#3498db';
    ctx.fillRect(x + 8, y + 2, 84, 8);
    // Control tower
    ctx.fillStyle = '#bdbdbd';
    ctx.fillRect(x + 88, y - 16, 16, 72);
    ctx.fillStyle = '#4fc3f7';
    ctx.fillRect(x + 90, y - 12, 12, 8);
    ctx.fillStyle = '#1565c0';
    ctx.fillRect(x + 93, y - 18, 6, 6);
    // Door
    ctx.fillStyle = '#0288d1';
    ctx.fillRect(x + 42, y + 48, 16, 8);
    // Runway markings
    ctx.fillStyle = '#fdd835';
    for (let i = 0; i < 5; i++) ctx.fillRect(x + 10 + i * 18, y + 58, 8, 2);
}

function drawTrainStation(ctx, x, y) {
    // Main 80x48
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 14, 80, 42);
    // Green roof
    ctx.fillStyle = '#27ae60';
    ctx.fillRect(x - 2, y + 8, 84, 8);
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(x + 10, y + 2, 60, 8);
    // Arches (3)
    for (let i = 0; i < 3; i++) {
        const ax = x + 8 + i * 24;
        ctx.fillStyle = '#5d4037';
        ctx.fillRect(ax, y + 30, 16, 20);
        ctx.fillStyle = '#3e2723';
        ctx.fillRect(ax + 2, y + 26, 12, 6);
    }
    // Clock
    ctx.fillStyle = '#ffffff';
    ctx.beginPath(); ctx.arc(x + 40, y + 20, 6, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(x + 39, y + 15, 2, 5);
    ctx.fillRect(x + 40, y + 19, 4, 1);
    // Rails
    ctx.fillStyle = '#616161';
    ctx.fillRect(x - 4, y + 56, 88, 2);
    ctx.fillRect(x - 4, y + 60, 88, 2);
    ctx.fillStyle = '#5d4037';
    for (let i = 0; i < 8; i++) ctx.fillRect(x - 2 + i * 11, y + 55, 4, 8);
}

function drawTheater(ctx, x, y) {
    // Main 96x64
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 22, 96, 50);
    // Pediment
    ctx.fillStyle = ENV.wallDark;
    ctx.fillRect(x - 2, y + 16, 100, 8);
    ctx.fillStyle = '#d35400';
    ctx.beginPath();
    ctx.moveTo(x + 6, y + 16);
    ctx.lineTo(x + 48, y);
    ctx.lineTo(x + 90, y + 16);
    ctx.closePath();
    ctx.fill();
    // Columns (4)
    for (let i = 0; i < 4; i++) {
        const cx = x + 12 + i * 22;
        ctx.fillStyle = ENV.wallLight;
        ctx.fillRect(cx, y + 22, 8, 34);
        ctx.fillStyle = ENV.wallDark;
        ctx.fillRect(cx - 1, y + 20, 10, 4);
        ctx.fillRect(cx - 1, y + 54, 10, 4);
    }
    // Marquee
    ctx.fillStyle = '#e67e22';
    ctx.fillRect(x + 16, y + 58, 64, 10);
    for (let i = 0; i < 7; i++) {
        ctx.fillStyle = (i % 2 === 0) ? '#fdd835' : '#fff9c4';
        ctx.fillRect(x + 20 + i * 8, y + 60, 4, 4);
    }
    // Door
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(x + 38, y + 62, 20, 10);
}

function drawRestaurantBuilding(ctx, x, y) {
    // Main 96x56
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 14, 96, 50);
    // Striped awning
    for (let i = 0; i < 12; i++) {
        ctx.fillStyle = (i % 2 === 0) ? '#d32f2f' : '#ffffff';
        ctx.fillRect(x + i * 8, y + 8, 8, 8);
    }
    // Left window
    ctx.fillStyle = '#fff3e0';
    ctx.fillRect(x + 8, y + 24, 22, 16);
    ctx.fillStyle = '#ffe0b2';
    ctx.fillRect(x + 18, y + 24, 2, 16);
    ctx.strokeStyle = '#5d4037'; ctx.lineWidth = 1;
    ctx.strokeRect(x + 8, y + 24, 22, 16);
    // Door
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(x + 38, y + 24, 14, 28);
    ctx.fillStyle = '#e8b830';
    ctx.fillRect(x + 48, y + 36, 2, 3);
    // Right window
    ctx.fillStyle = '#fff3e0';
    ctx.fillRect(x + 60, y + 24, 22, 16);
    ctx.fillStyle = '#ffe0b2';
    ctx.fillRect(x + 70, y + 24, 2, 16);
    ctx.strokeStyle = '#5d4037';
    ctx.strokeRect(x + 60, y + 24, 22, 16);
    // Chimney
    ctx.fillStyle = '#8d6e63';
    ctx.fillRect(x + 76, y - 2, 8, 12);
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(x + 74, y - 4, 12, 4);
    // Outdoor table
    ctx.fillStyle = '#8d6e63';
    ctx.fillRect(x + 14, y + 52, 18, 2);
    ctx.fillRect(x + 22, y + 54, 2, 6);
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(x + 10, y + 54, 5, 4);
    ctx.fillRect(x + 30, y + 54, 5, 4);
}

function drawMerchandiseShop(ctx, x, y) {
    // Main wall 80x50
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 14, 80, 50);
    // Striped awning (purple/white)
    for (let i = 0; i < 10; i++) {
        ctx.fillStyle = (i % 2 === 0) ? '#9c27b0' : '#ffffff';
        ctx.fillRect(x + i * 8, y + 8, 8, 8);
    }
    // Shop window (left) - display jersey
    ctx.fillStyle = '#e1bee7';
    ctx.fillRect(x + 6, y + 22, 24, 20);
    ctx.strokeStyle = '#5d4037'; ctx.lineWidth = 1;
    ctx.strokeRect(x + 6, y + 22, 24, 20);
    // Jersey silhouette in window
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x + 13, y + 25, 10, 12);
    ctx.fillStyle = '#9c27b0';
    ctx.fillRect(x + 14, y + 26, 8, 10);
    ctx.fillRect(x + 11, y + 26, 3, 4);
    ctx.fillRect(x + 22, y + 26, 3, 4);
    // Door
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(x + 34, y + 24, 14, 28);
    ctx.fillStyle = '#fdd835';
    ctx.fillRect(x + 44, y + 36, 2, 3);
    // Shop window (right) - display scarf
    ctx.fillStyle = '#e1bee7';
    ctx.fillRect(x + 52, y + 22, 24, 20);
    ctx.strokeStyle = '#5d4037';
    ctx.strokeRect(x + 52, y + 22, 24, 20);
    // Scarf in window
    ctx.fillStyle = '#fdd835';
    ctx.fillRect(x + 57, y + 28, 14, 3);
    ctx.fillStyle = '#9c27b0';
    ctx.fillRect(x + 55, y + 31, 4, 6);
    ctx.fillRect(x + 67, y + 31, 4, 6);
    // Flag on roof
    ctx.fillStyle = '#616161';
    ctx.fillRect(x + 68, y - 6, 2, 16);
    ctx.fillStyle = '#fdd835';
    ctx.fillRect(x + 70, y - 6, 8, 6);
    ctx.fillStyle = '#9c27b0';
    ctx.fillRect(x + 70, y - 3, 8, 3);
    // Star on sign
    ctx.fillStyle = '#fdd835';
    ctx.font = 'bold 8px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('\u2605', x + 40, y + 6);
}

// ==================== Decorations ====================

function drawTree(ctx, x, y) {
    ctx.fillStyle = ENV.treeTrunk;
    ctx.fillRect(x + 5, y + 16, 6, 16);
    ctx.fillStyle = ENV.treeTrunkDark;
    ctx.fillRect(x + 5, y + 16, 2, 16);
    ctx.fillStyle = ENV.treeLeaf[0];
    ctx.fillRect(x + 1, y + 8, 14, 10);
    ctx.fillStyle = ENV.treeLeaf[1];
    ctx.fillRect(x + 3, y + 2, 10, 8);
    ctx.fillStyle = ENV.treeLeaf[2];
    ctx.fillRect(x + 5, y, 6, 6);
    ctx.fillStyle = '#66bb6a';
    ctx.fillRect(x + 8, y + 3, 3, 2);
}

function drawFountainBase(ctx, x, y) {
    ctx.fillStyle = ENV.stone;
    ctx.fillRect(x + 2, y + 16, 28, 12);
    ctx.fillStyle = ENV.stoneDark;
    ctx.fillRect(x + 2, y + 26, 28, 2);
    ctx.fillStyle = ENV.stoneLight;
    ctx.fillRect(x + 2, y + 16, 28, 2);
    ctx.fillStyle = ENV.stone;
    ctx.fillRect(x + 12, y + 4, 8, 14);
    ctx.fillStyle = ENV.stoneLight;
    ctx.fillRect(x + 12, y + 4, 2, 14);
    ctx.fillStyle = ENV.stoneDark;
    ctx.fillRect(x + 10, y + 2, 12, 4);
    ctx.fillStyle = ENV.water[0];
    ctx.fillRect(x + 4, y + 18, 24, 6);
}

function drawFountainAnim(ctx, x, y, frame) {
    // Sparkle on water
    const t = frame * 0.08;
    ctx.fillStyle = ENV.waterLight;
    ctx.fillRect(x + 8 + Math.sin(t) * 4, y + 20, 2, 2);
    ctx.fillRect(x + 18 + Math.cos(t * 1.3) * 3, y + 21, 2, 2);
    // Water drops from top
    ctx.fillStyle = ENV.water[1];
    const dy1 = (frame % 20) * 0.6;
    const dy2 = ((frame + 10) % 20) * 0.6;
    if (dy1 < 10) ctx.fillRect(x + 14, y + 6 + dy1, 2, 2);
    if (dy2 < 10) ctx.fillRect(x + 18, y + 6 + dy2, 2, 2);
}

function drawLamppost(ctx, x, y) {
    ctx.fillStyle = '#424242';
    ctx.fillRect(x + 1, y + 8, 2, 16);
    ctx.fillStyle = '#616161';
    ctx.fillRect(x - 1, y + 6, 6, 3);
    ctx.fillStyle = '#fff9c4';
    ctx.fillRect(x, y + 4, 4, 3);
}

function drawFlower(ctx, x, y, color) {
    ctx.fillStyle = color || '#e91e63';
    ctx.fillRect(x, y, 2, 2);
    ctx.fillRect(x + 2, y, 2, 2);
    ctx.fillRect(x, y + 2, 2, 2);
    ctx.fillRect(x + 2, y + 2, 2, 2);
    ctx.fillStyle = '#fdd835';
    ctx.fillRect(x + 1, y + 1, 2, 2);
    ctx.fillStyle = '#4caf50';
    ctx.fillRect(x + 1, y + 4, 1, 3);
}

// ==================== Character Sprites (Walk Cycle) ====================

function drawCharacter(ctx, cx, cy, agentKey, walkFrame, direction) {
    const s = 2;
    const p = CHAR_PAL[agentKey];
    if (!p) return;
    const ox = cx - 8 * s;
    const oy = cy - 16 * s;

    // Hat / Hair
    if (p.toque) {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(ox + 5*s, oy - 2*s, 6*s, 3*s);
        ctx.fillStyle = '#e0e0e0';
        ctx.fillRect(ox + 6*s, oy - 3*s, 4*s, 2*s);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(ox + 4*s, oy + 1*s, 8*s, 1*s);
    } else if (p.hat) {
        ctx.fillStyle = p.hat;
        ctx.fillRect(ox + 4*s, oy, 8*s, 2*s);
        ctx.fillStyle = p.hatBrim;
        ctx.fillRect(ox + 3*s, oy + 2*s, 10*s, 1*s);
    } else {
        ctx.fillStyle = p.hair;
        ctx.fillRect(ox + 4*s, oy, 8*s, 3*s);
    }

    // Face
    ctx.fillStyle = p.skin;
    ctx.fillRect(ox + 4*s, oy + 3*s, 8*s, 3*s);
    // Eyes
    ctx.fillStyle = p.eyes;
    if (direction === 1) {
        ctx.fillRect(ox + 5*s, oy + 4*s, s, s);
        ctx.fillRect(ox + 8*s, oy + 4*s, s, s);
    } else if (direction === 2) {
        ctx.fillRect(ox + 7*s, oy + 4*s, s, s);
        ctx.fillRect(ox + 10*s, oy + 4*s, s, s);
    } else {
        ctx.fillRect(ox + 5*s, oy + 4*s, 2*s, s);
        ctx.fillRect(ox + 9*s, oy + 4*s, 2*s, s);
    }
    // Mouth
    ctx.fillStyle = '#c0392b';
    ctx.fillRect(ox + 7*s, oy + 5*s, 2*s, s);

    // Body
    ctx.fillStyle = p.body;
    ctx.fillRect(ox + 3*s, oy + 6*s, 10*s, 5*s);
    ctx.fillStyle = p.bodyDark;
    ctx.fillRect(ox + 3*s, oy + 6*s, s, 5*s);
    ctx.fillRect(ox + 12*s, oy + 6*s, s, 5*s);

    // Accent (bow tie for concierge, belt for others)
    if (agentKey === 'concierge') {
        ctx.fillStyle = p.acc;
        ctx.fillRect(ox + 7*s, oy + 6*s, 2*s, s);
    }

    // Arms
    ctx.fillStyle = p.skin;
    const armOffsets = [[7, 7], [6, 8], [8, 6]];
    const [lArm, rArm] = [armOffsets[walkFrame][0], armOffsets[walkFrame][1]];
    ctx.fillRect(ox + 1*s, oy + lArm*s, 2*s, 4*s);
    ctx.fillRect(ox + 13*s, oy + rArm*s, 2*s, 4*s);

    // Legs
    ctx.fillStyle = '#2c3e50';
    if (walkFrame === 0) {
        ctx.fillRect(ox + 5*s, oy + 11*s, 3*s, 3*s);
        ctx.fillRect(ox + 8*s, oy + 11*s, 3*s, 3*s);
    } else if (walkFrame === 1) {
        ctx.fillRect(ox + 4*s, oy + 11*s, 3*s, 4*s);
        ctx.fillRect(ox + 9*s, oy + 11*s, 3*s, 2*s);
    } else {
        ctx.fillRect(ox + 5*s, oy + 11*s, 3*s, 2*s);
        ctx.fillRect(ox + 9*s, oy + 11*s, 3*s, 4*s);
    }
    // Shoes
    ctx.fillStyle = '#3e2723';
    if (walkFrame === 0) {
        ctx.fillRect(ox + 4*s, oy + 14*s, 4*s, 2*s);
        ctx.fillRect(ox + 8*s, oy + 14*s, 4*s, 2*s);
    } else if (walkFrame === 1) {
        ctx.fillRect(ox + 3*s, oy + 15*s, 4*s, s);
        ctx.fillRect(ox + 9*s, oy + 13*s, 4*s, s);
    } else {
        ctx.fillRect(ox + 4*s, oy + 13*s, 4*s, s);
        ctx.fillRect(ox + 9*s, oy + 15*s, 4*s, s);
    }

    // Accessories
    if (agentKey === 'concierge') {
        ctx.fillStyle = '#e0e0e0';
        ctx.fillRect(ox + 15*s, oy + 8*s, 2*s, 3*s);
        ctx.fillStyle = '#9e9e9e';
        ctx.fillRect(ox + 15*s, oy + 9*s, 2*s, s);
    } else if (agentKey === 'hotel') {
        ctx.fillStyle = '#fdd835';
        ctx.fillRect(ox - s, oy + 8*s, 2*s, s);
        ctx.fillRect(ox - s, oy + 7*s, s, s);
    } else if (agentKey === 'ticket') {
        ctx.fillStyle = '#fff9c4';
        ctx.fillRect(ox + 15*s, oy + 8*s, 3*s, 2*s);
        ctx.fillStyle = '#ef5350';
        ctx.fillRect(ox + 15*s, oy + 9*s, 3*s, s);
    }
}

function drawExclamation(ctx, x, y) {
    ctx.fillStyle = '#fdd835';
    ctx.font = 'bold 12px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('!', x, y);
}

function drawCheckmark(ctx, x, y) {
    ctx.fillStyle = '#66bb6a';
    ctx.font = 'bold 10px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('\u2713', x, y);
}

function drawAgentLabel(ctx, x, y, label, color) {
    ctx.fillStyle = color;
    ctx.font = '7px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText(label, x, y + 22);
}

// ==================== Agent Registry ====================

const AGENTS = {
    concierge:  { x: 240, y: 240, color: '#e8b830', label: 'Concierge', icon: '\u2606' },
    hotel:      { x: 64,  y: 100, color: '#1565c0', label: 'Hotel',     icon: '\u2302' },
    flight:     { x: 240, y: 100, color: '#4fc3f7', label: 'Flight',    icon: '\u2708' },
    train:      { x: 400, y: 100, color: '#388e3c', label: 'Train',     icon: '\u2634' },
    ticket:     { x: 80,  y: 380, color: '#e65100', label: 'Ticket',    icon: '\u2660' },
    restaurant: { x: 400, y: 380, color: '#d32f2f', label: 'Restaurant',icon: '\u2615' },
    merchandise:{ x: 240, y: 400, color: '#9c27b0', label: 'Shop',       icon: '\u2605' },
};

const BUILDINGS = {
    hotel:      { x: 24,  y: 16,  draw: drawHotelBuilding },
    flight:     { x: 184, y: 16,  draw: drawAirportBuilding },
    train:      { x: 368, y: 16,  draw: drawTrainStation },
    ticket:     { x: 24,  y: 336, draw: drawTheater },
    restaurant: { x: 336, y: 340, draw: drawRestaurantBuilding },
    merchandise:{ x: 200, y: 350, draw: drawMerchandiseShop },
};

const DECORATIONS = {
    trees: [
        { x: 144, y: 176 }, { x: 160, y: 160 },
        { x: 304, y: 176 }, { x: 320, y: 160 },
        { x: 144, y: 272 }, { x: 160, y: 288 },
        { x: 304, y: 272 }, { x: 320, y: 288 },
        { x: 0, y: 144 }, { x: 462, y: 144 },
        { x: 0, y: 320 }, { x: 462, y: 320 },
    ],
    fountain: { x: 224, y: 224 },
    lampposts: [
        { x: 196, y: 104 }, { x: 268, y: 104 },
        { x: 196, y: 344 }, { x: 268, y: 344 },
    ],
    flowers: [
        { x: 128, y: 196, color: '#e91e63' }, { x: 340, y: 196, color: '#ff9800' },
        { x: 128, y: 296, color: '#9c27b0' }, { x: 340, y: 296, color: '#ff5722' },
        { x: 180, y: 180, color: '#f44336' }, { x: 292, y: 180, color: '#e91e63' },
        { x: 180, y: 300, color: '#ff9800' }, { x: 292, y: 300, color: '#9c27b0' },
    ],
};

/**
 * Pre-render the entire static scene (ground + buildings + decorations) onto an offscreen canvas.
 */
function renderStaticScene(ctx) {
    renderGround(ctx);
    Object.values(BUILDINGS).forEach(b => b.draw(ctx, b.x, b.y));
    DECORATIONS.trees.forEach(t => drawTree(ctx, t.x, t.y));
    drawFountainBase(ctx, DECORATIONS.fountain.x, DECORATIONS.fountain.y);
    DECORATIONS.lampposts.forEach(l => drawLamppost(ctx, l.x, l.y));
    DECORATIONS.flowers.forEach(f => drawFlower(ctx, f.x, f.y, f.color));
}
