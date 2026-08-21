/**
 * 3D Interactive WebGL Pipe & Spiral Weld Visualizer using Three.js
 * Supports Multi-pipe switching, Cutaway sectioning, and PNG Snapshot Export.
 */
class PipeVisualizer3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.pipeMesh = null;
        this.weldMesh = null;
        this.controls = null;
        this.animationFrameId = null;
        this.isCutaway = false;
        this.isRotating = true;
        this.currentPipeData = null;
    }

    init() {
        if (!this.container) return;
        if (typeof THREE === 'undefined') {
            console.warn("Three.js not loaded yet.");
            return;
        }

        // Clear existing
        this.container.innerHTML = '';
        const width = this.container.clientWidth || 600;
        const height = this.container.clientHeight || 450;

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0f172a);

        // Camera
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(25, 20, 35);

        // Renderer with preserveDrawingBuffer: true for PNG snapshots
        this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.container.appendChild(this.renderer.domElement);

        // OrbitControls
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
        }

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
        this.scene.add(ambientLight);

        const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.3);
        dirLight1.position.set(30, 40, 30);
        this.scene.add(dirLight1);

        const dirLight2 = new THREE.DirectionalLight(0xf59e0b, 0.9);
        dirLight2.position.set(-30, -20, -30);
        this.scene.add(dirLight2);

        // Grid Floor
        const gridHelper = new THREE.GridHelper(50, 25, 0x334155, 0x1e293b);
        gridHelper.position.y = -10;
        this.scene.add(gridHelper);

        // Resize Listener
        window.addEventListener('resize', () => this.onResize());

        // Start render loop
        this.animate();
    }

    onResize() {
        if (!this.container || !this.renderer || !this.camera) return;
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        if (width === 0 || height === 0) return;
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    renderPipe(pipeData) {
        if (!pipeData) return;
        this.currentPipeData = pipeData;
        if (!this.scene) this.init();
        if (!this.scene) return;

        // Remove old pipe & weld
        if (this.pipeMesh) this.scene.remove(this.pipeMesh);
        if (this.weldMesh) this.scene.remove(this.weldMesh);

        const d_mm = pipeData.input_summary.diameter_mm || 1219.0;
        const t_mm = pipeData.input_summary.wall_thickness_mm || 14.30;
        const process = (pipeData.input_summary.manufacturing_process || "SAWH").toUpperCase();

        // Scale factors for 3D visualization
        const outerRadius = 8.0;
        const length = 30.0;
        // Proportionally scale inner radius with safety bounds
        const thicknessRatio = Math.min(Math.max(t_mm / d_mm, 0.01), 0.20);
        const innerRadius = outerRadius * (1.0 - thicknessRatio * 3.5);

        // Create Hollow Pipe via Extruded 2D Shape
        const pipeShape = new THREE.Shape();
        const thetaStart = 0;
        const thetaLength = this.isCutaway ? Math.PI * 1.5 : Math.PI * 2;

        // Outer Arc
        pipeShape.absarc(0, 0, outerRadius, thetaStart, thetaStart + thetaLength, false);
        if (this.isCutaway) {
            pipeShape.lineTo(innerRadius * Math.cos(thetaStart + thetaLength), innerRadius * Math.sin(thetaStart + thetaLength));
            pipeShape.absarc(0, 0, innerRadius, thetaStart + thetaLength, thetaStart, true);
            pipeShape.lineTo(outerRadius * Math.cos(thetaStart), outerRadius * Math.sin(thetaStart));
        } else {
            const holePath = new THREE.Path();
            holePath.absarc(0, 0, innerRadius, 0, Math.PI * 2, true);
            pipeShape.holes.push(holePath);
        }

        const extrudeSettings = {
            depth: length,
            bevelEnabled: true,
            bevelSegments: 3,
            steps: 1,
            bevelSize: 0.1,
            bevelThickness: 0.1
        };

        const geom = new THREE.ExtrudeGeometry(pipeShape, extrudeSettings);
        geom.center();

        const steelMaterial = new THREE.MeshStandardMaterial({
            color: 0x64748b,
            metalness: 0.85,
            roughness: 0.25,
            side: THREE.DoubleSide
        });

        this.pipeMesh = new THREE.Mesh(geom, steelMaterial);
        this.pipeMesh.rotation.x = Math.PI / 2;
        this.scene.add(this.pipeMesh);

        // Add 3D Weld Seam (Spiral or Longitudinal)
        if (process.includes("SAWH")) {
            class SpiralCurve extends THREE.Curve {
                constructor(radius, height, turns) {
                    super();
                    this.radius = radius;
                    this.height = height;
                    this.turns = turns;
                }
                getPoint(t) {
                    const angle = t * Math.PI * 2 * this.turns;
                    const x = this.radius * Math.cos(angle);
                    const y = (t - 0.5) * this.height;
                    const z = this.radius * Math.sin(angle);
                    return new THREE.Vector3(x, y, z);
                }
            }

            const spiral = new SpiralCurve(outerRadius + 0.06, length, 2.5);
            const weldGeom = new THREE.TubeGeometry(spiral, 128, 0.28, 8, false);
            const weldMat = new THREE.MeshStandardMaterial({
                color: 0xd97706,
                emissive: 0x78350f,
                metalness: 0.5,
                roughness: 0.4
            });

            this.weldMesh = new THREE.Mesh(weldGeom, weldMat);
            this.scene.add(this.weldMesh);
        } else if (process.includes("ERW") || process.includes("HFW") || process.includes("LSAW")) {
            const weldGeom = new THREE.CylinderGeometry(0.25, 0.25, length, 16);
            const weldMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.6 });
            this.weldMesh = new THREE.Mesh(weldGeom, weldMat);
            this.weldMesh.position.set(0, 0, outerRadius + 0.06);
            this.weldMesh.rotation.x = Math.PI / 2;
            this.scene.add(this.weldMesh);
        }
    }

    toggleCutaway() {
        this.isCutaway = !this.isCutaway;
        if (this.currentPipeData) this.renderPipe(this.currentPipeData);
    }

    toggleRotation() {
        this.isRotating = !this.isRotating;
    }

    resetCamera() {
        if (this.camera && this.controls) {
            this.camera.position.set(25, 20, 35);
            this.controls.target.set(0, 0, 0);
            this.controls.update();
        }
    }

    exportSnapshotPNG() {
        if (!this.renderer || !this.scene || !this.camera) return;
        this.renderer.render(this.scene, this.camera);
        const dataUrl = this.renderer.domElement.toDataURL("image/png");
        const a = document.createElement("a");
        const pipeName = this.currentPipeData ? 
            `${this.currentPipeData.input_summary.diameter_inch}_${this.currentPipeData.input_summary.material_grade}_t${this.currentPipeData.input_summary.wall_thickness_mm}mm` 
            : "Boru_3D_Model";
        a.download = `3D_Boru_Modeli_${pipeName.replace(/["\s]/g, '_')}.png`;
        a.href = dataUrl;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    animate() {
        this.animationFrameId = requestAnimationFrame(() => this.animate());

        if (this.controls) this.controls.update();

        if (this.isRotating && this.pipeMesh) {
            this.pipeMesh.rotation.z += 0.005;
            if (this.weldMesh) {
                this.weldMesh.rotation.y += 0.005;
            }
        }

        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
}
