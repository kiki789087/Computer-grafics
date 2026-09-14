import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class Lab1App:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №1 — Вариант 20")
        self.root.geometry("900x650")

        self.image = None
        self.tk_image = None
        self.img_path = None
        self.changed_pixels = []

        top = tk.Frame(root)
        top.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.btn_open = tk.Button(top, text="Загрузить", width=14, command=self.on_open)
        self.btn_open.pack(side=tk.LEFT, padx=3)

        self.btn_process = tk.Button(top, text="Обработать", width=14,
                                     command=self.on_process, state=tk.DISABLED)
        self.btn_process.pack(side=tk.LEFT, padx=3)

        self.btn_save_png = tk.Button(top, text="Сохранить PNG", width=14,
                                      command=self.on_save_png, state=tk.DISABLED)
        self.btn_save_png.pack(side=tk.LEFT, padx=3)

        self.btn_save_pbm = tk.Button(top, text="Сохранить PBM", width=14,
                                      command=self.on_save_pbm, state=tk.DISABLED)
        self.btn_save_pbm.pack(side=tk.LEFT, padx=3)

        self.canvas = tk.Canvas(root, bg="lightgray",
                                highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status = tk.Label(root, text="Готов", anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def on_open(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Все поддерживаемые", "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG",  "*.png"),
                ("BMP",  "*.bmp"),
                ("GIF",  "*.gif"),
                ("TIFF", "*.tif *.tiff"),
                ("Все файлы", "*.*"),
            ]
        )
        if not path:
            return

        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return

        if img.mode != "RGB":
            img = img.convert("RGB")

        self.image = img
        self.img_path = path
        self.changed_pixels = []

        self.show_image()

        self.status.config(
            text=f"Файл: {path}   |   Размер: {img.width} x {img.height}   |   Режим: {img.mode}"
        )
        self.btn_process.config(state=tk.NORMAL)

    def on_process(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Сначала откройте изображение!")
            return

        w, h = self.image.size
        pix = self.image.load()

        points = [
            (0, 0,           (255, 191, 191)),
            (w // 2, h // 2, (191, 255, 191)),
            (w - 1, h - 1,   (191, 191, 255)),  
        ]

        self.changed_pixels = []
        for x, y, color in points:
            pix[x, y] = color
            self.changed_pixels.append((x, y))

        self.show_image()

        self.status.config(
            text=f"Точки поставлены: {self.changed_pixels}"
        )
        self.btn_save_png.config(state=tk.NORMAL)
        self.btn_save_pbm.config(state=tk.NORMAL)
        messagebox.showinfo("Готово", "Точки поставлены!")

    def on_save_png(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Нет изображения для сохранения!")
            return

        path = filedialog.asksaveasfilename(
            title="Сохранить как PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"),
                       ("Все файлы", "*.*")]
        )
        if not path:
            return

        try:
            self.image.save(path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
            return

        self.status.config(text=f"Сохранено PNG: {path}")
        messagebox.showinfo("Успех", f"Сохранено PNG:\n{path}")

    def on_save_pbm(self):
        if self.image is None:
            messagebox.showwarning("Внимание", "Нет изображения для сохранения!")
            return
        if not self.changed_pixels:
            messagebox.showwarning("Внимание",
                                   "Сначала нажмите «Обработать», потом сохраняйте PBM.")
            return

        path = filedialog.asksaveasfilename(
            title="Сохранить как PBM",
            defaultextension=".pbm",
            filetypes=[("PBM files", "*.pbm"),
                       ("Все файлы", "*.*")]
        )
        if not path:
            return

        w, h = self.image.size
        pbm_img = Image.new("1", (w, h), 0) 
        pbm_pix = pbm_img.load()

        for x, y in self.changed_pixels:
            pbm_pix[x, y] = 1

        try:
            pbm_img.save(path, format="PPM", bitmap_format="pbm")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить PBM:\n{e}")
            return

        self.status.config(text=f"Сохранено PBM: {path}")
        messagebox.showinfo("Успех",
                            f"Сохранено PBM:\n{path}\n\n"
                            f"Белых пикселей (изменённых): {len(self.changed_pixels)}")

    def show_image(self):
        if self.image is None:
            return

        w, h = self.image.size
        max_w, max_h = 850, 500
        scale = min(max_w / w, max_h / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)

        img_resized = self.image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img_resized)

        self.canvas.delete("all")
        self.canvas.config(width=new_w, height=new_h)
        self.canvas.create_image(new_w // 2, new_h // 2,
                                 anchor=tk.CENTER, image=self.tk_image)


def main():
    root = tk.Tk()
    app = Lab1App(root)
    root.mainloop()

if __name__ == "__main__":
    main()