import os
import re
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def _get_attr(attrs, name, default=None):
    m = re.search(rf'{name}\s*=\s*"([^"]*)"', attrs, re.IGNORECASE)
    return m.group(1) if m else default

def parse_svg(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    circles = []
    for m in re.finditer(r'<circle\b([^/>]*)/?>', content, re.IGNORECASE):
        a = m.group(1)
        circles.append({
            'cx': float(_get_attr(a, 'cx', '0')),
            'cy': float(_get_attr(a, 'cy', '0')),
            'r':  float(_get_attr(a, 'r',  '0')),
        })
    return circles

class Raster:
    def __init__(self, width, height, bg=1):
        self.w = width
        self.h = height
        self.data = bytearray([bg]) * (width * height)

    def set(self, x, y, color=0):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.data[y * self.w + x] = color

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.data[y * self.w + x]
        return 1

    def clear(self, color=1):
        self.data = bytearray([color]) * (self.w * self.h)

    def save_pbm(self, filename):
        with open(filename, 'w', encoding='ascii') as f:
            f.write('P1\n')
            f.write(f'# Iin-Yan {self.w}x{self.h}\n')
            f.write(f'{self.w} {self.h}\n')
            for y in range(self.h):
                row = self.data[y * self.w:(y + 1) * self.w]
                f.write(' '.join(str(b) for b in row))
                f.write('\n')

    def save_bmp(self, filename):
        import struct
        row_size = (self.w * 3 + 3) & ~3
        pixel_data_size = row_size * self.h
        file_size = 14 + 40 + pixel_data_size
        with open(filename, 'wb') as f:
            f.write(b'BM')
            f.write(struct.pack('<I', file_size))
            f.write(struct.pack('<HH', 0, 0))
            f.write(struct.pack('<I', 14 + 40))
            f.write(struct.pack('<I', 40))
            f.write(struct.pack('<i', self.w))
            f.write(struct.pack('<i', self.h))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 24))
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', pixel_data_size))
            f.write(struct.pack('<i', 2835))
            f.write(struct.pack('<i', 2835))
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', 0))
            for y in range(self.h - 1, -1, -1):
                row = bytearray()
                for x in range(self.w):
                    v = 0 if self.data[y * self.w + x] == 0 else 255
                    row += bytes((v, v, v))
                row += b'\x00' * (row_size - len(row))
                f.write(row)

def circle_equation_pts(r):
    pts = set()
    for x in range(0, int(r) + 1):
        y = math.sqrt(max(0.0, r * r - x * x))
        pts.add((x, int(round(y))))
        if x < r:
            y2 = math.sqrt(max(0.0, r * r - (x + 1) ** 2))
            steps = int(abs(y - y2))
            for k in range(1, steps + 1):
                t = k / (steps + 1)
                pts.add((x, int(round(y + t * (y2 - y)))))
    return pts

def circle_parametric_pts(r):
    pts = set()
    steps = max(16, int(2 * math.pi * r))
    for i in range(steps + 1):
        t = i * 2 * math.pi / steps
        x = int(round(r * math.cos(t)))
        y = int(round(r * math.sin(t)))
        pts.add((abs(x), abs(y)))
    return pts

def circle_bresenham_pts(r):
    pts = []
    x, y = 0, int(r)
    delta = 2 - 2 * int(r)
    while x <= y:
        pts.append((x, y))
        d1 = 2 * (delta + y) - 1
        d2 = 2 * (delta - x) - 1
        if delta < 0 and d1 <= 0:
            x += 1
            delta += 2 * x + 1
        elif delta > 0 and d2 > 0:
            y -= 1
            delta += -2 * y + 1
        else:
            x += 1
            y -= 1
            delta += 2 * (x - y)
    return pts

def _plot8(raster, cx, cy, x, y, color):
    raster.set(cx + x, cy + y, color)
    raster.set(cx - x, cy + y, color)
    raster.set(cx + x, cy - y, color)
    raster.set(cx - x, cy - y, color)
    raster.set(cx + y, cy + x, color)
    raster.set(cx - y, cy + x, color)
    raster.set(cx + y, cy - x, color)
    raster.set(cx - y, cy - x, color)

def draw_circle(raster, cx, cy, r, method, color=0):
    cx, cy, r = float(cx), float(cy), float(r)
    if r <= 0:
        return
    if method == 'equation':
        pts = circle_equation_pts(r)
    elif method == 'parametric':
        pts = circle_parametric_pts(r)
    else:
        pts = circle_bresenham_pts(r)
    for (x, y) in pts:
        _plot8(raster, cx, cy, x, y, color)

def draw_disc(raster, cx, cy, r, color):
    for y in range(int(cy - r), int(cy + r) + 1):
        dy = y - cy
        d2 = r * r - dy * dy
        if d2 < 0:
            continue
        half = int(math.sqrt(d2))
        for x in range(int(cx - half), int(cx + half) + 1):
            raster.set(x, y, color)

def build_iyan(raster, cx, cy, R, method='bresenham'):
    raster.clear(1)
    r_small = R / 2.0
    r_dot = R / 6.0
    upper = (cx, cy - r_small)
    lower = (cx, cy + r_small)
    for y in range(int(cy - R), int(cy + R) + 1):
        dy = y - cy
        d2 = R * R - dy * dy
        if d2 < 0:
            continue
        half = int(math.sqrt(d2))
        for x in range(int(cx - half), int(cx) + 1):
            raster.set(x, y, 0)
    draw_disc(raster, upper[0], upper[1], r_small, 0)
    draw_disc(raster, lower[0], lower[1], r_small, 1)
    draw_disc(raster, upper[0], upper[1], r_dot, 1)
    draw_disc(raster, lower[0], lower[1], r_dot, 0)
    draw_circle(raster, cx, cy, R, method, color=0)

def build_iyan_from_svg(raster, circles, method='bresenham'):
    raster.clear(1)
    if not circles:
        return
    cs = sorted(circles, key=lambda c: c['r'], reverse=True)
    big = cs[0]
    cx, cy, R = big['cx'], big['cy'], big['r']
    r_small = cs[1]['r'] if len(cs) >= 3 else R / 2.0
    r_dot = cs[3]['r'] if len(cs) >= 5 else R / 6.0
    upper = (cx, cy - r_small)
    lower = (cx, cy + r_small)
    for y in range(int(cy - R), int(cy + R) + 1):
        dy = y - cy
        d2 = R * R - dy * dy
        if d2 < 0:
            continue
        half = int(math.sqrt(d2))
        for x in range(int(cx - half), int(cx) + 1):
            raster.set(x, y, 0)
    draw_disc(raster, upper[0], upper[1], r_small, 0)
    draw_disc(raster, lower[0], lower[1], r_small, 1)
    draw_disc(raster, upper[0], upper[1], r_dot, 1)
    draw_disc(raster, lower[0], lower[1], r_dot, 0)
    draw_circle(raster, cx, cy, R, method, color=0)
class IYanApp:
    def __init__(self, root):
        self.root = root
        root.geometry('1100x720')
        root.minsize(1200, 600)
        self.raster = None
        self.svg_circles = None
        self.photo = None
        self._build_ui()
    def _build_ui(self):
        top = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        top.pack(side=tk.TOP, fill=tk.X)
        f1 = tk.LabelFrame(top, text='Настройки холста', padx=8, pady=5)
        f1.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        tk.Label(f1, text='Ширина:').grid(row=0, column=0, sticky='e')
        self.e_width = tk.Entry(f1, width=6)
        self.e_width.insert(0, '500')
        self.e_width.grid(row=0, column=1)

        tk.Label(f1, text='Высота:').grid(row=0, column=2, sticky='e')
        self.e_height = tk.Entry(f1, width=6)
        self.e_height.insert(0, '500')
        self.e_height.grid(row=0, column=3)

        tk.Button(f1, text='Создать',
                  command=self.on_create).grid(row=0, column=4, padx=5)

        f2 = tk.LabelFrame(top, text='Параметры инь-ян', padx=8, pady=5)
        f2.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        tk.Label(f2, text='Центр X:').grid(row=0, column=0, sticky='e')
        self.e_cx = tk.Entry(f2, width=6)
        self.e_cx.insert(0, '250')
        self.e_cx.grid(row=0, column=1)

        tk.Label(f2, text='Y:').grid(row=0, column=2, sticky='e')
        self.e_cy = tk.Entry(f2, width=6)
        self.e_cy.insert(0, '250')
        self.e_cy.grid(row=0, column=3)

        tk.Label(f2, text='Радиус:').grid(row=1, column=0, sticky='e')
        self.e_r = tk.Entry(f2, width=6)
        self.e_r.insert(0, '80')
        self.e_r.grid(row=1, column=1)

        f3 = tk.LabelFrame(top, text='Действия', padx=8, pady=5)
        f3.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

        tk.Button(f3, text='Сохранить BMP',
                  command=self.on_save_bmp).grid(row=0, column=0, padx=3)
        tk.Button(f3, text='Сохранить PBM',
                  command=self.on_save_pbm).grid(row=0, column=1, padx=3)
        tk.Button(f3, text='Очистить',
                  command=self.on_clear).grid(row=0, column=2, padx=3)

        f4 = tk.LabelFrame(top, text='Загрузка из SVG', padx=8, pady=5)
        f4.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')

        tk.Button(f4, text='Загрузить SVG',
                  command=self.on_load_svg).pack(fill=tk.X)
        self.lbl_svg = tk.Label(f4, text='SVG не загружен',
                                fg='red', wraplength=150)
        self.lbl_svg.pack()
        tk.Button(f4, text='Применить параметры',
                  command=self.on_apply_params).pack(fill=tk.X, pady=3)

        f5 = tk.LabelFrame(top, text='Алгоритмы рисования', padx=8, pady=5)
        f5.grid(row=0, column=4, padx=5, pady=5, sticky='nsew')

        tk.Button(f5, text='Уравнение',
                  command=lambda: self.on_draw('equation')
                  ).grid(row=0, column=0, padx=3, pady=3, sticky='ew')
        tk.Button(f5, text='Параметрическое',
                  command=lambda: self.on_draw('parametric')
                  ).grid(row=0, column=1, padx=3, pady=3, sticky='ew')
        tk.Button(f5, text='Брезенхем',
                  command=lambda: self.on_draw('bresenham')
                  ).grid(row=1, column=0, padx=3, pady=3, sticky='ew')
        tk.Button(f5, text='Встроенный',
                  command=lambda: self.on_draw('builtin')
                  ).grid(row=1, column=1, padx=3, pady=3, sticky='ew')

        self.canvas = tk.Canvas(self.root, bg='white',
                                bd=2, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _get_size(self):
        try:
            w = int(self.e_width.get())
            h = int(self.e_height.get())
        except ValueError:
            messagebox.showerror('Ошибка', 'Ширина/высота должны быть числами')
            return None
        if w <= 0 or h <= 0:
            messagebox.showerror('Ошибка', 'Размеры должны быть > 0')
            return None
        return w, h

    def _get_figure_params(self):
        try:
            cx = float(self.e_cx.get())
            cy = float(self.e_cy.get())
            r = float(self.e_r.get())
        except ValueError:
            messagebox.showerror('Ошибка', 'Проверьте числовые поля')
            return None
        return cx, cy, r

    def on_create(self):
        size = self._get_size()
        if not size:
            return
        w, h = size
        self.raster = Raster(w, h, bg=1)
        self._render()

    def on_draw(self, method):
        if self.raster is None:
            messagebox.showinfo('Инфо','Сначала нажмите «Создать» для создания холста')
            return
        params = self._get_figure_params()
        if not params:
            return
        cx, cy, r = params
        if self.svg_circles and len(self.svg_circles) >= 3:
            build_iyan_from_svg(self.raster, self.svg_circles, method=method)
        else:
            build_iyan(self.raster, cx, cy, r, method=method)
        self._render()

    def on_load_svg(self):
        path = filedialog.askopenfilename(
            title='Выберите SVG-файл',
            filetypes=[('SVG files', '*.svg'), ('All files', '*.*')])
        if not path:
            return
        try:
            self.svg_circles = parse_svg(path)
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось прочитать SVG:\n{e}')
            self.svg_circles = None
            return
        n = len(self.svg_circles)
        if n == 0:
            self.lbl_svg.config(text='Окружностей нет', fg='red')
            messagebox.showwarning('Внимание', 'В SVG не найдено окружностей')
            return
        self.lbl_svg.config(text=f'Загружено окружностей: {n}', fg='green')

    def on_apply_params(self):
        if not self.svg_circles:
            messagebox.showinfo('Инфо','Сначала загрузите SVG')
            return
        c = self.svg_circles[0]
        self.e_cx.delete(0, tk.END); self.e_cx.insert(0, str(int(c['cx'])))
        self.e_cy.delete(0, tk.END); self.e_cy.insert(0, str(int(c['cy'])))
        self.e_r.delete(0, tk.END);  self.e_r.insert(0, str(int(c['r'])))
        messagebox.showinfo('Готово','Параметры применены. Выберите алгоритм рисования.')

    def _render(self):
        if not self.raster:
            self.canvas.delete('all')
            return
        w, h = self.raster.w, self.raster.h
        self.photo = tk.PhotoImage(width=w, height=h)
        rows = []
        for y in range(h):
            row = []
            for x in range(w):
                v = 0 if self.raster.data[y * w + x] == 0 else 255
                row.append(f'#{v:02x}{v:02x}{v:02x}')
            rows.append('{' + ' '.join(row) + '}')
        self.photo.put(' '.join(rows), to=(0, 0))
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=(0, 0, w, h))

    def on_save_bmp(self):
        if not self.raster:
            messagebox.showinfo('Инфо', 'Сначала создайте изображение')
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.bmp',
            filetypes=[('BMP files', '*.bmp')])
        if not path:
            return
        self.raster.save_bmp(path)
        messagebox.showinfo('Готово', f'Сохранено:\n{path}')

    def on_save_pbm(self):
        if not self.raster:
            messagebox.showinfo('Инфо', 'Сначала создайте изображение')
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.pbm',
            filetypes=[('PBM files', '*.pbm')])
        if not path:
            return
        self.raster.save_pbm(path)
        messagebox.showinfo('Готово', f'Сохранено:\n{path}')

    def on_clear(self):
        self.canvas.delete('all')
        self.raster = None
        self.photo = None
        self.svg_circles = None
        self.lbl_svg.config(text='SVG не загружен', fg='red')

def create_default_svg(filename, size=500):
    R = size * 0.4
    cx, cy = size / 2.0, size / 2.0
    r = R / 2.0
    rd = R / 6.0
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">
  <circle cx="{cx}" cy="{cy}" r="{R}"  stroke="black" fill="none"/>
  <circle cx="{cx}" cy="{cy - r}" r="{r}" stroke="black" fill="none"/>
  <circle cx="{cx}" cy="{cy + r}" r="{r}" stroke="black" fill="none"/>
  <circle cx="{cx}" cy="{cy - r}" r="{rd}" stroke="black" fill="none"/>
  <circle cx="{cx}" cy="{cy + r}" r="{rd}" stroke="black" fill="none"/>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

if __name__ == '__main__':
    if not os.path.exists('iyan.svg'):
        create_default_svg('iyan.svg', 500)
    root = tk.Tk()
    app = IYanApp(root)
    root.mainloop()