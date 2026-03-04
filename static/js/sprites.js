/**
 * sprites.js - RPG Village pixel art: tilemap, buildings, character sprites
 * Style: Final Fantasy 2 NES (1988) - Black outlines, NES palette, detailed tiles
 */

// ==================== NES Palette ====================

const NES_PALETTE = {
    black:      '#000000',
    darkGray:   '#585858',
    gray:       '#A0A0A0',
    lightGray:  '#BCBCBC',
    white:      '#F8F8F8',
    darkRed:    '#A81000',
    red:        '#F83800',
    lightRed:   '#FC7460',
    paleRed:    '#FCA0A0',
    darkBlue:   '#0000BC',
    blue:       '#0058F8',
    lightBlue:  '#3CBCFC',
    paleBlue:   '#A4E4FC',
    darkGreen:  '#005800',
    green:      '#00A800',
    lightGreen: '#58F898',
    paleGreen:  '#B8F8B8',
    darkBrown:  '#503000',
    brown:      '#AC7C00',
    tan:        '#F0BC3C',
    paleTan:    '#FCE0A8',
    darkPurple: '#44009C',
    purple:     '#6844FC',
    lightPurple:'#B884FC',
    palePurple: '#D8B8F8',
    skin:       '#FCBCB0',
    skinMed:    '#E4A672',
    skinDark:   '#C48424',
    darkOrange: '#944A00',
    orange:     '#E47818',
    lightOrange:'#FCA044',
    yellow:     '#F8D830',
    lightYellow:'#F8F878',
    paleYellow: '#FCFCB0',
    darkCyan:   '#006858',
    cyan:       '#00B8A8',
    lightCyan:  '#68D8D8',
};

// ==================== Environment Palette (NES-mapped) ====================

const ENV = {
    grass:      ['#188C00', '#0A6C00', '#30A020'],
    grassDark:  '#005800',
    grassLight: '#58F898',
    path:       ['#E4A672', '#C48424', '#D09848'],
    pathEdge:   '#503000',
    pathJoint:  '#AC7C00',
    wall: '#F8F8F8', wallDark: '#BCBCBC', wallLight: '#F8F8F8',
    treeTrunk: '#503000', treeTrunkDark: '#3C1800',
    treeLeaf: ['#005800', '#00A800', '#30A020'],
    water: ['#0058F8', '#3CBCFC'], waterLight: '#A4E4FC',
    stone: '#A0A0A0', stoneDark: '#585858', stoneLight: '#BCBCBC',
    dirt:       ['#C48424', '#AC7C00', '#B88C20'],
    dirtDark:   '#944A00',
    dirtLight:  '#D09848',
};

const CHAR_PAL = {
    concierge:  { skin:'#FCBCB0', hair:'#503000', body:'#6844FC', bodyDark:'#44009C', eyes:'#000000', acc:'#F83800' },
    hotel:      { skin:'#FCBCB0', hair:'#200800', body:'#0058F8', bodyDark:'#0000BC', eyes:'#000000', acc:'#F8D830' },
    flight:     { skin:'#E4A672', hair:'#000000', body:'#3CBCFC', bodyDark:'#0058F8', eyes:'#000000', acc:'#F8F8F8', hat:'#0000BC', hatBrim:'#0058F8' },
    train:      { skin:'#FCBCB0', hair:'#503000', body:'#00A800', bodyDark:'#005800', eyes:'#000000', acc:'#F8D830', hat:'#005800', hatBrim:'#00A800' },
    ticket:     { skin:'#C48424', hair:'#000000', body:'#E47818', bodyDark:'#944A00', eyes:'#000000', acc:'#F8F8F8' },
    restaurant: { skin:'#FCBCB0', hair:'#503000', body:'#F83800', bodyDark:'#A81000', eyes:'#000000', acc:'#F8F8F8', toque:true },
    merchandise:{ skin:'#E4A672', hair:'#000000', body:'#B884FC', bodyDark:'#6844FC', eyes:'#000000', acc:'#F8D830' },
    insurance:  { skin:'#FCBCB0', hair:'#200800', body:'#00A800', bodyDark:'#005800', eyes:'#000000', acc:'#F8D830' },
};

// ==================== Ground ====================

const TS = 16; // tile size
const GW = 30, GH = 30; // grid dimensions

function tileHash(x, y) { return ((x * 7 + y * 13 + x * y * 3) & 0x7fffffff) % 3; }
function tileHash2(x, y) { return ((x * 11 + y * 17 + x * y * 7) & 0x7fffffff) % 20; }

function isPathTile(tx, ty) {
    const x = tx, y = ty;
    if (y >= 6 && y <= 7 && x >= 1 && x <= 28) return true;
    if (y >= 21 && y <= 22 && x >= 1 && x <= 28) return true;
    if (x >= 14 && x <= 15 && y >= 6 && y <= 22) return true;
    if (x >= 3 && x <= 4 && y >= 4 && y <= 6) return true;
    if (x >= 25 && x <= 26 && y >= 4 && y <= 6) return true;
    if (x >= 4 && x <= 5 && y >= 22 && y <= 24) return true;
    if (x >= 24 && x <= 25 && y >= 22 && y <= 24) return true;
    // Flight side path
    if (x >= 14 && x <= 15 && y >= 4 && y <= 5) return true;
    if (x >= 14 && x <= 15 && y >= 22 && y <= 24) return true;
    if (x >= 12 && x <= 17 && y >= 13 && y <= 17) return true;
    // Insurance path (extending plaza right)
    if (y >= 14 && y <= 15 && x >= 18 && x <= 25) return true;
    // Insurance connector (north from path to building)
    if (x >= 24 && x <= 25 && y >= 11 && y <= 14) return true;
    return false;
}

function isDirtZone(tx, ty) {
    // Hotel footprint (px 24..104, py 32..80) + 1-tile margin
    if (tx >= 0 && tx <= 7 && ty >= 0 && ty <= 5) return true;
    // Airport footprint (px 184..304, py 0..72) + margin
    if (tx >= 10 && tx <= 19 && ty >= 0 && ty <= 5) return true;
    // Train footprint (px 368..448, py 30..72) + margin
    if (tx >= 22 && tx <= 29 && ty >= 0 && ty <= 5) return true;
    // Theater footprint (px 24..120, py 358..408) + margin
    if (tx >= 0 && tx <= 8 && ty >= 21 && ty <= 29) return true;
    // Shop footprint (px 200..280, py 350..400) + margin
    if (tx >= 11 && tx <= 18 && ty >= 21 && ty <= 29) return true;
    // Restaurant footprint (px 336..432, py 354..404) + margin
    if (tx >= 21 && tx <= 29 && ty >= 21 && ty <= 29) return true;
    // Insurance building footprint (px 376..456, py 144..232) + margin
    if (tx >= 22 && tx <= 29 && ty >= 8 && ty <= 16) return true;
    return false;
}

function renderGround(ctx) {
    for (let ty = 0; ty < GH; ty++) {
        for (let tx = 0; tx < GW; tx++) {
            const px = tx * TS, py = ty * TS;
            const h = tileHash(tx, ty);
            const h2 = tileHash2(tx, ty);
            if (isPathTile(tx, ty)) {
                // Base path color
                ctx.fillStyle = ENV.path[h];
                ctx.fillRect(px, py, TS, TS);
                // Cobblestone joints
                ctx.fillStyle = ENV.pathJoint;
                ctx.fillRect(px, py + 5, TS, 1);
                ctx.fillRect(px, py + 11, TS, 1);
                if (ty % 2 === 0) {
                    ctx.fillRect(px + 4, py, 1, 5);
                    ctx.fillRect(px + 12, py, 1, 5);
                    ctx.fillRect(px, py + 6, 1, 5);
                    ctx.fillRect(px + 8, py + 6, 1, 5);
                    ctx.fillRect(px + 4, py + 12, 1, 4);
                    ctx.fillRect(px + 12, py + 12, 1, 4);
                } else {
                    ctx.fillRect(px, py, 1, 5);
                    ctx.fillRect(px + 8, py, 1, 5);
                    ctx.fillRect(px + 4, py + 6, 1, 5);
                    ctx.fillRect(px + 12, py + 6, 1, 5);
                    ctx.fillRect(px, py + 12, 1, 4);
                    ctx.fillRect(px + 8, py + 12, 1, 4);
                }
                // Path-grass border detection
                ctx.fillStyle = ENV.pathEdge;
                if (tx > 0 && !isPathTile(tx - 1, ty)) ctx.fillRect(px, py, 1, TS);
                if (tx < GW - 1 && !isPathTile(tx + 1, ty)) ctx.fillRect(px + TS - 1, py, 1, TS);
                if (ty > 0 && !isPathTile(tx, ty - 1)) ctx.fillRect(px, py, TS, 1);
                if (ty < GH - 1 && !isPathTile(tx, ty + 1)) ctx.fillRect(px, py + TS - 1, TS, 1);
            } else if (isDirtZone(tx, ty)) {
                // Dirt/earth around buildings
                ctx.fillStyle = ENV.dirt[h];
                ctx.fillRect(px, py, TS, TS);
                // Subtle cracks / pebbles
                if (h2 === 0) {
                    ctx.fillStyle = ENV.dirtDark;
                    ctx.fillRect(px + 6, py + 4, 4, 1);
                }
                if (h2 === 9) {
                    ctx.fillStyle = ENV.dirtDark;
                    ctx.fillRect(px + 2, py + 11, 3, 1);
                    ctx.fillRect(px + 11, py + 7, 1, 3);
                }
                if (h2 === 15) {
                    ctx.fillStyle = ENV.dirtLight;
                    ctx.fillRect(px + 8, py + 10, 2, 2);
                }
                // Dirt-grass border: 1px dark edge where dirt meets grass
                ctx.fillStyle = ENV.dirtDark;
                if (tx > 0 && !isPathTile(tx-1,ty) && !isDirtZone(tx-1,ty)) ctx.fillRect(px, py, 1, TS);
                if (tx < GW-1 && !isPathTile(tx+1,ty) && !isDirtZone(tx+1,ty)) ctx.fillRect(px+TS-1, py, 1, TS);
                if (ty > 0 && !isPathTile(tx,ty-1) && !isDirtZone(tx,ty-1)) ctx.fillRect(px, py, TS, 1);
                if (ty < GH-1 && !isPathTile(tx,ty+1) && !isDirtZone(tx,ty+1)) ctx.fillRect(px, py+TS-1, TS, 1);
            } else {
                // Grass (middle open areas)
                ctx.fillStyle = ENV.grass[h];
                ctx.fillRect(px, py, TS, TS);
                // Sparse grass blades
                if (h2 === 0) {
                    ctx.fillStyle = ENV.grassDark;
                    ctx.fillRect(px + 7, py + 10, 1, 3);
                }
                if (h2 === 7) {
                    ctx.fillStyle = ENV.grassLight;
                    ctx.fillRect(px + 3, py + 9, 1, 3);
                }
                // Rare flower
                if (h2 === 13) {
                    ctx.fillStyle = NES_PALETTE.red;
                    ctx.fillRect(px + 5, py + 6, 2, 2);
                    ctx.fillStyle = NES_PALETTE.yellow;
                    ctx.fillRect(px + 5, py + 6, 1, 1);
                }
            }
        }
    }
}

// ==================== Outline Helper ====================

function outlineRect(ctx, x, y, w, h) {
    ctx.fillStyle = NES_PALETTE.black;
    ctx.fillRect(x, y, w, 1);
    ctx.fillRect(x, y + h - 1, w, 1);
    ctx.fillRect(x, y, 1, h);
    ctx.fillRect(x + w - 1, y, 1, h);
}

function roofTexture(ctx, x, y, w, h, spacing) {
    ctx.fillStyle = NES_PALETTE.black;
    for (let i = spacing; i < w; i += spacing) {
        ctx.fillRect(x + i, y + 1, 1, h - 2);
    }
}

// ==================== Buildings ====================

function drawHotelBuilding(ctx, x, y) {
    // Main wall
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 16, 80, 48);
    ctx.fillStyle = ENV.wallDark;
    ctx.fillRect(x, y + 16, 80, 2);
    outlineRect(ctx, x, y + 16, 80, 48);
    // Roof (red)
    ctx.fillStyle = NES_PALETTE.darkRed;
    ctx.fillRect(x - 2, y + 10, 84, 8);
    ctx.fillStyle = NES_PALETTE.red;
    ctx.fillRect(x + 6, y + 2, 68, 10);
    ctx.fillStyle = '#881000';
    ctx.fillRect(x + 16, y - 2, 48, 6);
    outlineRect(ctx, x - 2, y + 10, 84, 8);
    outlineRect(ctx, x + 6, y + 2, 68, 10);
    outlineRect(ctx, x + 16, y - 2, 48, 6);
    roofTexture(ctx, x + 6, y + 2, 68, 10, 10);
    // Windows (3 floors x 3)
    for (let f = 0; f < 3; f++) {
        for (let w = 0; w < 3; w++) {
            const wx = x + 8 + w * 24, wy = y + 22 + f * 12;
            ctx.fillStyle = NES_PALETTE.lightBlue;
            ctx.fillRect(wx, wy, 10, 8);
            ctx.fillStyle = NES_PALETTE.blue;
            ctx.fillRect(wx + 4, wy, 2, 8);
            ctx.fillRect(wx, wy + 3, 10, 2);
            outlineRect(ctx, wx, wy, 10, 8);
        }
    }
    // Door
    ctx.fillStyle = NES_PALETTE.darkBrown;
    ctx.fillRect(x + 32, y + 52, 16, 12);
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 44, y + 57, 3, 3);
    outlineRect(ctx, x + 32, y + 52, 16, 12);
    // "H" sign
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.font = 'bold 10px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('H', x + 40, y + 9);
}

function drawAirportBuilding(ctx, x, y) {
    // Terminal
    ctx.fillStyle = ENV.wallLight;
    ctx.fillRect(x, y + 14, 100, 42);
    outlineRect(ctx, x, y + 14, 100, 42);
    // Glass front
    ctx.fillStyle = NES_PALETTE.paleBlue;
    ctx.fillRect(x + 4, y + 22, 88, 26);
    ctx.fillStyle = NES_PALETTE.lightBlue;
    for (let i = 0; i < 7; i++) ctx.fillRect(x + 4 + i * 13, y + 22, 2, 26);
    outlineRect(ctx, x + 4, y + 22, 88, 26);
    // Blue roof
    ctx.fillStyle = NES_PALETTE.darkBlue;
    ctx.fillRect(x - 2, y + 8, 104, 8);
    ctx.fillStyle = NES_PALETTE.blue;
    ctx.fillRect(x + 8, y + 2, 84, 8);
    outlineRect(ctx, x - 2, y + 8, 104, 8);
    outlineRect(ctx, x + 8, y + 2, 84, 8);
    roofTexture(ctx, x + 8, y + 2, 84, 8, 12);
    // Control tower
    ctx.fillStyle = NES_PALETTE.lightGray;
    ctx.fillRect(x + 88, y - 16, 16, 72);
    outlineRect(ctx, x + 88, y - 16, 16, 72);
    ctx.fillStyle = NES_PALETTE.lightBlue;
    ctx.fillRect(x + 90, y - 12, 12, 8);
    outlineRect(ctx, x + 90, y - 12, 12, 8);
    ctx.fillStyle = NES_PALETTE.darkBlue;
    ctx.fillRect(x + 93, y - 18, 6, 6);
    outlineRect(ctx, x + 93, y - 18, 6, 6);
    // Door
    ctx.fillStyle = NES_PALETTE.blue;
    ctx.fillRect(x + 42, y + 48, 16, 8);
    outlineRect(ctx, x + 42, y + 48, 16, 8);
    // Runway markings
    ctx.fillStyle = NES_PALETTE.yellow;
    for (let i = 0; i < 5; i++) ctx.fillRect(x + 10 + i * 18, y + 58, 8, 2);
}

function drawTrainStation(ctx, x, y) {
    // Main
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 14, 80, 42);
    outlineRect(ctx, x, y + 14, 80, 42);
    // Green roof
    ctx.fillStyle = NES_PALETTE.darkGreen;
    ctx.fillRect(x - 2, y + 8, 84, 8);
    ctx.fillStyle = NES_PALETTE.green;
    ctx.fillRect(x + 10, y + 2, 60, 8);
    outlineRect(ctx, x - 2, y + 8, 84, 8);
    outlineRect(ctx, x + 10, y + 2, 60, 8);
    roofTexture(ctx, x + 10, y + 2, 60, 8, 10);
    // Arches
    for (let i = 0; i < 3; i++) {
        const ax = x + 8 + i * 24;
        ctx.fillStyle = NES_PALETTE.darkBrown;
        ctx.fillRect(ax, y + 30, 16, 20);
        ctx.fillStyle = '#3C1800';
        ctx.fillRect(ax + 2, y + 26, 12, 6);
        outlineRect(ctx, ax, y + 26, 16, 24);
    }
    // Clock
    ctx.fillStyle = NES_PALETTE.white;
    ctx.beginPath(); ctx.arc(x + 40, y + 20, 6, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = NES_PALETTE.black; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(x + 40, y + 20, 6, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = NES_PALETTE.black;
    ctx.fillRect(x + 39, y + 15, 2, 5);
    ctx.fillRect(x + 40, y + 19, 4, 1);
    // Rails
    ctx.fillStyle = NES_PALETTE.darkGray;
    ctx.fillRect(x - 4, y + 56, 88, 2);
    ctx.fillRect(x - 4, y + 60, 88, 2);
    ctx.fillStyle = NES_PALETTE.darkBrown;
    for (let i = 0; i < 8; i++) ctx.fillRect(x - 2 + i * 11, y + 55, 4, 8);
}

function drawTheater(ctx, x, y) {
    // Main
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 22, 96, 50);
    outlineRect(ctx, x, y + 22, 96, 50);
    // Pediment
    ctx.fillStyle = ENV.wallDark;
    ctx.fillRect(x - 2, y + 16, 100, 8);
    outlineRect(ctx, x - 2, y + 16, 100, 8);
    ctx.fillStyle = NES_PALETTE.orange;
    ctx.beginPath();
    ctx.moveTo(x + 6, y + 16);
    ctx.lineTo(x + 48, y);
    ctx.lineTo(x + 90, y + 16);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = NES_PALETTE.black; ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x + 6, y + 16);
    ctx.lineTo(x + 48, y);
    ctx.lineTo(x + 90, y + 16);
    ctx.closePath();
    ctx.stroke();
    // Columns
    for (let i = 0; i < 4; i++) {
        const cx = x + 12 + i * 22;
        ctx.fillStyle = ENV.wallLight;
        ctx.fillRect(cx, y + 22, 8, 34);
        ctx.fillStyle = ENV.wallDark;
        ctx.fillRect(cx - 1, y + 20, 10, 4);
        ctx.fillRect(cx - 1, y + 54, 10, 4);
        outlineRect(ctx, cx, y + 22, 8, 34);
        outlineRect(ctx, cx - 1, y + 20, 10, 4);
        outlineRect(ctx, cx - 1, y + 54, 10, 4);
    }
    // Marquee
    ctx.fillStyle = NES_PALETTE.orange;
    ctx.fillRect(x + 16, y + 58, 64, 10);
    outlineRect(ctx, x + 16, y + 58, 64, 10);
    for (let i = 0; i < 7; i++) {
        ctx.fillStyle = (i % 2 === 0) ? NES_PALETTE.yellow : NES_PALETTE.paleYellow;
        ctx.fillRect(x + 20 + i * 8, y + 60, 4, 4);
    }
    // Door
    ctx.fillStyle = NES_PALETTE.darkBrown;
    ctx.fillRect(x + 38, y + 62, 20, 10);
    outlineRect(ctx, x + 38, y + 62, 20, 10);
}

function drawRestaurantBuilding(ctx, x, y) {
    // Main wall
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 14, 96, 50);
    outlineRect(ctx, x, y + 14, 96, 50);
    // Striped awning
    for (let i = 0; i < 12; i++) {
        ctx.fillStyle = (i % 2 === 0) ? NES_PALETTE.red : NES_PALETTE.white;
        ctx.fillRect(x + i * 8, y + 8, 8, 8);
    }
    outlineRect(ctx, x, y + 8, 96, 8);
    // Left window
    ctx.fillStyle = NES_PALETTE.paleTan;
    ctx.fillRect(x + 8, y + 24, 22, 16);
    ctx.fillStyle = NES_PALETTE.tan;
    ctx.fillRect(x + 18, y + 24, 2, 16);
    outlineRect(ctx, x + 8, y + 24, 22, 16);
    // Door
    ctx.fillStyle = NES_PALETTE.darkBrown;
    ctx.fillRect(x + 38, y + 24, 14, 28);
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 48, y + 36, 2, 3);
    outlineRect(ctx, x + 38, y + 24, 14, 28);
    // Right window
    ctx.fillStyle = NES_PALETTE.paleTan;
    ctx.fillRect(x + 60, y + 24, 22, 16);
    ctx.fillStyle = NES_PALETTE.tan;
    ctx.fillRect(x + 70, y + 24, 2, 16);
    outlineRect(ctx, x + 60, y + 24, 22, 16);
    // Chimney
    ctx.fillStyle = NES_PALETTE.brown;
    ctx.fillRect(x + 76, y - 2, 8, 12);
    ctx.fillStyle = NES_PALETTE.darkBrown;
    ctx.fillRect(x + 74, y - 4, 12, 4);
    outlineRect(ctx, x + 76, y - 2, 8, 12);
    outlineRect(ctx, x + 74, y - 4, 12, 4);
    // Outdoor table
    ctx.fillStyle = NES_PALETTE.brown;
    ctx.fillRect(x + 14, y + 52, 18, 2);
    ctx.fillRect(x + 22, y + 54, 2, 6);
    ctx.fillStyle = NES_PALETTE.darkBrown;
    ctx.fillRect(x + 10, y + 54, 5, 4);
    ctx.fillRect(x + 30, y + 54, 5, 4);
}

function drawMerchandiseShop(ctx, x, y) {
    // Main wall
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 14, 80, 50);
    outlineRect(ctx, x, y + 14, 80, 50);
    // Striped awning (purple/white)
    for (let i = 0; i < 10; i++) {
        ctx.fillStyle = (i % 2 === 0) ? NES_PALETTE.lightPurple : NES_PALETTE.white;
        ctx.fillRect(x + i * 8, y + 8, 8, 8);
    }
    outlineRect(ctx, x, y + 8, 80, 8);
    // Shop window (left) - display jersey
    ctx.fillStyle = NES_PALETTE.palePurple;
    ctx.fillRect(x + 6, y + 22, 24, 20);
    outlineRect(ctx, x + 6, y + 22, 24, 20);
    // Jersey silhouette
    ctx.fillStyle = NES_PALETTE.white;
    ctx.fillRect(x + 13, y + 25, 10, 12);
    ctx.fillStyle = NES_PALETTE.lightPurple;
    ctx.fillRect(x + 14, y + 26, 8, 10);
    ctx.fillRect(x + 11, y + 26, 3, 4);
    ctx.fillRect(x + 22, y + 26, 3, 4);
    // Door
    ctx.fillStyle = NES_PALETTE.darkBrown;
    ctx.fillRect(x + 34, y + 24, 14, 28);
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 44, y + 36, 2, 3);
    outlineRect(ctx, x + 34, y + 24, 14, 28);
    // Shop window (right) - display scarf
    ctx.fillStyle = NES_PALETTE.palePurple;
    ctx.fillRect(x + 52, y + 22, 24, 20);
    outlineRect(ctx, x + 52, y + 22, 24, 20);
    // Scarf in window
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 57, y + 28, 14, 3);
    ctx.fillStyle = NES_PALETTE.lightPurple;
    ctx.fillRect(x + 55, y + 31, 4, 6);
    ctx.fillRect(x + 67, y + 31, 4, 6);
    // Flag on roof
    ctx.fillStyle = NES_PALETTE.darkGray;
    ctx.fillRect(x + 68, y - 6, 2, 16);
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 70, y - 6, 8, 6);
    ctx.fillStyle = NES_PALETTE.lightPurple;
    ctx.fillRect(x + 70, y - 3, 8, 3);
    outlineRect(ctx, x + 70, y - 6, 8, 6);
    // Star sign
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.font = 'bold 8px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('\u2605', x + 40, y + 6);
}

function drawInsuranceBuilding(ctx, x, y) {
    // Main wall
    ctx.fillStyle = ENV.wall;
    ctx.fillRect(x, y + 16, 80, 48);
    ctx.fillStyle = ENV.wallDark;
    ctx.fillRect(x, y + 16, 80, 2);
    outlineRect(ctx, x, y + 16, 80, 48);
    // Green roof (BNP Paribas Cardif)
    ctx.fillStyle = NES_PALETTE.darkGreen;
    ctx.fillRect(x - 2, y + 10, 84, 8);
    ctx.fillStyle = NES_PALETTE.green;
    ctx.fillRect(x + 6, y + 2, 68, 10);
    outlineRect(ctx, x - 2, y + 10, 84, 8);
    outlineRect(ctx, x + 6, y + 2, 68, 10);
    roofTexture(ctx, x + 6, y + 2, 68, 10, 10);
    // Large window (left) - glass front
    ctx.fillStyle = NES_PALETTE.paleBlue;
    ctx.fillRect(x + 8, y + 24, 22, 16);
    ctx.fillStyle = NES_PALETTE.lightBlue;
    ctx.fillRect(x + 18, y + 24, 2, 16);
    outlineRect(ctx, x + 8, y + 24, 22, 16);
    // Door (green)
    ctx.fillStyle = NES_PALETTE.darkGreen;
    ctx.fillRect(x + 34, y + 28, 14, 24);
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 44, y + 38, 2, 3);
    outlineRect(ctx, x + 34, y + 28, 14, 24);
    // Large window (right) - glass front
    ctx.fillStyle = NES_PALETTE.paleBlue;
    ctx.fillRect(x + 52, y + 24, 22, 16);
    ctx.fillStyle = NES_PALETTE.lightBlue;
    ctx.fillRect(x + 62, y + 24, 2, 16);
    outlineRect(ctx, x + 52, y + 24, 22, 16);
    // Shield emblem on roof
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 34, y - 2, 12, 6);
    ctx.fillStyle = NES_PALETTE.green;
    ctx.fillRect(x + 36, y, 8, 3);
    outlineRect(ctx, x + 34, y - 2, 12, 6);
    // Euro sign on building
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.font = 'bold 8px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('\u20AC', x + 40, y + 56);
}

// ==================== Decorations ====================

function drawTree(ctx, x, y) {
    // Trunk
    ctx.fillStyle = ENV.treeTrunk;
    ctx.fillRect(x + 5, y + 16, 6, 16);
    ctx.fillStyle = ENV.treeTrunkDark;
    ctx.fillRect(x + 5, y + 16, 2, 16);
    outlineRect(ctx, x + 5, y + 16, 6, 16);
    // Canopy
    ctx.fillStyle = ENV.treeLeaf[0];
    ctx.fillRect(x + 1, y + 8, 14, 10);
    ctx.fillStyle = ENV.treeLeaf[1];
    ctx.fillRect(x + 3, y + 2, 10, 8);
    ctx.fillStyle = ENV.treeLeaf[2];
    ctx.fillRect(x + 5, y, 6, 6);
    ctx.fillStyle = NES_PALETTE.lightGreen;
    ctx.fillRect(x + 8, y + 3, 3, 2);
    // Canopy outline
    ctx.fillStyle = NES_PALETTE.black;
    // Bottom of lower canopy
    ctx.fillRect(x + 1, y + 17, 14, 1);
    // Sides of lower canopy
    ctx.fillRect(x, y + 8, 1, 10);
    ctx.fillRect(x + 14, y + 8, 1, 10);
    // Top outline following canopy shape
    ctx.fillRect(x + 1, y + 8, 2, 1);
    ctx.fillRect(x + 13, y + 8, 2, 1);
    ctx.fillRect(x + 3, y + 2, 2, 1);
    ctx.fillRect(x + 11, y + 2, 2, 1);
    ctx.fillRect(x + 2, y + 2, 1, 6);
    ctx.fillRect(x + 12, y + 2, 1, 6);
    ctx.fillRect(x + 5, y - 1, 6, 1);
    ctx.fillRect(x + 4, y, 1, 2);
    ctx.fillRect(x + 10, y, 1, 2);
}

function drawFountainBase(ctx, x, y) {
    ctx.fillStyle = ENV.stone;
    ctx.fillRect(x + 2, y + 16, 28, 12);
    ctx.fillStyle = ENV.stoneDark;
    ctx.fillRect(x + 2, y + 26, 28, 2);
    ctx.fillStyle = ENV.stoneLight;
    ctx.fillRect(x + 2, y + 16, 28, 2);
    outlineRect(ctx, x + 2, y + 16, 28, 12);
    // Pillar
    ctx.fillStyle = ENV.stone;
    ctx.fillRect(x + 12, y + 4, 8, 14);
    ctx.fillStyle = ENV.stoneLight;
    ctx.fillRect(x + 12, y + 4, 2, 14);
    outlineRect(ctx, x + 12, y + 4, 8, 14);
    // Top
    ctx.fillStyle = ENV.stoneDark;
    ctx.fillRect(x + 10, y + 2, 12, 4);
    outlineRect(ctx, x + 10, y + 2, 12, 4);
    // Water
    ctx.fillStyle = ENV.water[0];
    ctx.fillRect(x + 4, y + 18, 24, 6);
}

function drawFountainAnim(ctx, x, y, frame) {
    const t = frame * 0.08;
    ctx.fillStyle = ENV.waterLight;
    ctx.fillRect(x + 8 + Math.sin(t) * 4, y + 20, 2, 2);
    ctx.fillRect(x + 18 + Math.cos(t * 1.3) * 3, y + 21, 2, 2);
    ctx.fillStyle = ENV.water[1];
    const dy1 = (frame % 20) * 0.6;
    const dy2 = ((frame + 10) % 20) * 0.6;
    if (dy1 < 10) ctx.fillRect(x + 14, y + 6 + dy1, 2, 2);
    if (dy2 < 10) ctx.fillRect(x + 18, y + 6 + dy2, 2, 2);
}

function drawLamppost(ctx, x, y) {
    ctx.fillStyle = NES_PALETTE.darkGray;
    ctx.fillRect(x + 1, y + 8, 2, 16);
    ctx.fillStyle = NES_PALETTE.darkGray;
    ctx.fillRect(x - 1, y + 6, 6, 3);
    ctx.fillStyle = NES_PALETTE.paleYellow;
    ctx.fillRect(x, y + 4, 4, 3);
    // Outline
    ctx.fillStyle = NES_PALETTE.black;
    ctx.fillRect(x, y + 8, 1, 16);
    ctx.fillRect(x + 3, y + 8, 1, 16);
}

function drawFlower(ctx, x, y, color) {
    ctx.fillStyle = color || NES_PALETTE.red;
    ctx.fillRect(x, y, 2, 2);
    ctx.fillRect(x + 2, y, 2, 2);
    ctx.fillRect(x, y + 2, 2, 2);
    ctx.fillRect(x + 2, y + 2, 2, 2);
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.fillRect(x + 1, y + 1, 2, 2);
    ctx.fillStyle = NES_PALETTE.green;
    ctx.fillRect(x + 1, y + 4, 1, 3);
}

// ==================== Character Shadow ====================

function drawCharacterShadow(ctx, cx, cy) {
    ctx.save();
    ctx.globalAlpha = 0.3;
    ctx.fillStyle = NES_PALETTE.black;
    ctx.beginPath();
    ctx.ellipse(cx, cy + 2, 10, 3, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
}

// ==================== Character Sprites (4-Frame Walk, Directional) ====================

function drawCharacter(ctx, cx, cy, agentKey, walkFrame, direction, overrideColor) {
    const s = 2;
    const p = CHAR_PAL[agentKey];
    if (!p) return;
    const ox = cx - 8 * s;
    const oy = cy - 16 * s;
    const c = (color) => overrideColor || color;
    const frame = walkFrame % 4;

    // ---- HEAD ----
    if (direction === 3) {
        // Back view: hair covers entire head
        ctx.fillStyle = c(p.hair);
        ctx.fillRect(ox + 4*s, oy, 8*s, 6*s);
        // Ear hints
        ctx.fillStyle = c(p.skin);
        ctx.fillRect(ox + 3*s, oy + 3*s, s, 2*s);
        ctx.fillRect(ox + 12*s, oy + 3*s, s, 2*s);
    } else {
        // Hair / Hat / Toque
        if (p.toque) {
            ctx.fillStyle = c(NES_PALETTE.white);
            ctx.fillRect(ox + 5*s, oy - 2*s, 6*s, 3*s);
            ctx.fillStyle = c(NES_PALETTE.lightGray);
            ctx.fillRect(ox + 6*s, oy - 3*s, 4*s, 2*s);
            ctx.fillStyle = c(NES_PALETTE.white);
            ctx.fillRect(ox + 4*s, oy + s, 8*s, s);
        } else if (p.hat) {
            ctx.fillStyle = c(p.hat);
            ctx.fillRect(ox + 4*s, oy, 8*s, 2*s);
            ctx.fillStyle = c(p.hatBrim);
            ctx.fillRect(ox + 3*s, oy + 2*s, 10*s, s);
        } else {
            ctx.fillStyle = c(p.hair);
            ctx.fillRect(ox + 4*s, oy, 8*s, 3*s);
        }

        // Face (directional)
        ctx.fillStyle = c(p.skin);
        if (direction === 1) {
            // Left: face shifted, hair shows on right
            ctx.fillRect(ox + 3*s, oy + 3*s, 8*s, 3*s);
            ctx.fillStyle = c(p.hair);
            ctx.fillRect(ox + 10*s, oy + 3*s, 2*s, 2*s);
        } else if (direction === 2) {
            // Right: face shifted, hair shows on left
            ctx.fillRect(ox + 5*s, oy + 3*s, 8*s, 3*s);
            ctx.fillStyle = c(p.hair);
            ctx.fillRect(ox + 4*s, oy + 3*s, 2*s, 2*s);
        } else {
            // Front (direction 0)
            ctx.fillRect(ox + 4*s, oy + 3*s, 8*s, 3*s);
        }

        // Eyes
        ctx.fillStyle = c(p.eyes);
        if (direction === 0) {
            ctx.fillRect(ox + 5*s, oy + 4*s, 2*s, s);
            ctx.fillRect(ox + 9*s, oy + 4*s, 2*s, s);
        } else if (direction === 1) {
            ctx.fillRect(ox + 4*s, oy + 4*s, s, s);
            ctx.fillRect(ox + 7*s, oy + 4*s, s, s);
        } else if (direction === 2) {
            ctx.fillRect(ox + 8*s, oy + 4*s, s, s);
            ctx.fillRect(ox + 11*s, oy + 4*s, s, s);
        }

        // Mouth
        ctx.fillStyle = c(NES_PALETTE.darkRed);
        if (direction === 0) {
            ctx.fillRect(ox + 7*s, oy + 5*s, 2*s, s);
        } else if (direction === 1) {
            ctx.fillRect(ox + 5*s, oy + 5*s, 2*s, s);
        } else if (direction === 2) {
            ctx.fillRect(ox + 9*s, oy + 5*s, 2*s, s);
        }
    }

    // ---- BODY ----
    ctx.fillStyle = c(p.body);
    ctx.fillRect(ox + 3*s, oy + 6*s, 10*s, 5*s);
    ctx.fillStyle = c(p.bodyDark);
    ctx.fillRect(ox + 3*s, oy + 6*s, s, 5*s);
    ctx.fillRect(ox + 12*s, oy + 6*s, s, 5*s);

    // Accent (bow tie for concierge)
    if (agentKey === 'concierge') {
        ctx.fillStyle = c(p.acc);
        ctx.fillRect(ox + 7*s, oy + 6*s, 2*s, s);
    }

    // ---- ARMS ----
    ctx.fillStyle = c(p.skin);
    const armOffsets = [[7, 7], [6, 8], [7, 7], [8, 6]];
    const [lArm, rArm] = armOffsets[frame];
    ctx.fillRect(ox + s, oy + lArm*s, 2*s, 4*s);
    ctx.fillRect(ox + 13*s, oy + rArm*s, 2*s, 4*s);

    // ---- LEGS ----
    ctx.fillStyle = c(NES_PALETTE.darkBlue);
    if (frame === 0 || frame === 2) {
        ctx.fillRect(ox + 5*s, oy + 11*s, 3*s, 3*s);
        ctx.fillRect(ox + 8*s, oy + 11*s, 3*s, 3*s);
    } else if (frame === 1) {
        ctx.fillRect(ox + 4*s, oy + 11*s, 3*s, 4*s);
        ctx.fillRect(ox + 9*s, oy + 11*s, 3*s, 2*s);
    } else {
        ctx.fillRect(ox + 5*s, oy + 11*s, 3*s, 2*s);
        ctx.fillRect(ox + 9*s, oy + 11*s, 3*s, 4*s);
    }

    // ---- SHOES ----
    ctx.fillStyle = c(NES_PALETTE.darkBrown);
    if (frame === 0 || frame === 2) {
        ctx.fillRect(ox + 4*s, oy + 14*s, 4*s, 2*s);
        ctx.fillRect(ox + 8*s, oy + 14*s, 4*s, 2*s);
    } else if (frame === 1) {
        ctx.fillRect(ox + 3*s, oy + 15*s, 4*s, s);
        ctx.fillRect(ox + 9*s, oy + 13*s, 4*s, s);
    } else {
        ctx.fillRect(ox + 4*s, oy + 13*s, 4*s, s);
        ctx.fillRect(ox + 9*s, oy + 15*s, 4*s, s);
    }

    // ---- ACCESSORIES ----
    if (agentKey === 'concierge') {
        ctx.fillStyle = c(NES_PALETTE.lightGray);
        ctx.fillRect(ox + 15*s, oy + 8*s, 2*s, 3*s);
        ctx.fillStyle = c(NES_PALETTE.gray);
        ctx.fillRect(ox + 15*s, oy + 9*s, 2*s, s);
    } else if (agentKey === 'hotel') {
        ctx.fillStyle = c(NES_PALETTE.yellow);
        ctx.fillRect(ox - s, oy + 8*s, 2*s, s);
        ctx.fillRect(ox - s, oy + 7*s, s, s);
    } else if (agentKey === 'ticket') {
        ctx.fillStyle = c(NES_PALETTE.paleYellow);
        ctx.fillRect(ox + 15*s, oy + 8*s, 3*s, 2*s);
        ctx.fillStyle = c(NES_PALETTE.red);
        ctx.fillRect(ox + 15*s, oy + 9*s, 3*s, s);
    }
}

function drawExclamation(ctx, x, y) {
    ctx.fillStyle = NES_PALETTE.yellow;
    ctx.font = 'bold 12px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('!', x, y);
}

function drawCheckmark(ctx, x, y) {
    ctx.fillStyle = NES_PALETTE.lightGreen;
    ctx.font = 'bold 10px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('\u2713', x, y);
}

function drawAgentLabel(ctx, x, y, label, color) {
    ctx.font = '7px "Press Start 2P", monospace';
    ctx.textAlign = 'center';
    const tw = ctx.measureText(label).width;
    const pad = 4;
    const bx = x - tw / 2 - pad;
    const by = y + 22 - 7 - 1;
    const bw = tw + pad * 2;
    const bh = 7 + pad;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
    ctx.fillRect(bx, by, bw, bh);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.strokeRect(bx, by, bw, bh);
    ctx.fillStyle = color;
    ctx.fillText(label, x, y + 22);
}

// ==================== Agent Registry ====================

const AGENTS = {
    concierge:  { x: 240, y: 240, color: '#6844FC', label: 'Concierge', icon: '\u2606' },
    hotel:      { x: 64,  y: 100, color: '#0058F8', label: 'Hotel',     icon: '\u2302' },
    flight:     { x: 240, y: 100, color: '#3CBCFC', label: 'Flight',    icon: '\u2708' },
    train:      { x: 400, y: 100, color: '#00A800', label: 'Train',     icon: '\u2634' },
    ticket:     { x: 80,  y: 380, color: '#E47818', label: 'Ticket',    icon: '\u2660' },
    restaurant: { x: 400, y: 380, color: '#F83800', label: 'Restaurant',icon: '\u2615' },
    merchandise:{ x: 240, y: 380, color: '#B884FC', label: 'Shop',       icon: '\u2605' },
    insurance:  { x: 416, y: 240, color: '#00A800', label: 'Insurance',  icon: '\u20AC' },
};

const BUILDINGS = {
    hotel:      { x: 24,  y: 16,  draw: drawHotelBuilding },
    flight:     { x: 184, y: 16,  draw: drawAirportBuilding },
    train:      { x: 368, y: 16,  draw: drawTrainStation },
    ticket:     { x: 24,  y: 336, draw: drawTheater },
    restaurant: { x: 336, y: 340, draw: drawRestaurantBuilding },
    merchandise:{ x: 200, y: 336, draw: drawMerchandiseShop },
    insurance:  { x: 376, y: 168, draw: drawInsuranceBuilding },
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
        { x: 128, y: 196, color: '#F83800' }, { x: 340, y: 196, color: '#E47818' },
        { x: 128, y: 296, color: '#B884FC' }, { x: 340, y: 296, color: '#FC7460' },
        { x: 180, y: 180, color: '#F83800' }, { x: 292, y: 180, color: '#F83800' },
        { x: 180, y: 300, color: '#E47818' }, { x: 292, y: 300, color: '#B884FC' },
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
