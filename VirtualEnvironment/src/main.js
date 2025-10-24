import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';
import { Reflector } from 'three/examples/jsm/objects/Reflector.js';
import { RectAreaLightUniformsLib } from 'three/examples/jsm/lights/RectAreaLightUniformsLib.js';

function degreesToRadians(degrees) {
    return degrees * (Math.PI / 180);
}

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xC8E6C9);

// Camera
const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 15;
const camera = new THREE.OrthographicCamera(
    frustumSize * aspect / -2,
    frustumSize * aspect / 2,
    frustumSize / 2,
    frustumSize / -2,
    0.1,
    100
);
camera.position.set(10, 10, 10);
camera.lookAt(0, 0, 0);

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
controls.target.set(0, 0, 0);
controls.maxPolarAngle = Math.PI / 2;
controls.minPolarAngle = 0;
controls.enablePan = false;
controls.update();

// Lighting Setup
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

const windowLight = new THREE.RectAreaLight(0xaaccff, 1, 4, 5);
windowLight.position.set(6, 2.5, -2.5);
windowLight.lookAt(-5, 2.5, -2.5);
scene.add(windowLight);

const plantSpotlight = new THREE.SpotLight(0xccffcc, 4, 12, Math.PI * 0.15, 0.6, 1);
plantSpotlight.position.set(3.5, 5, -2.5);
plantSpotlight.target.position.set(2.2, 0.15, -4.2);
scene.add(plantSpotlight);
scene.add(plantSpotlight.target);

const dogSpotlight = new THREE.SpotLight(0xffffff, 3, 10, Math.PI * 0.2, 0.5, 1);
dogSpotlight.position.set(3, 4, -1);
dogSpotlight.target.position.set(3.9, 0.25, -3.2);
dogSpotlight.castShadow = true;
dogSpotlight.shadow.bias = -0.002;
scene.add(dogSpotlight);
scene.add(dogSpotlight.target);

// Room Group
const room = new THREE.Group();
scene.add(room);

// Diorama Box (Walls and Floor)
const WALL_THICKNESS = 0.3;
const ROOM_SIZE = 10;
const ROOM_HEIGHT = 5;
room.position.y = -ROOM_HEIGHT / 2;

const brownEdgeMaterial = new THREE.MeshStandardMaterial({ color: 0x8B4513, roughness: 0.7, metalness: 0 });
const textureLoader = new THREE.TextureLoader();
const colorTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_Color.jpg');
const roughnessTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_Roughness.jpg');
const normalTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_NormalGL.jpg');
const aoTexture = textureLoader.load('textures/WoodFloor009_1K-JPG_AmbientOcclusion.jpg');

[colorTexture, roughnessTexture, normalTexture, aoTexture].forEach(texture => {
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(0.5, 0.5);
    texture.center.set(0.5, 0.5);
    texture.rotation = Math.PI / 2;
});

const floorTopMaterial = new THREE.MeshStandardMaterial({
    color: 0xbbbbbb,
    map: colorTexture,
    roughnessMap: roughnessTexture,
    normalMap: normalTexture,
    aoMap: aoTexture,
    aoMapIntensity: 1,
});

const wallInnerMaterial = new THREE.MeshStandardMaterial({ color: 0x4F604D, roughness: 0.8, metalness: 0 });

const floorGeometry = new THREE.BoxGeometry(ROOM_SIZE, WALL_THICKNESS, ROOM_SIZE);
floorGeometry.setAttribute('uv2', new THREE.BufferAttribute(floorGeometry.attributes.uv.array, 2));
const floorMaterials = [brownEdgeMaterial, brownEdgeMaterial, floorTopMaterial, brownEdgeMaterial, brownEdgeMaterial, brownEdgeMaterial];
const floor = new THREE.Mesh(floorGeometry, floorMaterials);
floor.position.set(0, 0, 0);
floor.receiveShadow = true;
floor.castShadow = true;
room.add(floor);

const backWallGeometry = new THREE.BoxGeometry(ROOM_SIZE, ROOM_HEIGHT, WALL_THICKNESS);
const backWallMaterials = [brownEdgeMaterial, brownEdgeMaterial, brownEdgeMaterial, brownEdgeMaterial, wallInnerMaterial, brownEdgeMaterial];
const backWall = new THREE.Mesh(backWallGeometry, backWallMaterials);
backWall.position.set(0, ROOM_HEIGHT / 2, -ROOM_SIZE / 2 + WALL_THICKNESS / 2);
backWall.receiveShadow = true;
backWall.castShadow = true;
room.add(backWall);

const leftWallGeometry = new THREE.BoxGeometry(WALL_THICKNESS, ROOM_HEIGHT, ROOM_SIZE);
const leftWallMaterials = [wallInnerMaterial, brownEdgeMaterial, brownEdgeMaterial, brownEdgeMaterial, brownEdgeMaterial, brownEdgeMaterial];
const leftWall = new THREE.Mesh(leftWallGeometry, leftWallMaterials);
leftWall.position.set(-ROOM_SIZE / 2 + WALL_THICKNESS / 2, ROOM_HEIGHT / 2, 0);
leftWall.receiveShadow = true;
leftWall.castShadow = true;
room.add(leftWall);

// Loaders
const gltfLoader = new GLTFLoader();
const fbxLoader = new FBXLoader();

// Shadow utility
const setShadows = (object) => {
    object.traverse((child) => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });
};

// Load All Static GLB Models (keeping your original positions)
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

// Animation Mixers and Character Management
let dogMixer;
let femaleCharacter;
let currentAction;
let animations = {};
let animationsLoaded = 0;
const totalAnimations = 4;

// Scene Management (removed cameraOffset)
const scenes = {
    walking: {
        position: { x: 0, y: 0.15, z: 0 },
        rotation: { y: 0 },
        animation: 'walk'
    },
    studying: {
        position: { x: -3.5, y: 0.17, z: -2 },
        rotation: { y: degreesToRadians(-180) },
        animation: 'sit'
    },
    petting: {
        position: { x: 1.8, y: 0.15, z: -3.2 },
        rotation: { y: degreesToRadians(45) },
        animation: 'pet'
    },
    sleeping: {
        position: { x: -1.8, y: 1, z: 2 },
        rotation: { y: degreesToRadians(10) },
        animation: 'sleep'
    }
};

let currentScene = 'walking';
let isTransitioning = false;

// Load Animated Dog
gltfLoader.load('models/dog.glb', (gltf) => {
    const dog = gltf.scene;
    dog.scale.set(0.5, 0.5, 0.5);
    dog.position.set(2.5, 0.1, -2.9);
    setShadows(dog);
    room.add(dog);

    dogMixer = new THREE.AnimationMixer(dog);
    if (gltf.animations.length) {
        dogMixer.clipAction(gltf.animations[0]).play();
    }
});

// Create a shared female character container
femaleCharacter = new THREE.Group();
femaleCharacter.position.set(0, 0.15, 0);
femaleCharacter.rotation.y = 0;
room.add(femaleCharacter);

// Character models for different animations
let characterModels = {};

// Load all female character animations
function loadFemaleAnimation(name, filename) {
    fbxLoader.load(filename, (fbx) => {
        fbx.scale.set(0.02, 0.02, 0.02);
        setShadows(fbx);
        
        characterModels[name] = fbx;
        fbx.visible = false;
        femaleCharacter.add(fbx);
        
        if (fbx.animations.length) {
            const mixer = new THREE.AnimationMixer(fbx);
            animations[name] = {
                action: mixer.clipAction(fbx.animations[0]),
                mixer: mixer,
                model: fbx
            };
        }
        
        animationsLoaded++;
        
        if (animationsLoaded === totalAnimations) {
            switchToAnimation('walk');
        }
        
        console.log(`Loaded ${name} animation (${animationsLoaded}/${totalAnimations})`);
    }, undefined, (error) => {
        console.error(`Error loading ${name}:`, error);
    });
}

// Load all animations
loadFemaleAnimation('walk', 'models/female_walk.fbx');
loadFemaleAnimation('sit', 'models/female_sitting.fbx');
loadFemaleAnimation('pet', 'models/female_petting.fbx');
loadFemaleAnimation('sleep', 'models/female_sleeping.fbx');

// Function to switch between animation models
function switchToAnimation(animName) {
    if (!animations[animName]) return;
    
    Object.keys(characterModels).forEach(key => {
        characterModels[key].visible = false;
    });
    
    const anim = animations[animName];
    anim.model.visible = true;
    anim.action.reset();
    anim.action.play();
    currentAction = anim;
}

// Simple lerp function for smooth transitions
function lerp(start, end, factor) {
    return start + (end - start) * factor;
}

// Transition to a new scene (without camera movement)
function transitionToScene(sceneName) {
    if (isTransitioning || animationsLoaded < totalAnimations || sceneName === currentScene) return;
    
    isTransitioning = true;
    const targetScene = scenes[sceneName];
    const startPos = { ...femaleCharacter.position };
    const startRot = femaleCharacter.rotation.y;
    
    let progress = 0;
    const duration = 2000;
    const startTime = Date.now();
    
    const direction = new THREE.Vector2(
        targetScene.position.x - startPos.x,
        targetScene.position.z - startPos.z
    );
    const walkingRotation = Math.atan2(direction.x, direction.y);
    
    function animate() {
        const elapsed = Date.now() - startTime;
        progress = Math.min(elapsed / duration, 1);
        
        const eased = progress < 0.5
            ? 2 * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        if (progress < 0.9 && currentScene !== sceneName) {
            if (!currentAction || currentAction !== animations.walk) {
                switchToAnimation('walk');
            }
            femaleCharacter.rotation.y = lerp(startRot, walkingRotation, eased);
        } else if (progress >= 0.9) {
            if (animations[targetScene.animation] && currentAction !== animations[targetScene.animation]) {
                switchToAnimation(targetScene.animation);
            }
            femaleCharacter.rotation.y = lerp(walkingRotation, targetScene.rotation.y, (progress - 0.9) * 10);
        }
        
        femaleCharacter.position.x = lerp(startPos.x, targetScene.position.x, eased);
        femaleCharacter.position.y = lerp(startPos.y, targetScene.position.y, eased);
        femaleCharacter.position.z = lerp(startPos.z, targetScene.position.z, eased);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            isTransitioning = false;
            currentScene = sceneName;
        }
    }
    
    animate();
}

// UI Event Listeners
document.getElementById('btn-walking').addEventListener('click', () => transitionToScene('walking'));
document.getElementById('btn-studying').addEventListener('click', () => transitionToScene('studying'));
document.getElementById('btn-petting').addEventListener('click', () => transitionToScene('petting'));
document.getElementById('btn-sleeping').addEventListener('click', () => transitionToScene('sleeping'));

// Update loading status
setInterval(() => {
    const loadingDiv = document.getElementById('loading-status');
    if (animationsLoaded >= totalAnimations) {
        loadingDiv.classList.add('hidden');
    } else {
        loadingDiv.textContent = `Loading animations... ${animationsLoaded}/${totalAnimations}`;
    }
}, 100);

// Highlight active scene
function updateUIHighlight() {
    const buttons = ['walking', 'studying', 'petting', 'sleeping'];
    buttons.forEach(scene => {
        const btn = document.getElementById(`btn-${scene}`);
        if (scene === currentScene) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

setInterval(updateUIHighlight, 100);

// Clock for Animation
const clock = new THREE.Clock();

// Animation Loop
const tick = () => {
    const delta = clock.getDelta();

    if (dogMixer) {
        dogMixer.update(delta);
    }

    Object.keys(animations).forEach(key => {
        if (animations[key].mixer) {
            animations[key].mixer.update(delta);
        }
    });

    controls.update();
    renderer.render(scene, camera);
    window.requestAnimationFrame(tick);
};
tick();

// Resize Handler
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