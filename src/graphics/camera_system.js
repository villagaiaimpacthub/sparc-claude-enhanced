// Camera System - Chase and Cockpit Views
class CameraSystem {
    constructor() {
        this.position = {x: 0, y: 10, z: -20};
        this.target = {x: 0, y: 0, z: 0};
        this.up = {x: 0, y: 1, z: 0};
        this.fov = 60;
        this.aspectRatio = 16/9;
        this.near = 0.1;
        this.far = 2000;
        this.mode = 'chase'; // 'chase', 'cockpit', 'free'
        this.chaseDistance = 25;
        this.chaseHeight = 8;
        this.smoothing = 0.1;
    }
    
    init() {
        // Set up mouse controls for free camera mode
        this.setupMouseControls();
        
        // Set up keyboard controls for camera switching
        this.setupKeyboardControls();
        
        console.log('Camera system initialized');
    }
    
    setupMouseControls() {
        let mouseDown = false;
        let lastMouseX = 0;
        let lastMouseY = 0;
        
        document.addEventListener('mousedown', (e) => {
            mouseDown = true;
            lastMouseX = e.clientX;
            lastMouseY = e.clientY;
        });
        
        document.addEventListener('mouseup', () => {
            mouseDown = false;
        });
        
        document.addEventListener('mousemove', (e) => {
            if (mouseDown && this.mode === 'free') {
                const deltaX = e.clientX - lastMouseX;
                const deltaY = e.clientY - lastMouseY;
                
                // Rotate camera based on mouse movement
                this.rotateFreeCamera(deltaX * 0.01, deltaY * 0.01);
                
                lastMouseX = e.clientX;
                lastMouseY = e.clientY;
            }
        });
        
        // Mouse wheel for zoom
        document.addEventListener('wheel', (e) => {
            if (this.mode === 'chase') {
                this.chaseDistance += e.deltaY * 0.1;
                this.chaseDistance = Math.max(5, Math.min(100, this.chaseDistance));
            }
        });
    }
    
    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case '1':
                    this.mode = 'chase';
                    console.log('Switched to chase camera');
                    break;
                case '2':
                    this.mode = 'cockpit';
                    console.log('Switched to cockpit camera');
                    break;
                case '3':
                    this.mode = 'free';
                    console.log('Switched to free camera');
                    break;
            }
        });
    }
    
    update(aircraftState, deltaTime) {
        switch(this.mode) {
            case 'chase':
                this.updateChaseCamera(aircraftState, deltaTime);
                break;
            case 'cockpit':
                this.updateCockpitCamera(aircraftState, deltaTime);
                break;
            case 'free':
                this.updateFreeCamera(aircraftState, deltaTime);
                break;
        }
    }
    
    updateChaseCamera(aircraftState, deltaTime) {
        const pos = aircraftState.position || {x: 0, y: 0, z: 0};
        const rot = aircraftState.rotation || {pitch: 0, roll: 0, yaw: 0};
        
        // Calculate ideal chase camera position
        const offsetX = -Math.sin(rot.yaw) * this.chaseDistance;
        const offsetZ = -Math.cos(rot.yaw) * this.chaseDistance;
        const offsetY = this.chaseHeight + Math.sin(rot.pitch) * 5;
        
        const idealPosition = {
            x: pos.x + offsetX,
            y: pos.y + offsetY,
            z: pos.z + offsetZ
        };
        
        // Smooth camera movement
        this.position.x = this.lerp(this.position.x, idealPosition.x, this.smoothing);
        this.position.y = this.lerp(this.position.y, idealPosition.y, this.smoothing);
        this.position.z = this.lerp(this.position.z, idealPosition.z, this.smoothing);
        
        // Look at aircraft
        this.target.x = pos.x;
        this.target.y = pos.y;
        this.target.z = pos.z;
    }
    
    updateCockpitCamera(aircraftState, deltaTime) {
        const pos = aircraftState.position || {x: 0, y: 0, z: 0};
        const rot = aircraftState.rotation || {pitch: 0, roll: 0, yaw: 0};
        
        // Position camera inside cockpit
        this.position.x = pos.x + Math.sin(rot.yaw) * 2;
        this.position.y = pos.y + 1;
        this.position.z = pos.z + Math.cos(rot.yaw) * 2;
        
        // Look forward based on aircraft orientation
        this.target.x = pos.x + Math.sin(rot.yaw) * 100;
        this.target.y = pos.y + Math.tan(rot.pitch) * 100;
        this.target.z = pos.z + Math.cos(rot.yaw) * 100;
    }
    
    updateFreeCamera(aircraftState, deltaTime) {
        // Free camera maintains its position unless moved by mouse
        // Can be enhanced with WASD movement
    }
    
    rotateFreeCamera(deltaX, deltaY) {
        // Rotate free camera around its position
        // Simplified rotation implementation
        this.target.x += deltaX * 10;
        this.target.y += deltaY * 10;
    }
    
    getViewMatrix() {
        // Create view matrix (look-at matrix)
        // Simplified implementation - in reality use proper math library
        return this.createLookAtMatrix(this.position, this.target, this.up);
    }
    
    getProjectionMatrix() {
        // Create perspective projection matrix
        return this.createPerspectiveMatrix(this.fov, this.aspectRatio, this.near, this.far);
    }
    
    createLookAtMatrix(eye, target, up) {
        // Simplified look-at matrix creation
        // In production, use a proper math library like gl-matrix
        return [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            -eye.x, -eye.y, -eye.z, 1
        ];
    }
    
    createPerspectiveMatrix(fov, aspect, near, far) {
        // Simplified perspective matrix
        const f = Math.tan(Math.PI * 0.5 - 0.5 * fov * Math.PI / 180);
        const rangeInv = 1.0 / (near - far);
        
        return [
            f / aspect, 0, 0, 0,
            0, f, 0, 0,
            0, 0, (near + far) * rangeInv, -1,
            0, 0, near * far * rangeInv * 2, 0
        ];
    }
    
    setAspectRatio(aspectRatio) {
        this.aspectRatio = aspectRatio;
    }
    
    lerp(a, b, t) {
        return a + (b - a) * t;
    }
}