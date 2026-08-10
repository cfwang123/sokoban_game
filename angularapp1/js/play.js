/* 零构建可玩；Angular 组件见 src/app/app.component.ts */
(function () {
  var state = SokobanCore.newGame();
  var board = document.getElementById('board');
  var status = document.getElementById('status');

  function render() {
    board.innerHTML = '';
    for (var y = 0; y < state.height; y++) {
      var row = document.createElement('div');
      row.className = 'row';
      for (var x = 0; x < state.width; x++) {
        var ch = SokobanCore.cellAt(state, x, y);
        var span = document.createElement('span');
        span.className = 'cell';
        if (ch === '#') span.className += ' c-wall';
        else if (ch === '.') span.className += ' c-goal';
        else if (ch === '$') span.className += ' c-box';
        else if (ch === '*') span.className += ' c-boxg';
        else if (ch === '@' || ch === '+') span.className += ' c-player';
        span.textContent = ch;
        row.appendChild(span);
      }
      board.appendChild(row);
    }
    status.textContent = 'moves=' + state.moves + (state.won ? ' WIN!' : '');
  }

  document.querySelectorAll('.btns button[data-dx]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      SokobanCore.tryMove(state, +btn.getAttribute('data-dx'), +btn.getAttribute('data-dy'));
      render();
    });
  });
  document.getElementById('btnZ').onclick = function () {
    SokobanCore.undo(state);
    render();
  };
  document.getElementById('btnR').onclick = function () {
    state = SokobanCore.newGame();
    render();
  };
  window.addEventListener('keydown', function (e) {
    var k = e.key.toLowerCase();
    if (k === 'w' || e.key === 'ArrowUp') SokobanCore.tryMove(state, 0, -1);
    else if (k === 's' || e.key === 'ArrowDown') SokobanCore.tryMove(state, 0, 1);
    else if (k === 'a' || e.key === 'ArrowLeft') SokobanCore.tryMove(state, -1, 0);
    else if (k === 'd' || e.key === 'ArrowRight') SokobanCore.tryMove(state, 1, 0);
    else if (k === 'z') SokobanCore.undo(state);
    else if (k === 'r') state = SokobanCore.newGame();
    else return;
    render();
  });
  render();
})();
