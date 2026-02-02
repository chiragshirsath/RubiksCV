let stream = null;
let cubeFaces = {};
let currentSolution = null;
let currentMoveIndex = 0;
let logicalMoveIndex = 0;
let pressesRemaining = 0;
let cubeState = null;
let currentMode = 'camera'; // 'camera' or 'manual'
let selectedColor = 'W';
let selectedFace = 'U';

const faceOrder = ['U', 'R', 'F', 'D', 'L', 'B'];
const colorMap = {
    'W': { name: 'White', class: 'sticker-white' },
    'Y': { name: 'Yellow', class: 'sticker-yellow' },
    'R': { name: 'Red', class: 'sticker-red' },
    'O': { name: 'Orange', class: 'sticker-orange' },
    'G': { name: 'Green', class: 'sticker-green' },
    'B': { name: 'Blue', class: 'sticker-blue' }
};

// Mode switching
document.getElementById('cameraModeBtn').addEventListener('click', () => switchMode('camera'));
document.getElementById('manualModeBtn').addEventListener('click', () => switchMode('manual'));

// Camera controls
document.getElementById('startCamera').addEventListener('click', startCamera);
document.getElementById('stopCamera').addEventListener('click', stopCamera);

// Face scanning
document.querySelectorAll('.face-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const face = btn.dataset.face;
        scanFace(face);
    });
});

// Manual editor controls
document.querySelectorAll('.color-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedColor = btn.dataset.color;
    });
});

document.querySelectorAll('.face-tab').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.face-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedFace = btn.dataset.face;
        renderManualFaceEditor();
    });
});

document.getElementById('clearFaceBtn').addEventListener('click', clearCurrentFace);
document.getElementById('clearAllBtn').addEventListener('click', clearAllFaces);

// Solve button
document.getElementById('solveBtn').addEventListener('click', solveCube);

// Move navigation
document.getElementById('nextMoveBtn').addEventListener('click', handleNextMove);

// Initialize manual editor
renderManualFaceEditor();

async function startCamera() {
    try {
        // Try to get the back camera first
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: { exact: "environment" },
                width: { ideal: 640 }, 
                height: { ideal: 480 }
            } 
        });
    } catch (err) {
        console.log("Back camera not found, falling back to any camera...");
        // Fallback: Opens whatever camera is available (Webcam on laptop)
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 }, 
                height: { ideal: 480 }
            } 
        });
    }
    
    const video = document.getElementById('video');
    video.srcObject = stream;
    document.getElementById('startCamera').style.display = 'none';
    document.getElementById('stopCamera').style.display = 'inline-block';
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    const video = document.getElementById('video');
    video.srcObject = null;
    document.getElementById('startCamera').style.display = 'inline-block';
    document.getElementById('stopCamera').style.display = 'none';
}

async function scanFace(face) {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!stream) {
        alert('Please start the camera first!');
        return;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    try {
        const response = await fetch('/api/classify-colors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData, debug: true })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        cubeFaces[face] = data.colors;
        
        // Show HSV values in console for debugging
        if (data.hsv_values) {
            console.log(`Scanned ${face} face HSV values:`, data.hsv_values);
            // Show center sticker HSV (most important)
            const centerHSV = data.hsv_values[4]; // Center is index 4 (0-8 grid)
            console.log(`Center sticker (${face}): H=${centerHSV.h}, S=${centerHSV.s}, V=${centerHSV.v} -> ${centerHSV.color}`);
        }
        
        updateScannedFaces();
        updateCubeDisplay();
        
        // Mark button as scanned
        document.querySelector(`[data-face="${face}"]`).classList.add('scanned');
        
    } catch (err) {
        alert('Error scanning face: ' + err.message);
    }
}

function updateScannedFaces() {
    const count = Object.keys(cubeFaces).length;
    // Update all scanned count elements
    document.querySelectorAll('.scanned-count').forEach(el => {
        el.textContent = count;
    });
    
    // Update all scanned list elements
    document.querySelectorAll('.scanned-list').forEach(list => {
        list.innerHTML = '';
        Object.keys(cubeFaces).forEach(face => {
            const badge = document.createElement('span');
            badge.className = 'scanned-badge';
            badge.textContent = face;
            list.appendChild(badge);
        });
    });
    
    // Update face button states
    document.querySelectorAll('.face-btn').forEach(btn => {
        const face = btn.dataset.face;
        if (cubeFaces[face] && cubeFaces[face].length === 9) {
            btn.classList.add('scanned');
        } else {
            btn.classList.remove('scanned');
        }
    });
    
    document.getElementById('solveBtn').disabled = count !== 6;
}

function updateCubeDisplay() {
    const display = document.getElementById('cubeDisplay');
    display.innerHTML = '';
    
    faceOrder.forEach(face => {
        if (cubeFaces[face]) {
            const faceDiv = document.createElement('div');
            faceDiv.className = 'cube-face';
            faceDiv.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; font-weight: bold; margin-bottom: 5px;">${face}</div>`;
            
            cubeFaces[face].forEach((color, idx) => {
                const sticker = document.createElement('div');
                sticker.className = `cube-sticker ${colorMap[color].class}`;
                sticker.textContent = color;
                faceDiv.appendChild(sticker);
            });
            
            display.appendChild(faceDiv);
        }
    });
}

async function solveCube() {
    if (Object.keys(cubeFaces).length !== 6) {
        alert('Please scan all 6 faces first!');
        return;
    }
    
    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cube_faces: cubeFaces })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        currentSolution = data;
        currentMoveIndex = 0;
        logicalMoveIndex = 0;
        cubeState = JSON.parse(JSON.stringify(cubeFaces)); // Deep copy
        pressesRemaining = getRequiredPresses(currentSolution.moves[0]) || 1;
        
        document.getElementById('solutionText').textContent = `Solution: ${data.solution}`;
        document.getElementById('solutionSection').style.display = 'block';
        
        // Initialize move display
        showNextMove();
        
    } catch (err) {
        alert('Error solving cube: ' + err.message);
    }
}

function showNextMove() {
    if (!currentSolution || currentMoveIndex >= currentSolution.expanded_moves.length) {
        document.getElementById('currentMove').innerHTML = '<div style="font-size: 48px;">🎉</div><div>Solved!</div>';
        document.getElementById('visualCubeContainer').innerHTML = '';
        document.getElementById('moveNumber').textContent = '';
        document.getElementById('moveDescription').textContent = '🎉 Cube Solved!';
        document.getElementById('nextMoveBtn').disabled = true;
        return;
    }
    
    const move = currentSolution.expanded_moves[currentMoveIndex];
    const totalMoves = currentSolution.expanded_moves.length;
    
    // Update move number
    document.getElementById('moveNumber').textContent = `Move ${currentMoveIndex + 1} of ${totalMoves}`;
    
    // Create visual cube representation
    renderVisualCube(move);
    
    // Display move description
    let moveDesc = '';
    if (move === 'TURN_BACK') {
        moveDesc = '↻ Rotate the cube to show the back face';
    } else {
        const face = move[0];
        const direction = move.length > 1 ? (move[1] === "'" ? "counter-clockwise" : move[1] === "2" ? "180° (twice)" : "clockwise") : "clockwise";
        const faceNames = {
            'U': 'Up', 'R': 'Right', 'F': 'Front', 
            'D': 'Down', 'L': 'Left', 'B': 'Back'
        };
        moveDesc = `Turn ${faceNames[face]} face ${direction}`;
    }
    document.getElementById('moveDescription').textContent = moveDesc;
    
    // Display move image/notation
    const moveDisplay = document.getElementById('currentMove');
    if (move === 'TURN_BACK') {
        moveDisplay.innerHTML = '<img src="/Resources/TURN_BACK.png" alt="Turn Back" style="max-width: 150px; height: auto; display: block; margin: 10px auto;">';
    } else {
        const moveImagePath = `/Resources/${move}.png`;
        moveDisplay.innerHTML = `
            <img src="${moveImagePath}" alt="${move}" style="max-width: 150px; height: auto; display: block; margin: 10px auto;" 
                 onerror="this.style.display='none';">
            <div style="font-size: 32px; font-weight: bold; color: #667eea; text-align: center; margin-top: 10px;">${move}</div>
        `;
    }
    
    document.getElementById('nextMoveBtn').textContent = 'Next Move';
    document.getElementById('nextMoveBtn').disabled = false;
}

function renderVisualCube(move) {
    const container = document.getElementById('visualCubeContainer');
    container.innerHTML = '';
    
    if (move === 'TURN_BACK') {
        container.innerHTML = '<div class="turn-back-indicator">↻ Rotate Cube</div>';
        return;
    }
    
    const face = move[0];
    const isCounterClockwise = move.includes("'");
    const isDouble = move.includes("2");
    
    // Create a 3D-like cube visualization showing which face to turn
    const cubeWrapper = document.createElement('div');
    cubeWrapper.className = 'visual-cube-wrapper';
    
    // Create the cube net (unfolded view)
    const cubeNet = document.createElement('div');
    cubeNet.className = 'cube-net';
    
    // Define face positions in the net (standard Rubik's cube net layout)
    // Grid: 3 rows x 4 columns
    // Row 1: [empty, U, empty, empty]
    // Row 2: [L, F, R, B]
    // Row 3: [empty, D, empty, empty]
    const facePositions = {
        'U': { gridArea: '1 / 2 / 2 / 3', label: 'U', name: 'Up' },
        'F': { gridArea: '2 / 2 / 3 / 3', label: 'F', name: 'Front' },
        'D': { gridArea: '3 / 2 / 4 / 3', label: 'D', name: 'Down' },
        'L': { gridArea: '2 / 1 / 3 / 2', label: 'L', name: 'Left' },
        'R': { gridArea: '2 / 3 / 3 / 4', label: 'R', name: 'Right' },
        'B': { gridArea: '2 / 4 / 3 / 5', label: 'B', name: 'Back' }
    };
    
    // Get current cube state (use cubeState if available, otherwise cubeFaces)
    const currentState = cubeState || cubeFaces;
    
    // Create all faces
    faceOrder.forEach(faceName => {
        const faceDiv = document.createElement('div');
        faceDiv.className = 'visual-cube-face';
        faceDiv.style.gridArea = facePositions[faceName].gridArea;
        
        // Show center color if available
        if (currentState[faceName] && currentState[faceName][4]) {
            const centerColor = currentState[faceName][4];
            const colorClass = colorMap[centerColor]?.class || '';
            faceDiv.classList.add(colorClass);
        }
        
        // Add face label
        const label = document.createElement('div');
        label.textContent = facePositions[faceName].label;
        label.style.fontSize = '28px';
        label.style.fontWeight = 'bold';
        label.style.zIndex = '2';
        label.style.position = 'relative';
        // Make label visible on colored backgrounds
        if (faceName === face) {
            label.style.color = 'white';
            label.style.textShadow = '2px 2px 4px rgba(0,0,0,0.8)';
        } else {
            label.style.color = '#333';
        }
        faceDiv.appendChild(label);
        
        // Highlight the face being turned
        if (faceName === face) {
            faceDiv.classList.add('active-face');
            // Add rotation indicator
            const arrow = document.createElement('div');
            arrow.className = 'rotation-arrow';
            if (isCounterClockwise) {
                arrow.textContent = '↺';
                arrow.style.animation = 'rotateCounterClockwise 1s linear infinite';
            } else if (isDouble) {
                arrow.textContent = '⟲';
                arrow.style.animation = 'rotateDouble 1s linear infinite';
            } else {
                arrow.textContent = '↻';
                arrow.style.animation = 'rotateClockwise 1s linear infinite';
            }
            faceDiv.appendChild(arrow);
            
            // Add direction text
            const directionText = document.createElement('div');
            directionText.style.position = 'absolute';
            directionText.style.bottom = '5px';
            directionText.style.left = '50%';
            directionText.style.transform = 'translateX(-50%)';
            directionText.style.fontSize = '11px';
            directionText.style.color = 'white';
            directionText.style.textShadow = '1px 1px 2px rgba(0,0,0,0.8)';
            directionText.style.fontWeight = '600';
            if (isCounterClockwise) {
                directionText.textContent = "Counter-clockwise";
            } else if (isDouble) {
                directionText.textContent = "180° (twice)";
            } else {
                directionText.textContent = "Clockwise";
            }
            faceDiv.appendChild(directionText);
        }
        
        cubeNet.appendChild(faceDiv);
    });
    
    cubeWrapper.appendChild(cubeNet);
    container.appendChild(cubeWrapper);
}

async function handleNextMove() {
    if (!currentSolution || currentMoveIndex >= currentSolution.expanded_moves.length) {
        return;
    }
    
    const expandedMove = currentSolution.expanded_moves[currentMoveIndex];
    
    if (expandedMove === 'TURN_BACK') {
        // Just advance to next move for turn back
        currentMoveIndex++;
        showNextMove();
        return;
    }
    
    // Decrement presses remaining
    pressesRemaining--;
    currentMoveIndex++;
    
    // If we've completed all presses for this logical move, apply it
    if (pressesRemaining === 0 && logicalMoveIndex < currentSolution.moves.length) {
        const logicalMove = currentSolution.moves[logicalMoveIndex];
        
        try {
            const response = await fetch('/api/apply-move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    state: cubeState, 
                    move: logicalMove 
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            cubeState = data.state;
            updateCubeStateDisplay();
            
            // Move to next logical move
            logicalMoveIndex++;
            if (logicalMoveIndex < currentSolution.moves.length) {
                pressesRemaining = getRequiredPresses(currentSolution.moves[logicalMoveIndex]);
            }
            
        } catch (err) {
            alert('Error applying move: ' + err.message);
            return;
        }
    }
    
    showNextMove();
}

function getRequiredPresses(move) {
    if (!move) return 0;
    if (move.endsWith('2')) {
        return 2;
    } else if (move[0] === 'B') {
        return 3;
    }
    return 1;
}


function updateCubeStateDisplay() {
    // Update cubeFaces with new state
    Object.keys(cubeState).forEach(face => {
        cubeFaces[face] = cubeState[face];
    });
    updateCubeDisplay();
    // Also update manual editor if in manual mode
    if (currentMode === 'manual') {
        renderManualFaceEditor();
    }
}

// Manual editing functions
function switchMode(mode) {
    currentMode = mode;
    
    if (mode === 'camera') {
        document.getElementById('cameraModeBtn').classList.add('active');
        document.getElementById('manualModeBtn').classList.remove('active');
        document.getElementById('cameraSection').style.display = 'block';
        document.getElementById('scanSection').style.display = 'block';
        document.getElementById('manualEditor').style.display = 'none';
    } else {
        document.getElementById('cameraModeBtn').classList.remove('active');
        document.getElementById('manualModeBtn').classList.add('active');
        document.getElementById('cameraSection').style.display = 'none';
        document.getElementById('scanSection').style.display = 'none';
        document.getElementById('manualEditor').style.display = 'block';
        renderManualFaceEditor();
    }
    
    updateScannedFaces();
}

function renderManualFaceEditor() {
    const editor = document.getElementById('manualFaceEditor');
    editor.innerHTML = '';
    
    // Create a 3x3 grid for the selected face
    const grid = document.createElement('div');
    grid.className = 'manual-face-grid';
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(3, 1fr)';
    grid.style.gap = '5px';
    grid.style.maxWidth = '300px';
    grid.style.margin = '20px auto';
    
    // Initialize face if it doesn't exist
    if (!cubeFaces[selectedFace]) {
        cubeFaces[selectedFace] = ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'];
    }
    
    // Create 9 clickable stickers
    for (let i = 0; i < 9; i++) {
        const sticker = document.createElement('div');
        const currentColor = cubeFaces[selectedFace][i] || 'W';
        sticker.className = `manual-sticker ${colorMap[currentColor].class}`;
        sticker.textContent = currentColor;
        sticker.dataset.index = i;
        sticker.style.cursor = 'pointer';
        sticker.style.aspectRatio = '1';
        sticker.style.borderRadius = '5px';
        sticker.style.display = 'flex';
        sticker.style.alignItems = 'center';
        sticker.style.justifyContent = 'center';
        sticker.style.fontWeight = 'bold';
        sticker.style.fontSize = '20px';
        sticker.style.color = '#333';
        sticker.style.transition = 'transform 0.1s';
        
        sticker.addEventListener('click', () => handleStickerClick(selectedFace, i));
        sticker.addEventListener('mouseenter', () => {
            sticker.style.transform = 'scale(1.1)';
        });
        sticker.addEventListener('mouseleave', () => {
            sticker.style.transform = 'scale(1)';
        });
        
        grid.appendChild(sticker);
    }
    
    editor.appendChild(grid);
}

function handleStickerClick(face, index) {
    if (!cubeFaces[face]) {
        cubeFaces[face] = ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'];
    }
    
    cubeFaces[face][index] = selectedColor;
    renderManualFaceEditor();
    updateCubeDisplay();
    updateScannedFaces();
}

function clearCurrentFace() {
    if (cubeFaces[selectedFace]) {
        cubeFaces[selectedFace] = ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'];
        renderManualFaceEditor();
        updateCubeDisplay();
        updateScannedFaces();
    }
}

function clearAllFaces() {
    if (confirm('Are you sure you want to clear all faces?')) {
        cubeFaces = {};
        renderManualFaceEditor();
        updateCubeDisplay();
        updateScannedFaces();
    }
}
