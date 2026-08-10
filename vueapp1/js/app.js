/* vueapp1 — Vue 3 推箱子教学（CDN，无构建） */
const { createApp, reactive, onMounted, onUnmounted } = Vue;

createApp({
  setup() {
    const state = reactive(SokobanCore.newGame());

    function move(dx, dy) {
      SokobanCore.tryMove(state, dx, dy);
    }
    function doUndo() {
      SokobanCore.undo(state);
    }
    function reset() {
      const g = SokobanCore.newGame();
      Object.keys(state).forEach((k) => delete state[k]);
      Object.assign(state, g);
    }
    function cellChar(x, y) {
      return SokobanCore.cellAt(state, x, y);
    }
    function cellClass(x, y) {
      const ch = SokobanCore.cellAt(state, x, y);
      if (ch === '#') return 'c-wall';
      if (ch === '.') return 'c-goal';
      if (ch === '$') return 'c-box';
      if (ch === '*') return 'c-boxg';
      if (ch === '@' || ch === '+') return 'c-player';
      return 'c-floor';
    }
    function onKey(e) {
      const k = e.key.toLowerCase();
      if (k === 'w' || e.key === 'ArrowUp') move(0, -1);
      else if (k === 's' || e.key === 'ArrowDown') move(0, 1);
      else if (k === 'a' || e.key === 'ArrowLeft') move(-1, 0);
      else if (k === 'd' || e.key === 'ArrowRight') move(1, 0);
      else if (k === 'z') doUndo();
      else if (k === 'r') reset();
    }
    onMounted(() => window.addEventListener('keydown', onKey));
    onUnmounted(() => window.removeEventListener('keydown', onKey));
    return { state, move, doUndo, reset, cellChar, cellClass };
  },
}).mount('#app');
