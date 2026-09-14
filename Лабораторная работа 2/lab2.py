import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import math


class DrawFigure:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x650")

        self.source_image = None
        self.result_image = None
        self.photo_source = None
        self.photo_result = None

        self.create_widgets()

    def create_widgets(self):
        top = tk.Frame(self.root, bg="#e5e5e5", height=80)
        top.pack(fill=tk.X, padx=10, pady=5)
        top.pack_propagate(False)

        tk.Label(top, text="Ширина:").place(x=10, y=10)
        self.edit_w = tk.Entry(top, width=7)
        self.edit_w.insert(0, "600")
        self.edit_w.place(x=70, y=8)

        tk.Label(top, text="Высота:").place(x=140, y=10)
        self.edit_h = tk.Entry(top, width=7)
        self.edit_h.insert(0, "600")
        self.edit_h.place(x=200, y=8)

        tk.Button(top, text="Создать", width=11, command=self.create_new).place(x=270, y=6)
        tk.Button(top, text="Открыть", width=11, command=self.load_image).place(x=365, y=6)
        tk.Button(top, text="Перенести", width=11, command=self.insert_fragment).place(x=460, y=6)
        tk.Button(top, text="Координаты", width=11, command=self.draw_axes).place(x=555, y=6)
        tk.Button(top, text="2^x", width=11, command=self.draw_graph).place(x=650, y=6)
        tk.Button(top, text="Сохранить", width=11, command=self.save_image).place(x=745, y=6)
        tk.Button(top, text="Сохранить PBM", width=12, command=self.save_as_pbm).place(x=840, y=6)

        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left = tk.LabelFrame(bottom, text="Новое изображение")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.canvas_result = tk.Canvas(left, bg="#d0d0d0")
        self.canvas_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        right = tk.LabelFrame(bottom, text="Исходное изображение")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.canvas_source = tk.Canvas(right, bg="#d0d0d0")
        self.canvas_source.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    def create_new(self):
        try:
            w, h = int(self.edit_w.get()), int(self.edit_h.get())
            if w <= 0 or h <= 0:
                raise ValueError
            self.result_image = Image.new("RGB", (w, h), "white")
            self.show_result()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные размеры.")


    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp"), ("Все файлы", "*.*")]
        )
        if not path:
            return
        try:
            self.source_image = Image.open(path).convert("RGB")
            self.show_source()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


    def insert_fragment(self):
        if self.result_image is None or self.source_image is None:
            messagebox.showerror("Ошибка", "Сначала создайте и откройте изображения.")
            return

        SW, SH = self.source_image.size


        cx = SW // 2
        cy = SH // 2

        w = SW // 6
        h = SH // 6



        W, H = self.result_image.size
        dst_x = W // 2
        dst_y = H // 2

        for q in range(h + 1):
            for p in range(w + 1):
                if p * h + q * w <= w * h:
                    px = cx - p
                    py = cy + q
                    if 0 <= px < SW and 0 <= py < SH:
                        tx = dst_x - p
                        ty = dst_y + q
                        if 0 <= tx < W and 0 <= ty < H:
                            self.result_image.putpixel(
                                (tx, ty),
                                self.source_image.getpixel((px, py))
                            )

        draw = ImageDraw.Draw(self.result_image)
        draw.polygon(
            [
                (dst_x, dst_y),
                (dst_x - w, dst_y),
                (dst_x, dst_y + h),
            ],
            outline=(220, 0, 0)
        )

        self.show_result()


    def draw_axes(self):
        if self.result_image is None:
            messagebox.showerror("Ошибка", "Сначала создайте изображение.")
            return

        draw = ImageDraw.Draw(self.result_image)
        w, h = self.result_image.size

        cx = w // 2
        cy = h // 2


        draw.line((cx, 10, cx, h - 10), fill="black", width=2)
        draw.line((cx - 5, 20, cx, 10, cx + 5, 20), fill="black", width=2)


        draw.line((10, cy, w - 10, cy), fill="black", width=2)
        draw.line((w - 20, cy - 5, w - 10, cy, w - 20, cy + 5), fill="black", width=2)


        for i in range(0, w, 10):
            draw.line((i, cy - 2, i, cy + 2), fill="black")
        for i in range(0, h, 10):
            draw.line((cx - 2, i, cx + 2, i), fill="black")


        draw.text((cx + 3, cy + 3), "0", fill="black")
        draw.text((w - 20, cy + 5), "x", fill="black")
        draw.text((cx + 5, 2), "y", fill="black")

        self.show_result()


    def draw_graph(self):
        if self.result_image is None:
            messagebox.showerror("Ошибка", "Сначала создайте изображение.")
            return

        draw = ImageDraw.Draw(self.result_image)
        w, h = self.result_image.size

        cx = w // 2
        cy = h // 2

        draw.text((cx + 40, cy - 60), "y = 2^x", fill=(200, 40, 40))

        scale_x = 30
        scale_y = 15

        points = []
        x = -4.0
        step = 0.02
        while x <= 4.0:
            y = 2.0 ** x
            px = cx + int(x * scale_x)
            py = cy - int(y * scale_y)
            if 0 <= px < w and 0 <= py < h:
                points.append((px, py))
            x += step

        if len(points) > 1:
            draw.line(points, fill=(200, 40, 40), width=2)

        self.show_result()


    def show_result(self):
        if self.result_image is None:
            return
        img = self.result_image.copy()
        scale = min(480 / img.width, 480 / img.height, 1)
        size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(size, Image.Resampling.LANCZOS)
        self.photo_result = ImageTk.PhotoImage(img)
        self.canvas_result.delete("all")
        self.canvas_result.create_image(size[0] // 2, size[1] // 2, image=self.photo_result)

    def show_source(self):
        if self.source_image is None:
            return
        img = self.source_image.copy()
        scale = min(480 / img.width, 480 / img.height, 1)
        size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(size, Image.Resampling.LANCZOS)
        self.photo_source = ImageTk.PhotoImage(img)
        self.canvas_source.delete("all")
        self.canvas_source.create_image(size[0] // 2, size[1] // 2, image=self.photo_source)


    def save_image(self):
        if self.result_image is None:
            messagebox.showerror("Ошибка", "Нет изображения для сохранения.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if path:
            self.result_image.save(path)
            messagebox.showinfo("Готово", "Изображение сохранено.")


    def save_as_pbm(self):
        if self.result_image is None:
            messagebox.showerror("Ошибка", "Нет изображения для сохранения.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pbm",
            filetypes=[("PBM (текстовый)", "*.pbm"), ("Все файлы", "*.*")]
        )
        if not path:
            return

        try:

            img = self.result_image.convert("1")
            width, height = img.size

            pixels = img.getdata()
            bits = [1 if p > 128 else 0 for p in pixels]

            with open(path, "w", encoding="ascii") as f:
                f.write("P1\n")
                f.write(f"# Saved from Computer-graphics lab (variant 20)\n")
                f.write(f"{width} {height}\n")
                for y in range(height):
                    row = bits[y * width:(y + 1) * width]
                    f.write(" ".join(map(str, row)) + "\n")

            messagebox.showinfo("Готово", "Изображение сохранено в текстовом формате PBM (P1).")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить PBM:\n{e}")


root = tk.Tk()
app = DrawFigure(root)
root.mainloop()