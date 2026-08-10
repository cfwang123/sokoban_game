/* reactapp1 — React 推箱子教学（CDN + Babel，无需 npm build） */
const { useState, useEffect, useCallback } = React;

function Board({ state }) {
  const rows = [];
  for (let y = 0; y < state.height; y++) {
    const cells = [];
    for (let x = 0; x < state.width; x++) {
      const ch = SokobanCore.cellAt(state, x, y);
      cells.push(
        <span key={x + "," + y} className={"cell c-" + (ch === " " ? "floor" : ch === "#" ? "wall" : ch === "." ? "goal" : ch === "$" ? "box" : ch === "*" ? "boxg" : ch === "@" || ch === "+" ? "player" : "floor")}>
          {ch === " " ? "\u00a0" : ch}
        </span>
      );
    }
    rows.push(
      <div className="row" key={y}>
        {cells}
      </div>
    );
  }
  return <div className="board">{rows}</div>;
}

function App() {
  const [state, setState] = useState(() => SokobanCore.newGame());

  const apply = useCallback((fn) => {
    setState((prev) => {
      const next = SokobanCore.cloneState(prev);
      fn(next);
      return next;
    });
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      const k = e.key.toLowerCase();
      if (k === "w" || e.key === "ArrowUp") apply((s) => SokobanCore.tryMove(s, 0, -1));
      else if (k === "s" || e.key === "ArrowDown") apply((s) => SokobanCore.tryMove(s, 0, 1));
      else if (k === "a" || e.key === "ArrowLeft") apply((s) => SokobanCore.tryMove(s, -1, 0));
      else if (k === "d" || e.key === "ArrowRight") apply((s) => SokobanCore.tryMove(s, 1, 0));
      else if (k === "z") apply((s) => SokobanCore.undo(s));
      else if (k === "r") setState(SokobanCore.newGame());
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [apply]);

  return (
    <div className="app">
      <h1>Sokoban · React</h1>
      <p className="hint">WASD / 方向键 · Z 撤销 · R 重置 · 无需 npm 构建</p>
      <Board state={state} />
      <p className="status">
        moves={state.moves}
        {state.won ? " WIN!" : ""}
      </p>
      {state.won && <p className="win">Level clear!</p>}
      <div className="btns">
        <button type="button" onClick={() => apply((s) => SokobanCore.tryMove(s, 0, -1))}>W</button>
        <button type="button" onClick={() => apply((s) => SokobanCore.tryMove(s, -1, 0))}>A</button>
        <button type="button" onClick={() => apply((s) => SokobanCore.tryMove(s, 0, 1))}>S</button>
        <button type="button" onClick={() => apply((s) => SokobanCore.tryMove(s, 1, 0))}>D</button>
        <button type="button" onClick={() => apply((s) => SokobanCore.undo(s))}>Z</button>
        <button type="button" onClick={() => setState(SokobanCore.newGame())}>R</button>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
