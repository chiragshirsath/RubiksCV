let stream = null;
let cubeFaces = {};
let currentSolution = null;
let currentMoveIndex = 0;
let logicalMoveIndex = 0;
let pressesRemaining = 0;
let cubeState = null;

const faceOrder = ['U', 'R', 'F', 'D', 'L', 'B'];
const colorMap = {
    'W': { name: 'White', class: 'sticker-white' },
    'Y': { name: 'Yellow', class: 'sticker-yellow' },
    'R': { name: 'Red', class: 'sticker-red' },
    'O': { name: 'Orange', class: 'sticker-orange' },
    'G': { name: 'Green', class: 'sticker-green' },
    'B': { name: 'Blue', class: 'sticker-blue' }
};

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

// Solve button
document.getElementById('solveBtn').addEventListener('click', solveCube);

// Move navigation
document.getElementById('nextMoveBtn').addEventListener('click', showNextMove);
document.getElementById('applyMoveBtn').addEventListener('click', applyCurrentMove);

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'user',
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        const video = document.getElementById('video');
        video.srcObject = stream;
        document.getElementById('startCamera').style.display = 'none';
        document.getElementById('stopCamera').style.display = 'inline-block';
    } catch (err) {
        alert('Error accessing camera: ' + err.message);
    }
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
    document.getElementById('scannedCount').textContent = count;
    
    const list = document.getElementById('scannedList');
    list.innerHTML = '';
    Object.keys(cubeFaces).forEach(face => {
        const badge = document.createElement('span');
        badge.className = 'scanned-badge';
        badge.textContent = face;
        list.appendChild(badge);
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
        
        showNextMove();
        
    } catch (err) {
        alert('Error solving cube: ' + err.message);
    }
}

function showNextMove() {
    if (!currentSolution || currentMoveIndex >= currentSolution.expanded_moves.length) {
        document.getElementById('currentMove').textContent = '🎉 Solved!';
        document.getElementById('nextMoveBtn').disabled = true;
        return;
    }
    
    const move = currentSolution.expanded_moves[currentMoveIndex];
    const moveDisplay = document.getElementById('currentMove');
    
    if (move === 'TURN_BACK') {
        moveDisplay.innerHTML = '↻<br><span style="font-size: 0.4em;">Rotate cube to show back face</span>';
    } else {
        moveDisplay.textContent = move;
    }
    
    document.getElementById('applyMoveBtn').style.display = 'inline-block';
    document.getElementById('nextMoveBtn').textContent = 'Next Move';
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

async function applyCurrentMove() {
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

function updateCubeStateDisplay() {
    // Update cubeFaces with new state
    Object.keys(cubeState).forEach(face => {
        cubeFaces[face] = cubeState[face];
    });
    updateCubeDisplay();
}
