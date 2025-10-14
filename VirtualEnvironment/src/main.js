import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { Reflector } from 'three/examples/jsm/objects/Reflector.js';

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
renderer.physicallyCorrectLights = true;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.5;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// 🌤️ Balanced Lighting Setup
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const hemisphereLight = new THREE.HemisphereLight(0xddeeff, 0x202020, 1.0);
scene.add(hemisphereLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
keyLight.position.set(8, 10, 5);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(4096, 4096);
keyLight.shadow.camera.near = 0.5;
keyLight.shadow.camera.far = 50;
keyLight.shadow.camera.left = -15;
keyLight.shadow.camera.right = 15;
keyLight.shadow.camera.top = 15;
keyLight.shadow.camera.bottom = -15;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xfff8e1, 0.8);
fillLight.position.set(-5, 5, -8);
scene.add(fillLight);

const rimLight = new THREE.PointLight(0xffffff, 0.4, 30);
rimLight.position.set(0, 5, 5);
scene.add(rimLight);

const lampLight = new THREE.PointLight(0xffd580, 1.2, 8);
lampLight.position.set(-4.3, 3.0, 4.6);
lampLight.castShadow = true;
scene.add(lampLight);

// Room
const room = new THREE.Group();
scene.add(room);

// Floor
const floorGeometry = new THREE.PlaneGeometry(10, 10);
const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xD2B48C, roughness: 0.7, metalness: 0 });
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
room.add(floor);

// Walls
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
  chest.position.set(0.8, 0.15, -4.2);
  setShadows(chest);
  room.add(chest);
});

// Mirror with reflection
gltfLoader.load('models/mirror.glb', (gltf) => {
  const mirror = gltf.scene;
  mirror.scale.set(1.8, 1.8, 1.8);
  mirror.position.set(0.8, 2.5, -4.95);
  mirror.rotation.y = Math.PI / 2;
  setShadows(mirror);

  mirror.traverse((child) => {
    if (child.isMesh) {
      const geometry = child.geometry;
      const reflectiveSurface = new Reflector(geometry, {
        clipBias: 0.003,
        textureWidth: window.innerWidth * window.devicePixelRatio,
        textureHeight: window.innerHeight * window.devicePixelRatio,
        color: 0x888888,
      });
      reflectiveSurface.position.copy(child.position);
      reflectiveSurface.rotation.copy(child.rotation);
      reflectiveSurface.scale.copy(child.scale);
      child.parent.add(reflectiveSurface);
      child.visible = false;
    }
  });

  room.add(mirror);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
  const shelf = gltf.scene;
  shelf.scale.set(0.25, 0.25, 0.25);
  shelf.position.set(0.8, 2.6, -4.5);
  // setShadows(shelf);
  room.add(shelf);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
  const shelf = gltf.scene;
  shelf.scale.set(0.25, 0.25, 0.25);
  shelf.position.set(0.8, 3.3, -4.5);
  // setShadows(shelf);
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
  windowModel.position.set(6.3, 0.5, -2.5);
  windowModel.rotation.y = degreesToRadians(270);
  setShadows(windowModel);
  room.add(windowModel);
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
  frame.rotation.y = Math.PI / 2;
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

gltfLoader.load('models/clock.glb', (gltf) => {
  const clock = gltf.scene;
  clock.scale.set(1.2, 1.2, 1.2);
  clock.position.set(-5, 4, -2.6);
  setShadows(clock);
  room.add(clock);
});

gltfLoader.load('models/books.glb', (gltf) => {
  const books = gltf.scene;
  books.scale.set(0.3, 0.3, 0.3);
  books.position.set(0.1, 4, -4.5);
  books.rotation.y = -Math.PI / 2;
  // setShadows(books);
  room.add(books);
});

gltfLoader.load('models/books.glb', (gltf) => {
  const books = gltf.scene;
  books.scale.set(0.3, 0.3, 0.3);
  books.position.set(1.5, 3.3, -4.5);
  books.rotation.y = -Math.PI / 2;
  // setShadows(books);
  room.add(books);
});

gltfLoader.load('models/small_plant.glb', (gltf) => {
  const small_plant = gltf.scene;
  small_plant.scale.set(2, 2, 2);
  small_plant.position.set(-0.1, 3.4, -4.5);
  // setShadows(small_plant);
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
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});
