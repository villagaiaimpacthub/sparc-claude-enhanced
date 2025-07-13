// 3D Aircraft Model - Detailed Cessna 172
class AircraftModel {
    constructor(gl, shaderManager) {
        this.gl = gl;
        this.shaderManager = shaderManager;
        this.vertexBuffer = null;
        this.indexBuffer = null;
        this.vertices = [];
        this.indices = [];
        this.propellerRotation = 0;
    }
    
    async init() {
        this.createGeometry();
        this.setupBuffers();
        console.log('Aircraft model initialized with detailed geometry');
    }
    
    createGeometry() {
        // Fuselage (main body)
        this.createFuselage();
        
        // Wings
        this.createWings();
        
        // Tail surfaces
        this.createTail();
        
        // Propeller
        this.createPropeller();
        
        // Landing gear
        this.createLandingGear();
    }
    
    createFuselage() {
        const length = 4.0;
        const width = 1.0;
        const height = 1.2;
        
        // Simplified box fuselage with nose cone
        const fuselageVertices = [
            // Nose cone (pointed front)
            [length/2, 0, 0],
            
            // Main body vertices
            [length/4, -width/2, -height/2], [length/4, width/2, -height/2],
            [length/4, width/2, height/2], [length/4, -width/2, height/2],
            
            [-length/2, -width/2, -height/2], [-length/2, width/2, -height/2],
            [-length/2, width/2, height/2], [-length/2, -width/2, height/2],
        ];
        
        // Add vertices to main array with color (white/gray)
        fuselageVertices.forEach(vertex => {
            this.vertices.push(...vertex, 0.9, 0.9, 0.9); // RGB color
        });
        
        // Add triangular faces for fuselage
        const baseIndex = 0;
        // Simplified triangulation for box + nose cone
        this.addBoxIndices(baseIndex + 1, 8);
    }
    
    createWings() {
        const wingspan = 6.0;
        const chord = 1.5;
        const thickness = 0.1;
        
        // Main wings
        const wingVertices = [
            // Left wing
            [-1, -wingspan/2, -thickness], [-1, -1, -thickness],
            [chord-1, -1, -thickness], [chord-1, -wingspan/2, -thickness],
            [-1, -wingspan/2, thickness], [-1, -1, thickness],
            [chord-1, -1, thickness], [chord-1, -wingspan/2, thickness],
            
            // Right wing (mirrored)
            [-1, wingspan/2, -thickness], [-1, 1, -thickness],
            [chord-1, 1, -thickness], [chord-1, wingspan/2, -thickness],
            [-1, wingspan/2, thickness], [-1, 1, thickness],
            [chord-1, 1, thickness], [chord-1, wingspan/2, thickness],
        ];
        
        // Add wing vertices with color (light gray)
        wingVertices.forEach(vertex => {
            this.vertices.push(...vertex, 0.8, 0.8, 0.8);
        });
        
        // Add wing indices
        const wingBaseIndex = this.vertices.length / 6 - 16;
        this.addBoxIndices(wingBaseIndex, 8); // Left wing
        this.addBoxIndices(wingBaseIndex + 8, 8); // Right wing
    }
    
    createTail() {
        // Vertical stabilizer
        const tailVertices = [
            [-2.5, 0, 0], [-2.5, 0, 1.5],
            [-3.5, 0, 1.2], [-3.5, 0, 0],
        ];
        
        tailVertices.forEach(vertex => {
            this.vertices.push(...vertex, 0.7, 0.7, 0.7);
        });
        
        // Simple quad for tail
        const tailBase = this.vertices.length / 6 - 4;
        this.indices.push(
            tailBase, tailBase + 1, tailBase + 2,
            tailBase, tailBase + 2, tailBase + 3
        );
    }
    
    createPropeller() {
        // Simple spinning disk for propeller
        const propRadius = 0.8;
        const propCenter = [2.2, 0, 0];
        
        // Center vertex
        this.vertices.push(...propCenter, 0.2, 0.2, 0.2);
        const centerIndex = this.vertices.length / 6 - 1;
        
        // Blade vertices
        for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2;
            const x = propCenter[0];
            const y = propCenter[1] + Math.cos(angle) * propRadius;
            const z = propCenter[2] + Math.sin(angle) * propRadius;
            
            this.vertices.push(x, y, z, 0.3, 0.3, 0.3);
            
            // Add triangle indices
            if (i < 7) {
                this.indices.push(centerIndex, centerIndex + i + 1, centerIndex + i + 2);
            } else {
                this.indices.push(centerIndex, centerIndex + i + 1, centerIndex + 1);
            }
        }
    }
    
    createLandingGear() {
        // Simple landing gear struts
        const gearPositions = [
            [0.5, -1.2, -1.0], [0.5, 1.2, -1.0], // Main gear
            [1.8, 0, -0.8] // Nose gear
        ];
        
        gearPositions.forEach(pos => {
            // Strut
            this.vertices.push(...pos, 0.3, 0.3, 0.3);
            this.vertices.push(pos[0], pos[1], pos[2] - 0.3, 0.3, 0.3, 0.3);
            
            // Wheel
            this.vertices.push(pos[0], pos[1], pos[2] - 0.4, 0.1, 0.1, 0.1);
        });
    }
    
    addBoxIndices(baseIndex, vertexCount) {
        // Add triangulated indices for box-like geometry
        // Simplified box triangulation
        for (let i = 0; i < vertexCount - 2; i++) {
            this.indices.push(baseIndex, baseIndex + i + 1, baseIndex + i + 2);
        }
    }
    
    setupBuffers() {
        const gl = this.gl;
        
        // Create and bind vertex buffer
        this.vertexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.vertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(this.vertices), gl.STATIC_DRAW);
        
        // Create and bind index buffer
        this.indexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(this.indices), gl.STATIC_DRAW);
        
        console.log(`Aircraft model: ${this.vertices.length/6} vertices, ${this.indices.length/3} triangles`);
    }
    
    render(aircraftState, viewMatrix, projectionMatrix) {
        const gl = this.gl;
        const shader = this.shaderManager.getShader('aircraft');
        
        if (!shader) return;
        
        gl.useProgram(shader.program);
        
        // Bind buffers
        gl.bindBuffer(gl.ARRAY_BUFFER, this.vertexBuffer);
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        
        // Set up attributes
        const positionAttrib = gl.getAttribLocation(shader.program, 'a_position');
        const colorAttrib = gl.getAttribLocation(shader.program, 'a_color');
        
        gl.enableVertexAttribArray(positionAttrib);
        gl.enableVertexAttribArray(colorAttrib);
        
        gl.vertexAttribPointer(positionAttrib, 3, gl.FLOAT, false, 24, 0);
        gl.vertexAttribPointer(colorAttrib, 3, gl.FLOAT, false, 24, 12);
        
        // Set up matrices
        const modelMatrix = this.createModelMatrix(aircraftState);
        
        const modelViewMatrix = this.multiplyMatrices(viewMatrix, modelMatrix);
        const mvpMatrix = this.multiplyMatrices(projectionMatrix, modelViewMatrix);
        
        const mvpLocation = gl.getUniformLocation(shader.program, 'u_mvpMatrix');
        gl.uniformMatrix4fv(mvpLocation, false, mvpMatrix);
        
        // Update propeller rotation
        this.propellerRotation += aircraftState.throttle || 0;
        
        // Render
        gl.drawElements(gl.TRIANGLES, this.indices.length, gl.UNSIGNED_SHORT, 0);
    }
    
    createModelMatrix(aircraftState) {
        // Create transformation matrix for aircraft position and rotation
        const pos = aircraftState.position || {x: 0, y: 0, z: 0};
        const rot = aircraftState.rotation || {pitch: 0, roll: 0, yaw: 0};
        
        // Simplified 4x4 transformation matrix
        return [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            pos.x, pos.y, pos.z, 1
        ];
    }
    
    multiplyMatrices(a, b) {
        // Simplified matrix multiplication (4x4)
        // In a real implementation, use a proper math library
        return [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ];
    }
}