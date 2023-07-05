import os
import tkinter as tk
import tkinter.font as tk_font
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image, ImageGrab
import cv2
import numpy as np
import pytesseract
from pathlib import Path


def open_text_file():
    try:
        name = fd.askopenfilename()
        if name:
            with open(name, "r") as f:
                lines = f.read()
                txt_main.insert(tk.END, lines)
    except Exception as e:
        messagebox.showinfo(message="Failed to open the text file: {}".format(str(e)))


def save_text_file():
    try:
        name = fd.asksaveasfile(filetypes=(("Text files", "*.txt"), ("All files", "*.*"))).name
        input_text = txt_main.get('1.0', tk.END)
        f = open(name, 'w')
        f.write(input_text)
        f.close()
    except Exception as e:
        messagebox.showinfo(message="Failed to save the text file: {}".format(str(e)))


def list_dirs_file():
    name = fd.askdirectory()
    txt_main.delete("1.0", tk.END)
    for line in tree(Path(name)):
        txt_main.insert(tk.END, line)


def tree(dir_path: Path, prefix: str = ''):
    # prefix components:
    # space = '    '
    # branch = '│   '
    space = '    '
    branch = '    '
    # # pointers:
    # tee = '├── '
    # last = '└── '
    tee = '    '
    last = '    '

    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name + "\n"
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)


def increase_text_font():
    font_size = font_style['size']
    font_style.configure(size=font_size + 2)


def decrease_text_font():
    font_size = font_style['size']
    font_style.configure(size=font_size - 2)


def do_popup(event):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()


def norm_image(image_input):
    image = image_input

    if var_normalize.get() == 1:
        norm_img = np.zeros((image_input.shape[0], image_input.shape[1]))
        normalize_value1 = normalize_scale1.get()
        normalize_value2 = normalize_scale2.get()
        image = cv2.normalize(image_input, norm_img, normalize_value1, normalize_value2, cv2.NORM_MINMAX)

    if var_gray.get() == 1:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if var_threshold.get() == 1:
        threshold_value = threshold_scale.get()
        threshold_max_value = threshold_max_scale.get()
        if selected_threshold_option.get() == "Regular":
            image = cv2.threshold(image, threshold_value, threshold_max_value, cv2.THRESH_BINARY)[1]
        elif selected_threshold_option.get() == "Adaptive":
            # Apply Gaussian adaptive thresholding
            block_size = 11  # Size of the neighborhood for adaptive thresholding
            c = 2  # Constant subtracted from the mean or weighted mean
            image = cv2.adaptiveThreshold(image, threshold_max_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                          block_size, c)

    if var_blur.get() == 1:
        blur_kernel = blur_scale.get()
        image = cv2.GaussianBlur(image, (blur_kernel, blur_kernel), 0)

    return image


def process_image(img_path):
    try:
        if img_path:
            img = ImageTk.PhotoImage(file=img_path)
            lblImage.config(image=img)
            lblImage.image = img
            if var_extract_text.get() == 1:
                img_ocr = np.array(Image.open(img_path))
                get_text(img_ocr)

            if var_image_processing.get() == 1:
                img_normalized = np.array(Image.open(img_path))
                img_normalized = norm_image(img_normalized)
                img_normalized = Image.fromarray(img_normalized)
                img_normalized_tk = ImageTk.PhotoImage(img_normalized)
                lblNormalized.config(image=img_normalized_tk)
                lblNormalized.image = img_normalized_tk
    except Exception as e:
        messagebox.showinfo(message="Failed to open the image file: {}".format(str(e)))


def open_image_file():
    try:
        img_path = fd.askopenfilename()
        process_image(img_path)
    except Exception as e:
        messagebox.showinfo(message="Failed to open the image file: {}".format(str(e)))


def paste_image():
    try:
        temp_path = "some_image.tiff"
        im = ImageGrab.grabclipboard()
        if im:
            im.save(temp_path)
            process_image(temp_path)
            os.remove(temp_path)
    except Exception as e:
        messagebox.showinfo(message="Failed to paste the image: {}".format(str(e)))


def get_text(image):
    try:
        img_ocr = norm_image(image)
        # Set the path to your Tesseract installation
        pytesseract.pytesseract.tesseract_cmd = r'C:\Python311\tesseract-ocr\tesseract.exe'
        text_ocr = pytesseract.image_to_string(img_ocr)
        txt_main.delete('1.0', tk.END)
        txt_main.insert(tk.END, text_ocr)
    except Exception as e:
        messagebox.showinfo(message="Failed to extract text from the image: {}".format(str(e)))


def activate_image_processing():
    if var_image_processing.get() == 1:
        ch_normalize.pack(side=tk.LEFT, anchor='ne')
        ch_threshold.pack(side=tk.LEFT, anchor='ne')
        ch_blur.pack(side=tk.LEFT, anchor='ne')
        ch_gray.pack(side=tk.LEFT, anchor='ne')
        frame_normalize.pack(fill=tk.BOTH)
        frame_threshold_a.pack(fill=tk.BOTH)
        frame_threshold_b.pack(fill=tk.BOTH)
        frame_blur.pack(fill=tk.BOTH)
        container_normalized.pack(fill=tk.BOTH)
    else:
        ch_normalize.pack_forget()
        var_normalize.set(0)
        ch_threshold.pack_forget()
        var_threshold.set(0)
        ch_blur.pack_forget()
        var_blur.set(0)
        ch_gray.pack_forget()
        var_gray.set(0)
        normalize_scale1.pack_forget()
        normalize_scale2.pack_forget()
        threshold_label.pack_forget()
        threshold_dropdown.pack_forget()
        threshold_scale.pack_forget()
        threshold_max_scale.pack_forget()
        blur_scale.pack_forget()
        frame_normalize.pack_forget()
        frame_threshold_a.pack_forget()
        frame_threshold_b.pack_forget()
        frame_blur.pack_forget()
        container_normalized.pack_forget()


def activate_normalize():
    if var_normalize.get() == 1:
        normalize_scale1.pack(side=tk.LEFT, padx=10, pady=5)
        normalize_scale2.pack(side=tk.LEFT, padx=10, pady=5)
        frame_normalize.pack(fill=tk.BOTH)
        container_normalized.pack_forget()
        container_normalized.pack(fill=tk.BOTH)
    else:
        normalize_scale1.pack_forget()
        normalize_scale2.pack_forget()
        frame_normalize.pack_forget()
        container_normalized.pack_forget()
        container_normalized.pack(fill=tk.BOTH)


def activate_var_threshold():
    if var_threshold.get() == 1:
        threshold_label.pack(side=tk.LEFT, padx=10, pady=5)
        threshold_dropdown.pack(side=tk.LEFT, padx=10, pady=5)
        threshold_scale.pack(side=tk.LEFT, padx=10, pady=5)
        threshold_max_scale.pack(side=tk.LEFT, padx=10, pady=5)
        frame_threshold_a.pack(fill=tk.BOTH)
        frame_threshold_b.pack(fill=tk.BOTH)
        container_normalized.pack_forget()
        container_normalized.pack(fill=tk.BOTH)
    else:
        threshold_label.pack_forget()
        threshold_dropdown.pack_forget()
        threshold_scale.pack_forget()
        threshold_max_scale.pack_forget()
        frame_threshold_a.pack_forget()
        frame_threshold_b.pack_forget()
        container_normalized.pack_forget()
        container_normalized.pack(fill=tk.BOTH)


def activate_var_blur():
    if var_blur.get() == 1:
        blur_scale.pack(side=tk.LEFT, padx=10, pady=5)
        frame_blur.pack(fill=tk.BOTH)
        container_normalized.pack_forget()
        container_normalized.pack(fill=tk.BOTH)
    else:
        blur_scale.pack_forget()
        frame_blur.pack_forget()
        container_normalized.pack_forget()
        container_normalized.pack(fill=tk.BOTH)


past = 1


def odd_fix(n):
    global past
    n = int(n)
    if not n % 2:
        blur_scale.set(n + 1 if n > past else n - 1)
        past = blur_scale.get()


def handle_threshold_selection(selection):
    if selection == "Regular":
        threshold_max_scale.pack_forget()
        threshold_scale.pack(side=tk.LEFT, padx=10, pady=5)
        threshold_max_scale.pack(side=tk.LEFT, padx=10, pady=5)
    elif selection == "Adaptive":
        threshold_scale.pack_forget()


root = tk.Tk()
font_style = tk_font.Font(family="Courier New", size=14)
root.title("NdNote (developed by Neven Dujmovic)")
root.geometry("500x500+1200+100")
root.attributes('-topmost', True)

tab_parent = ttk.Notebook(root)

# Tab 1: Text
tab1 = ttk.Frame(tab_parent)
tab_parent.add(tab1, text="Text")

frame_topTab1 = tk.Frame(tab1)
frame_topTab1.pack(fill=tk.BOTH)

btn_openFile = tk.Button(frame_topTab1, text='File Open', bd='5', command=open_text_file)
btn_openFile.pack(side=tk.LEFT, padx=10, pady=5, anchor='ne')

btn_saveFile = tk.Button(frame_topTab1, text='File Save', bd='5', command=save_text_file)
btn_saveFile.pack(side=tk.LEFT, padx=10, pady=5, anchor='ne')

btn_listDirs = tk.Button(frame_topTab1, text='List Dirs & Files', bd='5', command=list_dirs_file)
btn_listDirs.pack(side=tk.LEFT, padx=10, pady=5, anchor='ne')

btn_textSizeIncrease = tk.Button(frame_topTab1, text='<+>', bd='5', command=increase_text_font)
btn_textSizeIncrease.pack(side=tk.RIGHT, padx=5, pady=5, anchor='ne')

btn_textSizeDecrease = tk.Button(frame_topTab1, text='>-<', bd='5', command=decrease_text_font)
btn_textSizeDecrease.pack(side=tk.RIGHT, padx=0, pady=5, anchor='ne')

txt_main = tk.Text(tab1, height=20, width=100, bg='#ffffff', fg='#000000', font=font_style, wrap=tk.WORD)
txt_main.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, padx=10, pady=10, anchor='e')

y_scrollbar = tk.Scrollbar(tab1, orient=tk.VERTICAL, command=txt_main.yview)
y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
txt_main["yscrollcommand"] = y_scrollbar.set

m = tk.Menu(txt_main, tearoff=0)
m.add_command(label="Cut", command=lambda: root.focus_get().event_generate("<<Cut>>"))
m.add_command(label="Copy", command=lambda: root.focus_get().event_generate("<<Copy>>"))
m.add_command(label="Paste", command=lambda: root.focus_get().event_generate("<<Paste>>"))
m.add_separator()
m.add_command(label="Select All", command=lambda: root.focus_get().event_generate("<<SelectAll>>"))

txt_main.bind("<Button-3>", do_popup)

# Tab 2: Image
tab2 = ttk.Frame(tab_parent)
tab_parent.add(tab2, text="Image")

frame_topTab2 = tk.Frame(tab2)
frame_topTab2.pack(fill=tk.BOTH)

btn_openFile = tk.Button(frame_topTab2, text='File Open', bd='5', command=open_image_file)
btn_openFile.pack(side=tk.LEFT, padx=10, pady=5, anchor='ne')

var_extract_text = tk.IntVar()
ch_extract_text = tk.Checkbutton(frame_topTab2, text='Convert Image to Text', variable=var_extract_text, onvalue=1,
                                 offvalue=0)
ch_extract_text.pack(side=tk.LEFT, anchor='ne')

btn_paste = tk.Button(frame_topTab2, text="Paste image", command=paste_image)
btn_paste.pack(side=tk.RIGHT, padx=20, pady=5, anchor='ne')

container = ttk.Frame(tab2)
canvas = tk.Canvas(container)
scrollbar_Y = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
scrollbar_X = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=canvas.xview)
scrollable_frame = ttk.Frame(canvas)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar_Y.set)
canvas.configure(xscrollcommand=scrollbar_X.set)

scrollbar_X.pack(side=tk.TOP, fill=tk.X)

lblImage = ttk.Label(scrollable_frame)
lblImage.pack()

container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES, padx=10, pady=10, anchor='e')
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
scrollbar_Y.pack(side=tk.LEFT, fill=tk.Y)

# Tab 3: Image preprocessing
tab3 = ttk.Frame(tab_parent)
tab_parent.add(tab3, text="Image preprocessing")

frame_image_processing = tk.Frame(tab3)
frame_image_processing.pack(fill=tk.BOTH)

var_image_processing = tk.IntVar()
ch_image_processing = tk.Checkbutton(frame_image_processing, text='Image preprocessing', variable=var_image_processing,
                                     onvalue=1, offvalue=0, command=activate_image_processing)
ch_image_processing.pack(side=tk.LEFT, anchor='ne')

var_normalize = tk.IntVar()
ch_normalize = tk.Checkbutton(frame_image_processing, text='Normalize', variable=var_normalize, onvalue=1, offvalue=0,
                              command=activate_normalize)
# ch_normalize.pack(side=tk.LEFT, anchor='ne')

var_threshold = tk.IntVar()
ch_threshold = tk.Checkbutton(frame_image_processing, text='Threshold', variable=var_threshold, onvalue=1, offvalue=0,
                              command=activate_var_threshold)
# ch_threshold.pack(side=tk.LEFT, anchor='ne')

var_blur = tk.IntVar()
ch_blur = tk.Checkbutton(frame_image_processing, text='Blur', variable=var_blur, onvalue=1, offvalue=0,
                         command=activate_var_blur)
# ch_blur.pack(side=tk.LEFT, anchor='ne')

var_gray = tk.IntVar()
ch_gray = tk.Checkbutton(frame_image_processing, text='Grayscale', variable=var_gray, onvalue=1, offvalue=0)
# ch_gray.pack(side=tk.LEFT, anchor='ne')

frame_normalize = tk.Frame(tab3)
frame_normalize.pack(fill=tk.BOTH)

normalize_scale1 = tk.Scale(frame_normalize, from_=0, to=100, orient=tk.HORIZONTAL, length=200, label="Normalize alpha")
normalize_scale1.set(0)
# normalize_scale1.pack(side=tk.LEFT, padx=10, pady=5)

normalize_scale2 = tk.Scale(frame_normalize, from_=0, to=255, orient=tk.HORIZONTAL, length=200, label="Normalize beta")
normalize_scale2.set(255)
# normalize_scale2.pack(side=tk.LEFT, padx=10, pady=5)

frame_threshold_a = tk.Frame(tab3)
frame_threshold_a.pack(fill=tk.BOTH)

# Dropdown variable
selected_threshold_option = tk.StringVar()
selected_threshold_option.set("--")  # Set pre-selected value

# Label for the dropdown
threshold_label = tk.Label(frame_threshold_a, text="Select a type of threshold:")
# threshold_label.pack(side=tk.LEFT, padx=10, pady=5)

# Dropdown control
threshold_dropdown = tk.OptionMenu(frame_threshold_a, selected_threshold_option, "--", "Regular", "Adaptive",
                                   command=handle_threshold_selection)
# threshold_dropdown.pack(side=tk.LEFT, padx=10, pady=5)

frame_threshold_b = tk.Frame(tab3)
frame_threshold_b.pack(fill=tk.BOTH)

threshold_scale = tk.Scale(frame_threshold_b, from_=0, to=255, orient=tk.HORIZONTAL, length=200,
                           label="Threshold Scale")
threshold_scale.set(100)
# threshold_scale.pack(side=tk.LEFT, padx=10, pady=5)

threshold_max_scale = tk.Scale(frame_threshold_b, from_=0, to=255, orient=tk.HORIZONTAL, length=200,
                               label="Threshold Max Scale")
threshold_max_scale.set(255)
# threshold_max_scale.pack(side=tk.LEFT, padx=10, pady=5)

frame_blur = tk.Frame(tab3)
frame_blur.pack(fill=tk.BOTH)

blur_scale = tk.Scale(frame_blur, from_=1, to=55, command=odd_fix, orient=tk.HORIZONTAL, length=200,
                      label="Blur Kernel Size")
blur_scale.set(1)
# blur_scale.pack(side=tk.LEFT, padx=10, pady=5)

container_normalized = ttk.Frame(tab3)
canvas_normalized = tk.Canvas(container_normalized)
scrollbar_normalized_Y = ttk.Scrollbar(container_normalized, orient=tk.VERTICAL, command=canvas_normalized.yview)
scrollbar_normalized_X = ttk.Scrollbar(container_normalized, orient=tk.HORIZONTAL, command=canvas_normalized.xview)
scrollable_frame_normalized = ttk.Frame(canvas_normalized)

canvas_normalized.create_window((0, 0), window=scrollable_frame_normalized, anchor="nw")
canvas_normalized.configure(yscrollcommand=scrollbar_normalized_Y.set)
canvas_normalized.configure(xscrollcommand=scrollbar_normalized_X.set)

scrollbar_normalized_X.pack(side=tk.TOP, fill=tk.X)

lblNormalized = ttk.Label(scrollable_frame_normalized)
lblNormalized.pack()

container_normalized.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES, padx=10, pady=10, anchor='e')
canvas_normalized.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
scrollbar_normalized_Y.pack(side=tk.LEFT, fill=tk.Y)

# Pack everything
tab_parent.pack(expand=tk.YES, fill='both')
root.mainloop()
