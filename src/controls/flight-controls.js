// Flight Controls System
class FlightControls {
    constructor() {
        this.throttle = 0;
        this.elevatorInput = 0;
        this.aileronInput = 0;
        this.rudderInput = 0;
        this.setupControls();
    }
    
    setupControls() {
        // Throttle control
        const throttleSlider = document.getElementById('throttle');
        if (throttleSlider) {
            throttleSlider.addEventListener('input', (e) => {
                this.throttle = e.target.value / 100;
            });
        }
        
        // Keyboard controls for flight surfaces
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowUp':
                case 'w':
                    this.elevatorInput = Math.max(this.elevatorInput - 0.1, -1);
                    break;
                case 'ArrowDown':
                case 's':
                    this.elevatorInput = Math.min(this.elevatorInput + 0.1, 1);
                    break;
                case 'ArrowLeft':
                case 'a':
                    this.aileronInput = Math.max(this.aileronInput - 0.1, -1);
                    break;
                case 'ArrowRight':
                case 'd':
                    this.aileronInput = Math.min(this.aileronInput + 0.1, 1);
                    break;
                case 'q':
                    this.rudderInput = Math.max(this.rudderInput - 0.1, -1);
                    break;
                case 'e':
                    this.rudderInput = Math.min(this.rudderInput + 0.1, 1);
                    break;
            }
        });
        
        document.addEventListener('keyup', (e) => {
            // Gradually return controls to center when released
            switch(e.key) {
                case 'ArrowUp':
                case 'ArrowDown':
                case 'w':
                case 's':
                    this.elevatorInput *= 0.9;
                    break;
                case 'ArrowLeft':
                case 'ArrowRight':
                case 'a':
                case 'd':
                    this.aileronInput *= 0.9;
                    break;
                case 'q':
                case 'e':
                    this.rudderInput *= 0.9;
                    break;
            }
        });
    }
    
    getThrottle() {
        return this.throttle;
    }
    
    getElevator() {
        return this.elevatorInput;
    }
    
    getAilerons() {
        return this.aileronInput;
    }
    
    getRudder() {
        return this.rudderInput;
    }
}