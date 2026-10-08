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
            `Boru Gövdesi (Kaynaksız) • W = 38,1 mm • G = 50,0 mm • R ≥ 25 mm • t = ${t.toFixed(2)} mm • ${grade}`
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

        // Construct 2D Dog-Bone profile in X-Y plane
        const shape = new THREE.Shape();
        shape.moveTo(-halfL, halfC);
        shape.lineTo(-xGrip, halfC);
        shape.bezierCurveTo(-9.5, halfC, -7.5, halfW, -halfA, halfW); // R >= 25 mm fillet
        shape.lineTo(halfA, halfW);
        shape.bezierCurveTo(7.5, halfW, 9.5, halfC, xGrip, halfC);   // R >= 25 mm fillet
        shape.lineTo(halfL, halfC);
        shape.lineTo(halfL, -halfC);
        shape.lineTo(xGrip, -halfC);
        shape.bezierCurveTo(9.5, -halfC, 7.5, -halfW, halfA, -halfW);
        shape.lineTo(-halfA, -halfW);
        shape.bezierCurveTo(-7.5, -halfW, -9.5, -halfC, -xGrip, -halfC);
        shape.lineTo(-halfL, -halfC);
        shape.closePath();

        const extrudeSettings = {
            depth: thk,
            bevelEnabled: true,
            bevelSegments: 2,
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
