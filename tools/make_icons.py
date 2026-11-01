#!/usr/bin/env python3
"""Make the LAST and BRIDGE app icons.

Writes:
  LAST/last-icon.png      512x512 LAST icon (window icon; installed as pixmaps/last.png)
  BRIDGE/bridge-icon.png  512x512 BRIDGE icon (window icon; installed as pixmaps/bridge.png)

LAST is a DE-9 serial plug inside a ticked ring with TX/RX arrows; BRIDGE is an arch bridge
between two virtual ports with the null-modem crossover under its deck. Both are drawn in the
same style as the PyGEM and Pylot icons. The apps scale the PNG down for the window themselves.

Run from anywhere: python3 tools/make_icons.py. Needs PySide6 (drawing).
"""
from __future__ import annotations

import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAST_PNG = os.path.join(ROOT, "LAST", "last-icon.png")
BRIDGE_PNG = os.path.join(ROOT, "BRIDGE", "bridge-icon.png")
SIZE = 512


def start(top, bottom):
    """A transparent image with the rounded gradient tile drawn, and its painter."""
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter

    img = QImage(SIZE, SIZE, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    tile = QRectF(8, 8, SIZE - 16, SIZE - 16)
    grad = QLinearGradient(tile.topLeft(), tile.bottomRight())
    grad.setColorAt(0, QColor(top))
    grad.setColorAt(1, QColor(bottom))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(grad)
    p.drawRoundedRect(tile, 96, 96)
    return img, p


def pen(color, width):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QPen

    return QPen(QColor(color), width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)


def draw_last(path: str):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QColor, QPolygonF

    img, p = start("#1a4a7a", "#081a2e")
    c = QPointF(SIZE / 2, SIZE / 2)
    R = 196.0

    def polar(r, a):
        rad = math.radians(a)
        return QPointF(c.x() + r * math.sin(rad), c.y() - r * math.cos(rad))

    # ring with degree ticks
    p.setPen(pen("#3d9bff", 10))
    p.setBrush(QColor("#0c2440"))
    p.drawEllipse(c, R, R)
    for a in range(0, 360, 10):
        major = a % 90 == 0
        p.setPen(pen("#e6edf5", 8 if major else 4))
        p.drawLine(polar(R - (38 if major else 22), a), polar(R - 10, a))

    # DE-9 plug: shell, face, 5 + 4 pins
    def trapezoid(cx, cy, top_w, bottom_w, h):
        return QPolygonF([QPointF(cx - top_w / 2, cy - h / 2), QPointF(cx + top_w / 2, cy - h / 2),
                          QPointF(cx + bottom_w / 2, cy + h / 2), QPointF(cx - bottom_w / 2, cy + h / 2)])

    pc, w, h = QPointF(256, 262), 236, 112
    p.setPen(pen("#9fb3c8", 10))
    p.setBrush(QColor("#9fb3c8"))
    p.drawPolygon(trapezoid(pc.x(), pc.y(), w, w * 0.78, h))
    p.setPen(pen("#0c2440", 6))
    p.setBrush(QColor("#0c2440"))
    p.drawPolygon(trapezoid(pc.x(), pc.y(), w * 0.84, w * 0.84 * 0.76, h * 0.68))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#e6edf5"))
    gap = w * 0.84 / 6.2
    for i in range(5):
        p.drawEllipse(QPointF(pc.x() + (i - 2) * gap, pc.y() - h * 0.14), 13, 13)
    for i in range(4):
        p.drawEllipse(QPointF(pc.x() + (i - 1.5) * gap, pc.y() + h * 0.15), 13, 13)

    # TX (out, orange) and RX (in, green) arrows
    def arrow(a, b, color):
        head = 36
        ang = math.atan2(b.y() - a.y(), b.x() - a.x())
        p.setPen(pen(color, 14))
        p.drawLine(a, QPointF(b.x() - math.cos(ang) * head * 0.6, b.y() - math.sin(ang) * head * 0.6))
        p.setPen(pen(color, 4))
        p.setBrush(QColor(color))
        p.drawPolygon(QPolygonF([b, QPointF(b.x() - head * math.cos(ang - 0.5), b.y() - head * math.sin(ang - 0.5)),
                                 QPointF(b.x() - head * math.cos(ang + 0.5), b.y() - head * math.sin(ang + 0.5))]))

    arrow(QPointF(150, 160), QPointF(362, 160), "#ff6a3d")
    arrow(QPointF(362, 362), QPointF(150, 362), "#3fd365")
    p.end()
    img.save(path)


def draw_bridge(path: str):
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QPainterPath

    img, p = start("#0f5c8c", "#062a45")
    deck_y = 280
    ends, rise = (96, 416), 100   # arch feet x, and the control points' height

    def arch_point(t):
        x = (1 - t) ** 3 * 96 + 3 * (1 - t) ** 2 * t * 150 + 3 * (1 - t) * t ** 2 * 362 + t ** 3 * 416
        y = (1 - t) ** 3 * deck_y + 3 * (1 - t) ** 2 * t * rise + 3 * (1 - t) * t ** 2 * rise + t ** 3 * deck_y
        return QPointF(x, y)

    # hangers, then the arch over them
    p.setPen(pen("#9cc9e6", 6))
    for i in range(1, 8):
        top = arch_point(i / 8)
        p.drawLine(top, QPointF(top.x(), deck_y))
    arch = QPainterPath(QPointF(ends[0], deck_y))
    arch.cubicTo(QPointF(150, rise), QPointF(362, rise), QPointF(ends[1], deck_y))
    p.setPen(pen("#e6edf5", 16))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(arch)
    # null-modem crossover under the deck: TX of each end goes to RX of the other
    p.setPen(pen("#ffd23f", 12))
    p.drawLine(QPointF(130, deck_y + 34), QPointF(382, deck_y + 84))
    p.setPen(pen("#3fd365", 12))
    p.drawLine(QPointF(130, deck_y + 84), QPointF(382, deck_y + 34))
    deck = pen("#e6edf5", 14)
    deck.setCapStyle(Qt.PenCapStyle.FlatCap)
    p.setPen(deck)
    p.drawLine(QPointF(70, deck_y), QPointF(442, deck_y))
    # the two virtual ports at the arch feet
    for x in ends:
        p.setPen(pen("#062a45", 8))
        p.setBrush(QColor("#5fb8f0"))
        p.drawRoundedRect(QRectF(x - 40, deck_y + 24, 80, 70), 16, 16)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#062a45"))
        for dx in (-18, 0, 18):
            p.drawEllipse(QPointF(x + dx, deck_y + 50), 5, 5)
        for dx in (-9, 9):
            p.drawEllipse(QPointF(x + dx, deck_y + 70), 5, 5)
    p.end()
    img.save(path)


def main():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841 (QPainter needs an app)
    draw_last(LAST_PNG)
    draw_bridge(BRIDGE_PNG)
    print(f"Icons written: {LAST_PNG}, {BRIDGE_PNG}")


if __name__ == "__main__":
    main()
