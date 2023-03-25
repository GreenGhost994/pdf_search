import tkinter as tk
from tkinter import IntVar, StringVar, ttk, Radiobutton, Checkbutton
from version import VERSION, PROGRAM_NAME, PROGRAM_ABOUT
from components.pdfs import get_data_from_pdfs, analyze_pdf_with_tesseract
from components.data import load_data, dump_data, update_data, search_data
from os.path import isdir, join, isfile, dirname
from os import startfile, listdir
import threading


class SearchGUI:
    def __init__(self, master):
        self.master=master
        master.title(f'{PROGRAM_NAME}')
        master.geometry("300x90")
        master.configure(bg='white')
        master.resizable(width=False, height=False)

        menubar=tk.Menu(master)
        filemenu=tk.Menu(menubar, tearoff=0)
        filemenu.config(bg="white")
        filemenu.add_command(label="Reload data", command=self.get_pdf_data)
        filemenu.add_command(label="Settings", command=self.program_settings)
        filemenu.add_command(label="About", command=self.get_about)
        menubar.add_cascade(label="Menu", menu=filemenu)
        menubar.config(bg="white")
        master.config(menu=menubar)

        self.find_phrase_label=tk.Label(master, text="Find phrase:")
        self.find_phrase_label.config(bg="white")
        self.find_phrase_label.pack()

        find_word_text=IntVar()
        self.find_word=tk.Entry(master, justify='center', text=find_word_text, borderwidth=0)
        find_word_text.set(load_data('settings').get('phrase', 'Enter phrase here'))
        self.find_word.pack(fill=tk.X, expand=True, pady=5)

        self.find_data_button=tk.Button(master, text="Search", command=self.find_data)
        self.find_data_button.config(bg="gray90", relief='flat', activebackground="gray90", borderwidth=0)
        self.find_data_button.pack(fill=tk.X, expand=True)

        master.bind('<Return>', lambda event: self.find_data())

        CreateToolTip(self.find_word, '1. Reload data. (Menu)\n2. Enter phrase here. (Under Find phrase)\n3. Press '
                                      'Enter or Search.')

    def get_pdf_data(self):
        """Create popup with path selection"""

        popup=tk.Toplevel(self.master)
        popup.geometry("400x65")
        popup.iconbitmap('icon.ico')
        popup.configure(bg='white')
        popup.resizable(width=False, height=False)

        folder_path_label=tk.Label(popup, text="Folder path:")
        folder_path_label.config(bg="white")
        folder_path_label.pack(fill=tk.X, expand=True)

        folder_path_text=IntVar()
        folder_path_entry=tk.Entry(popup, text=folder_path_text, justify='center')
        folder_path_text.set(load_data('settings').get('path', ''))
        folder_path_entry.pack(fill=tk.X, expand=True)

        ok_button=tk.Button(popup, text="Load data", command=lambda: self.handle_folder_path(popup,
                                                                                             folder_path_entry.get()))
        ok_button.config(bg="SkyBlue3", relief='flat', activebackground="SkyBlue3", borderwidth=0)
        ok_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        cancel_button=tk.Button(popup, text="Cancel", command=popup.destroy)
        cancel_button.config(bg="gray85", relief='flat', activebackground="gray85", borderwidth=0)
        cancel_button.pack(side=tk.RIGHT)

        CreateToolTip(popup, '1. Enter folder path with pdf files.\n2. Press Load data.\n\nLoading data may take some time. You only need to load the data once if there is no change in the files.')
        popup.grab_set()
        popup.focus_set()

    def handle_folder_path(self, popup, folder_path):
        """Analyze all files in folder and create progressbar."""

        if isdir(folder_path):
            for widget in popup.winfo_children():
                widget.destroy()

            self.progress=ttk.Progressbar(popup, orient="horizontal", length=100, mode="determinate", value=0)
            self.progress.pack(fill=tk.BOTH, expand=True)

            self.progress_label=tk.Label(popup, text="Inicialization")
            self.progress_label.config(bg="white")
            self.progress_label.pack(fill=tk.X, expand=True)

            update_data('settings', path=folder_path)
            settings_data = load_data('settings')
            mode=settings_data.get('mode', 'elements')
            tesseract_status=settings_data.get('tesseract_activate', 0)
            tesseract_path=settings_data.get('tesseract_path', '')
            no_of_files=len([x for x in listdir(folder_path) if x.lower().endswith('.pdf')])
            results={}

            def process_pdfs():
                try:
                    nonlocal results
                    nonlocal no_of_files
                    for filename in listdir(folder_path):
                        if filename.endswith('.pdf'):
                            self.progress_label.config(text=filename)
                            res = get_data_from_pdfs(folder_path, filename, mode)

                            # add tesseract results
                            if tesseract_status:
                                tess_res=analyze_pdf_with_tesseract(folder_path, filename, mode, tesseract_path, 'pol')
                                new_res={}
                                for key in res.keys() | tess_res.keys():
                                    new_res[key]=res.get(key, []) + tess_res.get(key, [])
                                res = new_res

                            results.update(res)
                            self.progress["value"]+=100 / no_of_files
                            self.progress.update_idletasks()

                    dump_data(results, 'data')
                    popup.destroy()
                except RuntimeError as e:
                    print(e)

            def before_close():
                if hasattr(self, "progress") and self.progress is not None:
                    self.progress.stop()
                    self.progress.destroy()
                self.master.destroy()

            popup.protocol('WM_DELETE_WINDOW', before_close)
            threading.Thread(target=process_pdfs).start()

    def show_results(self):
        """Display list of files containing keywords."""

        def open_file():
            selection=lbx.curselection()
            if selection:
                file_path=lbx.get(selection[0])
                startfile(join(load_data('settings').get('path', ''), file_path))

        def list_of_drawings(files):
            lbx.delete(0, tk.END)
            for f in files:
                lbx.insert(0, f)
            lbx_height=min(lbx.size(), 10)
            item_height=lbx.winfo_reqheight() // lbx_height
            popup_height=min(lbx_height * item_height + 100, lbx_height * lbx.size() + 100)
            lbx.config(height=lbx_height, width=max(len(max(files, key=len)), 30))
            popup.geometry(f"{max(len(max(files, key=len)) * 10, 300)}x{popup_height}")
            popup.configure(bg='white')

        results=search_data(self.find_word.get(), load_data('settings').get('type', 'exact'))
        if results:
            self.find_data_button.config(text='Search')
            popup=tk.Toplevel(self.master)
            popup.iconbitmap('icon.ico')

            lbx=tk.Listbox(popup, borderwidth=0, highlightthickness=0)
            lbx.pack(fill="both", expand=1, padx=5)
            list_of_drawings(results)

            lbx.bind("<Double-Button-1>", lambda x: open_file())

            popup.grab_set()
            popup.focus_set()

            popup.bind('<Escape>', lambda e: popup.destroy())
            popup.bind("<BackSpace>", lambda e: popup.destroy())
            popup.protocol("WM_DELETE_WINDOW", popup.destroy)
        else:
            self.find_data_button.config(text="Not found")

    def find_data(self):
        update_data('settings', phrase=self.find_word.get())
        self.show_results()

    def get_about(self):
        """Display about data."""

        popup=tk.Toplevel(self.master)
        popup.iconbitmap('icon.ico')
        popup.configure(bg='white')

        version_label=tk.Label(popup, text=f"Version: {VERSION}")
        version_label.configure(bg='white')
        version_label.pack(pady=5, padx=10)

        author_label=tk.Label(popup, text="Author: Piotr Zieliński")
        author_label.configure(bg='white')
        author_label.pack(pady=5, padx=10)

        program_about_data='\n'.join(PROGRAM_ABOUT)
        info_label=tk.Label(popup, text=f"{program_about_data}")
        info_label.configure(bg='white')
        info_label.pack(pady=5, padx=10)

        popup.grab_set()
        popup.focus_set()

        popup.protocol("WM_DELETE_WINDOW", popup.destroy)

    def program_settings(self):
        """Settings panel."""

        popup=tk.Toplevel(self.master)
        popup.geometry("290x310")
        popup.iconbitmap('icon.ico')
        popup.configure(bg='white')

        # Mode
        mode_label=tk.Label(popup, text=f"Load mode:")
        mode_label.configure(bg='white')
        mode_label.pack(fill=tk.X, expand=True)

        self.rv1=StringVar(popup, load_data('settings').get('mode', 'elements'))
        style1=ttk.Style(popup)
        style1.configure("TRadiobutton", bg="white")
        values1={"All text".ljust(23): "text",
                 "Element names": "elements", }
        for (text, value) in values1.items():
            Radiobutton(popup, text=text, variable=self.rv1,
                        value=value, bg="white").pack(side='top', fill=tk.X, expand=True)

        ttk.Separator(popup, orient='horizontal').pack(fill='x', padx=5)

        # Type
        type_label=tk.Label(popup, text="Search type:")
        type_label.configure(bg='white')
        type_label.pack(fill=tk.X, expand=True)

        self.rv2=StringVar(popup, load_data('settings').get('type', 'exact'))
        style2=ttk.Style(popup)
        style2.configure("TRadiobutton", bg="white")
        values2={"Exact match".ljust(32): "exact",
                 "Phrase included in string": "included", }

        for (text, value) in values2.items():
            Radiobutton(popup, text=text, variable=self.rv2,
                        value=value, bg="white").pack(side='top', fill=tk.X, expand=True)

        ttk.Separator(popup, orient='horizontal').pack(fill='x', padx=5)

        # Tesseract
        self.cb_var=IntVar()
        checkbox_tesseract=Checkbutton(popup, text="Activate Tesseract (optical character recognition)", variable=self.cb_var, bg='white')
        self.cb_var.set(load_data('settings').get('tesseract_activate', 0))
        checkbox_tesseract.pack(fill=tk.X, expand=True, pady=5)

        tesseract_label=tk.Label(popup, text=f"Tesseract path:")
        tesseract_label.configure(bg='white')
        tesseract_label.pack(fill=tk.X, expand=True)

        self.tesseract_path_text=StringVar()
        self.tesseract_path=tk.Entry(popup, justify='center', text=self.tesseract_path_text, borderwidth=0)
        self.tesseract_path_text.set(load_data('settings').get('tesseract_path', r'path/to/tesseract.exe'))
        self.tesseract_path.pack(fill=tk.X, expand=True, pady=5)

        tesseract_lang_label=tk.Label(popup, text=f"Tesseract language:")
        tesseract_lang_label.configure(bg='white')
        tesseract_lang_label.pack(fill=tk.X, expand=True)

        self.tesseract_lang_text=StringVar()
        self.tesseract_lang=tk.Entry(popup, justify='center', text=self.tesseract_lang_text, borderwidth=0)
        self.tesseract_lang_text.set(load_data('settings').get('tesseract_lang', r'eng'))
        self.tesseract_lang.pack(fill=tk.X, expand=True, pady=5)

        # Apply button
        self.confirm_button=tk.Button(popup, text="Apply", command=lambda: self.apply_settings(popup))
        self.confirm_button.config(bg="gray90", relief='flat', activebackground="gray90", borderwidth=0)
        self.confirm_button.pack(fill=tk.X, expand=True)


        popup.grab_set()
        popup.focus_set()

        popup.protocol("WM_DELETE_WINDOW", popup.destroy)

        CreateToolTip(popup, 'All text:\nGet all strings from pdfs and store them in database.\n\nElement names:\n'
                             'Get filtered strings and store them in database (Strings with "_" and starting with '
                             'F... or 2F...)\n\n\nExact match:\nIf text contains more than keyword, '
                             'string would be not included.\n\nPhrase '
                             'is included in string:\nEg. '
                             '"W_123" '
                             'included in "W_ABC and W_123".\n\n\nTesseract is a text recognition (OCR) '
                             'Engine that can identify text on pdf. Use this method to analyze not selectable text on pdfs.\n'
                             "It is slow process so use only if necessary.\n"
                             "I recommend to use Search type: Phrase is included in string while using tesseract.")

    def apply_settings(self, popup):
        if self.cb_var.get():
            if not isfile(self.tesseract_path_text.get()):
                self.confirm_button.config(text="tesseract.exe not found")
                return
            elif not any(value.startswith(self.tesseract_lang_text.get()+'.traineddata') for value in listdir(join(dirname(
                self.tesseract_path_text.get()), 'tessdata'))):
                self.confirm_button.config(text="tesseract language not found")
                return
            update_data('settings', mode=self.rv1.get(), type=self.rv2.get(),
                        tesseract_path=self.tesseract_path_text.get(),
                        tesseract_lang=self.tesseract_lang_text.get(),
                        tesseract_activate=self.cb_var.get())
        else:
            update_data('settings', mode=self.rv1.get(), type=self.rv2.get(),
                        tesseract_activate=self.cb_var.get())
        popup.destroy()


class CreateToolTip(object):
    """create a tooltip for a given widget"""

    def __init__(self, widget, text='widget info'):
        self.waittime=500  # miliseconds
        self.wraplength=180  # pixels
        self.widget=widget
        self.text=text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id=None
        self.tw=None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id=self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id=self.id
        self.id=None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x=y=0
        x, y, cx, cy=self.widget.bbox("insert")
        x+=self.widget.winfo_rootx() + 25
        y+=self.widget.winfo_rooty() + 20
        self.tw=tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label=tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw=self.tw
        self.tw=None
        if tw:
            tw.destroy()
