from components.gui import SearchGUI
from license import check_license
import tkinter as tk
from tkinter import messagebox

if __name__ == '__main__':
    if check_license():
        root=tk.Tk()
        root.iconbitmap('icon.ico')
        crawler_gui=SearchGUI(root)
        root.mainloop()
    else:
        messagebox.showinfo(title='License expired', message='Please contact author')



