import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

function degreesToRadians(degrees) {
  return degrees * (Math.PI / 180);
}

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffc0cb);

// Camera
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(5, 5, 5);

// Renderer
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(5, 10, 7.5);
scene.add(directionalLight);

const pointLight = new THREE.PointLight(0xffffff, 0.5);
pointLight.position.set(-5, 5, 2.5);
scene.add(pointLight);

// Room
const room = new THREE.Group();
scene.add(room);

// Floor
const floorGeometry = new THREE.PlaneGeometry(10, 10);
const floorMaterial = new THREE.MeshStandardMaterial({ color: 0xffe0bd });
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
room.add(floor);

// Walls
const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xfde2e2 });

const wall1 = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), wallMaterial);
wall1.position.set(0, 2.5, -5);
room.add(wall1);

const wall2 = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), wallMaterial);
wall2.position.set(-5, 2.5, 0);
wall2.rotation.y = Math.PI / 2;
room.add(wall2);

// GLTF Loader
const gltfLoader = new GLTFLoader();

// Load Models
gltfLoader.load('models/desk.glb', (gltf) => {
  const desk = gltf.scene;
  desk.scale.set(0.5, 0.5, 0.5);
  desk.position.set(-2.7, 1.7, -3.7);
  room.add(desk);
});

gltfLoader.load('models/chair.glb', (gltf) => {
  const chair = gltf.scene;
  chair.scale.set(2.5,2.5, 2.5);
  chair.position.set(2.7, 0.05, -4.4);
  chair.rotation.y = Math.PI;
  room.add(chair);
});

gltfLoader.load('models/computer.glb', (gltf) => {
  const computer = gltf.scene;
  // Make the model much smaller
  computer.scale.set(0.0004, 0.0004, 0.0004); 

  // Increased the Y-position to lift the smaller model onto the desk
  computer.position.set(-3, 1.8, -4);  
  // You might need to adjust the position after resizing
  room.add(computer);
});

gltfLoader.load('models/bed.glb', (gltf) => {
  const bed = gltf.scene;
  bed.scale.set(2.5,2.5,2.5);
  bed.position.set(-1.8, 0.3, 2);
  bed.rotation.y = Math.PI/2;
  room.add(bed);
});

gltfLoader.load('models/lamp.glb', (gltf) => {
  const lamp = gltf.scene;
  lamp.scale.set(0.015, 0.015, 0.015);
  lamp.position.set(-4.3, 0, 4.6);
  room.add(lamp);
});

gltfLoader.load('models/chest.glb', (gltf) => {
  const chest = gltf.scene;
  chest.scale.set(2.2, 2.2, 2.2);
  chest.position.set(0.8, 0.15, -4.2);
  room.add(chest);
});

gltfLoader.load('models/mirror.glb', (gltf) => {
  const mirror = gltf.scene;
  mirror.scale.set(1.8, 1.8, 1.8);
  mirror.position.set(0.8, 2.5, -4.95);
  mirror.rotation.y = Math.PI/2;
  room.add(mirror);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
    const shelf = gltf.scene;
    shelf.scale.set(0.25, 0.25, 0.25);
    shelf.position.set(0.8, 2.6, -4.5);
    room.add(shelf);
});

gltfLoader.load('models/shelf.glb', (gltf) => {
    const shelf = gltf.scene;
    shelf.scale.set(0.25, 0.25, 0.25);
    shelf.position.set(0.8, 3.3, -4.5);
    room.add(shelf);
});

gltfLoader.load('models/indoor_plant.glb', (gltf) => {
    const indoor_plant = gltf.scene;
    indoor_plant.scale.set(0.3, 0.3, 0.3);
    indoor_plant.position.set(2.2, 0.15, -4.2);
    room.add(indoor_plant);
});



gltfLoader.load('models/window.glb', (gltf) => {
    const window = gltf.scene;
    window.scale.set(0.04, 0.04, 0.04);
    window.position.set(6.3, 0.5, -2.5);
     const angleInDegrees = 270;
    window.rotation.y = degreesToRadians(angleInDegrees);
    room.add(window);
});

gltfLoader.load('models/carpet.glb', (gltf) => {
    const carpet = gltf.scene;
    carpet.scale.set(2.5, 2.5, 2.5);
    carpet.position.set(1, -0.1, 2);
    // const angleInDegrees = 270;
    // carpet.rotation.y = degreesToRadians(angleInDegrees);
    room.add(carpet);
});

gltfLoader.load('models/frame.glb', (gltf) => {
    const frame = gltf.scene;
    frame.scale.set(1, 1, 1);
    frame.position.set(-5, 2, 1.9);
    // const angleInDegrees = 270;
    frame.rotation.y = Math.PI/2;
    room.add(frame);
});

gltfLoader.load('models/dog_bed.glb', (gltf) => {
    const dog_bed = gltf.scene;
    dog_bed.scale.set(1.2, 1.2, 1.2);
    dog_bed.position.set(3.9, 0.23, -4);
    // const angleInDegrees = 270;
    // dog_bed.rotation.y = Math.PI/2;
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