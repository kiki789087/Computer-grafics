import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import colorsys
class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Преобразование изображений")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")
        self.img1_original = None
        self.img1_processed = None
        self.img2_original = None
        self.img2_blended = None
        self.frame_tl = tk.Frame(root, bg="white", width=300, height=250, highlightbackground="black",highlightthickness=1)
        self.frame_tl.place(x=30, y=30)
        self.frame_tl.pack_propagate(False)
        self.frame_bl = tk.Frame(root, bg="white", width=300, height=250, highlightbackground="black",highlightthickness=1)
        self.frame_bl.place(x=30, y=310)
        self.frame_bl.pack_propagate(False)
        self.frame_tr = tk.Frame(root, bg="white", width=300, height=250, highlightbackground="black", highlightthickness=1)
        self.frame_tr.place(x=570, y=30)
        self.frame_tr.pack_propagate(False)
        self.frame_br = tk.Frame(root, bg="white", width=300, height=250, highlightbackground="black", highlightthickness=1)
        self.frame_br.place(x=570, y=310)
        self.frame_br.pack_propagate(False)
        self.btn_open1 = tk.Button(root, text="Открыть 1 фото", width=15, command=self.open_image1)
        self.btn_open1.place(x=385, y=90)
        self.btn_process = tk.Button(root, text="Преобразовать", width=15, command=self.process_image1)
        self.btn_process.place(x=385, y=130)
        self.btn_save1 = tk.Button(root, text="Сохранить", width=15, command=self.save_image1)
        self.btn_save1.place(x=385, y=170)
        self.btn_open2 = tk.Button(root, text="Открыть 2 фото", width=15, command=self.open_image2)
        self.btn_open2.place(x=385, y=410)
        self.btn_blend = tk.Button(root, text="Наложить", width=15, command=self.blend_images)
        self.btn_blend.place(x=385, y=450)
        self.btn_save2 = tk.Button(root, text="Сохранить", width=15, command=self.save_image2)
        self.btn_save2.place(x=385, y=490)
    def show_image(self, img, frame):
        try:
            img_copy = img.copy()
            img_copy.thumbnail((290, 240), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img_copy)
            for widget in frame.winfo_children():
                widget.destroy()
            lbl = tk.Label(frame, image=tk_img, bg="white")
            lbl.image = tk_img
            lbl.pack(expand=True)
        except Exception as e: messagebox.showerror("Ошибка", f"Не удалось отобразить изображение:\n{e}")
    def open_image1(self):
        path = filedialog.askopenfilename(filetypes=[("Netpbm Images", "*.ppm *.pgm"), ("All Files", "*.*")])
        if path:
            try:
                self.img1_original = Image.open(path).convert("RGB")
                self.show_image(self.img1_original, self.frame_tl)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
    def open_image2(self):
        path = filedialog.askopenfilename(filetypes=[("Netpbm Images", "*.ppm *.pgm"), ("All Files", "*.*")])
        if path:
            try:
                self.img2_original = Image.open(path).convert("RGB")
                self.show_image(self.img2_original, self.frame_bl)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
    def process_image1(self):
        if not self.img1_original:
            messagebox.showwarning("Внимание", "Сначала откройте 1 фото!")
            return
        width, height = self.img1_original.size
        pixels = self.img1_original.load()
        processed_img = Image.new("RGB", (width, height))
        new_pixels = processed_img.load()
        for y in range(height):
            k = 1.0 - y / max(1, height - 1)
            for x in range(width):
                r, g, b = pixels[x, y]
                h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                s_new = s * k
                r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s_new, v)
                new_pixels[x, y] = (int(r_new * 255), int(g_new * 255), int(b_new * 255))
        self.img1_processed = processed_img
        self.show_image(self.img1_processed, self.frame_tr)
    def blend_images(self):
        if not self.img1_original or not self.img2_original:
            messagebox.showwarning("Внимание", "Откройте оба фото (1 и 2) для наложения!")
            return
        width = min(self.img1_original.width, self.img2_original.width)
        height = min(self.img1_original.height, self.img2_original.height)
        img1_crop = self.img1_original.crop((0, 0, width, height))
        img2_crop = self.img2_original.crop((0, 0, width, height))
        pix1 = img1_crop.load()
        pix2 = img2_crop.load()
        blended_img = Image.new("RGB", (width, height))
        new_pixels = blended_img.load()
        for y in range(height):
            for x in range(width):
                r1, g1, b1 = pix1[x, y]
                r2, g2, b2 = pix2[x, y]
                h1, s1, v1 = colorsys.rgb_to_hsv(r1 / 255.0, g1 / 255.0, b1 / 255.0)
                h2, s2, v2 = colorsys.rgb_to_hsv(r2 / 255.0, g2 / 255.0, b2 / 255.0)
                r_res, g_res, b_res = colorsys.hsv_to_rgb(h1, s2, v1)
                new_pixels[x, y] = (int(r_res * 255), int(g_res * 255), int(b_res * 255))
        self.img2_blended = blended_img
        self.show_image(self.img2_blended, self.frame_br)
    def save_image1(self):
        if not self.img1_processed:
            messagebox.showwarning("Внимание", "Нет обработанного изображения для сохранения!")
            return
        path = filedialog.asksaveasfilename(defaultextension=".ppm",
                                            filetypes=[("Netpbm PPM", "*.ppm")])
        if path:
            self.img1_processed.save(path)
            messagebox.showinfo("Успех", "Изображение успешно сохранено!")
    def save_image2(self):
        if not self.img2_blended:
            messagebox.showwarning("Внимание", "Нет результата наложения для сохранения!")
            return
        path = filedialog.asksaveasfilename(defaultextension=".ppm",
                                            filetypes=[("Netpbm PPM", "*.ppm")])
        if path:
            self.img2_blended.save(path)
            messagebox.showinfo("Успех", "Изображение успешно сохранено!")
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()