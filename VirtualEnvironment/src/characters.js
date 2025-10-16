// ============================================
// CHARACTER SYSTEM (using GLB models)
// ============================================

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// ===== Load GLTF Models =====
export function loadGirlModel(scene, gltfPath = 'models/cartoon_girl.glb') {
  return new Promise((resolve, reject) => {
    const loader = new GLTFLoader();
    loader.load(
      gltfPath,
      (gltf) => {
        const girl = gltf.scene;
        girl.name = 'girl';

        // Fix arms-up pose by resetting animations
        if (gltf.animations && gltf.animations.length > 0) {
          const mixer = new THREE.AnimationMixer(girl);
          // Play idle/standing animation if available
          const idleClip = gltf.animations.find(clip => 
            clip.name.toLowerCase().includes('idle') || 
            clip.name.toLowerCase().includes('stand')
          );
          if (idleClip) {
            mixer.clipAction(idleClip).play();
          }
        }

        girl.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
            
            // Ensure materials are visible
            if (child.material) {
              if (Array.isArray(child.material)) {
                child.material.forEach(mat => {
                  mat.side = THREE.DoubleSide;
                });
              } else {
                child.material.side = THREE.DoubleSide;
              }
            }
          }
        });

        // Adjust scale and position for your model
        girl.scale.set(1, 1, 1);
        girl.position.set(1.5, -2.29, 1.4);
        girl.rotation.y = Math.PI / 2;

        scene.add(girl);
        resolve(girl);
      },
      undefined,
      reject
    );
  });
}

export function loadDogModel(scene, gltfPath = 'models/shiba_inu_dog.glb') {
  return new Promise((resolve, reject) => {
    const loader = new GLTFLoader();
    loader.load(
      gltfPath,
      (gltf) => {
        const dog = gltf.scene;
        dog.name = 'dog';

        dog.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;

            // FIX BLACK DOG: Brighten materials and ensure visibility
            if (child.material) {
              if (Array.isArray(child.material)) {
                child.material.forEach(mat => {
                  mat.side = THREE.DoubleSide;
                  // Increase emissive for darker materials
                  if (mat.color) {
                    mat.emissive.copy(mat.color);
                    mat.emissiveIntensity = 0.3;
                  }
                  // Reduce metalness/roughness if needed
                  if (mat.metalness !== undefined) {
                    mat.metalness = Math.min(mat.metalness, 0.5);
                  }
                  if (mat.roughness !== undefined) {
                    mat.roughness = Math.min(mat.roughness, 0.8);
                  }
                });
              } else {
                child.material.side = THREE.DoubleSide;
                if (child.material.color) {
                  child.material.emissive.copy(child.material.color);
                  child.material.emissiveIntensity = 0.3;
                }
                if (child.material.metalness !== undefined) {
                  child.material.metalness = Math.min(child.material.metalness, 0.5);
                }
                if (child.material.roughness !== undefined) {
                  child.material.roughness = Math.min(child.material.roughness, 0.8);
                }
              }
            }
          }
        });

        dog.scale.set(0.2, 0.2, 0.2);
        dog.position.set(3, -2.29, 1.0);
        dog.rotation.y = Math.PI / 4;

        scene.add(dog);
        resolve(dog);
      },
      undefined,
      reject
    );
  });
}

// ============================================
// CHARACTER CONTROLLER (animation + logic)
// ============================================
export class CharacterController {
  constructor(girl, dog) {
    this.girl = girl;
    this.dog = dog;
    this.time = 0;

    // Store state
    this.state = {
      girlAction: 'petting',
      dogAction: 'sitting',
      girlInitialPos: new THREE.Vector3(1.4, 0.01, 1.4),
      dogInitialPos: new THREE.Vector3(1.9, 0.01, 1.0),
    };
  }

  // ===== GIRL ACTIONS =====
  girlWalk() {
    this.state.girlAction = 'walking';
    this.girl.position.copy(new THREE.Vector3(1, 0.01, 1));
    this.girl.rotation.set(0, 0, 0);
  }

  girlSitOnChair(chairPosition) {
    this.state.girlAction = 'sitting';
    this.girl.position.set(chairPosition.x, 0.35, chairPosition.z);
    this.girl.rotation.y = Math.PI;
  }

  girlLayOnBed(bedPosition) {
    this.state.girlAction = 'laying';
    this.girl.position.set(bedPosition.x + 0.5, 0.35, bedPosition.z);
    this.girl.rotation.set(Math.PI / 2, Math.PI / 2, 0);
  }

  girlPetDog(dogBedPosition) {
    this.state.girlAction = 'petting';
    this.girl.position.set(dogBedPosition.x - 0.8, 0.01, dogBedPosition.z + 0.6);
    this.girl.rotation.y = -Math.PI / 4;
    this.dog.position.set(dogBedPosition.x, 0.01, dogBedPosition.z - 0.3);
    this.dog.rotation.y = Math.PI / 4;
    this.state.dogAction = 'sitting';
  }

  // ===== DOG ACTIONS =====
  dogWalk() {
    this.state.dogAction = 'walking';
    this.dog.position.copy(new THREE.Vector3(2, 0.01, 0.8));
    this.dog.rotation.set(0, 0, 0);
  }

  dogSleepOnBed(dogBedPosition) {
    this.state.dogAction = 'sleeping';
    this.dog.position.set(dogBedPosition.x, 0.01, dogBedPosition.z);
    this.dog.rotation.set(0, 0, Math.PI / 8);
  }

  reset() {
    this.state.girlAction = 'petting';
    this.state.dogAction = 'sitting';
    this.girl.position.copy(this.state.girlInitialPos);
    this.girl.rotation.y = -Math.PI / 4;
    this.dog.position.copy(this.state.dogInitialPos);
    this.dog.rotation.y = Math.PI / 4;
  }

  // ===== UPDATE LOOP (light animation) =====
  update(deltaTime = 0.016) {
    this.time += deltaTime;

    if (this.state.dogAction === 'walking') {
      const t = this.time;
      const r = 0.3;
      this.dog.position.x = this.state.dogInitialPos.x + Math.cos(t) * r;
      this.dog.position.z = this.state.dogInitialPos.z + Math.sin(t) * r;
      this.dog.rotation.y = -t;
    } else if (this.state.dogAction === 'sitting') {
      this.dog.rotation.y = Math.PI / 4 + Math.sin(this.time * 2) * 0.1;
    }

    if (this.state.girlAction === 'petting') {
      this.girl.rotation.y = -Math.PI / 4 + Math.sin(this.time * 1.5) * 0.05;
    }
  }
}