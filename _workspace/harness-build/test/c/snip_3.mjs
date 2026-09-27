import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { assetPaths, usable } from './assets.js';

export async function loadModel(id, size = [1, 1, 1]) {
  const [path] = assetPaths(id);
  if (usable(id) && path) {
    try { return (await new GLTFLoader().loadAsync(path)).scene; }
    catch { window.__game?.missingAssets.add(path); }
  } else window.__game?.missingAssets.add(id);
  const box = new THREE.Mesh(new THREE.BoxGeometry(...size), new THREE.MeshStandardMaterial({ color: 0x888888 }));
  box.name = `placeholder:${id}`;
  return box;
}
