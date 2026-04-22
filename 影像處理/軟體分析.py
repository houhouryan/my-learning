import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageFilter
import numpy as np

# ---------------------------------------------------
# Utility: 等比例縮放
# ---------------------------------------------------
def resize_keep_ratio(img, max_width=450):
    w, h = img.size
    if w <= max_width:
        return img
    scale = max_width / w
    new_size = (int(w*scale), int(h*scale))
    return img.resize(new_size)

# ---------------------------------------------------
# 中值濾波
# ---------------------------------------------------
def median_filter(arr, ksize):
    pad = ksize // 2
    padded = np.pad(arr, ((pad,pad),(pad,pad),(0,0)), mode="edge")
    out = np.zeros_like(arr)
    H, W, C = arr.shape

    for i in range(H):
        for j in range(W):
            window = padded[i:i+ksize, j:j+ksize]
            out[i, j] = np.median(window, axis=(0, 1))
    return out

# ---------------------------------------------------
# Laplacian 銳利化 (with alpha slider)
# ---------------------------------------------------
def laplacian_sharpen(arr, alpha=1.0):
    kernel = np.array([[0, -1, 0],
                       [-1, 4, -1],
                       [0, -1, 0]])

    pad = 1
    padded = np.pad(arr, ((pad,pad),(pad,pad),(0,0)), mode='edge')
    H, W, C = arr.shape

    lap = np.zeros_like(arr, dtype=np.float32)

    for i in range(H):
        for j in range(W):
            for c in range(3):
                window = padded[i:i+3, j:j+3, c]
                lap[i, j, c] = np.sum(window * kernel)

    sharpened = arr.astype(np.float32) + alpha * lap
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    return sharpened

# ---------------------------------------------------
# Unsharp Mask (更強烈銳利)
# ---------------------------------------------------
def unsharp_mask_pil(img, radius, amount):
    return img.filter(ImageFilter.UnsharpMask(radius=radius, percent=amount*100, threshold=0))

# ---------------------------------------------------
# 處理影像
# ---------------------------------------------------
def apply_filter():
    global arr_original, processed_img

    if arr_original is None:
        return

    # 右側顯示
    option = combo.get()

    if option == "原圖":
        out = arr_original

    elif option == "3×3 中值濾波":
        out = median_filter(arr_original, 3)

    elif option == "5×5 中值濾波":
        out = median_filter(arr_original, 5)

    elif option == "7×7 中值濾波":
        out = median_filter(arr_original, 7)

    elif option == "拉普拉斯銳利化":
        alpha = sharp_slider.get()
        out = laplacian_sharpen(arr_original, alpha)

    elif option == "Unsharp Mask":
        radius = radius_slider.get()
        amount = amount_slider.get()
        pil_img = Image.fromarray(arr_original)
        out = np.array(unsharp_mask_pil(pil_img, radius, amount))

    processed_img = Image.fromarray(out)

    # 更新左右對照
    update_side_by_side()


# ---------------------------------------------------
# 左右滑動比較顯示
# ---------------------------------------------------
def update_side_by_side(event=None):
    if arr_original is None or processed_img is None:
        return

    # resize
    ori_display = resize_keep_ratio(Image.fromarray(arr_original))
    pro_display = resize_keep_ratio(processed_img)

    w, h = ori_display.size

    # create combined image
    split = compare_slider.get()
    cut = int(w * split)

    combined = Image.new("RGB", (w, h))
    combined.paste(ori_display.crop((0, 0, cut, h)), (0, 0))
    combined.paste(pro_display.crop((cut, 0, w, h)), (cut, 0))

    global tk_compare
    tk_compare = ImageTk.PhotoImage(combined)
    compare_label.config(image=tk_compare)


# ---------------------------------------------------
# 選擇圖片
# ---------------------------------------------------
def open_file():
    global arr_original, processed_img, tk_compare

    path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")]
    )
    if not path:
        return

    img = Image.open(path).convert("RGB")
    arr_original = np.array(img)
    processed_img = img

    update_side_by_side()


# ---------------------------------------------------
# zoom 放大鏡
# ---------------------------------------------------
def update_zoom(event):
    if arr_original is None:
        return
    if processed_img is None:
        return

    zoom_factor = zoom_slider.get()

    x = event.x
    y = event.y

    img = resize_keep_ratio(processed_img)
    w, h = img.size

    if x < 20 or y < 20 or x > w-20 or y > h-20:
        return

    crop = img.crop((x-20, y-20, x+20, y+20))
    crop = crop.resize((int(40*zoom_factor), int(40*zoom_factor)))

    global tk_zoom
    tk_zoom = ImageTk.PhotoImage(crop)
    zoom_label.config(image=tk_zoom)


# ---------------------------------------------------
# GUI START
# ---------------------------------------------------
window = tk.Tk()
window.title("進階影像處理 GUI（左右比較＋銳利化＋放大鏡）")
window.geometry("1100x800")

arr_original = None
processed_img = None

# --------------------------
# 控制列
# --------------------------
top_frame = tk.Frame(window)
top_frame.pack(pady=10)

btn_load = tk.Button(top_frame, text="選擇圖片", command=open_file, font=("Arial", 14))
btn_load.grid(row=0, column=0, padx=10)

combo = ttk.Combobox(top_frame, values=[
    "原圖",
    "3×3 中值濾波",
    "5×5 中值濾波",
    "7×7 中值濾波",
    "拉普拉斯銳利化",
    "Unsharp Mask"
], font=("Arial", 14), width=20, state="readonly")
combo.grid(row=0, column=1, padx=10)
combo.current(0)

btn_apply = tk.Button(top_frame, text="套用濾波", command=apply_filter, font=("Arial", 14))
btn_apply.grid(row=0, column=2, padx=10)

# --------------------------
# 調整滑桿（銳利化 α）
# --------------------------
tk.Label(window, text="拉普拉斯銳利化 α 強度", font=("Arial", 12)).pack()
sharp_slider = tk.Scale(window, from_=1, to=20, orient="horizontal")
sharp_slider.set(5)
sharp_slider.pack(pady=5)

# --------------------------
# Unsharp Mask 滑桿
# --------------------------
frame_um = tk.Frame(window)
frame_um.pack()

tk.Label(frame_um, text="Unsharp Mask：Radius", font=("Arial", 12)).grid(row=0, column=0)
radius_slider = tk.Scale(frame_um, from_=1, to=10, orient="horizontal")
radius_slider.set(2)
radius_slider.grid(row=0, column=1)

tk.Label(frame_um, text="Amount", font=("Arial", 12)).grid(row=0, column=2)
amount_slider = tk.Scale(frame_um, from_=1, to=5, orient="horizontal")
amount_slider.set(2)
amount_slider.grid(row=0, column=3)

# --------------------------
# 左右滑動比較
# --------------------------
tk.Label(window, text="左右比較滑桿（左：原圖 / 右：濾波後）", font=("Arial", 12)).pack(pady=3)
compare_slider = tk.Scale(window, from_=0.0, to=1.0, resolution=0.01,
                          orient="horizontal", command=update_side_by_side)
compare_slider.set(0.5)
compare_slider.pack()

# --------------------------
# 比較顯示
# --------------------------
compare_label = tk.Label(window)
compare_label.pack(pady=10)

# --------------------------
# Zoom 放大鏡
# --------------------------
tk.Label(window, text="放大倍率", font=("Arial", 12)).pack()
zoom_slider = tk.Scale(window, from_=2, to=10, orient="horizontal")
zoom_slider.set(4)
zoom_slider.pack()

zoom_label = tk.Label(window)
zoom_label.pack()

compare_label.bind("<Motion>", update_zoom)

window.mainloop()

