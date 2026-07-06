// ===== 推箱子 3D 引擎（three.js）=====
// 操作模式与 2D 版一致：方向键立即移动一格，无移动动画。
// 视角位置固定（距离/高度固定），可用鼠标拖拽旋转视角。

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const ANIM_INTERVAL = 60; // AI 回放每步间隔 ms
const HOLD_DELAY = 180;   // 按住方向键首次延迟 ms
const HOLD_INTERVAL = 90; // 按住后重复间隔 ms

const canvas = document.getElementById('gameCanvas');
const levelSelect = document.getElementById('levelSelect');
const moveCountEl = document.getElementById('moveCount');
const undoBtn = document.getElementById('undoBtn');
const resetBtn = document.getElementById('resetBtn');
const viewAnswerBtn = document.getElementById('viewAnswerBtn');
const aiStatus = document.getElementById('aiStatus');
const winOverlay = document.getElementById('winOverlay');
const winMoves = document.getElementById('winMoves');
const nextLevelBtn = document.getElementById('nextLevelBtn');

// ---- 游戏状态 ----
let state = null;
let animQueue = [];
let animTimer = null;
let inputLocked = false;
let holdTimer = null;
let holdDir = null;
let aiActive = false;

// ---- three.js 基础设施 ----
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);
scene.fog = new THREE.Fog(0x1a1a2e, 25, 70);

const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 200);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableZoom = false;
controls.enablePan = false;
controls.enableDamping = true;
controls.dampingFactor = 0.12;
controls.minPolarAngle = 0.2;
controls.maxPolarAngle = Math.PI / 2 - 0.05;

// ---- 灯光 ----
const ambient = new THREE.AmbientLight(0xffffff, 0.55);
scene.add(ambient);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
dirLight.position.set(8, 14, 6);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.near = 1;
dirLight.shadow.camera.far = 60;
dirLight.shadow.camera.left = -20;
dirLight.shadow.camera.right = 20;
dirLight.shadow.camera.top = 20;
dirLight.shadow.camera.bottom = -20;
dirLight.shadow.bias = -0.0005;
scene.add(dirLight);

const hemiLight = new THREE.HemisphereLight(0x8899bb, 0x222244, 0.35);
scene.add(hemiLight);

// ---- 关卡容器与共享几何/材质 ----
const levelGroup = new THREE.Group();
scene.add(levelGroup);

// 用于点击检测的隐形地面平面
let clickPlane = null;

const CELL = 1;          // 3D 中每格的世界单位
const WALL_H = 1.0;
const BOX_SIZE = 0.78;
const PLAYER_R = 0.32;
const PLAYER_BODY_H = 0.92;
const PLAYER_HEAD_R = 0.2;

const geoFloor = new THREE.BoxGeometry(CELL, 0.1, CELL);
const geoWall  = new THREE.BoxGeometry(CELL, WALL_H, CELL);
const geoBox   = new THREE.BoxGeometry(BOX_SIZE, BOX_SIZE, BOX_SIZE);
const geoBoxBand = new THREE.BoxGeometry(BOX_SIZE * 1.02, BOX_SIZE * 0.12, BOX_SIZE * 0.2);
const geoBoxSlat = new THREE.BoxGeometry(BOX_SIZE * 0.18, BOX_SIZE * 0.68, BOX_SIZE * 1.02);
const geoPlayerBody = new THREE.CapsuleGeometry(0.18, 0.34, 8, 16);
const geoPlayerHead = new THREE.SphereGeometry(PLAYER_HEAD_R, 24, 18);
const geoPlayerHat = new THREE.CylinderGeometry(0.22, 0.24, 0.12, 20);
const geoPlayerBrim = new THREE.CylinderGeometry(0.31, 0.31, 0.03, 24);
const geoPlayerArm = new THREE.CapsuleGeometry(0.06, 0.22, 6, 12);
const geoPlayerLeg = new THREE.CapsuleGeometry(0.07, 0.26, 6, 12);
const geoGoal  = new THREE.CylinderGeometry(0.28, 0.28, 0.04, 24);
const geoMoustache = new THREE.BoxGeometry(0.18, 0.035, 0.03);

const matFloor    = new THREE.MeshStandardMaterial({ color: 0x3a3a55, roughness: 0.85 });
const matFloorGoalCell = new THREE.MeshStandardMaterial({ color: 0x4a3a55, roughness: 0.85 });
const matWall     = new THREE.MeshStandardMaterial({ color: 0x4a4a6a, roughness: 0.7 });
const matGoal     = new THREE.MeshStandardMaterial({ color: 0xe94560, emissive: 0xe94560, emissiveIntensity: 0.6, roughness: 0.4 });
const matBoxWood  = new THREE.MeshStandardMaterial({ color: 0xb36b2f, roughness: 0.9 });
const matBoxWoodOn = new THREE.MeshStandardMaterial({ color: 0x6abf69, roughness: 0.72, emissive: 0x1e5c36, emissiveIntensity: 0.2 });
const matBoxBand  = new THREE.MeshStandardMaterial({ color: 0x6f3e16, roughness: 0.92 });
const matBoxBandOn = new THREE.MeshStandardMaterial({ color: 0x2e7d32, roughness: 0.82 });
const matPlayerCoat = new THREE.MeshStandardMaterial({ color: 0x355c9a, roughness: 0.58, metalness: 0.08 });
const matPlayerSkin = new THREE.MeshStandardMaterial({ color: 0xf0c7a4, roughness: 0.72 });
const matPlayerHat  = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.88 });
const matPlayerApron = new THREE.MeshStandardMaterial({ color: 0xd9e3f0, roughness: 0.8 });
const matPlayerBoots = new THREE.MeshStandardMaterial({ color: 0x4f3422, roughness: 0.9 });
const matPlayerHair = new THREE.MeshStandardMaterial({ color: 0x2b1d14, roughness: 0.86 });

// 动态网格对象引用
let boxMeshes = new Map();   // "x,y" -> Mesh
let playerGroup = null;      // Group（身体 + 朝向）
let levelBounds = { minX: 0, maxX: 0, minZ: 0, maxZ: 0 };
let hasInitializedCamera = false;

function createWoodTexture(baseHex, lineHex) {
  const size = 256;
  const canvasTex = document.createElement('canvas');
  canvasTex.width = size;
  canvasTex.height = size;
  const ctx = canvasTex.getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, size, size);
  grad.addColorStop(0, '#' + baseHex.toString(16).padStart(6, '0'));
  grad.addColorStop(1, '#6d3e1d');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);
  ctx.strokeStyle = '#' + lineHex.toString(16).padStart(6, '0');
  ctx.lineWidth = 6;
  for (let i = -size; i < size * 2; i += 34) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i - 40, size);
    ctx.stroke();
  }
  ctx.lineWidth = 2;
  ctx.strokeStyle = 'rgba(255,255,255,0.14)';
  for (let y = 18; y < size; y += 26) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.bezierCurveTo(size * 0.25, y - 8, size * 0.75, y + 8, size, y - 4);
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(canvasTex);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1, 1);
  texture.anisotropy = 8;
  return texture;
}

matBoxWood.map = createWoodTexture(0xb36b2f, 0x7a461d);
matBoxWoodOn.map = createWoodTexture(0x67b568, 0x2e7d32);
matBoxWood.needsUpdate = true;
matBoxWoodOn.needsUpdate = true;

function createBoxMesh(onGoal) {
  const group = new THREE.Group();
  const shell = new THREE.Mesh(geoBox, onGoal ? matBoxWoodOn : matBoxWood);
  shell.castShadow = true;
  shell.receiveShadow = true;
  group.add(shell);

  const bandA = new THREE.Mesh(geoBoxBand, onGoal ? matBoxBandOn : matBoxBand);
  bandA.position.y = BOX_SIZE * 0.18;
  group.add(bandA);

  const bandB = new THREE.Mesh(geoBoxBand, onGoal ? matBoxBandOn : matBoxBand);
  bandB.position.y = -BOX_SIZE * 0.18;
  group.add(bandB);

  const slatA = new THREE.Mesh(geoBoxSlat, onGoal ? matBoxBandOn : matBoxBand);
  slatA.position.x = -BOX_SIZE * 0.18;
  group.add(slatA);

  const slatB = new THREE.Mesh(geoBoxSlat, onGoal ? matBoxBandOn : matBoxBand);
  slatB.position.x = BOX_SIZE * 0.18;
  group.add(slatB);

  return group;
}

function updateBoxMeshAppearance(mesh, onGoal) {
  const [shell, bandA, bandB, slatA, slatB] = mesh.children;
  shell.material = onGoal ? matBoxWoodOn : matBoxWood;
  bandA.material = onGoal ? matBoxBandOn : matBoxBand;
  bandB.material = onGoal ? matBoxBandOn : matBoxBand;
  slatA.material = onGoal ? matBoxBandOn : matBoxBand;
  slatB.material = onGoal ? matBoxBandOn : matBoxBand;
}

function createPlayerMesh() {
  const group = new THREE.Group();

  const body = new THREE.Mesh(geoPlayerBody, matPlayerCoat);
  body.position.y = 0.62;
  body.castShadow = true;
  group.add(body);

  const apron = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.34, 0.06), matPlayerApron);
  apron.position.set(0, 0.55, 0.16);
  group.add(apron);

  const head = new THREE.Mesh(geoPlayerHead, matPlayerSkin);
  head.position.y = 1.0;
  head.castShadow = true;
  group.add(head);

  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.16, 20, 16), matPlayerHair);
  hair.position.set(0, 1.06, -0.03);
  hair.scale.set(1.02, 0.72, 0.96);
  group.add(hair);

  const hat = new THREE.Mesh(geoPlayerHat, matPlayerHat);
  hat.position.y = 1.18;
  group.add(hat);

  const brim = new THREE.Mesh(geoPlayerBrim, matPlayerHat);
  brim.position.y = 1.11;
  group.add(brim);

  const leftArm = new THREE.Mesh(geoPlayerArm, matPlayerCoat);
  leftArm.position.set(-0.24, 0.63, 0);
  leftArm.rotation.z = 0.45;
  group.add(leftArm);

  const rightArm = new THREE.Mesh(geoPlayerArm, matPlayerCoat);
  rightArm.position.set(0.24, 0.63, 0);
  rightArm.rotation.z = -0.45;
  group.add(rightArm);

  const leftHand = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), matPlayerSkin);
  leftHand.position.set(-0.34, 0.49, 0.02);
  group.add(leftHand);

  const rightHand = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), matPlayerSkin);
  rightHand.position.set(0.34, 0.49, 0.02);
  group.add(rightHand);

  const leftLeg = new THREE.Mesh(geoPlayerLeg, matPlayerBoots);
  leftLeg.position.set(-0.1, 0.18, 0);
  group.add(leftLeg);

  const rightLeg = new THREE.Mesh(geoPlayerLeg, matPlayerBoots);
  rightLeg.position.set(0.1, 0.18, 0);
  group.add(rightLeg);

  const leftEye = new THREE.Mesh(new THREE.SphereGeometry(0.025, 12, 10), new THREE.MeshStandardMaterial({ color: 0xffffff }));
  leftEye.position.set(-0.06, 1.02, 0.16);
  group.add(leftEye);

  const rightEye = new THREE.Mesh(new THREE.SphereGeometry(0.025, 12, 10), new THREE.MeshStandardMaterial({ color: 0xffffff }));
  rightEye.position.set(0.06, 1.02, 0.16);
  group.add(rightEye);

  const moustache = new THREE.Mesh(geoMoustache, matPlayerHair);
  moustache.position.set(0, 0.93, 0.17);
  group.add(moustache);

  return group;
}

// ---- 关卡管理 ----
function populateLevelSelect() {
  levelSelect.innerHTML = '';
  for (let i = 0; i < LEVELS_DATA.length; i++) {
    const opt = document.createElement('option');
    opt.value = i;
    const name = LEVELS_DATA[i].name || '';
    opt.textContent = '第' + (i + 1) + '关' + (name ? ' - ' + name : '');
    levelSelect.appendChild(opt);
  }
}

function getLastLevel() {
  const saved = localStorage.getItem('sokoban_3d_last_level');
  if (saved !== null) {
    const n = parseInt(saved, 10);
    if (!isNaN(n) && n >= 0 && n < LEVELS_DATA.length) return n;
  }
  return 0;
}

function saveLastLevel(index) {
  localStorage.setItem('sokoban_3d_last_level', String(index));
}

// ---- 解析关卡 ----
function parseLevel(index) {
  const raw = LEVELS_DATA[index].puzzle;
  const walls = new Set();
  const goals = new Set();
  const boxes = new Set();
  let player = null;

  for (let y = 0; y < raw.length; y++) {
    const row = raw[y];
    for (let x = 0; x < row.length; x++) {
      const ch = row[x];
      const key = x + ',' + y;
      switch (ch) {
        case '#': walls.add(key); break;
        case '.': goals.add(key); break;
        case '$': boxes.add(key); break;
        case '*': boxes.add(key); goals.add(key); break;
        case '@': player = { x, y }; break;
        case '+': player = { x, y }; goals.add(key); break;
      }
    }
  }
  return { walls, goals, boxes, player, index };
}

function loadLevel(index) {
  stopAI();
  clearAnimQueue();
  const parsed = parseLevel(index);
  state = {
    walls: parsed.walls,
    goals: parsed.goals,
    boxes: parsed.boxes,
    player: parsed.player,
    moves: 0,
    history: [],
    won: false,
    levelIndex: index,
    facing: 0 // 玩家朝向（弧度），0 = -Z（游戏上方）
  };
  saveLastLevel(index);
  levelSelect.value = index;
  buildScene();
  updateUI();
  winOverlay.classList.add('hidden');
}

function resetLevel() {
  if (!state) return;
  stopAI();
  clearAnimQueue();
  loadLevel(state.levelIndex);
}

// ---- 计算 3D 坐标 ----
// 游戏 (gx, gy) → 世界 (gx, 0, gy)
function cellToWorld(gx, gy) {
  return { x: gx, z: gy };
}

// ---- 构建场景 ----
function clearLevelGroup() {
  while (levelGroup.children.length > 0) {
    const obj = levelGroup.children[0];
    levelGroup.remove(obj);
    if (obj.geometry && obj.geometry !== geoFloor && obj.geometry !== geoWall &&
        obj.geometry !== geoBox && obj.geometry !== geoBoxBand &&
        obj.geometry !== geoBoxSlat && obj.geometry !== geoPlayerBody &&
        obj.geometry !== geoPlayerHead && obj.geometry !== geoPlayerHat &&
        obj.geometry !== geoPlayerBrim && obj.geometry !== geoPlayerArm &&
        obj.geometry !== geoPlayerLeg && obj.geometry !== geoGoal &&
        obj.geometry !== geoMoustache) {
      obj.geometry.dispose();
    }
  }
  boxMeshes.clear();
  playerGroup = null;
  if (clickPlane) {
    scene.remove(clickPlane);
    clickPlane.geometry.dispose();
    clickPlane = null;
  }
}

function buildScene() {
  clearLevelGroup();

  let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
  const allKeys = new Set([...state.walls, ...state.goals, ...state.boxes]);
  if (state.player) allKeys.add(state.player.x + ',' + state.player.y);
  for (const k of allKeys) {
    const [x, y] = k.split(',').map(Number);
    if (x < minX) minX = x;
    if (x > maxX) maxX = x;
    if (y < minZ) minZ = y;
    if (y > maxZ) maxZ = y;
  }
  levelBounds = { minX, maxX, minZ, maxZ };

  // 地板：覆盖整个关卡范围
  for (let z = minZ; z <= maxZ; z++) {
    for (let x = minX; x <= maxX; x++) {
      const key = x + ',' + z;
      const isGoalCell = state.goals.has(key);
      const floorMat = isGoalCell ? matFloorGoalCell : matFloor;
      const floor = new THREE.Mesh(geoFloor, floorMat);
      floor.position.set(x, -0.05, z);
      floor.receiveShadow = true;
      levelGroup.add(floor);
    }
  }

  // 墙
  for (const key of state.walls) {
    const [x, y] = key.split(',').map(Number);
    const wall = new THREE.Mesh(geoWall, matWall);
    wall.position.set(x, WALL_H / 2, y);
    wall.castShadow = true;
    wall.receiveShadow = true;
    levelGroup.add(wall);
  }

  // 目标点
  for (const key of state.goals) {
    const [x, y] = key.split(',').map(Number);
    const goal = new THREE.Mesh(geoGoal, matGoal);
    goal.position.set(x, 0.02, y);
    levelGroup.add(goal);
  }

  // 箱子
  for (const key of state.boxes) {
    const [x, y] = key.split(',').map(Number);
    const onGoal = state.goals.has(key);
    const box = createBoxMesh(onGoal);
    box.position.set(x, BOX_SIZE / 2 + 0.05, y);
    levelGroup.add(box);
    boxMeshes.set(key, box);
  }

  // 玩家
  playerGroup = createPlayerMesh();
  playerGroup.position.set(state.player.x, 0.02, state.player.y);
  playerGroup.rotation.y = state.facing;
  levelGroup.add(playerGroup);

  // 点击检测平面（覆盖整个关卡）
  const w = (maxX - minX + 1);
  const h = (maxZ - minZ + 1);
  const cx = (minX + maxX) / 2;
  const cz = (minZ + maxZ) / 2;
  const planeGeo = new THREE.PlaneGeometry(w, h);
  clickPlane = new THREE.Mesh(planeGeo, new THREE.MeshBasicMaterial({ visible: false }));
  clickPlane.rotation.x = -Math.PI / 2;
  clickPlane.position.set(cx, 0.05, cz);
  scene.add(clickPlane);

  // 相机定位
  positionCamera();
}

function positionCamera() {
  const { minX, maxX, minZ, maxZ } = levelBounds;
  const cx = (minX + maxX) / 2;
  const cz = (minZ + maxZ) / 2;
  const span = Math.max(maxX - minX, maxZ - minZ) + 2;
  const dist = span * 1.1 + 4;
  const nextTarget = new THREE.Vector3(cx, 0, cz);

  if (!hasInitializedCamera) {
    camera.position.set(cx, dist * 1.28, cz + dist * 0.16);
    camera.lookAt(cx, 0, cz);
    hasInitializedCamera = true;
  } else {
    const deltaX = cx - controls.target.x;
    const deltaZ = cz - controls.target.z;
    camera.position.x += deltaX;
    camera.position.z += deltaZ;
  }

  controls.target.copy(nextTarget);
  controls.target.set(cx, 0, cz);
  controls.minPolarAngle = 0.15;
  controls.maxPolarAngle = Math.PI / 2 - 0.05;
  controls.minAzimuthAngle = -Infinity;
  controls.maxAzimuthAngle = Infinity;
  controls.update();
}

// ---- 同步玩家/箱子网格位置（移动后调用，无动画） ----
function syncMeshes() {
  if (!state) return;
  // 玩家
  if (playerGroup) {
    playerGroup.position.set(state.player.x, 0.02, state.player.y);
    playerGroup.rotation.y = state.facing;
  }
  // 箱子：复用已有 mesh，按当前箱子位置重新分配
  const existing = Array.from(boxMeshes.values());
  boxMeshes.clear();
  const keys = Array.from(state.boxes);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    const [x, y] = key.split(',').map(Number);
    let mesh = existing[i];
    if (!mesh) {
      mesh = createBoxMesh(false);
      levelGroup.add(mesh);
    }
    updateBoxMeshAppearance(mesh, state.goals.has(key));
    mesh.position.set(x, BOX_SIZE / 2 + 0.05, y);
    boxMeshes.set(key, mesh);
  }
  for (let i = keys.length; i < existing.length; i++) {
    levelGroup.remove(existing[i]);
  }
}

// ---- 移动逻辑 ----
const FACING = {
  '0,-1': 0,            // up (-Z)
  '0,1': Math.PI,       // down (+Z)
  '-1,0': Math.PI / 2,  // left (-X)
  '1,0': -Math.PI / 2   // right (+X)
};

function tryMove(dx, dy) {
  if (!state || state.won || inputLocked) return false;

  const nx = state.player.x + dx;
  const ny = state.player.y + dy;
  const nKey = nx + ',' + ny;

  state.facing = FACING[dx + ',' + dy] ?? state.facing;

  if (state.walls.has(nKey)) { syncMeshes(); return false; }

  if (state.boxes.has(nKey)) {
    const bx = nx + dx;
    const by = ny + dy;
    const bKey = bx + ',' + by;
    if (state.walls.has(bKey) || state.boxes.has(bKey)) { syncMeshes(); return false; }

    const histEntry = {
      player: { x: state.player.x, y: state.player.y },
      boxMoved: { from: nKey, to: bKey }
    };
    state.history.push(histEntry);

    state.boxes.delete(nKey);
    state.boxes.add(bKey);
    state.player.x = nx;
    state.player.y = ny;
    state.moves++;
    syncMeshes();
    updateUI();
    checkWin();
    return true;
  }

  const histEntry = {
    player: { x: state.player.x, y: state.player.y },
    boxMoved: null
  };
  state.history.push(histEntry);
  state.player.x = nx;
  state.player.y = ny;
  syncMeshes();
  updateUI();
  return true;
}

// 不渲染的移动（用于鼠标点击寻路，批量执行后一次同步）
function tryMoveInstant(dx, dy) {
  if (!state || state.won) return false;

  const nx = state.player.x + dx;
  const ny = state.player.y + dy;
  const nKey = nx + ',' + ny;

  state.facing = FACING[dx + ',' + dy] ?? state.facing;

  if (state.walls.has(nKey)) return false;

  if (state.boxes.has(nKey)) {
    const bx = nx + dx;
    const by = ny + dy;
    const bKey = bx + ',' + by;
    if (state.walls.has(bKey) || state.boxes.has(bKey)) return false;

    const histEntry = {
      player: { x: state.player.x, y: state.player.y },
      boxMoved: { from: nKey, to: bKey }
    };
    state.history.push(histEntry);
    state.boxes.delete(nKey);
    state.boxes.add(bKey);
    state.player.x = nx;
    state.player.y = ny;
    state.moves++;
    checkWin();
    return true;
  }

  const histEntry = {
    player: { x: state.player.x, y: state.player.y },
    boxMoved: null
  };
  state.history.push(histEntry);
  state.player.x = nx;
  state.player.y = ny;
  return true;
}

function undo() {
  if (!state || state.won || inputLocked || state.history.length === 0) return;
  let entry = null;
  while (state.history.length > 0) {
    entry = state.history.pop();
    if (entry.boxMoved) break;
    state.player = entry.player;
  }
  if (!entry || !entry.boxMoved) {
    syncMeshes();
    updateUI();
    return;
  }
  state.player = entry.player;
  state.boxes.delete(entry.boxMoved.to);
  state.boxes.add(entry.boxMoved.from);
  state.moves--;
  syncMeshes();
  updateUI();
}

function checkWin() {
  let won = true;
  for (const b of state.boxes) {
    if (!state.goals.has(b)) { won = false; break; }
  }
  if (won) {
    state.won = true;
    winMoves.textContent = '共用 ' + state.moves + ' 步完成！';
    winOverlay.classList.remove('hidden');
    stopAI();
  }
}

// ---- 动画队列（AI 回放用，每步为瞬移） ----
function clearAnimQueue() {
  animQueue = [];
  if (animTimer) {
    clearInterval(animTimer);
    animTimer = null;
  }
  inputLocked = false;
}

function hasLevelSolution(index) {
  return !!(LEVELS_DATA[index].solution && LEVELS_DATA[index].solution.trim());
}

function getAnswerQueue(index) {
  const solution = LEVELS_DATA[index].solution;
  if (!solution) return [];
  const queue = [];
  const charMap = { U: 'up', D: 'down', L: 'left', R: 'right' };
  for (const ch of solution) {
    const dir = charMap[ch.toUpperCase()];
    if (dir) queue.push(dir);
  }
  return queue;
}

function refreshAnswerUI() {
  if (!state) {
    viewAnswerBtn.disabled = true;
    viewAnswerBtn.textContent = '查看答案';
    viewAnswerBtn.classList.remove('active');
    aiStatus.textContent = '';
    return;
  }
  if (aiActive) {
    viewAnswerBtn.disabled = false;
    viewAnswerBtn.textContent = '停止查看';
    viewAnswerBtn.classList.add('active');
    return;
  }
  const hasSolution = hasLevelSolution(state.levelIndex);
  viewAnswerBtn.disabled = !hasSolution || state.won;
  viewAnswerBtn.textContent = '查看答案';
  viewAnswerBtn.classList.remove('active');
  if (state.won) {
    aiStatus.textContent = '已过关';
  } else {
    aiStatus.textContent = hasSolution ? '本关有答案' : '本关暂无答案';
  }
}

function startAnimQueue(queue) {
  clearAnimQueue();
  if (!queue || queue.length === 0) return;
  animQueue = queue;
  inputLocked = true;

  const dirMap = {
    up: { dx: 0, dy: -1 },
    down: { dx: 0, dy: 1 },
    left: { dx: -1, dy: 0 },
    right: { dx: 1, dy: 0 }
  };

  animTimer = setInterval(() => {
    if (animQueue.length === 0) {
      clearInterval(animTimer);
      animTimer = null;
      inputLocked = false;
      if (aiActive) stopAI();
      return;
    }
    const dir = animQueue.shift();
    const d = dirMap[dir];
    if (d) {
      tryMoveInstant(d.dx, d.dy);
      syncMeshes();
      updateUI();
    }
  }, ANIM_INTERVAL);
}

// ---- 鼠标点击：raycast 到网格 ----
const raycaster = new THREE.Raycaster();
const mouseVec = new THREE.Vector2();

canvas.addEventListener('click', (e) => {
  if (!state || state.won || inputLocked || aiActive || !clickPlane) return;

  const rect = canvas.getBoundingClientRect();
  mouseVec.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  mouseVec.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouseVec, camera);
  const hits = raycaster.intersectObject(clickPlane, false);
  if (hits.length === 0) return;
  const p = hits[0].point;
  const gx = Math.round(p.x);
  const gy = Math.round(p.z);
  const gKey = gx + ',' + gy;

  if (gx < levelBounds.minX || gx > levelBounds.maxX || gy < levelBounds.minZ || gy > levelBounds.maxZ) return;

  // 点击玩家相邻的箱子 → 推 1 格
  if (state.boxes.has(gKey)) {
    const dx = gx - state.player.x;
    const dy = gy - state.player.y;
    if (Math.abs(dx) + Math.abs(dy) === 1) {
      tryMove(dx, dy);
    }
    return;
  }

  // 点击空地 → BFS 寻路，同步执行所有步
  if (!state.walls.has(gKey) && !state.boxes.has(gKey)) {
    const path = findPath(state, gx, gy);
    if (path && path.length > 0) {
      const dirMap = {
        up: { dx: 0, dy: -1 },
        down: { dx: 0, dy: 1 },
        left: { dx: -1, dy: 0 },
        right: { dx: 1, dy: 0 }
      };
      for (const dir of path) {
        const d = dirMap[dir];
        if (d) tryMoveInstant(d.dx, d.dy);
        if (state.won) break;
      }
      syncMeshes();
      updateUI();
    }
    return;
  }
});

function clearHold() {
  if (holdTimer) {
    clearTimeout(holdTimer);
    clearInterval(holdTimer);
    holdTimer = null;
  }
  holdDir = null;
}

// ---- 键盘 ----
const keyMap = {
  ArrowUp: { dx: 0, dy: -1 },
  ArrowDown: { dx: 0, dy: 1 },
  ArrowLeft: { dx: -1, dy: 0 },
  ArrowRight: { dx: 1, dy: 0 },
  w: { dx: 0, dy: -1 },
  W: { dx: 0, dy: -1 },
  s: { dx: 0, dy: 1 },
  S: { dx: 0, dy: 1 },
  a: { dx: -1, dy: 0 },
  A: { dx: -1, dy: 0 },
  d: { dx: 1, dy: 0 },
  D: { dx: 1, dy: 0 }
};

document.addEventListener('keydown', (e) => {
  if (e.key === 'z' || e.key === 'Z') { e.preventDefault(); undo(); return; }
  if (e.key === 'r' || e.key === 'R') { e.preventDefault(); resetLevel(); return; }
  if (e.key === 'F1') { e.preventDefault(); viewAnswerBtn.click(); return; }
  if (e.key === ' ' || e.key === 'Space') {
    e.preventDefault();
    if (state && state.won) {
      const next = state.levelIndex + 1;
      if (next < LEVELS_DATA.length) loadLevel(next);
      else winOverlay.classList.add('hidden');
    }
    return;
  }
  if (e.key === 'PageUp') {
    e.preventDefault();
    if (!state) return;
    const prev = state.levelIndex - 1;
    if (prev >= 0) loadLevel(prev);
    return;
  }
  if (e.key === 'PageDown') {
    e.preventDefault();
    if (!state) return;
    const next = state.levelIndex + 1;
    if (next < LEVELS_DATA.length) loadLevel(next);
    return;
  }

  const d = keyMap[e.key];
  if (!d) return;
  e.preventDefault();
  if (inputLocked || aiActive) return;

  if (holdDir !== e.key) {
    clearHold();
    tryMove(d.dx, d.dy);
    holdDir = e.key;
    holdTimer = setTimeout(() => {
      holdTimer = setInterval(() => {
        if (inputLocked || aiActive) { clearHold(); return; }
        tryMove(d.dx, d.dy);
      }, HOLD_INTERVAL);
    }, HOLD_DELAY);
  }
});

document.addEventListener('keyup', (e) => {
  if (holdDir === e.key) clearHold();
});

// ---- 查看答案 ----
function stopAI() {
  aiActive = false;
  clearAnimQueue();
  refreshAnswerUI();
}

function startAI() {
  if (!state || state.won) return;
  if (!hasLevelSolution(state.levelIndex)) { refreshAnswerUI(); return; }
  resetLevel();
  aiActive = true;
  aiStatus.textContent = '执行答案中...';
  refreshAnswerUI();
  const queue = getAnswerQueue(state.levelIndex);
  if (queue.length === 0) { stopAI(); return; }
  startAnimQueue(queue);
  aiStatus.textContent = '执行答案中...（' + queue.length + ' 步）';
}

viewAnswerBtn.addEventListener('click', () => {
  if (aiActive) stopAI();
  else startAI();
});

// ---- UI 更新 ----
function updateUI() {
  if (state) moveCountEl.textContent = '步数：' + state.moves;
  refreshAnswerUI();
}

// ---- 事件绑定 ----
levelSelect.addEventListener('change', () => {
  loadLevel(parseInt(levelSelect.value, 10));
});
undoBtn.addEventListener('click', undo);
resetBtn.addEventListener('click', resetLevel);

const shortcutOverlay = document.getElementById('shortcutOverlay');
const shortcutBtn = document.getElementById('shortcutBtn');
const shortcutCloseBtn = document.getElementById('shortcutCloseBtn');
shortcutBtn.addEventListener('click', () => shortcutOverlay.classList.remove('hidden'));
shortcutCloseBtn.addEventListener('click', () => shortcutOverlay.classList.add('hidden'));
shortcutOverlay.addEventListener('click', (e) => {
  if (e.target === shortcutOverlay) shortcutOverlay.classList.add('hidden');
});

nextLevelBtn.addEventListener('click', () => {
  if (!state) return;
  const next = state.levelIndex + 1;
  if (next < LEVELS_DATA.length) loadLevel(next);
  else winOverlay.classList.add('hidden');
});

// ---- 渲染循环与尺寸 ----
function resizeRenderer() {
  const wrap = document.getElementById('canvasWrap');
  const w = wrap.clientWidth;
  const h = wrap.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resizeRenderer);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

// ---- 初始化 ----
populateLevelSelect();
resizeRenderer();
loadLevel(getLastLevel());
animate();
