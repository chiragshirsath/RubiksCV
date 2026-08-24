// State Variables
let stream = null;
let cubeFaces = {
    U: Array(9).fill('W'),
    L: Array(9).fill('O'),
    F: Array(9).fill('G'),
    R: Array(9).fill('R'),
    B: Array(9).fill('B'),
    D: Array(9).fill('Y')
};
let currentSolution = null;
let currentMoveIndex = 0;
let logicalMoveIndex = 0;
let cubeStateHistory = []; 
let pressesRemaining = 0;
let cubeState = null;
let currentMode = 'camera';
let selectedColor = 'W';
let selectedFace = 'U';
let currentStep = 1;
let reviewEditColor = 'W';
let selectedReviewSticker = null;

// Constants
const faceOrder = ['U', 'R', 'F', 'D', 'L', 'B'];
const colorMap = {
    'W': { name: 'White', css: '#ffffff', textColor: '#333' },
    'Y': { name: 'Yellow', css: '#FFD600', textColor: '#333' },
    'R': { name: 'Red', css: '#E53935', textColor: '#fff' },
    'O': { name: 'Orange', css: '#FF6D00', textColor: '#fff' },
    'G': { name: 'Green', css: '#43A047', textColor: '#fff' },
    'B': { name: 'Blue', css: '#1E88E5', textColor: '#fff' }
};
const faceColorMap = { U: 'W', R: 'R', F: 'G', D: 'Y', L: 'O', B: 'B' };
const faceNames = { U: 'Up', R: 'Right', F: 'Front', D: 'Down', L: 'Left', B: 'Back' };

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initGridOverlay();
    setupEventListeners();
    updateScanUI();
    goToStep(1);
    
    // Default manual grid empty
    clearAllFaces();
});

function setupEventListeners() {
    // Mode toggles
    document.getElementById('cameraModeBtn').addEventListener('click', () => switchMode('camera'));
    document.getElementById('manualModeBtn').addEventListener('click', () => switchMode('manual'));

    // Camera controls
    document.getElementById('startCamera').addEventListener('click', startCamera);
    document.getElementById('stopCamera').addEventListener('click', stopCamera);

    // Face chips (in strip)
    document.querySelectorAll('.face-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            const face = e.currentTarget.getAttribute('data-face');
            if (currentMode === 'camera') {
                scanFace(face);
            } else {
                switchManualFace(face);
            }
        });
    });

    // Manual face tabs
    document.getElementById('manualFaceTabs').addEventListener('click', (e) => {
        const tab = e.target.closest('.face-tab');
        if (tab) {
            switchManualFace(tab.getAttribute('data-face'));
        }
    });

    // Color palette
    document.getElementById('colorPalette').addEventListener('click', (e) => {
        const swatch = e.target.closest('.color-swatch');
        if (swatch) {
            document.querySelectorAll('#colorPalette .color-swatch').forEach(s => s.classList.remove('active'));
            swatch.classList.add('active');
            selectedColor = swatch.getAttribute('data-color');
        }
    });

    // Manual controls
    document.getElementById('clearFaceBtn').addEventListener('click', clearCurrentFace);
    document.getElementById('clearAllBtn').addEventListener('click', clearAllFaces);

    // Step navigation
    document.getElementById('reviewBtn').addEventListener('click', () => goToStep(2));
    document.getElementById('backToScanBtn').addEventListener('click', () => goToStep(1));
    document.getElementById('solveBtn').addEventListener('click', solveCube);
    document.getElementById('startOverBtn').addEventListener('click', startOver);
    document.getElementById('nextMoveBtn').addEventListener('click', handleNextMove);
    document.getElementById('prevMoveBtn').addEventListener('click', handlePrevMove);

    // Step Nav Indicators
    document.getElementById('stepBtn1').addEventListener('click', () => {
        if (currentStep > 1) goToStep(1);
    });
    document.getElementById('stepBtn2').addEventListener('click', () => {
        if (Object.keys(cubeFaces).length === 6 || currentStep > 2) goToStep(2);
    });
    document.getElementById('stepBtn3').addEventListener('click', () => {
        if (currentSolution) goToStep(3);
    });

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (currentStep === 3 && (e.key === ' ' || e.key === 'Enter')) {
            e.preventDefault();
            handleNextMove();
        }
    });

    // Review Palette
    document.getElementById('reviewPalette').addEventListener('click', (e) => {
        const swatch = e.target.closest('.color-swatch');
        if (swatch && selectedReviewSticker) {
            const color = swatch.getAttribute('data-color');
            const face = selectedReviewSticker.getAttribute('data-face');
            const index = parseInt(selectedReviewSticker.getAttribute('data-index'));
            cubeFaces[face][index] = color;
            selectedReviewSticker.style.background = colorMap[color].css;
            selectedReviewSticker.className = `net-sticker sticker-${color}`;
            selectedReviewSticker = null;
            document.getElementById('reviewPalette').style.display = 'none';
        }
    });
}

function initGridOverlay() {
    const grid = document.getElementById('gridOverlay');
    grid.innerHTML = '';
    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        grid.appendChild(cell);
    }
}

function goToStep(step) {
    currentStep = step;
    
    // Update content visibility
    [1, 2, 3].forEach(s => {
        const content = document.getElementById(`step${s}`);
        if (s === step) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });

    // Update nav buttons
    [1, 2, 3].forEach(s => {
        const btn = document.getElementById(`stepBtn${s}`);
        btn.classList.remove('active', 'completed');
        if (s < step) btn.classList.add('completed');
        else if (s === step) btn.classList.add('active');
    });

    if (step === 1) {
        if (currentMode === 'camera') startCamera();
        updateScanUI();
    } else {
        stopCamera();
    }

    if (step === 2) {
        document.getElementById('reviewPalette').style.display = 'none';
        renderReviewNet();
    }

    if (step === 3) {
        if (currentSolution) {
            cubeState = JSON.parse(JSON.stringify(currentSolution.initial_state || cubeFaces));
            currentMoveIndex = 0;
            logicalMoveIndex = 0;
            pressesRemaining = getRequiredPresses(currentSolution.expanded_moves[0]);
            renderSolveView();
        }
    }
}

function switchMode(mode) {
    currentMode = mode;
    document.getElementById('cameraModeBtn').classList.toggle('active', mode === 'camera');
    document.getElementById('manualModeBtn').classList.toggle('active', mode === 'manual');
    
    document.getElementById('cameraContainer').style.display = mode === 'camera' ? 'block' : 'none';
    document.getElementById('manualContainer').style.display = mode === 'manual' ? 'block' : 'none';

    if (mode === 'camera') {
        startCamera();
    } else {
        stopCamera();
        switchManualFace(selectedFace);
    }
}

// Camera Mode
async function startCamera() {
    if (stream) return;
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        const video = document.getElementById('video');
        video.srcObject = stream;
        document.getElementById('cameraPlaceholder').style.display = 'none';
        document.getElementById('gridOverlay').style.display = 'grid';
        document.getElementById('startCamera').style.display = 'none';
        document.getElementById('stopCamera').style.display = 'inline-block';
    } catch (err) {
        console.error("Camera error:", err);
        alert("Could not access camera.");
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        document.getElementById('video').srcObject = null;
        document.getElementById('cameraPlaceholder').style.display = 'flex';
        document.getElementById('gridOverlay').style.display = 'none';
        document.getElementById('startCamera').style.display = 'inline-block';
        document.getElementById('stopCamera').style.display = 'none';
    }
}

async function scanFace(face) {
    if (!stream) {
        alert("Start camera first!");
        return;
    }
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions to match video feed
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const dataUrl = canvas.toDataURL('image/jpeg');

    try {
        const response = await fetch('/api/classify-colors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl, debug: false })
        });
        const data = await response.json();
        
        if (data.colors && data.colors.length === 9) {
            cubeFaces[face] = data.colors;
            
            // Flash animation
            const flash = document.getElementById('scanFlash');
            flash.classList.add('active');
            setTimeout(() => flash.classList.remove('active'), 500);

            // Mark chip scanned
            document.querySelector(`.face-chip[data-face="${face}"]`).classList.add('scanned');
            
            updateScanUI();
            
            // Find next unscanned
            const nextFace = faceOrder.find(f => !cubeFaces[f]);
            document.querySelectorAll('.face-chip').forEach(c => c.classList.remove('next'));
            if (nextFace) {
                document.querySelector(`.face-chip[data-face="${nextFace}"]`).classList.add('next');
            }
        } else {
            alert("Could not detect 9 colors. Please align the cube with the grid.");
        }
    } catch (err) {
        console.error("Scan error:", err);
        alert("Error classifying colors.");
    }
}

// Manual Mode
function switchManualFace(face) {
    selectedFace = face;
    
    // Update tabs
    document.querySelectorAll('.face-tab').forEach(tab => {
        tab.classList.toggle('active', tab.getAttribute('data-face') === face);
    });
    
    // Update chips
    document.querySelectorAll('.face-chip').forEach(chip => {
        chip.classList.toggle('active', chip.getAttribute('data-face') === face);
    });

    renderManualGrid();
}

function renderManualGrid() {
    const grid = document.getElementById('manualGrid');
    grid.innerHTML = '';
    
    const colors = cubeFaces[selectedFace] || Array(9).fill('W');
    
    for (let i = 0; i < 9; i++) {
        const sticker = document.createElement('div');
        sticker.className = `manual-sticker sticker-${colors[i]}`;
        sticker.style.background = colorMap[colors[i]].css;
        sticker.addEventListener('click', () => {
            if (!cubeFaces[selectedFace]) {
                const solvedMap = { U: 'W', L: 'O', F: 'G', R: 'R', B: 'B', D: 'Y' };
                cubeFaces[selectedFace] = Array(9).fill(solvedMap[selectedFace]);
            }
            cubeFaces[selectedFace][i] = selectedColor;
            sticker.style.background = colorMap[selectedColor].css;
            sticker.className = `manual-sticker sticker-${selectedColor}`;
            checkManualFaceComplete();
        });
        grid.appendChild(sticker);
    }
}

function checkManualFaceComplete() {
    const colors = cubeFaces[selectedFace];
    if (colors && colors.length === 9) {
        document.querySelector(`.face-chip[data-face="${selectedFace}"]`).classList.add('scanned');
        updateScanUI();
    }
}

function clearCurrentFace() {
    const solvedMap = { U: 'W', L: 'O', F: 'G', R: 'R', B: 'B', D: 'Y' };
    cubeFaces[selectedFace] = Array(9).fill(solvedMap[selectedFace]);
    renderManualGrid();
    document.querySelector(`.face-chip[data-face="${selectedFace}"]`).classList.remove('scanned');
    updateScanUI();
}

function clearAllFaces() {
    cubeFaces = {
        U: Array(9).fill('W'),
        L: Array(9).fill('O'),
        F: Array(9).fill('G'),
        R: Array(9).fill('R'),
        B: Array(9).fill('B'),
        D: Array(9).fill('Y')
    };
    document.querySelectorAll('.face-chip').forEach(chip => chip.classList.remove('scanned', 'next'));
    if (currentMode === 'manual') renderManualGrid();
    updateScanUI();
}

// UI Updates
function updateScanUI() {
    const count = Object.keys(cubeFaces).length;
    document.getElementById('scanCount').textContent = `${count} / 6`;
    document.getElementById('reviewBtn').disabled = count < 6;
    renderThumbnails();
}

function renderThumbnails() {
    const container = document.getElementById('faceThumbnails');
    container.innerHTML = '';
    
    faceOrder.forEach(face => {
        const thumb = document.createElement('div');
        const hasColors = !!cubeFaces[face];
        thumb.className = `face-thumb ${hasColors ? 'filled' : 'empty'}`;
        
        let gridHtml = '';
        if (hasColors) {
            cubeFaces[face].forEach(c => {
                gridHtml += `<div class="thumb-sticker" style="background:${colorMap[c].css}"></div>`;
            });
        }
        
        const faceColor = faceColorMap[face];
        thumb.innerHTML = `
            <div class="face-thumb-label">
                <span class="chip-dot" style="background:${colorMap[faceColor].css}"></span> ${face}
            </div>
            <div class="thumb-grid">
                ${gridHtml}
            </div>
        `;
        container.appendChild(thumb);
    });
}

// Review Step
function renderReviewNet() {
    const container = document.getElementById('reviewCubeNet');
    container.innerHTML = '';
    
    const layout = {
        U: { r: 1, c: 2 },
        L: { r: 2, c: 1 },
        F: { r: 2, c: 2 },
        R: { r: 2, c: 3 },
        B: { r: 2, c: 4 },
        D: { r: 3, c: 2 }
    };
    
    faceOrder.forEach(face => {
        const pos = layout[face];
        const faceDiv = document.createElement('div');
        faceDiv.className = 'net-face';
        faceDiv.style.gridRow = `${pos.r}/${pos.r+1}`;
        faceDiv.style.gridColumn = `${pos.c}/${pos.c+1}`;
        
        const label = document.createElement('div');
        label.className = 'net-face-label';
        label.textContent = face;
        faceDiv.appendChild(label);
        
        const colors = cubeFaces[face];
        for (let i = 0; i < 9; i++) {
            const c = colors[i];
            const sticker = document.createElement('div');
            sticker.className = `net-sticker sticker-${c}`;
            sticker.style.background = colorMap[c].css;
            sticker.setAttribute('data-face', face);
            sticker.setAttribute('data-index', i);
            
            sticker.addEventListener('click', (e) => {
                selectedReviewSticker = sticker;
                const palette = document.getElementById('reviewPalette');
                palette.style.display = 'flex';
                // Position roughly near click
                const rect = sticker.getBoundingClientRect();
                palette.style.top = `${rect.bottom + window.scrollY + 10}px`;
                palette.style.left = `${Math.max(10, rect.left + window.scrollX - 50)}px`;
            });
            
            faceDiv.appendChild(sticker);
        }
        container.appendChild(faceDiv);
    });
}

// Solve
async function solveCube() {
    document.getElementById('solveBtn').disabled = true;
    document.getElementById('solveBtn').textContent = 'Solving...';
    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cube_faces: cubeFaces })
        });
        const data = await response.json();
        if (data.solution !== undefined) {
            currentSolution = data;
            // Setup initial solve state
            currentMoveIndex = 0;
            logicalMoveIndex = 0;
            cubeStateHistory = [];
            
            // Set initial state from cubeFaces
            currentSolution.initial_state = JSON.parse(JSON.stringify(cubeFaces));
            goToStep(3);
        } else {
            alert(data.error || "Could not solve cube. Check if colors are correct.");
        }
    } catch (err) {
        console.error(err);
        alert("Error communicating with server.");
    } finally {
        document.getElementById('solveBtn').disabled = false;
        document.getElementById('solveBtn').textContent = 'Solve Cube';
    }
}

// Solve Step
function renderSolveView() {
    renderMoveList();
    showCurrentMove();
}

function renderMoveList() {
    const list = document.getElementById('moveList');
    list.innerHTML = '';
    currentSolution.expanded_moves.forEach((move, i) => {
        const chip = document.createElement('div');
        chip.className = 'move-chip';
        chip.textContent = move;
        list.appendChild(chip);
    });
}

function getRequiredPresses(move) {
    if (!move) return 0;
    if (move === 'TURN_BACK') return 1;
    if (move.includes('2')) return 2;
    return move.startsWith('B') ? 3 : (move.includes('2') ? 2 : 1);
}

function getMoveDescription(move) {
    if (move === 'TURN_BACK') return "Rotate the entire cube to show the back face";
    const face = move[0];
    const modifier = move.substring(1);
    const fName = faceNames[face];
    
    let dir = "clockwise";
    if (modifier === "'") dir = "counter-clockwise";
    else if (modifier === "2") dir = "180 degrees (twice)";
    
    return `Turn the ${fName} face ${dir}`;
}

function getArrowSVG(move) {
    if (move === 'TURN_BACK') {
        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150" style="position:absolute; top:0; left:0; width:150px; height:150px; z-index:10; pointer-events:none;">
            <defs>
                <marker id="rotate-head" orient="auto" markerWidth="6" markerHeight="6" refX="5" refY="3">
                    <path d="M0,0 L6,3 L0,6 Z" fill="rgba(255, 255, 255, 0.9)" />
                </marker>
            </defs>
            <path d="M 20 75 Q 75 -20 130 75" stroke="rgba(255, 255, 255, 0.9)" stroke-width="8" fill="none" marker-end="url(#rotate-head)" />
            <text x="75" y="85" fill="white" font-size="20" font-weight="bold" text-anchor="middle">FLIP CUBE</text>
        </svg>`;
    }
    
    const face = move[0];
    const mod = move[1] || '';
    
    let path = '';
    let arrowHeadEnd = true; 
    let arrowHeadStart = false;
    
    if (mod === "'") {
        arrowHeadEnd = false;
        arrowHeadStart = true;
    }
    
    const strokeColor = 'rgba(255, 255, 0, 1)';
    
    if (face === 'U') path = 'M 135 25 L 15 25';
    else if (face === 'D') path = 'M 15 125 L 135 125';
    else if (face === 'R') path = 'M 125 135 L 125 15';
    else if (face === 'L') path = 'M 25 15 L 25 135';
    else if (face === 'F') path = 'M 35 35 A 56 56 0 1 1 35 115'; 
    
    let label = '';
    if (mod === '2') {
        label = `<rect x="55" y="55" width="40" height="40" rx="20" fill="rgba(0,0,0,0.6)" />
                 <text x="75" y="75" fill="#fff" font-size="18" font-weight="bold" text-anchor="middle" alignment-baseline="central">2x</text>`;
    }

    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150" style="position:absolute; top:0; left:0; width:150px; height:150px; z-index:10; pointer-events:none; filter: drop-shadow(0 0 8px rgba(0,0,0,0.8));">
        <defs>
            <marker id="arr-end" orient="auto" markerWidth="6" markerHeight="6" refX="5" refY="3">
                <path d="M0,0 L6,3 L0,6 Z" fill="${strokeColor}" />
            </marker>
            <marker id="arr-start" orient="auto" markerWidth="6" markerHeight="6" refX="1" refY="3">
                <path d="M6,0 L0,3 L6,6 Z" fill="${strokeColor}" />
            </marker>
        </defs>
        <path d="${path}" stroke="${strokeColor}" stroke-width="8" stroke-linecap="round" fill="none" 
              marker-end="${arrowHeadEnd ? 'url(#arr-end)' : ''}" 
              marker-start="${arrowHeadStart ? 'url(#arr-start)' : ''}" />
        ${label}
    </svg>`;
}

function showCurrentMove() {
    const moves = currentSolution.expanded_moves;
    
    // Check if done
    if (currentMoveIndex >= moves.length) {
        document.getElementById('progressFill').style.width = '100%';
        document.getElementById('progressText').textContent = 'Solved!';
        
        document.getElementById('moveBadge').textContent = '🎉';
        document.getElementById('moveLabel').textContent = '';
        document.getElementById('moveDesc').textContent = 'Cube Solved!';
        document.getElementById('nextMoveBtn').disabled = true;
        
        renderSolveCubeNet();
        return;
    }

    const move = moves[currentMoveIndex];
    
    // Update progress
    const pct = (currentMoveIndex / moves.length) * 100;
    document.getElementById('progressFill').style.width = `${pct}%`;
    document.getElementById('progressText').textContent = `Move ${currentMoveIndex + 1} / ${moves.length}`;
    
    // Update badge & desc
    document.getElementById('moveBadge').textContent = move === 'TURN_BACK' ? '🔄' : move;
    if (move === 'TURN_BACK') {
        document.getElementById('moveLabel').textContent = 'Rotate Cube';
    } else {
        document.getElementById('moveLabel').textContent = `${faceNames[move[0]]} Face`;
    }
    document.getElementById('moveDesc').textContent = getMoveDescription(move);
    
    // Render Front face background
    let bgGrid = '';
    if (cubeState && cubeState.F) {
        bgGrid = `<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; width: 100%; height: 100%; position: absolute; z-index: 1;">`;
        cubeState.F.forEach(c => {
            bgGrid += `<div style="background: ${colorMap[c].css}; border-radius: 4px; border: 1px solid rgba(0,0,0,0.5);"></div>`;
        });
        bgGrid += `</div>`;
    }
    
    // Move image overlaid on bgGrid
    document.getElementById('moveArrowArea').innerHTML = `
        <div style="position: relative; width: 150px; height: 150px; display: flex; align-items: center; justify-content: center;">
            ${bgGrid}
            ${getArrowSVG(move)}
        </div>
    `;
    
    const chips = document.getElementById('moveList').children;
    for (let i = 0; i < chips.length; i++) {
        chips[i].className = 'move-chip';
        if (i < currentMoveIndex) chips[i].classList.add('done');
        else if (i === currentMoveIndex) chips[i].classList.add('current');
    }
    
    // Highlight face in net
    renderSolveCubeNet();
}

async function handleNextMove() {
    const moves = currentSolution.expanded_moves;
    if (currentMoveIndex >= moves.length) return;
    
    const move = moves[currentMoveIndex];
    
    // Disable buttons while applying move
    document.getElementById('nextMoveBtn').disabled = true;
    document.getElementById('prevMoveBtn').disabled = true;
    
    try {
        // Save history before moving
        cubeStateHistory.push(JSON.parse(JSON.stringify(cubeState)));
        
        const response = await fetch('/api/apply-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: cubeState, move: move })
        });
        const data = await response.json();
        if (data.state) {
            cubeState = data.state;
            currentMoveIndex++;
            showCurrentMove();
        } else if (data.error) {
            console.error(data.error);
            cubeStateHistory.pop();
        }
    } catch (err) {
        console.error("Move error:", err);
        // pop the failed move
        cubeStateHistory.pop();
    } finally {
        if (currentMoveIndex < moves.length) {
            document.getElementById('nextMoveBtn').disabled = false;
        }
        document.getElementById('prevMoveBtn').disabled = currentMoveIndex === 0;
    }
}

function handlePrevMove() {
    if (currentMoveIndex > 0) {
        currentMoveIndex--;
        cubeState = cubeStateHistory.pop();
        showCurrentMove();
    }
    document.getElementById('prevMoveBtn').disabled = currentMoveIndex === 0;
    document.getElementById('nextMoveBtn').disabled = false;
}

function renderSolveCubeNet() {
    const container = document.getElementById('solveCubeNet');
    container.innerHTML = '';
    
    const layout = {
        U: { r: 1, c: 2 },
        L: { r: 2, c: 1 },
        F: { r: 2, c: 2 },
        R: { r: 2, c: 3 },
        B: { r: 2, c: 4 },
        D: { r: 3, c: 2 }
    };
    
    faceOrder.forEach(face => {
        const pos = layout[face];
        const faceDiv = document.createElement('div');
        faceDiv.className = 'solve-face';
        faceDiv.style.gridRow = `${pos.r}/${pos.r+1}`;
        faceDiv.style.gridColumn = `${pos.c}/${pos.c+1}`;
        
        const label = document.createElement('div');
        label.className = 'net-face-label';
        label.textContent = face;
        faceDiv.appendChild(label);
        
        const colors = cubeState[face];
        for (let i = 0; i < 9; i++) {
            const c = colors[i];
            const sticker = document.createElement('div');
            sticker.className = `solve-sticker sticker-${c}`;
            sticker.style.background = colorMap[c].css;
            faceDiv.appendChild(sticker);
        }
        
        container.appendChild(faceDiv);
    });
}

function startOver() {
    clearAllFaces();
    currentSolution = null;
    currentMoveIndex = 0;
    logicalMoveIndex = 0;
    document.getElementById('nextMoveBtn').disabled = false;
    goToStep(1);
}
