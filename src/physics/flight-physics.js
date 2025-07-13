// Flight Physics Engine
class FlightPhysics {
    constructor() {
        this.velocity = { x: 0, y: 0, z: 0 };
        this.position = { x: 0, y: 1000, z: 0 }; // Start at 1000ft altitude
        this.rotation = { pitch: 0, roll: 0, yaw: 0 };
        this.mass = 1000; // kg
        this.throttle = 0;
        this.controls = null;
        this.gravity = -9.81;
    }
    
    setControls(controls) {
        this.controls = controls;
    }
    
    calculateLift(airspeed, angleOfAttack) {
        const liftCoefficient = Math.sin(angleOfAttack * 2) * 1.2;
        return 0.5 * 1.225 * airspeed * airspeed * 16.2 * liftCoefficient;
    }
    
    calculateDrag(airspeed) {
        const dragCoefficient = 0.025;
        return 0.5 * 1.225 * airspeed * airspeed * 16.2 * dragCoefficient;
    }
    
    getAirspeed() {
        return Math.sqrt(this.velocity.x * this.velocity.x + this.velocity.z * this.velocity.z);
    }
    
    update(deltaTime) {
        if (!this.controls) return;
        
        // Get control inputs
        this.throttle = this.controls.getThrottle();
        const elevator = this.controls.getElevator();
        const ailerons = this.controls.getAilerons();
        const rudder = this.controls.getRudder();
        
        // Physics calculations
        const airspeed = this.getAirspeed();
        const thrust = this.throttle * 800; // Max 800N thrust
        const lift = this.calculateLift(airspeed, this.rotation.pitch);
        const drag = this.calculateDrag(airspeed);
        
        // Apply control inputs to rotation
        this.rotation.pitch += elevator * deltaTime * 0.5;
        this.rotation.roll += ailerons * deltaTime * 0.8;
        this.rotation.yaw += rudder * deltaTime * 0.3;
        
        // Limit rotation angles
        this.rotation.pitch = Math.max(-Math.PI/3, Math.min(Math.PI/3, this.rotation.pitch));
        this.rotation.roll = Math.max(-Math.PI/2, Math.min(Math.PI/2, this.rotation.roll));
        
        // Apply forces and update position
        this.updatePosition(deltaTime, thrust, lift, drag);
    }
    
    updatePosition(deltaTime, thrust, lift, drag) {
        // Force calculations
        const forwardForce = thrust - drag;
        const verticalForce = lift + (this.mass * this.gravity);
        
        // Apply forces to velocity
        this.velocity.z += forwardForce / this.mass * deltaTime;
        this.velocity.y += verticalForce / this.mass * deltaTime;
        
        // Apply rotation effects
        const pitchEffect = Math.sin(this.rotation.pitch);
        this.velocity.y += this.velocity.z * pitchEffect * deltaTime;
        
        // Update position
        this.position.x += this.velocity.x * deltaTime;
        this.position.y += this.velocity.y * deltaTime;
        this.position.z += this.velocity.z * deltaTime;
        
        // Ground collision
        if (this.position.y < 0) {
            this.position.y = 0;
            this.velocity.y = 0;
        }
    }
    
    getState() {
        return {
            altitude: this.position.y,
            airspeed: this.getAirspeed(),
            pitch: this.rotation.pitch,
            roll: this.rotation.roll,
            yaw: this.rotation.yaw,
            position: this.position,
            velocity: this.velocity
        };
    }
}
