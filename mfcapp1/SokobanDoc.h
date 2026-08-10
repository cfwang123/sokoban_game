// mfcapp1 — MFC 推箱子教学：文档类持有游戏状态
// 不要求在本仓库内编译；示意 MFC Doc/View 分层。
#pragma once

#include <afxwin.h>
#include <vector>
#include <set>
#include <string>

struct Hist {
    int px, py;
    CString boxFrom, boxTo;
    BOOL isPush;
};

class CSokobanDoc : public CDocument {
public:
    std::set<CString> walls, goals, boxes;
    int px, py, moves, width, height;
    BOOL won;
    std::vector<Hist> hist;

    CSokobanDoc();
    void LoadLevel();
    BOOL TryMove(int dx, int dy);
    BOOL Undo();
    CString Key(int x, int y) const;

    DECLARE_DYNCREATE(CSokobanDoc)
    DECLARE_MESSAGE_MAP()
};
