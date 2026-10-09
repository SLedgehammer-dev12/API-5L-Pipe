/**
 * API 5L Specimen 3D Interactive WebGL Visualizer using Three.js.
 * Provides high-fidelity, dimension-driven 3D models for API 5L test specimens:
 * - Tensile Strip (Çekme Şerit - 38.1 mm x t)
 * - Tensile Round Bar (Çekme Yuvarlak Çubuk - Table 21: 12.7 / 8.9 / 6.4 mm)
 * - Charpy V-Notch (Çentik Darbe CVN - 10x10x55 mm or Table 22 Sub-size)
 * - DWTT (Drop Weight Tear Test - 305x76x t mm with press-notch)
 */

class SpecimenVisualizer3D {
    constructor(containerElement) {
        this.container = typeof containerElement === 'string'
            ? document.getElementById(containerElement)
            : containerElement;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.animId = null;
        this.currentMeshGroup = null;
        this.autoRotate = true;
        this.isWireframe = false;
        this.specimenKey = null;
        this.pipeData = null;
        this.onResizeBound = this.onWindowResize.bind(this);
    }

    isSupported() {
        return typeof THREE !== 'undefined';
    }

    init() {
        if (!this.container) return false;
        if (!this.isSupported()) {
            this.container.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full p-6 text-center text-slate-400">
                    <span class="text-3xl mb-2">⚠️</span>
                    <p class="text-sm font-semibold text-slate-200">Three.js 3D kütüphanesi yüklenemedi.</p>
                    <p class="text-xs text-slate-400 mt-1">İnternet bağlantınızı kontrol edin veya 2D çizim görünümüne geçin.</p>
                </div>
            `;
            return false;
        }

        // Clean container
        this.container.innerHTML = '';
        this.container.style.position = 'relative';

        const width = this.container.clientWidth || 640;
        const height = this.container.clientHeight || 400;

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0b1120); // Dark slate studio backdrop

        // Camera
        this.camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 1000);
        this.camera.position.set(45, 35, 60);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.15;
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        // Controls
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.06;
            this.controls.maxDistance = 250;
            this.controls.minDistance = 8;
        }

        // Studio 3-Point Lighting
        const ambLight = new THREE.AmbientLight(0xffffff, 0.75);
        this.scene.add(ambLight);

        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x1e293b, 0.85);
        this.scene.add(hemiLight);

        const keyLight = new THREE.DirectionalLight(0xffffff, 1.4);
        keyLight.position.set(50, 70, 60);
        keyLight.castShadow = true;
        this.scene.add(keyLight);

        const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.9);
        fillLight.position.set(-60, 30, -40);
        this.scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0xfde68a, 0.7);
        rimLight.position.set(0, -40, -50);
        this.scene.add(rimLight);

        // Grid floor
        const grid = new THREE.GridHelper(90, 30, 0x334155, 0x1e293b);
        grid.position.y = -12;
        this.scene.add(grid);

        // Add Floating UI Overlay
        this.buildOverlayUI();

        // Resize Listener
        window.addEventListener('resize', this.onResizeBound);

        // Start Loop
        this.animate();
        return true;
    }

    buildOverlayUI() {
        const overlay = document.createElement('div');
        overlay.className = 'absolute inset-x-0 top-0 p-3 flex justify-between items-start pointer-events-none select-none z-10';
        overlay.innerHTML = `
            <div id="sp3d-badge-container" class="pointer-events-auto bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/80 text-white shadow-lg text-xs">
                <div id="sp3d-title" class="font-bold text-blue-400">3D Numune Modeli</div>
                <div id="sp3d-dim" class="text-[11px] text-slate-300 font-mono">Yükleniyor...</div>
            </div>
            <div class="pointer-events-auto flex items-center gap-1.5 bg-slate-900/80 backdrop-blur-md p-1 rounded-lg border border-slate-700/80 shadow-lg text-xs text-white">
                <button id="sp3d-btn-rot" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded transition text-[11px] font-semibold text-amber-300" title="Otomatik döndürmeyi aç/kapat">
                    ⟳ Döndür: Açık
                </button>
                <button id="sp3d-btn-wire" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded transition text-[11px] font-semibold text-slate-200" title="Tel kafes modunu aç/kapat">
                    🔲 Tel Kafes
                </button>
                <button id="sp3d-btn-reset" class="px-2 py-1 bg-blue-600 hover:bg-blue-500 rounded transition text-[11px] font-semibold text-white" title="Kamera açısını sıfırla">
                    ↺ Sıfırla
                </button>
            </div>
        `;
        this.container.appendChild(overlay);

        // Bottom instruction
        const footerHint = document.createElement('div');
        footerHint.className = 'absolute inset-x-0 bottom-2 text-center pointer-events-none select-none z-10 text-[10px] text-slate-400 tracking-wide';
        footerHint.innerText = '🖱️ Sol tık: Döndür • Sağ tık: Kaydır • Tekerlek: Yakınlaştır / Uzaklaştır';
        this.container.appendChild(footerHint);

        // Attach button handlers
        const btnRot = overlay.querySelector('#sp3d-btn-rot');
        if (btnRot) {
            btnRot.addEventListener('click', (e) => {
                e.stopPropagation();
                this.autoRotate = !this.autoRotate;
                btnRot.innerText = this.autoRotate ? '⟳ Döndür: Açık' : '⏸ Döndür: Kapalı';
                btnRot.className = this.autoRotate
                    ? 'px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded transition text-[11px] font-semibold text-amber-300'
                    : 'px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded transition text-[11px] font-semibold text-slate-400';
            });
        }

        const btnWire = overlay.querySelector('#sp3d-btn-wire');
        if (btnWire) {
            btnWire.addEventListener('click', (e) => {
                e.stopPropagation();
                this.isWireframe = !this.isWireframe;
                btnWire.className = this.isWireframe
                    ? 'px-2 py-1 bg-amber-600 hover:bg-amber-500 rounded transition text-[11px] font-semibold text-white'
                    : 'px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded transition text-[11px] font-semibold text-slate-200';
                this.applyWireframe(this.isWireframe);
            });
        }

        const btnReset = overlay.querySelector('#sp3d-btn-reset');
        if (btnReset) {
            btnReset.addEventListener('click', (e) => {
                e.stopPropagation();
                this.resetCamera();
            });
        }
    }

    updateBadge(title, dimStr) {
        const titleEl = this.container.querySelector('#sp3d-title');
        const dimEl = this.container.querySelector('#sp3d-dim');
        if (titleEl) titleEl.innerText = title;
        if (dimEl) dimEl.innerText = dimStr;
    }

    applyWireframe(enabled) {
        if (!this.currentMeshGroup) return;
        this.currentMeshGroup.traverse((child) => {
            if (child.isMesh && child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(m => m.wireframe = enabled);
                } else {
                    child.material.wireframe = enabled;
                }
            }
        });
    }

    resetCamera() {
        if (!this.camera || !this.controls) return;
        this.camera.position.set(45, 35, 60);
        this.controls.target.set(0, 0, 0);
        this.controls.update();
    }

    loadSpecimen(specimenKey, pipeData) {
        this.specimenKey = specimenKey;
        this.pipeData = pipeData || {};

        if (!this.scene) {
            if (!this.init()) return;
        }

        // Remove previous mesh
        if (this.currentMeshGroup) {
            this.scene.remove(this.currentMeshGroup);
            this.disposeGroup(this.currentMeshGroup);
            this.currentMeshGroup = null;
        }

        this.currentMeshGroup = new THREE.Group();

        switch (specimenKey) {
            case 'tensile_strip':
                this.buildTensileStrip(this.pipeData);
                break;
            case 'tensile_round':
                this.buildTensileRound(this.pipeData);
                break;
            case 'tensile_weld':
                this.buildTensileWeld(this.pipeData);
                break;
            case 'charpy':
                this.buildCharpy(this.pipeData);
                break;
            case 'dwtt':
                this.buildDWTT(this.pipeData);
                break;
            case 'flattening':
            case 'flattening_test':
                this.buildFlatteningTest3D(this.pipeData);
                break;
            case 'pipe_bevel':
            case 'bevel':
            case 'dimensional_bevel_ends':
                this.buildPipeBevel3D(this.pipeData);
                break;
            case 'pipe_straightness':
            case 'straightness':
            case 'dimensional_straightness':
                this.buildPipeStraightness3D(this.pipeData);
                break;
            default:
                this.buildGenericBlock(specimenKey);
                break;
        }

        this.scene.add(this.currentMeshGroup);
        this.applyWireframe(this.isWireframe);
    }

    // -------------------------------------------------------------
    // SPECIMEN 1: Tensile Strip (Boru Gövdesi Çekme Şerit - ASTM A370 Şekil 3)
    // Boru gövdesinden (ana metalden) alınır: Üzerinde KAYNAK DİKİŞİ BULUNMAZ.
    // -------------------------------------------------------------
    buildTensileStrip(pd) {
        const s = pd.input_summary || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.3;
        const proc = String(s.manufacturing_process || 'SAWH').toUpperCase();
        const grade = s.material_grade || 'X65';

        this.updateBadge(
            'Boru Gövdesi Çekme Şerit Numunesi (ASTM A370 Şekil 3)',
            `Boru Gövdesi (Kaynaksız) • W = 38,1 mm • G = 50,0 mm • R ≥ 25 mm (İçbükey / Concave Omuz) • t = ${t.toFixed(2)} mm • ${grade}`
        );

        // Materials
        const steelMat = new THREE.MeshStandardMaterial({
            color: 0xcbd5e1,
            metalness: 0.88,
            roughness: 0.24
        });

        const gripMat = new THREE.MeshStandardMaterial({
            color: 0x94a3b8,
            metalness: 0.9,
            roughness: 0.45
        });

        const gaugeLineMat = new THREE.MeshBasicMaterial({ color: 0x2563eb });

        // Dimensions (scaled for 3D viewport)
        // Length: 250 mm -> 50 units (scale 0.2)
        // Width: 38.1 mm -> 7.62 units (half = 3.81)
        // Grip Width C: 50.8 mm -> 10.16 units (half = 5.08)
        // Reduced Length A: 60 mm -> 12.0 units (half = 6.0)
        // Gauge Length G: 50 mm -> 10.0 units (half = 5.0)
        const scaleL = 0.2;
        const halfL = 125 * scaleL;      // 25.0
        const halfW = (38.1 / 2) * scaleL; // 3.81
        const halfC = (50.8 / 2) * scaleL; // 5.08
        const halfA = (60.0 / 2) * scaleL; // 6.0
        const halfG = (50.0 / 2) * scaleL; // 5.0
        const xGrip = 58 * scaleL;        // 11.6
        const thk = Math.max(1.2, Math.min(5.5, t * scaleL));

        // Construct 2D Dog-Bone profile in X-Y plane (concave fillet transition R >= 25 mm)
        // Concave transition: control points are positioned at inner reduced width (halfW / -halfW)
        // ensuring tangency with the gauge section and pure inward concave curvature (zero convex bulge)
        const cpFrac = 0.55;
        const cpXLeft = -halfA - (xGrip - halfA) * cpFrac;  // -9.08
        const cpXRight = halfA + (xGrip - halfA) * cpFrac;   // 9.08

        const shape = new THREE.Shape();
        shape.moveTo(-halfL, halfC);
        shape.lineTo(-xGrip, halfC);
        shape.quadraticCurveTo(cpXLeft, halfW, -halfA, halfW); // R >= 25 mm CONCAVE fillet
        shape.lineTo(halfA, halfW);
        shape.quadraticCurveTo(cpXRight, halfW, xGrip, halfC);  // R >= 25 mm CONCAVE fillet
        shape.lineTo(halfL, halfC);
        shape.lineTo(halfL, -halfC);
        shape.lineTo(xGrip, -halfC);
        shape.quadraticCurveTo(cpXRight, -halfW, halfA, -halfW); // R >= 25 mm CONCAVE fillet
        shape.lineTo(-halfA, -halfW);
        shape.quadraticCurveTo(cpXLeft, -halfW, -xGrip, -halfC); // R >= 25 mm CONCAVE fillet
        shape.lineTo(-halfL, -halfC);
        shape.closePath();

        const extrudeSettings = {
            depth: thk,
            bevelEnabled: true,
            bevelSegments: 2,
            curveSegments: 24,
            steps: 1,
            bevelSize: 0.1,
            bevelThickness: 0.1
        };

        const bodyGeom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        bodyGeom.center();
        // Rotate so X is length, Y is thickness, Z is width
        bodyGeom.rotateX(Math.PI / 2);

        const bodyMesh = new THREE.Mesh(bodyGeom, steelMat);
        bodyMesh.castShadow = true;
        bodyMesh.receiveShadow = true;
        this.currentMeshGroup.add(bodyMesh);

        // Grip Clamping Plates (serrated clamp ends on both tips)
        const gripLen = halfL - xGrip + 1.0;
        const gripGeom = new THREE.BoxGeometry(gripLen, thk + 0.25, halfC * 2 + 0.3);
        const leftGrip = new THREE.Mesh(gripGeom, gripMat);
        leftGrip.position.set(-halfL + gripLen / 2, 0, 0);
        this.currentMeshGroup.add(leftGrip);

        const rightGrip = new THREE.Mesh(gripGeom, gripMat);
        rightGrip.position.set(halfL - gripLen / 2, 0, 0);
        this.currentMeshGroup.add(rightGrip);

        // Gauge length marks (G = 50 mm / 2.0 in) on top surface
        const markGeom = new THREE.BoxGeometry(0.14, 0.08, halfW * 2);
        const markLeft = new THREE.Mesh(markGeom, gaugeLineMat);
        markLeft.position.set(-halfG, thk / 2 + 0.04, 0);
        this.currentMeshGroup.add(markLeft);

        const markRight = new THREE.Mesh(markGeom, gaugeLineMat);
        markRight.position.set(halfG, thk / 2 + 0.04, 0);
        this.currentMeshGroup.add(markRight);

        // Gauge Mark Anchor Spheres
        const sphereGeom = new THREE.SphereGeometry(0.2, 16, 16);
        const sphL = new THREE.Mesh(sphereGeom, gaugeLineMat);
        sphL.position.set(-halfG, thk / 2 + 0.1, 0);
        this.currentMeshGroup.add(sphL);

        const sphR = new THREE.Mesh(sphereGeom, gaugeLineMat);
        sphR.position.set(halfG, thk / 2 + 0.1, 0);
        this.currentMeshGroup.add(sphR);

        // Axial tension pull arrows (← F ... F →)
        this.addTensionArrows(-halfL, halfL, 0, 0, 6.0);

        // Camera placement
        this.camera.position.set(28, 22, 42);
        if (this.controls) this.controls.target.set(0, 0, 0);
    }

    // -------------------------------------------------------------
    // SPECIMEN 2: Tensile Round Bar (Boru Gövdesi Yuvarlak Çubuk - ASTM A370 Şekil 4/5)
    // Boru gövdesi cidar ortasından alınır: Üzerinde KAYNAK DİKİŞİ BULUNMAZ.
    // -------------------------------------------------------------
    buildTensileRound(pd) {
        const s = pd.input_summary || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.3;
        const dPipe = parseFloat(s.diameter_mm) || 1219.0;
        const proc = String(s.manufacturing_process || 'SAWH').toUpperCase();
        const isSmls = proc.includes('SMLS') || proc.includes('SEAMLESS');
        const grade = s.material_grade || 'X65';

        // Diameter per Table 21
        const dBar = isSmls ? (t >= 19.0 ? 12.7 : 6.4) : (typeof rsRoundBarDia === 'function' ? rsRoundBarDia(dPipe, t) : 8.9);

        this.updateBadge(
            'Boru Gövdesi Yuvarlak Çubuk Çekme Numunesi (ASTM A370 Şekil 4/5)',
            `Boru Gövdesi (Kaynaksız) • Mastar Çapı d = ${dBar.toFixed(1)} mm • G = 50,0 mm • R ≥ 10 mm • ${grade}`
        );

        const steelMat = new THREE.MeshStandardMaterial({
            color: 0xe2e8f0,
            metalness: 0.92,
            roughness: 0.18
        });

        const threadMat = new THREE.MeshStandardMaterial({
            color: 0x94a3b8,
            metalness: 0.88,
            roughness: 0.42
        });

        const gaugeLineMat = new THREE.MeshBasicMaterial({ color: 0x2563eb });

        const scale = 1.35;
        const rBar = (dBar / 2) * scale * 0.2;  // e.g. 12.7 -> ~1.71
        const rGrip = rBar * 1.85;              // threaded end radius
        const gaugeLen = 50 * scale * 0.2;     // ~13.5
        const shoulderLen = 14 * scale * 0.2;  // ~3.8
        const gripLen = 35 * scale * 0.2;      // ~9.5

        // 1. Central Gauge Cylinder (along X axis) - Pure Base Metal
        const gaugeGeom = new THREE.CylinderGeometry(rBar, rBar, gaugeLen, 32);
        gaugeGeom.rotateZ(Math.PI / 2);
        const gaugeMesh = new THREE.Mesh(gaugeGeom, steelMat);
        gaugeMesh.castShadow = true;
        this.currentMeshGroup.add(gaugeMesh);

        // 2. Gauge length scribe mark rings at G = 50 mm
        const ringGeom = new THREE.TorusGeometry(rBar + 0.03, 0.04, 8, 32);
        ringGeom.rotateY(Math.PI / 2);
        const markL = new THREE.Mesh(ringGeom, gaugeLineMat);
        markL.position.x = -gaugeLen / 2;
        this.currentMeshGroup.add(markL);

        const markR = new THREE.Mesh(ringGeom, gaugeLineMat);
        markR.position.x = gaugeLen / 2;
        this.currentMeshGroup.add(markR);

        // 3. Smooth Transition Shoulders (R >= 10 mm)
        const createShoulder = (xPos, isLeft) => {
            const rStart = isLeft ? rGrip : rBar;
            const rEnd = isLeft ? rBar : rGrip;
            const shGeom = new THREE.CylinderGeometry(rStart, rEnd, shoulderLen, 32);
            shGeom.rotateZ(Math.PI / 2);
            const shMesh = new THREE.Mesh(shGeom, steelMat);
            shMesh.position.x = xPos;
            return shMesh;
        };

        const leftShoulder = createShoulder(-gaugeLen / 2 - shoulderLen / 2, true);
        const rightShoulder = createShoulder(gaugeLen / 2 + shoulderLen / 2, false);
        this.currentMeshGroup.add(leftShoulder);
        this.currentMeshGroup.add(rightShoulder);

        // 4. Threaded Grips (Left & Right)
        const createGrip = (xPos) => {
            const g = new THREE.Group();
            const mainCyl = new THREE.CylinderGeometry(rGrip, rGrip, gripLen, 32);
            mainCyl.rotateZ(Math.PI / 2);
            const mainMesh = new THREE.Mesh(mainCyl, threadMat);
            g.add(mainMesh);

            // Thread groove rings for realistic threaded look
            const ringCount = 8;
            const step = gripLen / (ringCount + 1);
            for (let i = 1; i <= ringCount; i++) {
                const trGeom = new THREE.TorusGeometry(rGrip * 1.02, 0.1, 8, 32);
                trGeom.rotateY(Math.PI / 2);
                const trMesh = new THREE.Mesh(trGeom, threadMat);
                trMesh.position.x = -gripLen / 2 + i * step;
                g.add(trMesh);
            }

            g.position.x = xPos;
            return g;
        };

        const totalHalfL = gaugeLen / 2 + shoulderLen + gripLen;
        const leftGrip = createGrip(-gaugeLen / 2 - shoulderLen - gripLen / 2);
        const rightGrip = createGrip(gaugeLen / 2 + shoulderLen + gripLen / 2);
        this.currentMeshGroup.add(leftGrip);
        this.currentMeshGroup.add(rightGrip);

        // Axial tension pull arrows
        this.addTensionArrows(-totalHalfL, totalHalfL, 0, 0, 5.5);

        // Camera
        this.camera.position.set(24, 18, 38);
        if (this.controls) this.controls.target.set(0, 0, 0);
    }

    // -------------------------------------------------------------
    // SPECIMEN 3: Transverse Weld Tensile (Kaynak Çekme Testi - ASTM A370 Şekil A2.3)
    // Kaynak dikişi tam ortada ENİNE yönde (Z ekseni) yer alır; çekme kuvveti X eksenindedir.
    // -------------------------------------------------------------
    buildTensileWeld(pd) {
        const s = pd.input_summary || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.3;
        const grade = s.material_grade || 'X65';

        this.updateBadge(
            'Kaynak Çekme Testi Numunesi (ASTM A370 Şekil A2.3 / API 5L 10.2.3.3)',
            `Enine Kaynak Dikişi (Merkezde) • W = 38,1 mm • t = ${t.toFixed(2)} mm • Çekme Eksenine Dik Kaynak • Rm ≥ SMTS`
        );

        const steelMat = new THREE.MeshStandardMaterial({
            color: 0xcbd5e1,
            metalness: 0.86,
            roughness: 0.26
        });

        const gripMat = new THREE.MeshStandardMaterial({
            color: 0x94a3b8,
            metalness: 0.9,
            roughness: 0.45
        });

        // Weld metal (golden-bronze fusion zone)
        const weldMat = new THREE.MeshStandardMaterial({
            color: 0xd97706,
            emissive: 0x78350f,
            emissiveIntensity: 0.25,
            metalness: 0.8,
            roughness: 0.32
        });

        // Heat-affected zone (HAZ / ITAB)
        const hazMat = new THREE.MeshStandardMaterial({
            color: 0x818cf8,
            metalness: 0.82,
            roughness: 0.3
        });

        const scaleL = 0.2;
        const totalL = 250 * scaleL;       // 50.0
        const halfL = totalL / 2;          // 25.0
        const width = 38.1 * scaleL;       // 7.62 (Z ekseni boyunca en)
        const halfW = width / 2;           // 3.81
        const thk = Math.max(1.2, Math.min(5.5, t * scaleL));
        const gripL = 70 * scaleL;         // 14.0

        // 1. Base Plate (Specimen Strip aligned along X axis, width along Z axis)
        const bodyGeom = new THREE.BoxGeometry(totalL, thk, width);
        const bodyMesh = new THREE.Mesh(bodyGeom, steelMat);
        bodyMesh.castShadow = true;
        bodyMesh.receiveShadow = true;
        this.currentMeshGroup.add(bodyMesh);

        // 2. Serrated Grip Pads on both ends
        const gripGeom = new THREE.BoxGeometry(gripL, thk + 0.25, width + 0.3);
        const leftGrip = new THREE.Mesh(gripGeom, gripMat);
        leftGrip.position.x = -halfL + gripL / 2;
        this.currentMeshGroup.add(leftGrip);

        const rightGrip = new THREE.Mesh(gripGeom, gripMat);
        rightGrip.position.x = halfL - gripL / 2;
        this.currentMeshGroup.add(rightGrip);

        // 3. Central Transverse Weld Seam (ENİNE DİKİŞ — Z ekseni boyunca uzanır!)
        const weldHalfW = 1.4; // Seam width in X direction (approx 14 mm full scale)
        const weldZoneGeom = new THREE.BoxGeometry(weldHalfW * 2, thk + 0.04, width);
        const weldZoneMesh = new THREE.Mesh(weldZoneGeom, weldMat);
        weldZoneMesh.position.set(0, 0, 0);
        this.currentMeshGroup.add(weldZoneMesh);

        // 4. Weld Reinforcement Cap (Kapak Pasosu — Top surface, runs along Z axis across the width)
        const capGeom = new THREE.CylinderGeometry(weldHalfW * 1.1, weldHalfW * 1.3, width, 24);
        capGeom.rotateX(Math.PI / 2); // Cylinder axis aligns with Z axis (enine yön)
        const weldCap = new THREE.Mesh(capGeom, weldMat);
        weldCap.scale.set(1.0, 0.35, 1.0);
        weldCap.position.set(0, thk / 2 + 0.12, 0);
        this.currentMeshGroup.add(weldCap);

        // 5. Weld Root Pass (Kök Pasosu — Bottom surface, runs along Z axis across the width)
        const rootGeom = capGeom.clone();
        const weldRoot = new THREE.Mesh(rootGeom, weldMat);
        weldRoot.scale.set(0.9, 0.25, 1.0);
        weldRoot.position.set(0, -thk / 2 - 0.1, 0);
        this.currentMeshGroup.add(weldRoot);

        // 6. Transverse Weld Solidification Ripple Scales (Kaynak Dikiş Dalgaları)
        const rippleCount = 7;
        const rippleStep = width / (rippleCount + 1);
        for (let i = 1; i <= rippleCount; i++) {
            const ripGeom = new THREE.TorusGeometry(weldHalfW * 1.05, 0.08, 6, 24);
            ripGeom.scale.set(1.0, 0.38, 1.0);
            const ripMesh = new THREE.Mesh(ripGeom, weldMat);
            ripMesh.position.set(0, thk / 2 + 0.15, -halfW + i * rippleStep);
            this.currentMeshGroup.add(ripMesh);
        }

        // 7. HAZ (Heat-Affected Zone / ITAB) Bands running transversely across width in Z
        const hazW = 1.0;
        const hazGeom = new THREE.BoxGeometry(hazW, thk + 0.02, width);
        const hazL = new THREE.Mesh(hazGeom, hazMat);
        hazL.position.set(-weldHalfW - hazW / 2, 0, 0);
        this.currentMeshGroup.add(hazL);

        const hazR = new THREE.Mesh(hazGeom, hazMat);
        hazR.position.set(weldHalfW + hazW / 2, 0, 0);
        this.currentMeshGroup.add(hazR);

        // 8. Tensile pull arrows (← F ... F →) pulling along X (perpendicular to weld seam)
        this.addTensionArrows(-halfL, halfL, 0, 0, 6.0);

        // Camera
        this.camera.position.set(28, 22, 42);
        if (this.controls) this.controls.target.set(0, 0, 0);
    }

    // -------------------------------------------------------------
    // SPECIMEN 4: Charpy V-Notch (Çentik Darbe - ISO 148-1 / ASTM A370)
    // Fiziksel kural: Çentik, ÖRS DESTEKLERİ TARAFINDA (çekme yüzünde) yer alır.
    // Vurucu çekiç (sarkaç) çentiğin zıt yüzündeki düz yüzeye (basma yüzüne) çarpar.
    // -------------------------------------------------------------
    buildCharpy(pd) {
        const tt = pd.toughness_and_tests || {};
        const sizeLabel = String(tt.notch_specimen_size || '10 x 10 mm (Tam Boy)');

        let widthMm = 10.0;
        if (sizeLabel.includes('7.5')) widthMm = 7.5;
        else if (sizeLabel.includes('6.67')) widthMm = 6.67;
        else if (sizeLabel.includes('5 x 10')) widthMm = 5.0;

        this.updateBadge(
            'Charpy V-Çentik Numunesi (ISO 148-1 / ASTM A370)',
            `${widthMm} × 10 × 55 mm • Çentik Örs Tarafında (Çekme Yüzü) • 40 mm Açıklık`
        );

        const steelMat = new THREE.MeshStandardMaterial({
            color: 0xe2e8f0,
            metalness: 0.9,
            roughness: 0.22
        });

        const notchFaceMat = new THREE.MeshStandardMaterial({
            color: 0xf59e0b,
            metalness: 0.85,
            roughness: 0.25
        });

        const anvilMat = new THREE.MeshStandardMaterial({
            color: 0x334155,
            metalness: 0.92,
            roughness: 0.38
        });

        const strikerMat = new THREE.MeshStandardMaterial({
            color: 0xd97706,
            metalness: 0.88,
            roughness: 0.28
        });

        const scale = 0.55;
        const L = 55 * scale;           // 30.25
        const H = 10 * scale;           // 5.5
        const W = widthMm * scale;      // 5.5 (or sub-size)
        const notchDepth = 2.0 * scale; // 1.1
        const halfL = L / 2;            // 15.125
        const halfH = H / 2;            // 2.75
        const notchHalfW = notchDepth * Math.tan((22.5 * Math.PI) / 180); // 45° included angle (~0.455)

        // Charpy Specimen Shape in X-Y plane:
        // TOP FACE (+halfH) is FLAT (struck by striker pendulum)
        // BOTTOM FACE (-halfH) has the 45° V-NOTCH pointing UP (rests between anvils on tension side)
        const shape = new THREE.Shape();
        shape.moveTo(-halfL, halfH);                 // Top-left
        shape.lineTo(halfL, halfH);                  // Top flat face (striker impact face)
        shape.lineTo(halfL, -halfH);                 // Right end
        shape.lineTo(notchHalfW, -halfH);            // Bottom face approaching notch
        shape.lineTo(0, -halfH + notchDepth);        // 45° V-notch apex pointing UP into bar
        shape.lineTo(-notchHalfW, -halfH);           // Bottom face leaving notch
        shape.lineTo(-halfL, -halfH);                // Bottom-left
        shape.closePath();

        const extrudeSettings = {
            depth: W,
            bevelEnabled: true,
            bevelSegments: 2,
            steps: 1,
            bevelSize: 0.08,
            bevelThickness: 0.08
        };

        const charpyGeom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        charpyGeom.center();
        const charpyMesh = new THREE.Mesh(charpyGeom, steelMat);
        charpyMesh.castShadow = true;
        charpyMesh.receiveShadow = true;
        this.currentMeshGroup.add(charpyMesh);

        // Notch interior highlight prism (at bottom face pointing up)
        const notchHlGeom = new THREE.ConeGeometry(notchHalfW * 1.5, notchDepth, 4);
        // Default Cone points UP (+Y), which matches the bottom notch apex pointing UP!
        const notchHl = new THREE.Mesh(notchHlGeom, notchFaceMat);
        notchHl.position.set(0, -halfH + notchDepth / 2, 0);
        notchHl.scale.set(1.1, 1.0, W / 2.2);
        this.currentMeshGroup.add(notchHl);

        // 40 mm Hardened Anvil Supports at BOTTOM (supporting specimen on notched side)
        const anvilSpan = 40 * scale; // 22.0
        const anvilRad = 1.3;
        const anvilLen = W * 1.8;

        const anvilGeom = new THREE.CylinderGeometry(anvilRad, anvilRad, anvilLen, 24);
        anvilGeom.rotateX(Math.PI / 2);

        const leftAnvil = new THREE.Mesh(anvilGeom, anvilMat);
        leftAnvil.position.set(-anvilSpan / 2, -halfH - anvilRad, 0);
        this.currentMeshGroup.add(leftAnvil);

        const rightAnvil = new THREE.Mesh(anvilGeom, anvilMat);
        rightAnvil.position.set(anvilSpan / 2, -halfH - anvilRad, 0);
        this.currentMeshGroup.add(rightAnvil);

        // Pendulum Striker Tup above TOP UNNOTCHED FACE (striking opposite the notch)
        const strikerGeom = new THREE.ConeGeometry(2.6, 5.0, 4);
        strikerGeom.rotateZ(Math.PI); // Point downwards towards top face
        const striker = new THREE.Mesh(strikerGeom, strikerMat);
        striker.position.set(0, halfH + 4.8, 0);
        striker.scale.set(1.1, 1.0, W / 2.4);
        this.currentMeshGroup.add(striker);

        // Downward Impact Force Arrow (↓ F_darbe) striking back of the notch
        this.addImpactArrow(0, halfH + 8.5, halfH + 5.5, 0);

        // Camera
        this.camera.position.set(24, 18, 34);
        if (this.controls) this.controls.target.set(0, 0, 0);
    }

    // -------------------------------------------------------------
    // SPECIMEN 5: DWTT (Drop Weight Tear Test - API 5L 9.9 / ASTM E436)
    // Fiziksel kural: 45° pres çentik mesnet örsleri tarafında (alt kenarda),
    // düşen ağırlık (tup) ise çentiğin karşısındaki üst düz kenara çarpar.
    // -------------------------------------------------------------
    buildDWTT(pd) {
        const s = pd.input_summary || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.3;

        this.updateBadge(
            'DWTT Numunesi (API 5L 9.9 / ASTM E436)',
            `305 × 76 × ${t.toFixed(1)} mm (Tam Cidar) • Çentik Örs Tarafında • 254 mm Açıklık • Sünek Alan ≥ %85`
        );

        const plateMat = new THREE.MeshStandardMaterial({
            color: 0x94a3b8,
            metalness: 0.88,
            roughness: 0.32
        });

        const notchMat = new THREE.MeshStandardMaterial({
            color: 0xef4444,
            metalness: 0.75,
            roughness: 0.28
        });

        const anvilMat = new THREE.MeshStandardMaterial({
            color: 0x334155,
            metalness: 0.92,
            roughness: 0.4
        });

        const tupMat = new THREE.MeshStandardMaterial({
            color: 0xf59e0b,
            metalness: 0.9,
            roughness: 0.28
        });

        const scale = 0.12;
        const L = 305 * scale;           // 36.6
        const H = 76 * scale;            // 9.12
        const W = Math.max(1.4, Math.min(5.5, t * scale)); // ~1.7
        const notchDepth = 5.08 * scale; // 0.61
        const notchHalfW = notchDepth * Math.tan((22.5 * Math.PI) / 180);
        const halfL = L / 2;
        const halfH = H / 2;

        // Plate Shape in X-Y plane:
        // TOP is FLAT edge struck by drop hammer
        // BOTTOM has 45° press-notch pointing UP
        const shape = new THREE.Shape();
        shape.moveTo(-halfL, halfH);
        shape.lineTo(halfL, halfH);          // Flat top edge struck by falling tup
        shape.lineTo(halfL, -halfH);
        shape.lineTo(notchHalfW, -halfH);
        shape.lineTo(0, -halfH + notchDepth);// 45° press-notch pointing UP
        shape.lineTo(-notchHalfW, -halfH);
        shape.lineTo(-halfL, -halfH);
        shape.closePath();

        const extrudeSettings = {
            depth: W,
            bevelEnabled: true,
            bevelSegments: 2,
            steps: 1,
            bevelSize: 0.08,
            bevelThickness: 0.08
        };

        const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        geom.center();
        const plateMesh = new THREE.Mesh(geom, plateMat);
        plateMesh.castShadow = true;
        plateMesh.receiveShadow = true;
        this.currentMeshGroup.add(plateMesh);

        // Press-notch indicator cone (at bottom edge pointing up)
        const notchHlGeom = new THREE.ConeGeometry(notchHalfW * 1.8, notchDepth * 1.2, 4);
        const notchHl = new THREE.Mesh(notchHlGeom, notchMat);
        notchHl.position.set(0, -halfH + notchDepth / 2, 0);
        notchHl.scale.set(1.1, 1.0, W / 1.5);
        this.currentMeshGroup.add(notchHl);

        // Anvils at 254 mm (10") span at BOTTOM
        const anvilSpan = 254 * scale; // 30.48
        const anvilGeom = new THREE.CylinderGeometry(1.6, 1.6, W * 2.2, 20);
        anvilGeom.rotateX(Math.PI / 2);

        const leftAnvil = new THREE.Mesh(anvilGeom, anvilMat);
        leftAnvil.position.set(-anvilSpan / 2, -halfH - 1.6, 0);
        this.currentMeshGroup.add(leftAnvil);

        const rightAnvil = new THREE.Mesh(anvilGeom, anvilMat);
        rightAnvil.position.set(anvilSpan / 2, -halfH - 1.6, 0);
        this.currentMeshGroup.add(rightAnvil);

        // Falling Hammer Tup at TOP (impacting opposite the notch)
        const tupGeom = new THREE.CylinderGeometry(1.8, 3.2, 4.0, 16);
        const tup = new THREE.Mesh(tupGeom, tupMat);
        tup.position.set(0, halfH + 4.8, 0);
        this.currentMeshGroup.add(tup);

        // Impact force arrow
        this.addImpactArrow(0, halfH + 8.5, halfH + 5.2, 0);

        // Camera
        this.camera.position.set(32, 22, 44);
        if (this.controls) this.controls.target.set(0, 0, 0);
    }

    // -------------------------------------------------------------
    // Mechanical Force Vector Helpers
    // -------------------------------------------------------------
    addTensionArrows(xLeft, xRight, y, z, len = 5.5) {
        const arrowMat = new THREE.MeshStandardMaterial({
            color: 0xef4444,
            metalness: 0.8,
            roughness: 0.25
        });

        // Left Arrow pointing -X (← F)
        const lShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, len, 16), arrowMat);
        lShaft.rotateZ(Math.PI / 2);
        lShaft.position.set(xLeft - len / 2, y, z);
        this.currentMeshGroup.add(lShaft);

        const lHead = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1.2, 16), arrowMat);
        lHead.rotateZ(Math.PI / 2);
        lHead.position.set(xLeft - len, y, z);
        this.currentMeshGroup.add(lHead);

        // Right Arrow pointing +X (F →)
        const rShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, len, 16), arrowMat);
        rShaft.rotateZ(Math.PI / 2);
        rShaft.position.set(xRight + len / 2, y, z);
        this.currentMeshGroup.add(rShaft);

        const rHead = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1.2, 16), arrowMat);
        rHead.rotateZ(-Math.PI / 2);
        rHead.position.set(xRight + len, y, z);
        this.currentMeshGroup.add(rHead);
    }

    addImpactArrow(x, yTop, yBottom, z) {
        const arrowMat = new THREE.MeshStandardMaterial({
            color: 0xef4444,
            metalness: 0.8,
            roughness: 0.25
        });
        const len = Math.abs(yTop - yBottom);
        const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, len, 16), arrowMat);
        shaft.position.set(x, (yTop + yBottom) / 2, z);
        this.currentMeshGroup.add(shaft);

        const head = new THREE.Mesh(new THREE.ConeGeometry(0.55, 1.2, 16), arrowMat);
        head.rotateZ(Math.PI);
        head.position.set(x, yBottom, z);
        this.currentMeshGroup.add(head);
    }

    addCompressionArrows(x, yStart, yTarget, z, colorHex = 0xef4444) {
        const arrowMat = new THREE.MeshStandardMaterial({
            color: colorHex,
            metalness: 0.8,
            roughness: 0.25
        });
        const len = Math.abs(yStart - yTarget);
        const dir = yTarget < yStart ? 1 : -1;
        const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, len, 16), arrowMat);
        shaft.position.set(x, (yStart + yTarget) / 2, z);
        this.currentMeshGroup.add(shaft);

        const head = new THREE.Mesh(new THREE.ConeGeometry(0.65, 1.3, 16), arrowMat);
        if (dir > 0) head.rotateZ(Math.PI);
        head.position.set(x, yTarget, z);
        this.currentMeshGroup.add(head);
    }

    // -------------------------------------------------------------
    // SPECIMEN 6: Flattening Test Bench (API 5L 10.2.4.3 & BOTAŞ 3.3.3)
    // ERW / HFW Borularda İki Plaka Arası Ezme Testi (Plakalar, Halka, Kaynak)
    // -------------------------------------------------------------
    buildFlatteningTest3D(pd) {
        const s = (pd && pd.input_summary) || {};
        const d = parseFloat(s.diameter_mm) || 323.9;
        const dInch = s.diameter_inch || '12"';
        const t = parseFloat(s.wall_thickness_mm) || 9.53;
        const grade = s.material_grade || 'X52';
        const psl = s.psl_level || 'PSL2';

        // e factor & H distance calculation
        let e = 0.07;
        const gUpper = String(grade).toUpperCase();
        if (gUpper.includes('80')) e = 0.04;
        else if (gUpper.includes('70')) e = 0.05;
        else if (gUpper.includes('65') || gUpper.includes('60') || gUpper.includes('56')) e = 0.06;
        else if (gUpper.includes('52') || gUpper.includes('46')) e = 0.07;
        else if (gUpper.includes('42') || gUpper.includes('B') || gUpper.includes('245') || gUpper.includes('290')) e = 0.08;

        const t_over_d = t / d;
        const H = ((1.0 + e) * t) / (e + t_over_d);
        const H_duct = 0.33 * d;
        const H_sound = 2.0 * t;

        this.updateBadge(
            'ERW / HFW Boru Yassıltma Testi (API 5L 10.2.4.3 & BOTAŞ 3.3.3)',
            `${dInch} (${d.toFixed(1)} mm) x ${t.toFixed(2)} mm • ${grade} (${psl}) • H = ${H.toFixed(2)} mm (Kaynak Testi) • 0.33D = ${H_duct.toFixed(1)} mm • 2t = ${H_sound.toFixed(1)} mm`
        );

        // Viewport scale
        const sc = 26.0 / d;
        const r0 = (d / 2.0) * sc;
        const rY = (H / 2.0) * sc;
        const rX = Math.sqrt(Math.max(rY * rY * 1.2, 2.0 * r0 * r0 - rY * rY));
        const thk = Math.max(0.75, t * sc);
        const ringDepth = Math.max(5.5, Math.min(10.0, 60.0 * sc));

        // Materials
        const steelMat = new THREE.MeshStandardMaterial({
            color: 0x94a3b8,
            metalness: 0.85,
            roughness: 0.28
        });

        const platenMat = new THREE.MeshStandardMaterial({
            color: 0x334155,
            metalness: 0.9,
            roughness: 0.35
        });

        const pistonMat = new THREE.MeshStandardMaterial({
            color: 0x64748b,
            metalness: 0.92,
            roughness: 0.2
        });

        const weldMat = new THREE.MeshStandardMaterial({
            color: 0xf59e0b,
            emissive: 0x78350f,
            metalness: 0.7,
            roughness: 0.3
        });

        const indicatorMat = new THREE.MeshBasicMaterial({
            color: 0x38bdf8
        });

        // 1. Deformed Hollow Elliptical Ring (Extruded along Z)
        const outerEllipse = new THREE.Shape();
        const ptsCount = 64;
        for (let i = 0; i <= ptsCount; i++) {
            const theta = (i / ptsCount) * Math.PI * 2;
            const x = rX * Math.cos(theta);
            const y = rY * Math.sin(theta);
            if (i === 0) outerEllipse.moveTo(x, y);
            else outerEllipse.lineTo(x, y);
        }

        const innerHole = new THREE.Path();
        const rXIn = Math.max(0.5, rX - thk);
        const rYIn = Math.max(0.5, rY - thk);
        for (let i = ptsCount; i >= 0; i--) {
            const theta = (i / ptsCount) * Math.PI * 2;
            const x = rXIn * Math.cos(theta);
            const y = rYIn * Math.sin(theta);
            if (i === ptsCount) innerHole.moveTo(x, y);
            else innerHole.lineTo(x, y);
        }
        outerEllipse.holes.push(innerHole);

        const extrudeSettings = {
            depth: ringDepth,
            bevelEnabled: true,
            bevelSegments: 2,
            bevelSize: 0.12,
            bevelThickness: 0.12
        };
        const ringGeom = new THREE.ExtrudeGeometry(outerEllipse, extrudeSettings);
        ringGeom.translate(0, 0, -ringDepth / 2);
        const ringMesh = new THREE.Mesh(ringGeom, steelMat);
        ringMesh.castShadow = true;
        ringMesh.receiveShadow = true;
        this.currentMeshGroup.add(ringMesh);

        // 2. ERW Weld Seam along ring side at 90° (Saat 9 konumu: x = -rX, y = 0)
        const weldGeom = new THREE.CylinderGeometry(thk * 0.45, thk * 0.45, ringDepth, 16);
        weldGeom.rotateX(Math.PI / 2);
        const weldMesh = new THREE.Mesh(weldGeom, weldMat);
        weldMesh.position.set(-rX + (thk * 0.2), 0, 0);
        weldMesh.castShadow = true;
        this.currentMeshGroup.add(weldMesh);

        // 3. Upper Press Platen (Üst Pres Tablası) + Hydraulic Piston
        const platenW = rX * 2.5;
        const platenT = 2.2;
        const platenD = ringDepth * 1.5;
        const upperPlatenGeom = new THREE.BoxGeometry(platenW, platenT, platenD);
        const upperPlaten = new THREE.Mesh(upperPlatenGeom, platenMat);
        upperPlaten.position.set(0, rY + platenT / 2, 0);
        upperPlaten.castShadow = true;
        upperPlaten.receiveShadow = true;
        this.currentMeshGroup.add(upperPlaten);

        // Hydraulic Cylinder Piston
        const pistonGeom = new THREE.CylinderGeometry(2.2, 2.2, 7.0, 24);
        const piston = new THREE.Mesh(pistonGeom, pistonMat);
        piston.position.set(0, rY + platenT + 3.5, 0);
        piston.castShadow = true;
        this.currentMeshGroup.add(piston);

        // Force Arrows on Upper Platen
        this.addCompressionArrows(-rX * 0.6, rY + platenT + 6.0, rY + platenT + 0.8, 0, 0xef4444);
        this.addCompressionArrows(rX * 0.6, rY + platenT + 6.0, rY + platenT + 0.8, 0, 0xef4444);

        // 4. Lower Stationary Platen (Alt Sabit Tabla)
        const lowerPlatenGeom = new THREE.BoxGeometry(platenW * 1.08, platenT * 1.3, platenD * 1.15);
        const lowerPlaten = new THREE.Mesh(lowerPlatenGeom, platenMat);
        lowerPlaten.position.set(0, -rY - (platenT * 1.3) / 2, 0);
        lowerPlaten.receiveShadow = true;
        this.currentMeshGroup.add(lowerPlaten);

        // Upward Reaction Arrows on Lower Platen
        this.addCompressionArrows(-rX * 0.6, -rY - (platenT * 1.3) - 5.0, -rY - (platenT * 1.3) - 0.5, 0, 0x3b82f6);
        this.addCompressionArrows(rX * 0.6, -rY - (platenT * 1.3) - 5.0, -rY - (platenT * 1.3) - 0.5, 0, 0x3b82f6);

        // 5. Vertical Dimension Indicator Rods for H Distance (at x = rX + 3.5)
        const dimRodX = rX + 3.5;
        const rodGeom = new THREE.CylinderGeometry(0.12, 0.12, rY * 2, 12);
        const rod = new THREE.Mesh(rodGeom, indicatorMat);
        rod.position.set(dimRodX, 0, 0);
        this.currentMeshGroup.add(rod);

        const limitCapGeom = new THREE.BoxGeometry(1.6, 0.12, 1.6);
        const capTop = new THREE.Mesh(limitCapGeom, indicatorMat);
        capTop.position.set(dimRodX, rY, 0);
        this.currentMeshGroup.add(capTop);

        const capBottom = new THREE.Mesh(limitCapGeom, indicatorMat);
        capBottom.position.set(dimRodX, -rY, 0);
        this.currentMeshGroup.add(capBottom);

        // Adjust camera for cinematic perspective
        this.camera.position.set(34, 24, 38);
        this.camera.lookAt(0, 0, 0);
        if (this.controls) this.controls.target.set(0, 0, 0);
    }

    // -------------------------------------------------------------
    // SPECIMEN 7: Pipe End Geometry & Bevel Preparation (API 5L 9.12.5 & BOTAŞ 3.3.8)
    // 30° (+5°/-0°) Bevel Angle, 1.6 ± 0.8 mm Root Face, Out-of-Squareness e <= 1.6 mm
    // -------------------------------------------------------------
    buildPipeBevel3D(pd) {
        const s = (pd && pd.input_summary) || {};
        const d = parseFloat(s.diameter_mm) || 1219.0;
        const dInch = s.diameter_inch || '48"';
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const grade = s.material_grade || "X65";
        const std = s.standard_type || "BOTAŞ";

        this.updateBadge(
            'Boru Uç Geometrisi & Kaynak Ağzı (API 5L 9.12.5 & BOTAŞ 3.3.8)',
            `Pah Açısı: 30° (+5°/-0°) • Kök Yüzeyi: 1.6 ± 0.8 mm • Uç Dikliği e ≤ 1.6 mm • ${dInch} t=${t.toFixed(2)} mm • ${grade}`
        );

        // Materials
        const steelPipeMat = new THREE.MeshStandardMaterial({
            color: 0x475569,
            metalness: 0.85,
            roughness: 0.3
        });

        const machinedBevelMat = new THREE.MeshStandardMaterial({
            color: 0xf59e0b,
            metalness: 0.95,
            roughness: 0.15,
            emissive: 0x78350f,
            emissiveIntensity: 0.35
        });

        const rootLandingMat = new THREE.MeshStandardMaterial({
            color: 0xf43f5e,
            metalness: 0.8,
            roughness: 0.25,
            emissive: 0x881337,
            emissiveIntensity: 0.3
        });

        const guideLineMat = new THREE.LineBasicMaterial({
            color: 0x38bdf8,
            linewidth: 2
        });

        // 3D Geometry Scale
        const R_out = 14.0;
        const wallT = Math.min(3.2, Math.max(1.4, t * 0.18));
        const R_in = R_out - wallT;
        const rootC = 0.38; // root landing height ~ 1.6 mm scaled
        const R_root = R_in + rootC;
        const bevelDepth = wallT - rootC;
        const axialBevelLen = bevelDepth * Math.tan(30 * Math.PI / 180); // ~ tan(30) * bevelDepth
        const pipeLen = 14.0;

        // 1. Pipe main body (Cylinder between -pipeLen and -axialBevelLen)
        const outerBodyGeom = new THREE.CylinderGeometry(R_out, R_out, pipeLen - axialBevelLen, 64, 1, true);
        const outerBody = new THREE.Mesh(outerBodyGeom, steelPipeMat);
        outerBody.position.set(0, -(pipeLen + axialBevelLen) / 2, 0);
        this.currentMeshGroup.add(outerBody);

        const innerBodyGeom = new THREE.CylinderGeometry(R_in, R_in, pipeLen, 64, 1, true);
        const innerBody = new THREE.Mesh(innerBodyGeom, steelPipeMat);
        innerBody.position.set(0, -pipeLen / 2, 0);
        this.currentMeshGroup.add(innerBody);

        // 2. Machined Bevel Conical Frustum (Pah Yüzeyi - 30°)
        const bevelGeom = new THREE.CylinderGeometry(R_root, R_out, axialBevelLen, 64, 1, true);
        const bevelMesh = new THREE.Mesh(bevelGeom, machinedBevelMat);
        bevelMesh.position.set(0, -axialBevelLen / 2, 0);
        this.currentMeshGroup.add(bevelMesh);

        // 3. Root Face Landing Ring (Düşey Alın Yüzeyi - 1.6 mm)
        const ringGeom = new THREE.RingGeometry(R_in, R_root, 64);
        const rootRing = new THREE.Mesh(ringGeom, rootLandingMat);
        rootRing.rotation.x = -Math.PI / 2;
        rootRing.position.set(0, 0, 0);
        this.currentMeshGroup.add(rootRing);

        // Back End Cap Ring (at -pipeLen)
        const backRingGeom = new THREE.RingGeometry(R_in, R_out, 64);
        const backRing = new THREE.Mesh(backRingGeom, steelPipeMat);
        backRing.rotation.x = Math.PI / 2;
        backRing.position.set(0, -pipeLen, 0);
        this.currentMeshGroup.add(backRing);

        // 4. Secondary Abutting Ghost Pipe End (Alın Alına V-Oluk Birleşimi)
        const gapY = 0.5;
        const ghostBevelGeom = new THREE.CylinderGeometry(R_out, R_root, axialBevelLen, 64, 1, true);
        const ghostBevelMat = new THREE.MeshStandardMaterial({
            color: 0x60a5fa,
            metalness: 0.7,
            roughness: 0.3,
            transparent: true,
            opacity: 0.45
        });
        const ghostBevel = new THREE.Mesh(ghostBevelGeom, ghostBevelMat);
        ghostBevel.position.set(0, gapY + axialBevelLen / 2, 0);
        this.currentMeshGroup.add(ghostBevel);

        const ghostRootRing = new THREE.Mesh(ringGeom, rootLandingMat);
        ghostRootRing.rotation.x = Math.PI / 2;
        ghostRootRing.position.set(0, gapY, 0);
        this.currentMeshGroup.add(ghostRootRing);

        // 5. 3D Angle Indicator Arc & Dimension Rods
        const sqPoints = [
            new THREE.Vector3(R_out + 1.5, 0, 0),
            new THREE.Vector3(R_out + 1.5, -axialBevelLen, 0),
            new THREE.Vector3(R_out - 0.5, -axialBevelLen, 0)
        ];
        const sqGeom = new THREE.BufferGeometry().setFromPoints(sqPoints);
        const sqLine = new THREE.Line(sqGeom, guideLineMat);
        this.currentMeshGroup.add(sqLine);

        // Circular bevel angle indicator rod
        const arcGeom = new THREE.TorusGeometry(R_out + 0.2, 0.08, 8, 48, Math.PI / 4);
        const arcMesh = new THREE.Mesh(arcGeom, machinedBevelMat);
        arcMesh.rotation.x = Math.PI / 2;
        arcMesh.position.set(0, -axialBevelLen, 0);
        this.currentMeshGroup.add(arcMesh);

        // Adjust camera for isometric rim view
        this.camera.position.set(22, 16, 28);
        this.camera.lookAt(0, -2, 0);
        if (this.controls) this.controls.target.set(0, -2, 0);
    }

    // -------------------------------------------------------------
    // SPECIMEN 10: Pipe Straightness, Camber & End Straightness (API 5L 9.11.3 & BOTAŞ 5.5, 8.1.2.4)
    // -------------------------------------------------------------
    buildPipeStraightness3D(pd) {
        const s = (pd && pd.input_summary) || {};
        const d = parseFloat(s.diameter_mm) || 1219.0;
        const dInch = s.diameter_inch || '48"';
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const l_m = parseFloat(s.pipe_length_m) || 12.0;
        const grade = s.material_grade || 'X65';
        const std = s.standard_type || 'BOTAŞ';
        const isBotas = String(std).toUpperCase().includes('BOTAŞ') || String(std).toUpperCase().includes('BOTAS');

        const ratioPct = isBotas ? 0.15 : 0.20;
        const totLimitMm = ((ratioPct / 100.0) * l_m * 1000.0).toFixed(1);
        const endLimitMm = isBotas ? 3.0 : 4.0;

        this.updateBadge(
            'Boru Düzlük ve Uç Sapması (API 5L 9.11.3 & BOTAŞ 5.5, 8.1.2.4)',
            `${dInch} (OD ${d.toFixed(1)} mm) • t = ${t.toFixed(2)} mm • L = ${l_m.toFixed(1)} m • ${grade} • Maks. Sehim: ≤ ${totLimitMm} mm (%${ratioPct} × L) • Uç Sapma: ≤ ${endLimitMm.toFixed(1)} mm`
        );

        // Visual proportions
        const L_viz = 34.0;
        const R_out = 2.4;
        const maxBowY = 1.6;

        // 1. Deflected Pipe Body (Curved Tube Geometry)
        const curvePoints = [];
        const numSegments = 40;
        for (let i = 0; i <= numSegments; i++) {
            const u = i / numSegments;
            const x = -L_viz / 2.0 + u * L_viz;
            const y = 4.0 * maxBowY * u * (1.0 - u);
            curvePoints.push(new THREE.Vector3(x, y, 0));
        }
        const pipeCurve = new THREE.CatmullRomCurve3(curvePoints);
        const tubeGeom = new THREE.TubeGeometry(pipeCurve, 64, R_out, 32, false);

        const steelPipeMat = new THREE.MeshStandardMaterial({
            color: 0x475569,
            metalness: 0.85,
            roughness: 0.25,
            side: THREE.DoubleSide
        });
        const pipeMesh = new THREE.Mesh(tubeGeom, steelPipeMat);
        this.currentMeshGroup.add(pipeMesh);

        // 2. Optical Laser Collimator / Taut Wire Reference Datum Beam
        const laserGeom = new THREE.CylinderGeometry(0.12, 0.12, L_viz + 4.0, 16);
        const laserMat = new THREE.MeshBasicMaterial({
            color: 0x10b981,
            transparent: true,
            opacity: 0.95
        });
        const laserBeam = new THREE.Mesh(laserGeom, laserMat);
        laserBeam.rotation.z = Math.PI / 2;
        laserBeam.position.set(0, 0, 0);
        this.currentMeshGroup.add(laserBeam);

        // Laser emitters
        const emitterGeom = new THREE.CylinderGeometry(0.6, 0.6, 1.2, 16);
        const emitterMat = new THREE.MeshStandardMaterial({
            color: 0x059669,
            metalness: 0.9,
            roughness: 0.2
        });
        const leftEmitter = new THREE.Mesh(emitterGeom, emitterMat);
        leftEmitter.rotation.z = Math.PI / 2;
        leftEmitter.position.set(-L_viz / 2 - 2, 0, 0);
        this.currentMeshGroup.add(leftEmitter);

        const rightEmitter = new THREE.Mesh(emitterGeom, emitterMat);
        rightEmitter.rotation.z = Math.PI / 2;
        rightEmitter.position.set(L_viz / 2 + 2, 0, 0);
        this.currentMeshGroup.add(rightEmitter);

        // 3. Mid-Span Sagitta Deflection Indicator Rod
        const midRodGeom = new THREE.CylinderGeometry(0.15, 0.15, maxBowY, 16);
        const midRodMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
        const midRod = new THREE.Mesh(midRodGeom, midRodMat);
        midRod.position.set(0, maxBowY / 2, 0);
        this.currentMeshGroup.add(midRod);

        const sphGeom = new THREE.SphereGeometry(0.3, 16, 16);
        const apexSph = new THREE.Mesh(sphGeom, midRodMat);
        apexSph.position.set(0, maxBowY, 0);
        this.currentMeshGroup.add(apexSph);

        // 4. End Chord Gauges (1.0 m Straight Edge - Hassas Çelik Mastarlar)
        const chordLenViz = (1.0 / l_m) * L_viz;
        const mastarGeom = new THREE.BoxGeometry(chordLenViz, 0.35, 0.6);
        const mastarMat = new THREE.MeshStandardMaterial({
            color: 0x0284c7,
            metalness: 0.8,
            roughness: 0.2
        });

        const leftMastar = new THREE.Mesh(mastarGeom, mastarMat);
        leftMastar.position.set(-L_viz / 2 + chordLenViz / 2, R_out + 0.6, 0);
        this.currentMeshGroup.add(leftMastar);

        const rightMastar = new THREE.Mesh(mastarGeom, mastarMat);
        rightMastar.position.set(L_viz / 2 - chordLenViz / 2, R_out + 0.6, 0);
        this.currentMeshGroup.add(rightMastar);

        // 5. 7 Inspection Station Marker Rings
        const stationsU = [0.0, 1.0 / l_m, 0.25, 0.50, 0.75, (l_m - 1.0) / l_m, 1.0];
        stationsU.forEach((u, idx) => {
            const x = -L_viz / 2.0 + u * L_viz;
            const y = 4.0 * maxBowY * u * (1.0 - u);
            const stSphGeom = new THREE.SphereGeometry(idx === 3 ? 0.35 : 0.2, 12, 12);
            const stSphMat = new THREE.MeshBasicMaterial({
                color: idx === 3 ? 0xef4444 : (idx === 1 || idx === 5 ? 0x38bdf8 : 0x94a3b8)
            });
            const stMarker = new THREE.Mesh(stSphGeom, stSphMat);
            stMarker.position.set(x, y + R_out + 0.1, 0);
            this.currentMeshGroup.add(stMarker);
        });

        // Panoramic camera
        this.camera.position.set(0, 12, 38);
        this.camera.lookAt(0, maxBowY / 2, 0);
        if (this.controls) this.controls.target.set(0, maxBowY / 2, 0);
    }

    buildGenericBlock(key) {
        this.updateBadge('Numune Çizimi', key);
        const geom = new THREE.BoxGeometry(20, 10, 10);
        const mat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, metalness: 0.8, roughness: 0.3 });
        const mesh = new THREE.Mesh(geom, mat);
        this.currentMeshGroup.add(mesh);
    }

    // -------------------------------------------------------------
    // Lifecycle & Loop
    // -------------------------------------------------------------
    animate() {
        this.animId = requestAnimationFrame(() => this.animate());

        if (this.controls) {
            this.controls.update();
        }

        if (this.autoRotate && this.currentMeshGroup) {
            this.currentMeshGroup.rotation.y += 0.008;
        }

        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    onWindowResize() {
        if (!this.container || !this.renderer || !this.camera) return;
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        if (width === 0 || height === 0) return;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    disposeGroup(group) {
        if (!group) return;
        group.traverse((obj) => {
            if (obj.isMesh) {
                if (obj.geometry) obj.geometry.dispose();
                if (obj.material) {
                    if (Array.isArray(obj.material)) {
                        obj.material.forEach(m => m.dispose());
                    } else {
                        obj.material.dispose();
                    }
                }
            }
        });
    }

    dispose() {
        window.removeEventListener('resize', this.onResizeBound);

        if (this.animId) {
            cancelAnimationFrame(this.animId);
            this.animId = null;
        }

        if (this.currentMeshGroup) {
            this.disposeGroup(this.currentMeshGroup);
            this.currentMeshGroup = null;
        }

        if (this.renderer) {
            this.renderer.dispose();
            if (this.renderer.domElement && this.renderer.domElement.parentNode) {
                this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            }
            this.renderer = null;
        }

        this.scene = null;
        this.camera = null;
        this.controls = null;

        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Global visualizer instance for modals
window._specimenVisualizer3D = null;
