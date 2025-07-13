// Terrain System - Runway and Ground
class TerrainSystem {
    constructor(gl, shaderManager) {
        this.gl = gl;
        this.shaderManager = shaderManager;
        this.terrainBuffer = null;
        this.runwayBuffer = null;
        this.vertices = [];
        this.indices = [];
    }
    
    async init() {
        this.createTerrain();
        this.setupBuffers();
        console.log('Terrain system initialized');
    }
    
    createTerrain() {
        // Create large ground plane
        this.createGroundPlane();
        
        // Create runway
        this.createRunway();
        
        // Create distant mountains
        this.createMountains();
    }
    
    createGroundPlane() {
        const size = 1000;
        const segments = 20;
        const step = size / segments;
        
        // Generate grid of vertices
        for (let i = 0; i <= segments; i++) {
            for (let j = 0; j <= segments; j++) {
                const x = -size/2 + i * step;
                const z = -size/2 + j * step;
                const y = -10; // Ground level
                
                // Vertex position and grass color
                this.vertices.push(x, y, z, 0.2, 0.6, 0.2);
                
                // Create triangles
                if (i < segments && j < segments) {
                    const current = i * (segments + 1) + j;
                    const next = current + 1;
                    const below = current + (segments + 1);
                    const belowNext = below + 1;
                    
                    // Two triangles per quad
                    this.indices.push(
                        current, next, below,
                        next, belowNext, below
                    );
                }
            }
        }
    }
    
    createRunway() {
        const runwayLength = 200;
        const runwayWidth = 20;
        const runwayY = -9.5; // Slightly above ground
        
        // Runway vertices (dark gray)
        const runwayVertices = [
            [-runwayLength/2, runwayY, -runwayWidth/2, 0.3, 0.3, 0.3],
            [runwayLength/2, runwayY, -runwayWidth/2, 0.3, 0.3, 0.3],
            [runwayLength/2, runwayY, runwayWidth/2, 0.3, 0.3, 0.3],
            [-runwayLength/2, runwayY, runwayWidth/2, 0.3, 0.3, 0.3],
        ];
        
        const runwayBaseIndex = this.vertices.length / 6;
        runwayVertices.forEach(vertex => {
            this.vertices.push(...vertex);
        });
        
        // Runway quad indices
        this.indices.push(
            runwayBaseIndex, runwayBaseIndex + 1, runwayBaseIndex + 2,
            runwayBaseIndex, runwayBaseIndex + 2, runwayBaseIndex + 3
        );
        
        // Runway markings (white stripes)
        this.createRunwayMarkings(runwayBaseIndex + 4);
    }
    
    createRunwayMarkings(baseIndex) {
        const markingLength = 10;
        const markingWidth = 2;
        const spacing = 30;
        const runwayY = -9.4;
        
        for (let i = -3; i <= 3; i++) {
            const x = i * spacing;
            
            // White marking stripe
            this.vertices.push(
                x - markingLength/2, runwayY, -markingWidth/2, 1.0, 1.0, 1.0,
                x + markingLength/2, runwayY, -markingWidth/2, 1.0, 1.0, 1.0,
                x + markingLength/2, runwayY, markingWidth/2, 1.0, 1.0, 1.0,
                x - markingLength/2, runwayY, markingWidth/2, 1.0, 1.0, 1.0
            );
            
            const markingBase = baseIndex + i * 4 + 12; // Offset for markings
            this.indices.push(
                markingBase, markingBase + 1, markingBase + 2,
                markingBase, markingBase + 2, markingBase + 3
            );
        }
    }
    
    createMountains() {
        // Simple distant mountain range
        const mountainDistance = 800;
        const mountainHeight = 200;
        const numPeaks = 10;
        
        for (let i = 0; i < numPeaks; i++) {
            const angle = (i / numPeaks) * Math.PI * 2;
            const x = Math.cos(angle) * mountainDistance;
            const z = Math.sin(angle) * mountainDistance;
            const height = mountainHeight + Math.random() * 100;
            
            // Mountain peak (brown/gray)
            this.vertices.push(x, height, z, 0.5, 0.4, 0.3);
            this.vertices.push(x - 50, -10, z - 50, 0.4, 0.3, 0.2);
            this.vertices.push(x + 50, -10, z + 50, 0.4, 0.3, 0.2);
            
            const peakBase = this.vertices.length / 6 - 3;
            this.indices.push(peakBase, peakBase + 1, peakBase + 2);
        }
    }
    
    setupBuffers() {
        const gl = this.gl;
        
        // Create terrain buffer
        this.terrainBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.terrainBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(this.vertices), gl.STATIC_DRAW);
        
        // Index buffer
        this.indexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(this.indices), gl.STATIC_DRAW);
        
        console.log(`Terrain: ${this.vertices.length/6} vertices, ${this.indices.length/3} triangles`);
    }
    
    render(viewMatrix, projectionMatrix) {
        const gl = this.gl;
        const shader = this.shaderManager.getShader('terrain');
        
        if (!shader) return;
        
        gl.useProgram(shader.program);
        
        // Bind buffers
        gl.bindBuffer(gl.ARRAY_BUFFER, this.terrainBuffer);
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        
        // Set up attributes
        const positionAttrib = gl.getAttribLocation(shader.program, 'a_position');
        const colorAttrib = gl.getAttribLocation(shader.program, 'a_color');
        
        gl.enableVertexAttribArray(positionAttrib);
        gl.enableVertexAttribArray(colorAttrib);
        
        gl.vertexAttribPointer(positionAttrib, 3, gl.FLOAT, false, 24, 0);
        gl.vertexAttribPointer(colorAttrib, 3, gl.FLOAT, false, 24, 12);
        
        // Set matrices
        const mvpMatrix = this.multiplyMatrices(projectionMatrix, viewMatrix);
        const mvpLocation = gl.getUniformLocation(shader.program, 'u_mvpMatrix');
        gl.uniformMatrix4fv(mvpLocation, false, mvpMatrix);
        
        // Render terrain
        gl.drawElements(gl.TRIANGLES, this.indices.length, gl.UNSIGNED_SHORT, 0);
    }
    
    multiplyMatrices(a, b) {
        // Simplified matrix multiplication
        return [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ];
    }
}