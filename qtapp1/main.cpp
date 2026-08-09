/**
 * qtapp1 — Qt Widgets 推箱子桌面 demo（教学）
 * 需 Qt5/Qt6：qmake 或 cmake。
 */
#include <QApplication>
#include <QWidget>
#include <QPainter>
#include <QKeyEvent>
#include <QVector>
#include <QSet>
#include <QStringList>

static const int CELL = 40;
static const int PAD = 20;

struct Hist {
    QPoint player;
    QString boxFrom;
    QString boxTo;
    bool push = false;
};

class Board : public QWidget {
public:
    Board(QWidget *parent = nullptr) : QWidget(parent) {
        setFocusPolicy(Qt::StrongFocus);
        load();
        setFixedSize(PAD * 2 + w * CELL, PAD * 2 + h * CELL + 24);
        setWindowTitle(QStringLiteral("Sokoban Qt"));
    }

protected:
    void paintEvent(QPaintEvent *) override {
        QPainter p(this);
        p.fillRect(rect(), QColor(26, 26, 46));
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                QString k = key(x, y);
                QRect rc(PAD + x * CELL, PAD + y * CELL, CELL, CELL);
                if (walls.contains(k)) {
                    p.fillRect(rc, QColor(74, 74, 106));
                } else {
                    p.fillRect(rc, QColor(58, 58, 85));
                    p.setPen(QColor(68, 68, 102));
                    p.drawRect(rc);
                }
                if (goals.contains(k)) {
                    p.setBrush(QColor(233, 69, 96));
                    p.setPen(Qt::NoPen);
                    p.drawEllipse(rc.center(), 6, 6);
                }
                if (boxes.contains(k)) {
                    bool on = goals.contains(k);
                    p.fillRect(rc.adjusted(4, 4, -4, -4),
                                on ? QColor(46, 204, 113) : QColor(243, 156, 18));
                }
                if (player == QPoint(x, y)) {
                    p.setBrush(QColor(52, 152, 219));
                    p.setPen(Qt::NoPen);
                    p.drawEllipse(rc.center(), int(CELL * 0.35), int(CELL * 0.35));
                }
            }
        }
        p.setPen(Qt::white);
        p.drawText(8, height() - 6,
                   QString("moves=%1%2  WASD Z R Q")
                       .arg(moves)
                       .arg(won ? " WIN" : ""));
    }

    void keyPressEvent(QKeyEvent *e) override {
        switch (e->key()) {
        case Qt::Key_W: case Qt::Key_Up: tryMove(0, -1); break;
        case Qt::Key_S: case Qt::Key_Down: tryMove(0, 1); break;
        case Qt::Key_A: case Qt::Key_Left: tryMove(-1, 0); break;
        case Qt::Key_D: case Qt::Key_Right: tryMove(1, 0); break;
        case Qt::Key_Z: undo(); break;
        case Qt::Key_R: load(); break;
        case Qt::Key_Q: case Qt::Key_Escape: close(); break;
        default: QWidget::keyPressEvent(e); return;
        }
        update();
    }

private:
    static QString key(int x, int y) { return QString("%1,%2").arg(x).arg(y); }

    void load() {
        static const char *rows[] = {
            "#######",
            "#. . .#",
            "# $$$ #",
            "#.$@$.#",
            "# $$$ #",
            "#. . .#",
            "#######",
        };
        walls.clear(); goals.clear(); boxes.clear(); hist.clear();
        moves = 0; won = false; player = QPoint(0, 0);
        h = 7; w = 0;
        for (int y = 0; y < 7; y++) {
            QByteArray row(rows[y]);
            if (row.size() > w) w = row.size();
            for (int x = 0; x < row.size(); x++) {
                char ch = row[x];
                QString k = key(x, y);
                if (ch == '#') walls.insert(k);
                else if (ch == '.') goals.insert(k);
                else if (ch == '$') boxes.insert(k);
                else if (ch == '*') { boxes.insert(k); goals.insert(k); }
                else if (ch == '@') player = QPoint(x, y);
                else if (ch == '+') { player = QPoint(x, y); goals.insert(k); }
            }
        }
    }

    void checkWin() {
        for (const QString &b : boxes)
            if (!goals.contains(b)) { won = false; return; }
        won = true;
    }

    void tryMove(int dx, int dy) {
        if (won) return;
        int nx = player.x() + dx, ny = player.y() + dy;
        QString nk = key(nx, ny);
        if (walls.contains(nk)) return;
        if (boxes.contains(nk)) {
            int bx = nx + dx, by = ny + dy;
            QString bk = key(bx, by);
            if (walls.contains(bk) || boxes.contains(bk)) return;
            hist.append({player, nk, bk, true});
            boxes.remove(nk); boxes.insert(bk);
            player = QPoint(nx, ny);
            moves++;
            checkWin();
            return;
        }
        hist.append({player, QString(), QString(), false});
        player = QPoint(nx, ny);
    }

    void undo() {
        if (won || hist.isEmpty()) return;
        Hist e;
        while (!hist.isEmpty()) {
            e = hist.takeLast();
            if (e.push) break;
            player = e.player;
        }
        if (!e.push) return;
        player = e.player;
        boxes.remove(e.boxTo);
        boxes.insert(e.boxFrom);
        if (moves > 0) moves--;
        won = false;
    }

    QSet<QString> walls, goals, boxes;
    QPoint player;
    int moves = 0;
    bool won = false;
    int w = 0, h = 0;
    QVector<Hist> hist;
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    Board board;
    board.show();
    return app.exec();
}
