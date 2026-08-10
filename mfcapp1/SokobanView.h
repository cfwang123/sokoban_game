// mfcapp1 — MFC 视图：GDI 绘制 + 键盘
#pragma once
#include <afxwin.h>

class CSokobanDoc;

class CSokobanView : public CView {
public:
    CSokobanDoc *GetDocument() const;
    virtual void OnDraw(CDC *pDC);
    afx_msg void OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags);
    DECLARE_DYNCREATE(CSokobanView)
    DECLARE_MESSAGE_MAP()
};
