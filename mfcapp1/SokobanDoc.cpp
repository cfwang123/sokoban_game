// mfcapp1 — MFC 文档：玩法核心（教学）
#include "SokobanDoc.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

IMPLEMENT_DYNCREATE(CSokobanDoc, CDocument)

BEGIN_MESSAGE_MAP(CSokobanDoc, CDocument)
END_MESSAGE_MAP()

static const char *LEVEL[] = {
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
};

CSokobanDoc::CSokobanDoc()
{
    LoadLevel();
}

CString CSokobanDoc::Key(int x, int y) const
{
    CString s;
    s.Format(_T("%d,%d"), x, y);
    return s;
}

void CSokobanDoc::LoadLevel()
{
    walls.clear();
    goals.clear();
    boxes.clear();
    hist.clear();
    moves = 0;
    won = FALSE;
    px = py = 0;
    width = height = 0;
    int maxX = 0, maxY = 0;
    for (int y = 0; y < 7; y++) {
        maxY = y;
        const char *row = LEVEL[y];
        for (int x = 0; row[x]; x++) {
            if (x > maxX) maxX = x;
            CString k = Key(x, y);
            switch (row[x]) {
            case '#': walls.insert(k); break;
            case '.': goals.insert(k); break;
            case '$': boxes.insert(k); break;
            case '*': boxes.insert(k); goals.insert(k); break;
            case '@': px = x; py = y; break;
            case '+': px = x; py = y; goals.insert(k); break;
            }
        }
    }
    width = maxX + 1;
    height = maxY + 1;
}

BOOL CSokobanDoc::TryMove(int dx, int dy)
{
    if (won) return FALSE;
    int nx = px + dx, ny = py + dy;
    CString nk = Key(nx, ny);
    if (walls.count(nk)) return FALSE;
    if (boxes.count(nk)) {
        int bx = nx + dx, by = ny + dy;
        CString bk = Key(bx, by);
        if (walls.count(bk) || boxes.count(bk)) return FALSE;
        Hist h = { px, py, nk, bk, TRUE };
        hist.push_back(h);
        boxes.erase(nk);
        boxes.insert(bk);
        px = nx;
        py = ny;
        moves++;
        won = TRUE;
        for (const auto &b : boxes)
            if (!goals.count(b)) { won = FALSE; break; }
        return TRUE;
    }
    Hist h = { px, py, _T(""), _T(""), FALSE };
    hist.push_back(h);
    px = nx;
    py = ny;
    return TRUE;
}

BOOL CSokobanDoc::Undo()
{
    if (won || hist.empty()) return FALSE;
    while (!hist.empty()) {
        Hist e = hist.back();
        hist.pop_back();
        if (e.isPush) {
            px = e.px;
            py = e.py;
            boxes.erase((LPCTSTR)e.boxTo);
            boxes.insert((LPCTSTR)e.boxFrom);
            if (moves > 0) moves--;
            won = FALSE;
            return TRUE;
        }
        px = e.px;
        py = e.py;
    }
    return TRUE;
}
