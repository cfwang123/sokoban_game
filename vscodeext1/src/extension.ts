import * as vscode from "vscode";

/**
 * VS Code 扩展入口（教学）。
 * 命令「Sokoban: Open Game」打开 Webview，内嵌简易推箱子。
 */
export function activate(context: vscode.ExtensionContext) {
  const cmd = vscode.commands.registerCommand("sokoban.open", () => {
    const panel = vscode.window.createWebviewPanel(
      "sokoban",
      "推箱子",
      vscode.ViewColumn.Beside,
      { enableScripts: true, retainContextWhenHidden: true }
    );
    panel.webview.html = getHtml();
  });
  context.subscriptions.push(cmd);
}

export function deactivate() {}

function getHtml(): string {
  // 内联完整小游戏，避免额外资源路径问题
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Sokoban</title>
<style>
  body { margin:0; background:#1a1a2e; color:#eee; font-family:system-ui,sans-serif; }
  #bar { padding:8px 12px; display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
  button { background:#0f3460; color:#eee; border:1px solid #533483; border-radius:6px; padding:6px 10px; cursor:pointer; }
  canvas { display:block; margin:0 auto; background:#2d2d44; border-radius:8px; }
  #status { color:#aaa; font-size:12px; }
</style>
</head>
<body>
<div id="bar">
  <strong>推箱子</strong>
  <span id="info">LV1</span>
  <button id="undo">撤销</button>
  <button id="reset">重置</button>
  <button id="prev">上一关</button>
  <button id="next">下一关</button>
  <span id="status"></span>
</div>
<canvas id="c" width="360" height="360"></canvas>
<script>
const LEVELS = [
  { name:"1 L", puzzle:["###","#@#","#$#","#.#","###"] },
  { name:"1 R", puzzle:["#####","#.$@#","#####"] },
  { name:"Star", puzzle:["#######","#. . .#","# $$$ #","#.$@$.#","# $$$ #","#. . .#","#######"] }
];
let li=0, state=null;
const canvas=document.getElementById('c'), ctx=canvas.getContext('2d');

function parse(rows, index){
  const walls=new Set(), goals=new Set(), boxes=new Set();
  let player={x:0,y:0}, maxX=0, maxY=0;
  for(let y=0;y<rows.length;y++){
    maxY=y; const row=rows[y];
    for(let x=0;x<row.length;x++){
      maxX=Math.max(maxX,x); const k=x+','+y, ch=row[x];
      if(ch==='#') walls.add(k);
      else if(ch==='.') goals.add(k);
      else if(ch==='$') boxes.add(k);
      else if(ch==='*'){ boxes.add(k); goals.add(k); }
      else if(ch==='@') player={x,y};
      else if(ch==='+'){ player={x,y}; goals.add(k); }
    }
  }
  return {walls,goals,boxes,player,moves:0,won:false,history:[],w:maxX+1,h:maxY+1,index};
}
function tryMove(s,dx,dy){
  if(s.won) return;
  const nx=s.player.x+dx, ny=s.player.y+dy, nk=nx+','+ny;
  if(s.walls.has(nk)) return;
  if(s.boxes.has(nk)){
    const bk=(nx+dx)+','+(ny+dy);
    if(s.walls.has(bk)||s.boxes.has(bk)) return;
    s.history.push({px:s.player.x,py:s.player.y,from:nk,to:bk,push:true});
    s.boxes.delete(nk); s.boxes.add(bk);
    s.player={x:nx,y:ny}; s.moves++;
    s.won=[...s.boxes].every(b=>s.goals.has(b));
    return;
  }
  s.history.push({px:s.player.x,py:s.player.y,push:false});
  s.player={x:nx,y:ny};
}
function undo(s){
  if(s.won||!s.history.length) return;
  let e;
  while(s.history.length){
    e=s.history.pop();
    if(e.push) break;
    s.player={x:e.px,y:e.py};
  }
  if(!e||!e.push) return;
  s.player={x:e.px,y:e.py};
  s.boxes.delete(e.to); s.boxes.add(e.from);
  if(s.moves>0) s.moves--;
  s.won=false;
}
function load(i){
  li=Math.max(0,Math.min(LEVELS.length-1,i));
  state=parse(LEVELS[li].puzzle, li);
  draw();
}
function draw(){
  const s=state, pad=12;
  const cell=Math.floor(Math.min((canvas.width-pad*2)/s.w,(canvas.height-pad*2)/s.h));
  const ox=(canvas.width-cell*s.w)/2, oy=(canvas.height-cell*s.h)/2;
  ctx.fillStyle='#2d2d44'; ctx.fillRect(0,0,canvas.width,canvas.height);
  for(let y=0;y<s.h;y++) for(let x=0;x<s.w;x++){
    const k=x+','+y, px=ox+x*cell, py=oy+y*cell;
    ctx.fillStyle=s.walls.has(k)?'#4a4a6a':'#3a3a55';
    ctx.fillRect(px,py,cell-1,cell-1);
    if(s.goals.has(k)){ ctx.fillStyle='#e94560'; ctx.beginPath(); ctx.arc(px+cell/2,py+cell/2,cell*0.12,0,Math.PI*2); ctx.fill(); }
    if(s.boxes.has(k)){ ctx.fillStyle=s.goals.has(k)?'#2ecc71':'#f39c12'; ctx.fillRect(px+3,py+3,cell-7,cell-7); }
  }
  ctx.fillStyle='#3498db';
  ctx.beginPath();
  ctx.arc(ox+s.player.x*cell+cell/2, oy+s.player.y*cell+cell/2, cell*0.32, 0, Math.PI*2);
  ctx.fill();
  document.getElementById('info').textContent='LV'+(li+1)+'/'+LEVELS.length+' · '+LEVELS[li].name+' · 步'+s.moves;
  document.getElementById('status').textContent=s.won?'过关！':'方向键/WASD 移动';
}
window.addEventListener('keydown', e=>{
  const m={ArrowUp:[0,-1],ArrowDown:[0,1],ArrowLeft:[-1,0],ArrowRight:[1,0],w:[0,-1],s:[0,1],a:[-1,0],d:[1,0],W:[0,-1],S:[0,1],A:[-1,0],D:[1,0]};
  if(e.key==='z'||e.key==='Z'){ undo(state); draw(); e.preventDefault(); return; }
  if(e.key==='r'||e.key==='R'){ load(li); e.preventDefault(); return; }
  const d=m[e.key]; if(d){ tryMove(state,d[0],d[1]); draw(); e.preventDefault(); }
});
document.getElementById('undo').onclick=()=>{ undo(state); draw(); };
document.getElementById('reset').onclick=()=>load(li);
document.getElementById('prev').onclick=()=>load(li-1);
document.getElementById('next').onclick=()=>load(li+1);
load(0);
</script>
</body>
</html>`;
}
