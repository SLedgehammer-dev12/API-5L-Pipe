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
        this.pipeMaterial = null;
        this.gridHelper = null;
        this.lights = {};
        this.controls = null;
        this.animationFrameId = null;
        this.isCutaway = false;
        this.isRotating = true;
        this.isDark = true;
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

        // Camera
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(25, 20, 35);

        // Renderer with preserveDrawingBuffer: true for PNG snapshots
        this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.25;
        this.container.appendChild(this.renderer.domElement);

        // OrbitControls
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
        }

        // Lighting (multi-source for high-contrast technical drawing look)
        this.lights.ambient = new THREE.AmbientLight(0xffffff, 1.0);
        this.scene.add(this.lights.ambient);

        this.lights.hemisphere = new THREE.HemisphereLight(0xffffff, 0x475569, 1.1);
        this.scene.add(this.lights.hemisphere);

        this.lights.key = new THREE.DirectionalLight(0xffffff, 1.4);
        this.lights.key.position.set(30, 40, 30);
        this.scene.add(this.lights.key);

        this.lights.rim = new THREE.DirectionalLight(0x7dd3fc, 0.8);
        this.lights.rim.position.set(-30, -15, -30);
        this.scene.add(this.lights.rim);

        this.lights.fill = new THREE.DirectionalLight(0xf59e0b, 0.6);
        this.lights.fill.position.set(0, 10, -40);
        this.scene.add(this.lights.fill);

        // Apply initial theme (also creates the grid floor)
        this.applyTheme();

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
            color: this.isDark ? 0x94a3b8 : 0x475569,
            metalness: 0.4,
            roughness: 0.4,
            side: THREE.DoubleSide
        });
        this.pipeMaterial = steelMaterial;

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

            // Spiral weld: number of turns derived from the helix angle alpha
            // (turns = length * tan(alpha) / (2*pi*radius)); fallback 2.5 when not set.
            const spiralRadius = outerRadius + 0.06;
            const spiralTurns = (this.helixAngleDeg !== null && this.helixAngleDeg !== undefined)
                ? (length * Math.tan(this.helixAngleDeg * Math.PI / 180)) / (2 * Math.PI * spiralRadius)
                : 2.5;
            const spiral = new SpiralCurve(spiralRadius, length, spiralTurns);
            const weldGeom = new THREE.TubeGeometry(spiral, 128, 0.28, 8, false);
            const weldMat = new THREE.MeshStandardMaterial({
                color: 0xf59e0b,
                emissive: 0x92400e,
                emissiveIntensity: 0.6,
                metalness: 0.4,
                roughness: 0.35
            });

            this.weldMesh = new THREE.Mesh(weldGeom, weldMat);
            this.scene.add(this.weldMesh);
        } else if (process.includes("ERW") || process.includes("HFW") || process.includes("LSAW")) {
            const weldGeom = new THREE.CylinderGeometry(0.35, 0.35, length, 16);
            const weldMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0x92400e, emissiveIntensity: 0.6, metalness: 0.4, roughness: 0.35 });
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

    // Update the spiral weld seam to the given helix angle (deg) and re-render.
    setHelixAngle(deg) {
        this.helixAngleDeg = (deg === null || deg === undefined) ? null : Number(deg);
        if (this.currentPipeData) this.renderPipe(this.currentPipeData);
    }

    resetCamera() {
        if (this.camera && this.controls) {
            this.camera.position.set(25, 20, 35);
            this.controls.target.set(0, 0, 0);
            this.controls.update();
        }
    }

    toggleTheme() {
        this.isDark = !this.isDark;
        this.applyTheme();
    }

    applyTheme() {
        if (!this.scene) return;

        // Rebuild grid with theme-appropriate colors
        if (this.gridHelper) {
            this.scene.remove(this.gridHelper);
            this.gridHelper.geometry.dispose();
            this.gridHelper.material.dispose();
        }
        const gridCenter = this.isDark ? 0x475569 : 0x94a3b8;
        const gridLine = this.isDark ? 0x1e293b : 0xcbd5e1;
        this.gridHelper = new THREE.GridHelper(50, 25, gridCenter, gridLine);
        this.gridHelper.position.y = -10;
        this.scene.add(this.gridHelper);

        if (this.isDark) {
            this.scene.background = new THREE.Color(0x0f172a);
            this.renderer.toneMappingExposure = 1.25;
            if (this.pipeMaterial) this.pipeMaterial.color.set(0x94a3b8);
            if (this.lights.ambient) this.lights.ambient.intensity = 1.0;
            if (this.lights.hemisphere) this.lights.hemisphere.intensity = 1.1;
        } else {
            this.scene.background = new THREE.Color(0xf1f5f9);
            this.renderer.toneMappingExposure = 1.35;
            if (this.pipeMaterial) this.pipeMaterial.color.set(0x475569);
            if (this.lights.ambient) this.lights.ambient.intensity = 1.35;
            if (this.lights.hemisphere) this.lights.hemisphere.intensity = 1.35;
        }

        const btn = document.getElementById("btn-toggle-theme-3d");
        if (btn) {
            btn.innerHTML = this.isDark
                ? '☀️ Açık Tema'
                : '🌙 Koyu Tema';
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
