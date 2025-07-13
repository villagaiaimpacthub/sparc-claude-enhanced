// Simple WebGL Renderer for Flight Simulator
class WebGLRenderer {
    constructor() {
        this.canvas = null;
        this.gl = null;
    }
    
    setupCanvas() {
        this.canvas = document.getElementById('flight-canvas');
        if (this.canvas) {
            this.gl = this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl');
            if (this.gl) {
                this.gl.clearColor(0.5, 0.8, 1.0, 1.0); // Sky blue
                this.gl.enable(this.gl.DEPTH_TEST);
            }
        }
    }
    
    render(aircraftState) {
        if (this.gl) {
            this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
            
            // Simple horizon line based on aircraft pitch and roll
            if (aircraftState) {
                const pitch = aircraftState.pitch || 0;
                const roll = aircraftState.roll || 0;
                
                // Change background color based on altitude and attitude
                const altitude = aircraftState.altitude || 0;
                const skyBlue = Math.max(0.3, Math.min(1.0, altitude / 2000));
                this.gl.clearColor(0.5, 0.7 + skyBlue * 0.1, skyBlue, 1.0);
            }
        }
    }
}

// Flight Simulator Main Application
class FlightSimulator {
    constructor() {
        this.physics = new FlightPhysics();
        this.controls = new FlightControls();
        this.instruments = new FlightInstruments();
        this.renderer = new WebGLRenderer();
        this.lastTime = 0;
        this.running = false;
    }
    
    init() {
        this.setupCanvas();
        this.connectSystems();
        this.addInstructions();
        this.startGameLoop();
        console.log('Flight Simulator initialized!');
    }
    
    setupCanvas() {
        this.renderer.setupCanvas();
    }
    
    connectSystems() {
        // Connect physics to controls
        this.physics.setControls(this.controls);
    }
    
    addInstructions() {
        const instructions = document.createElement('div');
        instructions.className = 'instructions';
        instructions.innerHTML = `
            <h4>Flight Controls:</h4>
            <p>W/S or ↑/↓: Elevator (pitch)</p>
            <p>A/D or ←/→: Ailerons (roll)</p>
            <p>Q/E: Rudder (yaw)</p>
            <p>Throttle: Use slider →</p>
        `;
        document.body.appendChild(instructions);
    }
    
    startGameLoop() {
        this.running = true;
        this.gameLoop(0);
    }
    
    gameLoop(currentTime) {
        if (!this.running) return;
        
        const deltaTime = (currentTime - this.lastTime) / 1000; // Convert to seconds
        this.lastTime = currentTime;
        
        if (deltaTime > 0 && deltaTime < 0.1) { // Cap deltaTime to prevent large jumps
            this.update(deltaTime);
        }
        
        requestAnimationFrame((time) => this.gameLoop(time));
    }
    
    update(deltaTime) {
        this.physics.update(deltaTime);
        const aircraftState = this.physics.getState();
        this.instruments.update(aircraftState);
        this.renderer.render(aircraftState);
    }
    
    stop() {
        this.running = false;
    }
}

// Initialize the simulator when page loads
document.addEventListener('DOMContentLoaded', () => {
    const simulator = new FlightSimulator();
    simulator.init();
    
    // Make simulator accessible globally for debugging
    window.flightSimulator = simulator;
});
