// Shader Manager - WebGL Shader Compilation and Management
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
}