import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Reflector } from 'three/examples/jsm/objects/Reflector.js';
import { RectAreaLightUniformsLib } from 'three/examples/jsm/lights/RectAreaLightUniformsLib.js';
import { RectAreaLightHelper } from 'three/examples/jsm/helpers/RectAreaLightHelper.js';

function degreesToRadians(degrees) {
  return degrees * (Math.PI / 180);
}

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xC8E6C9);

// ✨ CHANGED: Replaced PerspectiveCamera with OrthographicCamera for a true isometric view
const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 15; // This value controls the "zoom" level. Increase to zoom out, decrease to zoom in.
const camera = new THREE.OrthographicCamera(
  frustumSize * aspect / -2,
  frustumSize * aspect / 2,
  frustumSize / 2,
  frustumSize / -2,
  0.1,
  100 // Clipping plane can be closer for orthographic cameras
);
camera.position.set(10, 10, 10); // The perfect 45-degree angle for an isometric view
camera.lookAt(0, 0, 0); // Look at the very center of the scene floor

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.physicallyCorrectLights = true;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.5;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Initialize RectAreaLight
RectAreaLightUniformsLib.init();

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
// ✨ CHANGED: Set the orbit controls target to the center of the floor to match the camera
controls.target.set(0, 0, 0);

// ✨ NEW: Limit camera rotation and disable panning
controls.maxPolarAngle = Math.PI / 2; // Prevent camera from going below the floor.
controls.minPolarAngle = 0; // Prevent camera from going directly overhead
controls.enablePan = false; // Disable panning to keep the scene centered.
controls.update(); // This is crucial to apply the new target immediately


// 🌤️ Final Natural Lighting Setup
const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(ambientLight);
const hemisphereLight = new THREE.HemisphereLight(0xddeeff, 0x202020, 0.8);
scene.add(hemisphereLight);
const ceilingLight = new THREE.PointLight(0xfff5e1, 1.5, 20, 1.5);
ceilingLight.position.set(0, 4.8, 0);
ceilingLight.castShadow = true;
ceilingLight.shadow.mapSize.set(2048, 2048);
ceilingLight.shadow.bias = -0.0001;
scene.add(ceilingLight);

// ==================================================================
// ✨ NEW LAMP LIGHTING ✨
// ==================================================================
const lampBulbPosition = new THREE.Vector3(-4.3, -0.5, 4.6);

const lampSpotlight = new THREE.SpotLight(0xffd580, 3, 10, Math.PI * 0.15, 0.3, 1.5);
lampSpotlight.position.copy(lampBulbPosition);
lampSpotlight.target.position.set(lampBulbPosition.x, 0, lampBulbPosition.z);
lampSpotlight.castShadow = true;
lampSpotlight.shadow.mapSize.width = 1024;
lampSpotlight.shadow.mapSize.height = 1024;
lampSpotlight.shadow.camera.near = 0.5;
lampSpotlight.shadow.camera.far = 10;
lampSpotlight.shadow.bias = -0.001;
scene.add(lampSpotlight);
scene.add(lampSpotlight.target);

const lampGlow = new THREE.PointLight(0xffd580, 1.6, 4);
lampGlow.position.copy(lampBulbPosition);
scene.add(lampGlow);
// ==================================================================

const windowLight = new THREE.RectAreaLight(0xaaccff, 1, 4, 5);
windowLight.position.set(6, 2.5, -2.5);
windowLight.lookAt(-5, 2.5, -2.5);
scene.add(windowLight);
const plantSpotlight = new THREE.SpotLight(0xccffcc, 4, 12, Math.PI * 0.15, 0.6, 1);
plantSpotlight.position.set(3.5, 5, -2.5);
plantSpotlight.target.position.set(2.2, 0.15, -4.2);
scene.add(plantSpotlight);
scene.add(plantSpotlight.target);

// Room
const room = new THREE.Group();
scene.add(room);


// ==================================================================
// ✨ DIORAMA BOX STYLE - WALLS AND FLOOR ✨
// ==================================================================

const WALL_THICKNESS = 0.3; // Kept your original thickness
const ROOM_SIZE = 10;
const ROOM_HEIGHT = 5;

// ✨ NEW: Move the entire room group down to vertically center it in the view
room.position.y = -ROOM_HEIGHT / 2;


// Brown material for outer edges/sides
const brownEdgeMaterial = new THREE.MeshStandardMaterial({
    color: 0x8B4513,
    roughness: 0.7,
    metalness: 0
});

// Setup texture loader
const textureLoader = new THREE.TextureLoader();

// Load wood floor textures
const colorTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_Color.jpg');
const roughnessTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_Roughness.jpg');
const normalTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_NormalGL.jpg');
const aoTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_AmbientOcclusion.jpg');

const textures = [colorTexture, roughnessTexture, normalTexture, aoTexture];
textures.forEach(texture => {
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(0.5, 0.5);
    texture.center.set(0.5, 0.5);
    texture.rotation = Math.PI / 2;
});

// Floor material (wood texture on top)
const floorTopMaterial = new THREE.MeshStandardMaterial({
    color: 0xbbbbbb,
    map: colorTexture,
    roughnessMap: roughnessTexture,
    normalMap: normalTexture,
    aoMap: aoTexture,
    aoMapIntensity: 1,
});

// Wall inner material (green)
const wallInnerMaterial = new THREE.MeshStandardMaterial({
    color: 0x4F604D,
    roughness: 0.8,
    metalness: 0
});

// ==================================================================
// FLOOR - Box with brown edges and wood top
// ==================================================================
const floorGeometry = new THREE.BoxGeometry(ROOM_SIZE, WALL_THICKNESS, ROOM_SIZE);
floorGeometry.setAttribute('uv2', new THREE.BufferAttribute(floorGeometry.attributes.uv.array, 2));

// Create materials array: [right, left, top, bottom, front, back]
const floorMaterials = [
    brownEdgeMaterial, // right
    brownEdgeMaterial, // left
    floorTopMaterial,  // top (wood texture)
    brownEdgeMaterial, // bottom (brown)
    brownEdgeMaterial, // front
    brownEdgeMaterial  // back
];

const floor = new THREE.Mesh(floorGeometry, floorMaterials);
floor.position.set(0, 0, 0);
floor.receiveShadow = true;
floor.castShadow = true;
room.add(floor);

// ==================================================================
// BACK WALL - Box with brown edges
// ==================================================================
const backWallGeometry = new THREE.BoxGeometry(ROOM_SIZE, ROOM_HEIGHT, WALL_THICKNESS);

// [right, left, top, bottom, front(inside-green), back(outside-brown)]
const backWallMaterials = [
    brownEdgeMaterial,   // right edge
    brownEdgeMaterial,   // left edge
    brownEdgeMaterial,   // top edge
    brownEdgeMaterial,   // bottom edge (connects to floor)
    wallInnerMaterial,   // front (inside - green)
    brownEdgeMaterial    // back (outside - brown)
];

const backWall = new THREE.Mesh(backWallGeometry, backWallMaterials);
backWall.position.set(0, ROOM_HEIGHT / 2, -ROOM_SIZE / 2 + WALL_THICKNESS / 2);
backWall.receiveShadow = true;
backWall.castShadow = true;
room.add(backWall);

// ==================================================================
// LEFT WALL - Box with brown edges
// ==================================================================
const leftWallGeometry = new THREE.BoxGeometry(WALL_THICKNESS, ROOM_HEIGHT, ROOM_SIZE);

// [right(inside-green), left(outside-brown), top, bottom, front, back]
const leftWallMaterials = [
    wallInnerMaterial,   // right (inside - green)
    brownEdgeMaterial,   // left (outside - brown)
    brownEdgeMaterial,   // top edge
    brownEdgeMaterial,   // bottom edge
    brownEdgeMaterial,   // front edge
    brownEdgeMaterial    // back edge
];

const leftWall = new THREE.Mesh(leftWallGeometry, leftWallMaterials);
leftWall.position.set(-ROOM_SIZE / 2 + WALL_THICKNESS / 2, ROOM_HEIGHT / 2, 0);
leftWall.receiveShadow = true;
leftWall.castShadow = true;
room.add(leftWall);

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

// Load Models (All positions remain unchanged)
gltfLoader.load('models/desk.glb', (gltf) => {
  const desk = gltf.scene;
  desk.scale.set(0.5, 0.5, 0.5);
  desk.position.set(-2.7, 1.7, -3.7);
  setShadows(desk);
  room.add(desk);
});

gltfLoader.load('models/chair.glb', (gltf) => {
  const chair = gltf.scene;
  chair.scale.set(2.5, 2.5, 2.5);
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
  bed.scale.set(2.5, 2.5, 2.5);
  bed.position.set(-1.8, 0.3, 2);
  bed.rotation.y = Math.PI / 2;
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
  chest.position.set(0.8, 0.15, -4);
  setShadows(chest);
  room.add(chest);
});

// Mirror with reflection
gltfLoader.load('models/mirror.glb', (gltf) => {
  const mirror = gltf.scene;
  mirror.scale.set(1.8, 1.8, 1.8);
  mirror.position.set(0.8, 2.5, -4.65);
  mirror.rotation.y = Math.PI / 2;
  setShadows(mirror);

  mirror.traverse((child) => {
    if (child.isMesh) {
      const reflectiveSurface = new Reflector(child.geometry, {
        clipBias: 0.003,
        textureWidth: window.innerWidth * window.devicePixelRatio,
        textureHeight: window.innerHeight * window.devicePixelRatio,
        color: 0x888888,
      });
      reflectiveSurface.position.copy(child.position);
      reflectiveSurface.rotation.copy(child.rotation);
      reflectiveSurface.scale.copy(child.scale);
      reflectiveSurface.receiveShadow = false;
      child.parent.add(reflectiveSurface);
      child.visible = false;
    }
  });

  room.add(mirror);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
  const shelf = gltf.scene;
  shelf.scale.set(0.25, 0.25, 0.25);
  shelf.position.set(0.8, 2.6, -4.2);
  room.add(shelf);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
  const shelf = gltf.scene;
  shelf.scale.set(0.25, 0.25, 0.25);
  shelf.position.set(0.8, 3.3, -4.2);
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
  const windowModel = gltf.scene;
  windowModel.scale.set(0.04, 0.04, 0.04);
  windowModel.position.set(6.3, 0.5, -2.3);
  windowModel.rotation.y = degreesToRadians(270);
  setShadows(windowModel);
  room.add(windowModel);
});

gltfLoader.load('models/carpet.glb', (gltf) => {
  const carpet = gltf.scene;
  carpet.scale.set(2.5, 2.5, 2.5);
  carpet.position.set(1, 0.05, 2);
  setShadows(carpet);
  room.add(carpet);
});

gltfLoader.load('models/frame.glb', (gltf) => {
  const frame = gltf.scene;
  frame.scale.set(1, 1, 1);
  frame.position.set(-4.7, 2, 1.9);
  frame.rotation.y = Math.PI / 2;
  setShadows(frame);
  room.add(frame);
});

gltfLoader.load('models/dog_bed.glb', (gltf) => {
  const dog_bed = gltf.scene;
  dog_bed.scale.set(1.2, 1.2, 1.2);
  dog_bed.position.set(3.9, 0.23, -3.6);
  setShadows(dog_bed);
  room.add(dog_bed);
});

gltfLoader.load('models/clock.glb', (gltf) => {
  const clock = gltf.scene;
  clock.scale.set(1.2, 1.2, 1.2);
  clock.position.set(-4.65, 4, -2.6);
  setShadows(clock);
  room.add(clock);
});

gltfLoader.load('models/books.glb', (gltf) => {
  const books = gltf.scene;
  books.scale.set(0.3, 0.3, 0.3);
  books.position.set(0.1, 4, -4.5);
  books.rotation.y = -Math.PI / 2;
  room.add(books);
});

gltfLoader.load('models/books.glb', (gltf) => {
  const books = gltf.scene;
  books.scale.set(0.3, 0.3, 0.3);
  books.position.set(1.5, 3.3, -4.5);
  books.rotation.y = -Math.PI / 2;
  room.add(books);
});

gltfLoader.load('models/small_plant.glb', (gltf) => {
  const small_plant = gltf.scene;
  small_plant.scale.set(2, 2, 2);
  small_plant.position.set(-0.1, 3.4, -4.5);
  room.add(small_plant);
});

// Animation Loop
const tick = () => {
  controls.update();
  renderer.render(scene, camera);
  window.requestAnimationFrame(tick);
};
tick();

// Resize Handling
// ✨ CHANGED: The resize handler must be updated to work with an OrthographicCamera
window.addEventListener('resize', () => {
  const aspect = window.innerWidth / window.innerHeight;
  camera.left = frustumSize * aspect / -2;
  camera.right = frustumSize * aspect / 2;
  camera.top = frustumSize / 2;
  camera.bottom = frustumSize / -2;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});