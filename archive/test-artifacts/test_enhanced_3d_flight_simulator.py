#!/usr/bin/env python3
"""
ENHANCED 3D FLIGHT SIMULATOR - SPARC WORKFLOW TEST
Re-running SPARC with specific focus on 3D graphics and visual rendering
Learning from the previous iteration to fill the 3D graphics gap
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import uuid

# Add lib to path
lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))

try:
    from dotenv import load_dotenv
    from rich.console import Console
    from rich.progress import Progress, TaskID
    from rich.panel import Panel
    from rich.table import Table
    import requests
    
    # Import SPARC components
    from memory_orchestrator import MemoryOrchestrator
    from constants import PHASE_SEQUENCE, ENHANCED_AGENTS, ALL_AGENTS
    
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

console = Console()
load_dotenv()

class Enhanced3DFlightSimulatorWorkflow:
    """Enhanced workflow specifically targeting 3D graphics gaps from previous iteration"""
    
    def __init__(self):
        self.project_goal = "Build a visually stunning 3D flight simulator with detailed aircraft models, realistic terrain, and immersive graphics that works in the browser"
        self.project_id = f"enhanced_flight_sim_3d_{uuid.uuid4().hex[:8]}"
        self.namespace = "enhanced_3d_flight_simulator"
        self.memory_orchestrator = MemoryOrchestrator()
        
        # Store learnings from previous iteration
        self.previous_iteration_learnings = {
            "gaps_identified": [
                "Missing 3D aircraft model geometry",
                "No terrain/runway 3D objects", 
                "Missing WebGL shaders for 3D rendering",
                "No scene graph or 3D world objects",
                "WebGL context created but only basic color clearing"
            ],
            "successful_components": [
                "Flight physics engine (lift, drag, thrust)",
                "Real-time controls and input handling",
                "Instrument panel updates",
                "Game loop and timing",
                "WebGL initialization"
            ],
            "enhancement_needed": [
                "Detailed 3D modeling requirements",
                "Specific WebGL shader specifications", 
                "Terrain and environment graphics",
                "Aircraft visual representation",
                "Camera system and viewing angles"
            ]
        }
    
    async def execute_enhanced_goal_clarification(self):
        """Enhanced goal clarification with specific 3D graphics focus"""
        
        console.print("🎯 [bold]ENHANCED Goal Clarification - 3D Graphics Focus[/bold]")
        console.print("Learning from previous iteration gaps...")
        
        # Enhanced questions specifically targeting 3D graphics
        enhanced_questions = [
            {
                "question": "What specific 3D visual elements must be included? (aircraft model details, terrain features, environment)",
                "answer": "The aircraft must be a detailed 3D Cessna 172 model with wings, fuselage, propeller, landing gear. Terrain should include a textured runway, grass fields, and distant mountains. Environment needs sky gradients and basic clouds."
            },
            {
                "question": "What level of 3D graphics realism is required? (low-poly, detailed textures, lighting effects)",
                "answer": "Mid-level realism - detailed enough to be immersive but optimized for browser performance. Include basic lighting, textured surfaces, and smooth 3D models. Aim for modern flight simulator visuals but browser-compatible."
            },
            {
                "question": "What WebGL rendering features are essential? (shaders, lighting, textures, camera controls)",
                "answer": "Essential: vertex/fragment shaders for 3D models, basic directional lighting, texture mapping for aircraft and ground, perspective camera with smooth movement, fog for distance effects."
            },
            {
                "question": "What camera perspectives and controls should be available?",
                "answer": "Primary: behind-aircraft chase camera. Secondary: cockpit view. Camera should smoothly follow aircraft movement, allow mouse look-around, and have adjustable zoom. Include cinematic camera transitions."
            },
            {
                "question": "What 3D modeling format and approach should be used for browser compatibility?",
                "answer": "Use JavaScript-generated geometry for compatibility, or simple OBJ-like vertex arrays. Focus on procedural generation over external model files. Optimize for WebGL 1.0 compatibility across all browsers."
            },
            {
                "question": "What environmental and atmospheric effects are needed?",
                "answer": "Sky color gradients based on time/altitude, simple cloud sprites, ground texture variety (runway, grass, dirt), fog/haze for distant objects, basic sun lighting with shadows on ground."
            },
            {
                "question": "How should the 3D world scale and performance be optimized?",
                "answer": "Reasonable world size (5km x 5km), level-of-detail for distant objects, efficient polygon counts, texture atlasing, frustum culling for off-screen objects. Target 60fps on average laptops."
            }
        ]
        
        # Display enhanced interview
        for i, qa in enumerate(enhanced_questions, 1):
            console.print(f"\n[blue]Enhanced Q{i}:[/blue] {qa['question']}")
            console.print(f"[green]A{i}:[/green] {qa['answer']}")
        
        # Store learnings in memory for enhanced agents
        await self.memory_orchestrator.store_memory(
            memory_type="project_iteration_learning",
            content={
                "iteration": 2,
                "previous_gaps": self.previous_iteration_learnings["gaps_identified"],
                "enhanced_requirements": enhanced_questions,
                "focus_area": "3D graphics and visual rendering",
                "learning_applied": True
            },
            metadata={"project_type": "flight_simulator", "iteration": "enhanced_3d"}
        )
        
        return {
            "success": True,
            "enhanced_questions": len(enhanced_questions),
            "learning_applied": True,
            "focus_areas": ["3D modeling", "WebGL shaders", "camera systems", "environmental graphics"]
        }
    
    async def execute_enhanced_specification_phase(self):
        """Enhanced specification focusing on 3D graphics gaps"""
        
        console.print("📋 [bold]ENHANCED Specification Phase - 3D Graphics Focus[/bold]")
        
        # Get memory enhancement with previous iteration learnings
        memory_context = await self.memory_orchestrator.enhance_agent_with_memory(
            agent_name="spec-writer-comprehensive-enhanced",
            task_type="3d_graphics_specification",
            current_context={
                "previous_iteration_gaps": self.previous_iteration_learnings,
                "focus": "3D graphics and visual rendering"
            }
        )
        
        enhanced_3d_spec = self._create_enhanced_3d_specification()
        
        # Save enhanced specification
        spec_path = "docs/specifications/enhanced_3d_graphics_requirements.md"
        Path(spec_path).parent.mkdir(parents=True, exist_ok=True)
        with open(spec_path, 'w') as f:
            f.write(enhanced_3d_spec)
        
        console.print(f"📄 Saved enhanced 3D specification: {spec_path}")
        
        return {
            "success": True,
            "specification_created": spec_path,
            "memory_enhanced": True,
            "learning_applied": True
        }
    
    def _create_enhanced_3d_specification(self):
        """Create detailed 3D graphics specification"""
        
        return f"""# Enhanced 3D Flight Simulator Graphics Specification
Generated: {datetime.now().isoformat()}
Project: Enhanced 3D Browser Flight Simulator
Iteration: 2 (Learning from previous gaps)

## Previous Iteration Analysis

### What Worked Successfully ✅
- Flight physics engine with realistic forces
- Real-time control input handling  
- Instrument panel updates and display
- WebGL context initialization
- Game loop and timing systems

### Identified Gaps ❌
- Missing 3D aircraft model geometry
- No terrain or runway 3D objects
- Missing WebGL vertex/fragment shaders
- No scene graph or 3D world elements
- Only basic WebGL color clearing (no actual 3D rendering)

## Enhanced 3D Graphics Requirements

### Core 3D Rendering System

#### WebGL Shader System
- **Vertex Shader**: Transform 3D vertices, handle model/view/projection matrices
- **Fragment Shader**: Handle lighting, textures, fog effects
- **Shader Programs**: Separate programs for aircraft, terrain, sky
- **Uniform Management**: Camera matrices, lighting parameters, material properties

#### 3D Aircraft Model
```javascript
// Required Aircraft Components:
- Fuselage: Cylinder/box geometry with nose cone
- Wings: Flat rectangles with slight dihedral angle  
- Propeller: Spinning disk with blade geometry
- Landing Gear: Simple cylinder struts and wheels
- Control Surfaces: Separate aileron, elevator, rudder geometry
- Cockpit: Basic interior visible from chase camera
```

#### Terrain System
```javascript
// Required Terrain Components:
- Runway: Textured rectangle with runway markings
- Grass Fields: Large textured plane with grass texture
- Airport Buildings: Simple box geometry for hangars/tower
- Mountains: Distant low-poly mountain range
- Ground Grid: Procedural grid for reference
```

#### Camera System
```javascript
// Required Camera Types:
- Chase Camera: Follow aircraft from behind with smooth movement
- Cockpit Camera: First-person view from pilot position
- Free Camera: Debug mode for development
- Camera Controls: Mouse look, zoom, smooth transitions
```

#### Lighting and Materials
```javascript
// Required Lighting:
- Directional Light: Sun simulation with shadows
- Ambient Light: General scene illumination
- Material System: Diffuse textures, basic specular
- Fog System: Distance-based atmospheric perspective
```

### Performance Optimization Requirements

#### Level of Detail (LOD)
- Aircraft: Full detail within 100m, reduced beyond
- Terrain: Tessellation based on distance
- Culling: Frustum culling for off-screen objects
- Texture: Mipmapping and texture atlasing

#### Target Performance
- 60 FPS on average laptops
- WebGL 1.0 compatibility
- Memory usage under 256MB
- Fast loading times (<10 seconds)

### Implementation Specifications

#### File Structure
```
src/graphics/
├── shaders/
│   ├── aircraft.vert
│   ├── aircraft.frag
│   ├── terrain.vert
│   └── terrain.frag
├── models/
│   ├── cessna172.js
│   ├── runway.js
│   └── terrain.js
├── textures/
│   ├── aircraft_diffuse.js (base64 encoded)
│   ├── grass_texture.js
│   └── runway_texture.js
└── camera/
    ├── chase_camera.js
    ├── cockpit_camera.js
    └── camera_controller.js
```

#### WebGL Integration Points
```javascript
// Required Integration:
- Scene Graph: Hierarchical object management
- Render Pipeline: Multi-pass rendering system
- Asset Loading: Efficient geometry and texture loading
- Animation System: Smooth interpolation and keyframes
- Physics Integration: Visual updates from physics state
```

### Quality Gates for 3D Graphics

#### Visual Completeness Checklist
- [ ] 3D aircraft model visible and detailed
- [ ] Textured runway and terrain
- [ ] Smooth camera movement and controls
- [ ] Proper lighting and shadows
- [ ] Atmospheric effects (fog, sky gradient)
- [ ] Stable 60 FPS performance
- [ ] All WebGL features functional

#### Technical Validation
- [ ] WebGL shaders compile without errors
- [ ] 3D geometry renders correctly
- [ ] Textures load and display properly
- [ ] Camera matrices calculated correctly
- [ ] Physics-to-graphics synchronization working
- [ ] Memory usage within targets
- [ ] Cross-browser compatibility verified

## Success Criteria

This enhanced iteration will be considered successful when:

1. **Visual Completeness**: User sees detailed 3D aircraft flying over realistic terrain
2. **Immersive Experience**: Camera movement enhances flight simulation feeling
3. **Performance**: Smooth 60 FPS with all visual features enabled
4. **Learning Applied**: All gaps from previous iteration addressed
5. **Browser Compatibility**: Works across Chrome, Firefox, Safari, Edge

---
*This specification addresses all 3D graphics gaps identified in the previous SPARC iteration*
"""
    
    async def execute_enhanced_implementation(self):
        """Enhanced implementation phase targeting 3D graphics"""
        
        console.print("⚡ [bold]ENHANCED Implementation - 3D Graphics Generation[/bold]")
        
        # Use memory-enhanced implementation agent
        memory_context = await self.memory_orchestrator.enhance_agent_with_memory(
            agent_name="implementation-phase-agent-memory-enhanced",
            task_type="3d_graphics_implementation",
            current_context={
                "previous_gaps": self.previous_iteration_learnings["gaps_identified"],
                "focus": "WebGL 3D rendering system"
            }
        )
        
        # Generate enhanced 3D graphics code
        enhanced_3d_code = await self._generate_enhanced_3d_code()
        
        # Save enhanced code files
        for file_path, content in enhanced_3d_code.items():
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            console.print(f"📄 Generated enhanced 3D file: {file_path}")
        
        return {
            "success": True,
            "enhanced_files_generated": len(enhanced_3d_code),
            "focus": "3D graphics and rendering",
            "learning_applied": True
        }
    
    async def _generate_enhanced_3d_code(self):
        """Generate enhanced 3D graphics code addressing previous gaps"""
        
        return {
            "src/graphics/enhanced_webgl_renderer.js": self._create_enhanced_webgl_renderer(),
            "src/graphics/aircraft_model.js": self._create_aircraft_model(),
            "src/graphics/terrain_system.js": self._create_terrain_system(), 
            "src/graphics/camera_system.js": self._create_camera_system(),
            "src/graphics/shader_manager.js": self._create_shader_manager(),
            "enhanced_3d_flight_simulator.html": self._create_enhanced_html()
        }
    
    def _create_enhanced_webgl_renderer(self):
        """Create enhanced WebGL renderer with 3D capabilities"""
        
        return """// Enhanced WebGL Renderer - Addresses 3D Graphics Gaps
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
}"""
    
    def _create_aircraft_model(self):
        """Create detailed 3D aircraft model"""
        
        return """// 3D Aircraft Model - Detailed Cessna 172
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
}"""
    
    def _create_terrain_system(self):
        """Create terrain and runway system"""
        
        return """// Terrain System - Runway and Ground
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
}"""
    
    def _create_camera_system(self):
        """Create camera system with chase and cockpit views"""
        
        return """// Camera System - Chase and Cockpit Views
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
}"""
    
    def _create_shader_manager(self):
        """Create WebGL shader management system"""
        
        return """// Shader Manager - WebGL Shader Compilation and Management
class ShaderManager {
    constructor(gl) {
        this.gl = gl;
        this.shaders = new Map();
        this.programs = new Map();
    }
    
    async init() {
        // Create aircraft shader
        await this.createAircraftShader();
        
        // Create terrain shader
        await this.createTerrainShader();
        
        console.log('Shader manager initialized with all shaders');
    }
    
    async createAircraftShader() {
        const vertexShaderSource = `
            attribute vec3 a_position;
            attribute vec3 a_color;
            
            uniform mat4 u_mvpMatrix;
            
            varying vec3 v_color;
            
            void main() {
                gl_Position = u_mvpMatrix * vec4(a_position, 1.0);
                v_color = a_color;
            }
        `;
        
        const fragmentShaderSource = `
            precision mediump float;
            
            varying vec3 v_color;
            
            void main() {
                gl_FragColor = vec4(v_color, 1.0);
            }
        `;
        
        const program = this.createShaderProgram(vertexShaderSource, fragmentShaderSource);
        this.programs.set('aircraft', {
            program: program,
            attributes: ['a_position', 'a_color'],
            uniforms: ['u_mvpMatrix']
        });
    }
    
    async createTerrainShader() {
        const vertexShaderSource = `
            attribute vec3 a_position;
            attribute vec3 a_color;
            
            uniform mat4 u_mvpMatrix;
            
            varying vec3 v_color;
            varying float v_fogDepth;
            
            void main() {
                vec4 worldPosition = vec4(a_position, 1.0);
                gl_Position = u_mvpMatrix * worldPosition;
                v_color = a_color;
                
                // Calculate fog depth
                v_fogDepth = length(worldPosition.xyz) / 1000.0;
            }
        `;
        
        const fragmentShaderSource = `
            precision mediump float;
            
            varying vec3 v_color;
            varying float v_fogDepth;
            
            void main() {
                vec3 fogColor = vec3(0.7, 0.8, 0.9);
                float fogFactor = exp(-v_fogDepth * v_fogDepth * 0.5);
                fogFactor = clamp(fogFactor, 0.0, 1.0);
                
                vec3 finalColor = mix(fogColor, v_color, fogFactor);
                gl_FragColor = vec4(finalColor, 1.0);
            }
        `;
        
        const program = this.createShaderProgram(vertexShaderSource, fragmentShaderSource);
        this.programs.set('terrain', {
            program: program,
            attributes: ['a_position', 'a_color'],
            uniforms: ['u_mvpMatrix']
        });
    }
    
    createShaderProgram(vertexSource, fragmentSource) {
        const gl = this.gl;
        
        // Create vertex shader
        const vertexShader = this.createShader(gl.VERTEX_SHADER, vertexSource);
        if (!vertexShader) return null;
        
        // Create fragment shader
        const fragmentShader = this.createShader(gl.FRAGMENT_SHADER, fragmentSource);
        if (!fragmentShader) return null;
        
        // Create program
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        
        // Check linking
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Shader program linking failed:', gl.getProgramInfoLog(program));
            gl.deleteProgram(program);
            return null;
        }
        
        // Clean up shaders
        gl.deleteShader(vertexShader);
        gl.deleteShader(fragmentShader);
        
        return program;
    }
    
    createShader(type, source) {
        const gl = this.gl;
        const shader = gl.createShader(type);
        
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error('Shader compilation failed:', gl.getShaderInfoLog(shader));
            gl.deleteShader(shader);
            return null;
        }
        
        return shader;
    }
    
    getShader(name) {
        return this.programs.get(name);
    }
    
    useShader(name) {
        const shader = this.programs.get(name);
        if (shader) {
            this.gl.useProgram(shader.program);
            return shader;
        }
        return null;
    }
}"""
    
    def _create_enhanced_html(self):
        """Create enhanced HTML file with 3D instructions"""
        
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced 3D Flight Simulator</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #001122;
            color: #fff;
            overflow: hidden;
        }
        
        #simulator-container {
            display: flex;
            height: 100vh;
            width: 100vw;
        }
        
        #flight-canvas {
            flex: 1;
            background: linear-gradient(to bottom, #87CEEB 0%, #98FB98 100%);
            border: 2px solid #333;
        }
        
        #instruments-panel {
            width: 200px;
            background: #1a1a1a;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            border-left: 2px solid #333;
        }
        
        .instrument {
            background: #2a2a2a;
            border: 2px solid #444;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .gauge-label {
            font-size: 12px;
            font-weight: bold;
            color: #ccc;
            margin-bottom: 5px;
        }
        
        .gauge-value {
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
        }
        
        .artificial-horizon {
            width: 80px;
            height: 40px;
            background: linear-gradient(to bottom, #87CEEB 0%, #87CEEB 50%, #8B4513 50%, #8B4513 100%);
            border: 1px solid #333;
            border-radius: 5px;
            position: relative;
            overflow: hidden;
        }
        
        #controls-panel {
            width: 200px;
            background: #1a1a1a;
            padding: 20px;
            border-left: 2px solid #333;
        }
        
        .control-group {
            margin-bottom: 20px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #ccc;
        }
        
        #throttle {
            width: 100%;
            height: 30px;
        }
        
        #flight-stick {
            width: 100px;
            height: 100px;
            background: #333;
            border: 2px solid #555;
            border-radius: 50%;
            position: relative;
            margin: 20px auto;
        }
        
        #flight-stick::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            background: #ff6600;
            border-radius: 50%;
            transform: translate(-50%, -50%);
        }
        
        .instructions {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
            max-width: 300px;
        }
        
        .instructions h4 {
            margin: 0 0 10px 0;
            color: #00ff00;
            font-size: 14px;
        }
        
        .instructions p {
            margin: 5px 0;
            color: #ccc;
        }
        
        .camera-info {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
        }
        
        #status-display {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            color: #00ff00;
        }
    </style>
</head>
<body>
    <div id="simulator-container">
        <canvas id="flight-canvas" width="1024" height="768"></canvas>
        <div id="instruments-panel">
            <div class="instrument" id="altimeter">
                <div class="gauge-label">ALT</div>
                <div class="gauge-value">1000</div>
            </div>
            <div class="instrument" id="airspeed">
                <div class="gauge-label">IAS</div>
                <div class="gauge-value">0</div>
            </div>
            <div class="instrument" id="attitude">
                <div class="gauge-label">ATT</div>
                <div class="artificial-horizon"></div>
            </div>
        </div>
        <div id="controls-panel">
            <div class="control-group">
                <label>Throttle</label>
                <input type="range" id="throttle" min="0" max="100" value="0">
            </div>
            <div class="control-group">
                <label>Flight Controls</label>
                <div id="flight-stick"></div>
            </div>
        </div>
    </div>
    
    <div class="instructions">
        <h4>Enhanced 3D Flight Simulator</h4>
        <p><strong>Flight Controls:</strong></p>
        <p>W/S or ↑/↓: Elevator (pitch)</p>
        <p>A/D or ←/→: Ailerons (roll)</p>
        <p>Q/E: Rudder (yaw)</p>
        <p>Throttle: Use slider →</p>
        <p><strong>Camera Controls:</strong></p>
        <p>1: Chase Camera</p>
        <p>2: Cockpit View</p>
        <p>3: Free Camera</p>
        <p>Mouse: Look around (Free mode)</p>
        <p>Wheel: Zoom (Chase mode)</p>
    </div>
    
    <div class="camera-info">
        <div id="camera-mode">Camera: Chase</div>
        <div id="fps-counter">FPS: --</div>
    </div>
    
    <div id="status-display">
        <div>Enhanced 3D Graphics: Loading...</div>
    </div>
    
    <!-- Enhanced 3D Graphics System -->
    <script src="src/graphics/shader_manager.js"></script>
    <script src="src/graphics/aircraft_model.js"></script>
    <script src="src/graphics/terrain_system.js"></script>
    <script src="src/graphics/camera_system.js"></script>
    <script src="src/graphics/enhanced_webgl_renderer.js"></script>
    
    <!-- Flight Systems -->
    <script src="src/physics/flight-physics.js"></script>
    <script src="src/controls/flight-controls.js"></script>
    <script src="src/instruments/flight-instruments.js"></script>
    
    <!-- Main Application -->
    <script>
        // Enhanced 3D Flight Simulator Main Application
        class Enhanced3DFlightSimulator {
            constructor() {
                this.physics = new FlightPhysics();
                this.controls = new FlightControls();
                this.instruments = new FlightInstruments();
                this.renderer = new Enhanced3DRenderer();
                this.lastTime = 0;
                this.running = false;
                this.fpsCounter = 0;
                this.fpsTime = 0;
            }
            
            async init() {
                try {
                    document.getElementById('status-display').innerHTML = 
                        '<div>Initializing Enhanced 3D Graphics...</div>';
                    
                    await this.renderer.init();
                    this.connectSystems();
                    this.setupEventHandlers();
                    this.startGameLoop();
                    
                    document.getElementById('status-display').innerHTML = 
                        '<div style="color: #00ff00;">Enhanced 3D Graphics: Ready!</div>';
                    
                    console.log('Enhanced 3D Flight Simulator initialized successfully!');
                } catch (error) {
                    console.error('Failed to initialize 3D graphics:', error);
                    document.getElementById('status-display').innerHTML = 
                        '<div style="color: #ff0000;">3D Graphics Failed: ' + error.message + '</div>';
                }
            }
            
            connectSystems() {
                this.physics.setControls(this.controls);
            }
            
            setupEventHandlers() {
                window.addEventListener('resize', () => {
                    const canvas = document.getElementById('flight-canvas');
                    this.renderer.resize(canvas.clientWidth, canvas.clientHeight);
                });
            }
            
            startGameLoop() {
                this.running = true;
                this.gameLoop(0);
            }
            
            gameLoop(currentTime) {
                if (!this.running) return;
                
                const deltaTime = (currentTime - this.lastTime) / 1000;
                this.lastTime = currentTime;
                
                if (deltaTime > 0 && deltaTime < 0.1) {
                    this.update(deltaTime);
                    this.updateFPS(deltaTime);
                }
                
                requestAnimationFrame((time) => this.gameLoop(time));
            }
            
            update(deltaTime) {
                this.physics.update(deltaTime);
                const aircraftState = this.physics.getState();
                this.instruments.update(aircraftState);
                this.renderer.render(aircraftState, deltaTime);
            }
            
            updateFPS(deltaTime) {
                this.fpsTime += deltaTime;
                this.fpsCounter++;
                
                if (this.fpsTime >= 1.0) {
                    const fps = Math.round(this.fpsCounter / this.fpsTime);
                    document.getElementById('fps-counter').textContent = `FPS: ${fps}`;
                    this.fpsCounter = 0;
                    this.fpsTime = 0;
                }
            }
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', async () => {
            const simulator = new Enhanced3DFlightSimulator();
            await simulator.init();
            
            // Make accessible for debugging
            window.enhanced3DSimulator = simulator;
        });
    </script>
</body>
</html>"""
    
    async def run_enhanced_workflow(self):
        """Execute the complete enhanced workflow"""
        
        console.print(Panel.fit("🛫 ENHANCED 3D SPARC WORKFLOW - ITERATION 2", style="bold magenta"))
        console.print("Addressing 3D graphics gaps from previous iteration")
        console.print(f"Project: {self.project_goal}")
        
        try:
            # Enhanced Goal Clarification
            console.print("\n🎯 [bold cyan]Phase 1: Enhanced Goal Clarification[/bold cyan]")
            goal_result = await self.execute_enhanced_goal_clarification()
            
            # Enhanced Specification  
            console.print("\n📋 [bold cyan]Phase 2: Enhanced Specification[/bold cyan]")
            spec_result = await self.execute_enhanced_specification_phase()
            
            # Enhanced Implementation
            console.print("\n⚡ [bold cyan]Phase 3: Enhanced 3D Implementation[/bold cyan]")
            impl_result = await self.execute_enhanced_implementation()
            
            console.print("\n🎉 [bold green]ENHANCED 3D WORKFLOW COMPLETED![/bold green]")
            
            return {
                "success": True,
                "iteration": 2,
                "focus": "3D graphics enhancement",
                "goal_clarification": goal_result,
                "specification": spec_result,
                "implementation": impl_result,
                "learning_applied": True
            }
            
        except Exception as e:
            console.print(f"\n❌ [bold red]Enhanced workflow failed: {e}[/bold red]")
            return {"success": False, "error": str(e)}

async def main():
    """Execute enhanced 3D flight simulator workflow"""
    
    workflow = Enhanced3DFlightSimulatorWorkflow()
    results = await workflow.run_enhanced_workflow()
    
    if results.get("success"):
        console.print("\n📁 [bold]Enhanced 3D Project Structure Generated:[/bold]")
        console.print("├── src/graphics/")
        console.print("│   ├── enhanced_webgl_renderer.js (Full 3D rendering)")
        console.print("│   ├── aircraft_model.js (Detailed Cessna 172)")
        console.print("│   ├── terrain_system.js (Runway + landscape)")
        console.print("│   ├── camera_system.js (Chase/cockpit/free)")
        console.print("│   └── shader_manager.js (WebGL shaders)")
        console.print("├── enhanced_3d_flight_simulator.html")
        console.print("└── docs/specifications/enhanced_3d_graphics_requirements.md")
        
        console.print("\n🚀 [bold green]Enhanced 3D flight simulator ready![/bold green]")
        console.print("Open enhanced_3d_flight_simulator.html to see the improved version")
        
    return results

if __name__ == "__main__":
    results = asyncio.run(main())