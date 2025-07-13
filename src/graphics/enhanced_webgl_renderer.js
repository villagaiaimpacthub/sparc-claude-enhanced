// Enhanced WebGL Renderer - Addresses 3D Graphics Gaps
class Enhanced3DRenderer {
    constructor() {
        this.canvas = null;
        this.gl = null;
        this.shaderManager = null;
        this.aircraftModel = null;
        this.terrainSystem = null;
        this.cameraSystem = null;
        this.initialized = false;
    }
    
    async init() {
        this.canvas = document.getElementById('flight-canvas');
        if (!this.canvas) {
            throw new Error('Canvas not found');
        }
        
        this.gl = this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl');
        if (!this.gl) {
            throw new Error('WebGL not supported');
        }
        
        // Initialize WebGL settings
        this.gl.enable(this.gl.DEPTH_TEST);
        this.gl.enable(this.gl.CULL_FACE);
        this.gl.clearColor(0.5, 0.8, 1.0, 1.0);
        
        // Initialize subsystems
        this.shaderManager = new ShaderManager(this.gl);
        await this.shaderManager.init();
        
        this.aircraftModel = new AircraftModel(this.gl, this.shaderManager);
        await this.aircraftModel.init();
        
        this.terrainSystem = new TerrainSystem(this.gl, this.shaderManager);
        await this.terrainSystem.init();
        
        this.cameraSystem = new CameraSystem();
        this.cameraSystem.init();
        
        this.initialized = true;
        console.log('Enhanced 3D Renderer initialized successfully!');
    }
    
    render(aircraftState, deltaTime) {
        if (!this.initialized) return;
        
        const gl = this.gl;
        
        // Clear buffers
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        
        // Update camera based on aircraft position
        this.cameraSystem.update(aircraftState, deltaTime);
        
        // Get camera matrices
        const viewMatrix = this.cameraSystem.getViewMatrix();
        const projectionMatrix = this.cameraSystem.getProjectionMatrix();
        
        // Render terrain first
        this.terrainSystem.render(viewMatrix, projectionMatrix);
        
        // Render aircraft
        this.aircraftModel.render(aircraftState, viewMatrix, projectionMatrix);
        
        // Update sky color based on altitude
        this.updateSkyColor(aircraftState.altitude);
    }
    
    updateSkyColor(altitude) {
        const normalizedAltitude = Math.max(0, Math.min(1, altitude / 3000));
        const skyBlue = 0.5 + normalizedAltitude * 0.3;
        this.gl.clearColor(0.5, 0.7 + skyBlue * 0.1, skyBlue, 1.0);
    }
    
    resize(width, height) {
        if (this.canvas) {
            this.canvas.width = width;
            this.canvas.height = height;
            this.gl.viewport(0, 0, width, height);
            
            if (this.cameraSystem) {
                this.cameraSystem.setAspectRatio(width / height);
            }
        }
    }
}