// Flight Instruments System
class FlightInstruments {
    constructor() {
        this.altimeter = document.getElementById('altimeter');
        this.airspeed = document.getElementById('airspeed');
        this.attitude = document.getElementById('attitude');
    }
    
    update(aircraftState) {
        this.updateAltimeter(aircraftState.altitude);
        this.updateAirspeed(aircraftState.airspeed);
        this.updateAttitude(aircraftState.pitch, aircraftState.roll);
    }
    
    updateAltimeter(altitude) {
        if (this.altimeter) {
            const altValue = this.altimeter.querySelector('.gauge-value');
            if (altValue) {
                altValue.textContent = Math.round(altitude);
            }
        }
    }
    
    updateAirspeed(airspeed) {
        if (this.airspeed) {
            const speedValue = this.airspeed.querySelector('.gauge-value');
            if (speedValue) {
                speedValue.textContent = Math.round(airspeed);
            }
        }
    }
    
    updateAttitude(pitch, roll) {
        if (this.attitude) {
            const horizon = this.attitude.querySelector('.artificial-horizon');
            if (horizon) {
                horizon.style.transform = `rotate(${roll}deg) translateY(${pitch * 5}px)`;
            }
        }
    }
}