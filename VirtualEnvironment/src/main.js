import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

function degreesToRadians(degrees) {
  return degrees * (Math.PI / 180);
}

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xC8E6C9);

// Camera
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(5, 5, 5);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
// Enable physically correct lighting and shadows
renderer.physicallyCorrectLights = true;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Lighting
// HemisphereLight for a soft ambient light from above and below
const hemisphereLight = new THREE.HemisphereLight(0xffeeb1, 0x080820, 1.5);
scene.add(hemisphereLight);

// DirectionalLight to simulate a main light source like the sun through a window
const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
directionalLight.position.set(10, 10, 10);
directionalLight.castShadow = true;
// Configure shadow properties for the directional light
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 50;
directionalLight.shadow.camera.left = -10;
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
scene.add(directionalLight);

// PointLight for a warmer, localized light source
const pointLight = new THREE.PointLight(0xff9000, 1, 10, 2);
pointLight.position.set(-5, 5, 2.5);
pointLight.castShadow = true;
scene.add(pointLight);


// Room
const room = new THREE.Group();
scene.add(room);

// Floor
const floorGeometry = new THREE.PlaneGeometry(10, 10);
// --- UPDATED FLOOR COLOR ---
// Switched to a lighter tan/brown color
const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xD2B48C, roughness: 0.7, metalness: 0 });
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
// Set receiveShadow to false to prevent shadows from appearing on the floor
floor.receiveShadow = false;
room.add(floor);

// Walls
// --- UPDATED WALL COLOR ---
// Switched to a pleasant, muted sage green
const wallMaterial = new THREE.MeshStandardMaterial({ color: 0x4F604D, roughness: 0.8, metalness: 0 });

const wall1 = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), wallMaterial);
wall1.position.set(0, 2.5, -5);
wall1.receiveShadow = true;
room.add(wall1);

const wall2 = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), wallMaterial);
wall2.position.set(-5, 2.5, 0);
wall2.rotation.y = Math.PI / 2;
wall2.receiveShadow = true;
room.add(wall2);

// GLTF Loader
const gltfLoader = new GLTFLoader();

const setShadows = (object) => {
    object.traverse((child) => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });
};

// Load Models
gltfLoader.load('models/desk.glb', (gltf) => {
  const desk = gltf.scene;
  desk.scale.set(0.5, 0.5, 0.5);
  desk.position.set(-2.7, 1.7, -3.7);
  setShadows(desk);
  room.add(desk);
});

gltfLoader.load('models/chair.glb', (gltf) => {
  const chair = gltf.scene;
  chair.scale.set(2.5,2.5, 2.5);
  chair.position.set(2.7, 0.05, -4.4);
  chair.rotation.y = Math.PI;
  setShadows(chair);
  room.add(chair);
});

gltfLoader.load('models/computer.glb', (gltf) => {
  const computer = gltf.scene;
  computer.scale.set(0.0004, 0.0004, 0.0004);
  computer.position.set(-3, 1.8, -4);
  setShadows(computer);
  room.add(computer);
});

gltfLoader.load('models/bed.glb', (gltf) => {
  const bed = gltf.scene;
  bed.scale.set(2.5,2.5,2.5);
  bed.position.set(-1.8, 0.3, 2);
  bed.rotation.y = Math.PI/2;
  setShadows(bed);
  room.add(bed);
});

gltfLoader.load('models/lamp.glb', (gltf) => {
  const lamp = gltf.scene;
  lamp.scale.set(0.015, 0.015, 0.015);
  lamp.position.set(-4.3, 0, 4.6);
  setShadows(lamp);
  room.add(lamp);
});

gltfLoader.load('models/chest.glb', (gltf) => {
  const chest = gltf.scene;
  chest.scale.set(2.2, 2.2, 2.2);
  chest.position.set(0.8, 0.15, -4.2);
  setShadows(chest);
  room.add(chest);
});

gltfLoader.load('models/mirror.glb', (gltf) => {
  const mirror = gltf.scene;
  mirror.scale.set(1.8, 1.8, 1.8);
  mirror.position.set(0.8, 2.5, -4.95);
  mirror.rotation.y = Math.PI/2;
  setShadows(mirror);
  room.add(mirror);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
    const shelf = gltf.scene;
    shelf.scale.set(0.25, 0.25, 0.25);
    shelf.position.set(0.8, 2.6, -4.5);
    setShadows(shelf);
    room.add(shelf);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
    const shelf = gltf.scene;
    shelf.scale.set(0.25, 0.25, 0.25);
    shelf.position.set(0.8, 3.3, -4.5);
    setShadows(shelf);
    room.add(shelf);
});

gltfLoader.load('models/indoor_plant.glb', (gltf) => {
    const indoor_plant = gltf.scene;
    indoor_plant.scale.set(0.3, 0.3, 0.3);
    indoor_plant.position.set(2.2, 0.15, -4.2);
    setShadows(indoor_plant);
    room.add(indoor_plant);
});



gltfLoader.load('models/window.glb', (gltf) => {
    const window = gltf.scene;
    window.scale.set(0.04, 0.04, 0.04);
    window.position.set(6.3, 0.5, -2.5);
     const angleInDegrees = 270;
    window.rotation.y = degreesToRadians(angleInDegrees);
    setShadows(window);
    room.add(window);
});

gltfLoader.load('models/carpet.glb', (gltf) => {
    const carpet = gltf.scene;
    carpet.scale.set(2.5, 2.5, 2.5);
    carpet.position.set(1, -0.1, 2);
    setShadows(carpet);
    room.add(carpet);
});

gltfLoader.load('models/frame.glb', (gltf) => {
    const frame = gltf.scene;
    frame.scale.set(1, 1, 1);
    frame.position.set(-5, 2, 1.9);
    frame.rotation.y = Math.PI/2;
    setShadows(frame);
    room.add(frame);
});

gltfLoader.load('models/dog_bed.glb', (gltf) => {
    const dog_bed = gltf.scene;
    dog_bed.scale.set(1.2, 1.2, 1.2);
    dog_bed.position.set(3.9, 0.23, -4);
    setShadows(dog_bed);
    room.add(dog_bed);
});

// Animation
const tick = () => {
  controls.update();
  renderer.render(scene, camera);
  window.requestAnimationFrame(tick);
};

tick();

// Handle window resizing
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});