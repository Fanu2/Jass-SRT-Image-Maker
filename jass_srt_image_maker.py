#!/usr/bin/env python3
"""
Jass SRT Image Maker v1.0
A standalone PySide6 SRT -> beautiful PNG card generator.

Requirements:
    pip install PySide6

Run:
    py jass_srt_image_maker.py
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import (
    QColor, QFont, QFontDatabase, QImage, QLinearGradient, QPainter,
    QPainterPath, QPen, QRadialGradient, QTransform
)
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QColorDialog, QComboBox, QFileDialog, QFontComboBox,
    QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QScrollArea, QSlider,
    QSpinBox, QDoubleSpinBox, QSplitter, QTabWidget, QTextEdit, QVBoxLayout, QWidget
)


@dataclass
class Subtitle:
    index: int
    start: str
    end: str
    text: str


def time_to_ms(value: str) -> int:
    h, m, s, ms = map(int, re.split(r"[:,]", value))
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def ms_to_time(ms: int) -> str:
    ms = max(0, ms)
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(text: str):
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    entries = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        try:
            idx = int(lines[0].strip())
            times = lines[1].strip()
            start, end = re.split(r"\s*-->\s*", times, maxsplit=1)
            body = "\n".join(lines[2:]).strip()
            entries.append(Subtitle(idx, start.strip(), end.strip(), body))
        except Exception:
            continue
    return entries


def srt_text(entries):
    return "\n\n".join(
        f"{i}\n{e.start} --> {e.end}\n{e.text}"
        for i, e in enumerate(entries, 1)
    ) + ("\n" if entries else "")


class Design:
    def __init__(self):
        self.preset = "Romantic Rose"
        self.bg1 = "#2b0b20"
        self.bg2 = "#7b174d"
        self.bg3 = "#f08aa7"
        self.text1 = "#fff7fb"
        self.text2 = "#ffd1e3"
        self.accent = "#ff5c9a"
        self.outline = "#5a173d"
        self.shadow = "#12050d"
        self.font_size = 58
        self.bold = True
        self.italic = False
        self.outline_width = 2
        self.shadow_blur = 8
        self.shadow_offset = 7
        self.padding = 80
        self.position = "Center"
        self.decoration = "Hearts"
        self.decoration_strength = 70
        self.overlay = 22
        self.rounded_card = True
        self.card_opacity = 30
        self.card_radius = 38
        self.glow = True
        self.word_highlight = False
        self.width = 1080
        self.height = 1920


PRESETS = {
    "Romantic Rose": dict(bg1="#23091a", bg2="#7d174c", bg3="#f49ab6", text1="#fffafd", text2="#ffd0e1", accent="#ff5c9a", decoration="Hearts"),
    "Rose Garden": dict(bg1="#102d1d", bg2="#6f1741", bg3="#d889a4", text1="#fff8f2", text2="#ffe2d4", accent="#f2a2b8", decoration="Flowers"),
    "Golden Sunset": dict(bg1="#38110b", bg2="#d65327", bg3="#ffd166", text1="#fffaf0", text2="#ffe3a1", accent="#fff0a8", decoration="Sunset"),
    "Midnight Love": dict(bg1="#060b25", bg2="#24115c", bg3="#7d4bc7", text1="#ffffff", text2="#d7c9ff", accent="#b88cff", decoration="Stars"),
    "Purple Dream": dict(bg1="#1d0c35", bg2="#6d2aa8", bg3="#d17bea", text1="#fffaff", text2="#f0d7ff", accent="#e1a1ff", decoration="Sparkles"),
    "Stardust": dict(bg1="#050611", bg2="#182d63", bg3="#5b75c8", text1="#ffffff", text2="#dce7ff", accent="#a9c8ff", decoration="Stars"),
    "Elegant Gold": dict(bg1="#15120b", bg2="#5c4515", bg3="#d4a83d", text1="#fffdf4", text2="#f8e6a8", accent="#f7d56a", decoration="Gold"),
    "Passion": dict(bg1="#210507", bg2="#8d1018", bg3="#ed4d42", text1="#fffafa", text2="#ffc7c7", accent="#ff6d6d", decoration="Hearts"),
    "Soft Blossom": dict(bg1="#33213b", bg2="#9b6b9f", bg3="#f4c6dc", text1="#fffaff", text2="#ffe5f1", accent="#ffb7d4", decoration="Flowers"),
    "Cinematic": dict(bg1="#070707", bg2="#252525", bg3="#777777", text1="#ffffff", text2="#d5d5d5", accent="#ffffff", decoration="Minimal"),
}


class PreviewCanvas(QLabel):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 500)
        self.setStyleSheet("background:#151515; border:1px solid #333;")
        self._image = None

    def set_image(self, image):
        self._image = image
        self._refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self):
        if self._image is None:
            return
        pix = self._image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        from PySide6.QtGui import QPixmap
        self.setPixmap(QPixmap.fromImage(pix))


class Renderer:
    @staticmethod
    def color(hex_value):
        return QColor(hex_value)

    @classmethod
    def background(cls, w, h, d: Design):
        image = QImage(w, h, QImage.Format_ARGB32)
        image.fill(QColor(d.bg1))
        p = QPainter(image)
        p.setRenderHint(QPainter.Antialiasing)

        # Diagonal multi-stop gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(d.bg1))
        grad.setColorAt(0.48, QColor(d.bg2))
        grad.setColorAt(1.0, QColor(d.bg3))
        p.fillRect(0, 0, w, h, grad)

        # Large soft light pools
        pools = [
            (0.18, 0.18, 0.55, 0.0),
            (0.82, 0.70, 0.48, 0.0),
            (0.35, 0.95, 0.40, 0.0),
        ]
        for x, y, radius, alpha in pools:
            rg = QRadialGradient(w*x, h*y, min(w,h)*radius)
            c = QColor(d.accent)
            c.setAlpha(55)
            rg.setColorAt(0, c)
            c2 = QColor(d.accent)
            c2.setAlpha(0)
            rg.setColorAt(1, c2)
            p.fillRect(0, 0, w, h, rg)

        # Subtle diagonal sheen
        sheen = QLinearGradient(0, h*0.15, w, h*0.85)
        c = QColor("#ffffff")
        c.setAlpha(12)
        sheen.setColorAt(0, c)
        c.setAlpha(0)
        sheen.setColorAt(0.45, c)
        c.setAlpha(12)
        sheen.setColorAt(1, c)
        p.fillRect(0, 0, w, h, sheen)
        p.end()
        return image

    @staticmethod
    def draw_heart(p, cx, cy, size, color, alpha=170):
        path = QPainterPath()
        s = size
        path.moveTo(cx, cy + s*0.75)
        path.cubicTo(cx - s*1.35, cy - s*0.05, cx - s*0.75, cy - s*0.95, cx, cy - s*0.35)
        path.cubicTo(cx + s*0.75, cy - s*0.95, cx + s*1.35, cy - s*0.05, cx, cy + s*0.75)
        c = QColor(color)
        c.setAlpha(alpha)
        p.setBrush(c)
        p.setPen(Qt.NoPen)
        p.drawPath(path)

    @staticmethod
    def draw_star(p, cx, cy, r, color, alpha=170):
        path = QPainterPath()
        import math
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.38
            a = -math.pi/2 + i * math.pi/5
            pt = QPointF(cx + math.cos(a)*rr, cy + math.sin(a)*rr)
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)
        path.closeSubpath()
        c = QColor(color)
        c.setAlpha(alpha)
        p.setBrush(c)
        p.setPen(Qt.NoPen)
        p.drawPath(path)

    @staticmethod
    def draw_flower(p, cx, cy, r, color):
        c = QColor(color)
        c.setAlpha(105)
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        for dx, dy in [(0,-r), (r,0), (0,r), (-r,0), (r*.7,-r*.7), (-r*.7,-r*.7)]:
            p.drawEllipse(QPointF(cx+dx, cy+dy), r*.65, r*.65)
        center = QColor("#ffd166")
        center.setAlpha(190)
        p.setBrush(center)
        p.drawEllipse(QPointF(cx, cy), r*.45, r*.45)

    @classmethod
    def decorations(cls, p, w, h, d):
        strength = max(0, min(100, d.decoration_strength))
        count = max(5, int(10 * strength / 70))
        color = d.accent
        import math
        # deterministic pseudo positions, so previews don't jump
        points = [
            (0.10,0.12),(0.88,0.15),(0.15,0.33),(0.84,0.39),
            (0.08,0.62),(0.91,0.66),(0.19,0.84),(0.78,0.88),
            (0.50,0.10),(0.50,0.93),(0.30,0.20),(0.70,0.28)
        ][:count]
        p.save()
        for i, (x,y) in enumerate(points):
            size = 10 + (i % 4) * 5
            if d.decoration == "Hearts":
                cls.draw_heart(p, w*x, h*y, size, color, 90 + (i%3)*25)
            elif d.decoration == "Stars" or d.decoration == "Sparkles":
                cls.draw_star(p, w*x, h*y, size, color, 100 + (i%3)*25)
                if d.decoration == "Sparkles":
                    pen = QPen(QColor(color))
                    pen.setWidthF(2)
                    p.setPen(pen)
                    p.setOpacity(.5)
                    p.drawLine(w*x-size*1.6, h*y, w*x+size*1.6, h*y)
                    p.drawLine(w*x, h*y-size*1.6, w*x, h*y+size*1.6)
                    p.setOpacity(1)
            elif d.decoration == "Flowers":
                cls.draw_flower(p, w*x, h*y, size, color)
            elif d.decoration == "Sunset":
                rg = QRadialGradient(w*x, h*y, size*5)
                c = QColor(color); c.setAlpha(80)
                rg.setColorAt(0,c)
                c.setAlpha(0); rg.setColorAt(1,c)
                p.fillRect(QRectF(w*x-size*5,h*y-size*5,size*10,size*10), rg)
            elif d.decoration == "Gold":
                cls.draw_star(p, w*x, h*y, size, color, 85)
        p.restore()

    @classmethod
    def text_lines(cls, painter, rect, text, d):
        font = QFont(d.font_family)
        font.setPixelSize(d.font_size)
        font.setBold(d.bold)
        font.setItalic(d.italic)
        painter.setFont(font)

        # Word wrapping
        words = text.replace("\n", " \n ").split()
        lines, current = [], ""
        max_width = rect.width()
        for word in words:
            if word == "\n":
                if current:
                    lines.append(current); current = ""
                lines.append("")
                continue
            test = word if not current else current + " " + word
            if painter.fontMetrics().horizontalAdvance(test) <= max_width or not current:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines, painter.fontMetrics().lineSpacing()

    @classmethod
    def render(cls, text, d: Design):
        w, h = d.width, d.height
        image = cls.background(w, h, d)
        p = QPainter(image)
        p.setRenderHint(QPainter.Antialiasing)
        cls.decorations(p, w, h, d)

        # Main translucent card
        card_w = w - d.padding*2
        card_h = min(h*0.64, max(360, h*0.50))
        if d.position == "Top":
            card_y = h*0.18
        elif d.position == "Bottom":
            card_y = h*0.62 - card_h/2
        else:
            card_y = h*0.50 - card_h/2
        card = QRectF(d.padding, card_y, card_w, card_h)

        if d.rounded_card:
            card_color = QColor("#000000")
            card_color.setAlpha(d.card_opacity)
            p.setBrush(card_color)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(card, d.card_radius, d.card_radius)

        inner = card.adjusted(48, 40, -48, -40)
        lines, line_h = cls.text_lines(p, inner, text, d)
        total_h = line_h * len(lines)
        y = inner.center().y() - total_h/2 + p.fontMetrics().ascent()

        # Render each line with shadow + outline + gradient fill.
        for line in lines:
            if line == "":
                y += line_h
                continue
            width = p.fontMetrics().horizontalAdvance(line)
            x = inner.center().x() - width/2
            baseline = y

            # shadow
            if d.shadow_blur > 0:
                shadow_font = QFont(font := d.font_family)
                shadow_font.setPixelSize(d.font_size)
                shadow_font.setBold(d.bold); shadow_font.setItalic(d.italic)
                p.setFont(shadow_font)
                shadow_color = QColor(d.shadow)
                shadow_color.setAlpha(180)
                p.setPen(shadow_color)
                p.drawText(QPointF(x+d.shadow_offset, baseline+d.shadow_offset), line)

            # outline
            if d.outline_width:
                pen = QPen(QColor(d.outline))
                pen.setWidthF(d.outline_width*2)
                pen.setJoinStyle(Qt.RoundJoin)
                p.setPen(pen)
                p.drawText(QPointF(x, baseline), line)

            # gradient fill
            grad = QLinearGradient(x, baseline-d.font_size, x+width, baseline)
            grad.setColorAt(0, QColor(d.text1))
            grad.setColorAt(1, QColor(d.text2))
            p.setPen(QPen(grad, 1))
            p.drawText(QPointF(x, baseline), line)

            if d.glow:
                glow_pen = QPen(QColor(d.accent))
                glow_pen.setWidthF(1)
                glow = QColor(d.accent); glow.setAlpha(55)
                p.setPen(glow)
                p.drawText(QPointF(x, baseline), line)
            y += line_h

        # Small accent line
        accent_pen = QPen(QColor(d.accent))
        accent_pen.setWidthF(4)
        p.setPen(accent_pen)
        cx = w/2
        p.drawLine(QPointF(cx-45, card.bottom()-34), QPointF(cx+45, card.bottom()-34))

        p.end()
        return image


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jass SRT Image Maker v1.0")
        self.resize(1450, 900)
        self.entries = []
        self.current = 0
        self.design = Design()
        self.design.font_family = "Georgia"
        self._build_ui()
        self._apply_preset("Romantic Rose")
        self._sample()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(10,10,10,10)

        top = QHBoxLayout()
        title = QLabel("JASS SRT IMAGE MAKER")
        title.setStyleSheet("font-size:24px;font-weight:700;")
        top.addWidget(title)
        top.addStretch()
        self.open_btn = QPushButton("📂  SELECT SRT FILE")
        self.save_srt_btn = QPushButton("💾  Save SRT")
        self.sample_btn = QPushButton("Sample")
        self.render_btn = QPushButton("Render Current")
        self.render_all_btn = QPushButton("Render All")
        for b in [self.open_btn,self.save_srt_btn,self.sample_btn,self.render_btn,self.render_all_btn]:
            top.addWidget(b)
        outer.addLayout(top)

        splitter = QSplitter(Qt.Horizontal)
        outer.addWidget(splitter, 1)

        # Left: SRT entries
        left = QWidget()
        ll = QVBoxLayout(left)
        subtitle_title = QLabel("SUBTITLES")
        subtitle_title.setStyleSheet("font-size:15px;font-weight:700;")
        ll.addWidget(subtitle_title)

        self.select_srt_btn = QPushButton("📂  SELECT SRT FILE")
        self.select_srt_btn.setMinimumHeight(44)
        self.select_srt_btn.setStyleSheet(
            "QPushButton { background:#ff4f9a; color:white; font-weight:700; "
            "font-size:14px; border:0; border-radius:8px; padding:8px 12px; } "
            "QPushButton:hover { background:#ff70ad; }"
        )
        ll.addWidget(self.select_srt_btn)

        self.list = QListWidget()
        ll.addWidget(self.list, 1)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Edit selected subtitle...")
        self.editor.setMaximumHeight(130)
        ll.addWidget(self.editor)
        self.apply_text_btn = QPushButton("Apply Text")
        ll.addWidget(self.apply_text_btn)
        splitter.addWidget(left)

        # Center preview
        center = QWidget()
        cl = QVBoxLayout(center)
        self.preview = PreviewCanvas(self)
        cl.addWidget(self.preview, 1)
        self.info = QLabel("1080 × 1920 • Portrait")
        self.info.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.info)
        splitter.addWidget(center)

        # Right controls
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right = QWidget()
        rl = QVBoxLayout(right)

        # Presets
        pg = QGroupBox("DESIGN PRESETS")
        pgl = QVBoxLayout(pg)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(PRESETS.keys())
        pgl.addWidget(self.preset_combo)
        rl.addWidget(pg)

        # Canvas
        cg = QGroupBox("CANVAS")
        cform = QFormLayout(cg)
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1080 × 1920 Portrait", "1920 × 1080 Landscape", "1080 × 1080 Square", "1200 × 1500 Portrait", "Custom"])
        cform.addRow("Size", self.size_combo)
        self.width_spin = QSpinBox(); self.width_spin.setRange(320, 5000); self.width_spin.setValue(1080)
        self.height_spin = QSpinBox(); self.height_spin.setRange(320, 5000); self.height_spin.setValue(1920)
        cform.addRow("Width", self.width_spin); cform.addRow("Height", self.height_spin)
        rl.addWidget(cg)

        # Text
        tg = QGroupBox("TEXT STYLE")
        tf = QFormLayout(tg)
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentText("Georgia")
        tf.addRow("Font", self.font_combo)
        self.font_size = QSpinBox(); self.font_size.setRange(18, 180); self.font_size.setValue(58)
        tf.addRow("Size", self.font_size)
        self.bold = QCheckBox("Bold"); self.bold.setChecked(True)
        self.italic = QCheckBox("Italic")
        row = QHBoxLayout(); row.addWidget(self.bold); row.addWidget(self.italic)
        tf.addRow("Weight", row)
        self.outline = QSpinBox(); self.outline.setRange(0,12); self.outline.setValue(2)
        tf.addRow("Outline", self.outline)
        self.glow = QCheckBox("Glow"); self.glow.setChecked(True)
        tf.addRow("", self.glow)
        rl.addWidget(tg)

        # Background colors
        bg = QGroupBox("COLOUR")
        bf = QFormLayout(bg)
        self.bg1 = QPushButton(); self.bg2 = QPushButton(); self.bg3 = QPushButton()
        self.text1 = QPushButton(); self.text2 = QPushButton(); self.accent = QPushButton()
        for label, btn in [("Background 1",self.bg1),("Background 2",self.bg2),("Background 3",self.bg3),
                           ("Text 1",self.text1),("Text 2",self.text2),("Accent",self.accent)]:
            btn.setFixedHeight(28); bf.addRow(label,btn)
            btn.clicked.connect(lambda checked=False, b=btn: self._choose_color(b))
        rl.addWidget(bg)

        # Layout
        lg = QGroupBox("LAYOUT & DECORATION")
        lf = QFormLayout(lg)
        self.position = QComboBox(); self.position.addItems(["Top","Center","Bottom"])
        self.decoration = QComboBox(); self.decoration.addItems(["Hearts","Flowers","Stars","Sparkles","Sunset","Gold","Minimal"])
        self.strength = QSlider(Qt.Horizontal); self.strength.setRange(0,100); self.strength.setValue(70)
        self.padding = QSpinBox(); self.padding.setRange(20,250); self.padding.setValue(80)
        self.card = QCheckBox("Translucent rounded text card"); self.card.setChecked(True)
        self.card_opacity = QSlider(Qt.Horizontal); self.card_opacity.setRange(0,80); self.card_opacity.setValue(30)
        lf.addRow("Position", self.position)
        lf.addRow("Decorations", self.decoration)
        lf.addRow("Decoration strength", self.strength)
        lf.addRow("Side padding", self.padding)
        lf.addRow("", self.card)
        lf.addRow("Card opacity", self.card_opacity)
        rl.addWidget(lg)

        # Export
        eg = QGroupBox("EXPORT")
        ef = QVBoxLayout(eg)
        self.output_label = QLabel("Output: choose folder when rendering")
        self.render_current2 = QPushButton("Render Current PNG")
        self.render_all2 = QPushButton("Render Entire SRT")
        ef.addWidget(self.output_label)
        ef.addWidget(self.render_current2); ef.addWidget(self.render_all2)
        rl.addWidget(eg)
        rl.addStretch()

        right_scroll.setWidget(right)
        splitter.addWidget(right_scroll)
        splitter.setSizes([280, 700, 380])

        # Signals
        self.open_btn.clicked.connect(self.open_srt)
        self.select_srt_btn.clicked.connect(self.open_srt)
        self.save_srt_btn.clicked.connect(self.save_srt)
        self.sample_btn.clicked.connect(self._sample)
        self.render_btn.clicked.connect(self.render_current)
        self.render_all_btn.clicked.connect(self.render_all)
        self.render_current2.clicked.connect(self.render_current)
        self.render_all2.clicked.connect(self.render_all)
        self.apply_text_btn.clicked.connect(self.apply_text)
        self.list.currentRowChanged.connect(self.select_entry)
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        self.size_combo.currentTextChanged.connect(self.size_changed)

        for widget in [self.font_combo, self.font_size, self.bold, self.italic, self.outline, self.glow,
                       self.position, self.decoration, self.strength, self.padding, self.card,
                       self.card_opacity, self.width_spin, self.height_spin]:
            if isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.refresh)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self.refresh)
            elif isinstance(widget, QSlider):
                widget.valueChanged.connect(self.refresh)
            else:
                widget.stateChanged.connect(self.refresh)

        self._style()

    def _style(self):
        self.setStyleSheet("""
            QMainWindow { background:#202020; color:#eeeeee; }
            QGroupBox { font-weight:600; border:1px solid #444; border-radius:8px; margin-top:10px; padding:10px; }
            QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 5px; }
            QPushButton { background:#343434; color:#f5f5f5; padding:8px 13px; border:1px solid #555; border-radius:7px; font-weight:600; }
            QPushButton:hover { background:#454545; }
            QListWidget, QTextEdit, QComboBox, QSpinBox { background:#292929; color:#f2f2f2; border:1px solid #4a4a4a; padding:5px; }
            QLabel { color:#eeeeee; }
        """)

    def _choose_color(self, button):
        current = getattr(self.design, self._button_attr(button))
        c = QColorDialog.getColor(QColor(current), self, "Choose colour")
        if c.isValid():
            setattr(self.design, self._button_attr(button), c.name())
            self._set_button_color(button, c.name())
            self.refresh()

    def _button_attr(self, b):
        return {self.bg1:"bg1",self.bg2:"bg2",self.bg3:"bg3",self.text1:"text1",self.text2:"text2",self.accent:"accent"}[b]

    def _set_button_color(self, button, value):
        button.setStyleSheet(f"background:{value}; color:white;")

    def _apply_preset(self, name):
        if name not in PRESETS: return
        for k,v in PRESETS[name].items():
            setattr(self.design,k,v)
        self.design.preset = name
        self._set_button_color(self.bg1,self.design.bg1); self._set_button_color(self.bg2,self.design.bg2)
        self._set_button_color(self.bg3,self.design.bg3); self._set_button_color(self.text1,self.design.text1)
        self._set_button_color(self.text2,self.design.text2); self._set_button_color(self.accent,self.design.accent)
        self.decoration.setCurrentText(self.design.decoration)
        self.refresh()

    def _sample(self):
        self.entries = [
            Subtitle(1,"00:00:00,000","00:00:04,000","Rosa, your name feels like a beautiful secret in my heart."),
            Subtitle(2,"00:00:04,000","00:00:08,000","Every time I think of you, my world becomes a little warmer."),
            Subtitle(3,"00:00:08,000","00:00:12,000","There is something about your smile that I could never resist."),
            Subtitle(4,"00:00:12,000","00:00:16,000","I want to be close to you, lost in the magic of your presence."),
            Subtitle(5,"00:00:16,000","00:00:20,000","Your eyes have a way of making everything else disappear."),
        ]
        self._populate()
        self.list.setCurrentRow(0)

    def _populate(self):
        self.list.clear()
        for e in self.entries:
            item = QListWidgetItem(f"{e.index:02d}   {e.start}  →  {e.end}\n      {e.text.replace(chr(10),' / ')}")
            self.list.addItem(item)

    def open_srt(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open SRT", "", "SubRip (*.srt);;All files (*.*)")
        if not path: return
        try:
            text = Path(path).read_text(encoding="utf-8-sig")
            self.entries = parse_srt(text)
            if not self.entries:
                raise ValueError("No valid SRT entries found.")
            self._populate()
            self.list.setCurrentRow(0)
            self.statusBar().showMessage(f"Loaded {len(self.entries)} subtitles")
        except Exception as exc:
            QMessageBox.critical(self, "SRT Error", str(exc))

    def save_srt(self):
        if not self.entries:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save SRT", "edited.srt", "SubRip (*.srt)")
        if path:
            Path(path).write_text(srt_text(self.entries), encoding="utf-8")
            self.statusBar().showMessage("SRT saved")

    def select_entry(self, row):
        if 0 <= row < len(self.entries):
            self.current = row
            self.editor.setPlainText(self.entries[row].text)
            self.refresh()

    def apply_text(self):
        if 0 <= self.current < len(self.entries):
            self.entries[self.current].text = self.editor.toPlainText().strip()
            self._populate()
            self.list.setCurrentRow(self.current)
            self.refresh()

    def size_changed(self, value):
        if value.startswith("1080 × 1920"):
            self.design.width, self.design.height = 1080,1920
        elif value.startswith("1920 × 1080"):
            self.design.width, self.design.height = 1920,1080
        elif value.startswith("1080 × 1080"):
            self.design.width, self.design.height = 1080,1080
        elif value.startswith("1200 × 1500"):
            self.design.width, self.design.height = 1200,1500
        else:
            self.design.width, self.design.height = self.width_spin.value(), self.height_spin.value()
        self.width_spin.setValue(self.design.width); self.height_spin.setValue(self.design.height)
        self.refresh()

    def refresh(self, *args):
        self.design.font_family = self.font_combo.currentFont().family()
        self.design.font_size = self.font_size.value()
        self.design.bold = self.bold.isChecked()
        self.design.italic = self.italic.isChecked()
        self.design.outline_width = self.outline.value()
        self.design.glow = self.glow.isChecked()
        self.design.position = self.position.currentText()
        self.design.decoration = self.decoration.currentText()
        self.design.decoration_strength = self.strength.value()
        self.design.padding = self.padding.value()
        self.design.rounded_card = self.card.isChecked()
        self.design.card_opacity = self.card_opacity.value()
        self.design.width = self.width_spin.value()
        self.design.height = self.height_spin.value()
        text = self.entries[self.current].text if self.entries and 0 <= self.current < len(self.entries) else "Rosa, you are the beautiful thought my heart returns to."
        image = Renderer.render(text, self.design)
        self.preview.set_image(image)
        self.info.setText(f"{self.design.width} × {self.design.height} • {self.design.preset}")

    def render_current(self):
        if not self.entries:
            QMessageBox.information(self, "Nothing to render", "Load an SRT or use Sample first.")
            return
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if not folder: return
        e = self.entries[self.current]
        image = Renderer.render(e.text, self.design)
        path = Path(folder) / f"{e.index:03d}.png"
        image.save(str(path), "PNG")
        self.statusBar().showMessage(f"Rendered {path.name}")

    def render_all(self):
        if not self.entries:
            QMessageBox.information(self, "Nothing to render", "Load an SRT or use Sample first.")
            return
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if not folder: return
        out = Path(folder)
        for i,e in enumerate(self.entries,1):
            image = Renderer.render(e.text, self.design)
            image.save(str(out / f"{i:03d}.png"), "PNG")
        self.statusBar().showMessage(f"Rendered {len(self.entries)} PNG images to {out}")
        QMessageBox.information(self, "Rendering complete", f"Rendered {len(self.entries)} images.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Jass SRT Image Maker")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
