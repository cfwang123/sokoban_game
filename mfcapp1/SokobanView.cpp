// mfcapp1 — MFC 视图绘制（教学）
#include "SokobanView.h"
#include "SokobanDoc.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

#define CELL 40
#define PAD 16

IMPLEMENT_DYNCREATE(CSokobanView, CView)

BEGIN_MESSAGE_MAP(CSokobanView, CView)
    ON_WM_KEYDOWN()
END_MESSAGE_MAP()

CSokobanDoc *CSokobanView::GetDocument() const
{
    return (CSokobanDoc *)m_pDocument;
}

void CSokobanView::OnDraw(CDC *pDC)
{
    CSokobanDoc *pDoc = GetDocument();
    if (!pDoc) return;

    CRect client;
    GetClientRect(&client);
    pDC->FillSolidRect(&client, RGB(26, 26, 46));

    for (int y = 0; y < pDoc->height; y++) {
        for (int x = 0; x < pDoc->width; x++) {
            CString k = pDoc->Key(x, y);
            CRect rc(PAD + x * CELL, PAD + y * CELL,
                     PAD + (x + 1) * CELL, PAD + (y + 1) * CELL);
            if (pDoc->walls.count(k)) {
                pDC->FillSolidRect(&rc, RGB(74, 74, 106));
            } else {
                pDC->FillSolidRect(&rc, RGB(58, 58, 85));
                pDC->Draw3dRect(&rc, RGB(68, 68, 102), RGB(68, 68, 102));
                if (pDoc->goals.count(k)) {
                    CBrush br(RGB(233, 69, 96));
                    CBrush *old = pDC->SelectObject(&br);
                    pDC->Ellipse(rc.CenterPoint().x - 6, rc.CenterPoint().y - 6,
                                 rc.CenterPoint().x + 6, rc.CenterPoint().y + 6);
                    pDC->SelectObject(old);
                }
                if (pDoc->boxes.count(k)) {
                    BOOL on = pDoc->goals.count(k) != 0;
                    CRect b = rc;
                    b.DeflateRect(4, 4);
                    pDC->FillSolidRect(&b, on ? RGB(46, 204, 113) : RGB(243, 156, 18));
                }
            }
            if (pDoc->px == x && pDoc->py == y) {
                CBrush br(RGB(52, 152, 219));
                CBrush *old = pDC->SelectObject(&br);
                pDC->Ellipse(rc.left + 6, rc.top + 6, rc.right - 6, rc.bottom - 6);
                pDC->SelectObject(old);
            }
        }
    }

    CString status;
    status.Format(_T("moves=%d%s  WASD Z R Esc"), pDoc->moves,
                  pDoc->won ? _T(" WIN") : _T(""));
    pDC->SetTextColor(RGB(255, 255, 255));
    pDC->SetBkMode(TRANSPARENT);
    pDC->TextOut(8, PAD + pDoc->height * CELL + 4, status);
}

void CSokobanView::OnKeyDown(UINT nChar, UINT nRepCnt, UINT nFlags)
{
    CSokobanDoc *pDoc = GetDocument();
    if (!pDoc) return;
    BOOL dirty = FALSE;
    switch (nChar) {
    case 'W': case VK_UP:    dirty = pDoc->TryMove(0, -1); break;
    case 'S': case VK_DOWN:  dirty = pDoc->TryMove(0, 1); break;
    case 'A': case VK_LEFT:  dirty = pDoc->TryMove(-1, 0); break;
    case 'D': case VK_RIGHT: dirty = pDoc->TryMove(1, 0); break;
    case 'Z': dirty = pDoc->Undo(); break;
    case 'R': pDoc->LoadLevel(); dirty = TRUE; break;
    case VK_ESCAPE: case 'Q':
        AfxGetMainWnd()->PostMessage(WM_CLOSE);
        return;
    }
    if (dirty) Invalidate();
    CView::OnKeyDown(nChar, nRepCnt, nFlags);
}
