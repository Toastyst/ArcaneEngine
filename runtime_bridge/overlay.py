import tkinter as tk

class Overlay:
    def __init__(self, position=(100, 100), size=(400, 300), conv_manager=None, input_handler=None):
        self.root = tk.Tk()
        self.root.geometry(f"{size[0]}x{size[1]}+{position[0]}+{position[1]}")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.8)
        self.root.overrideredirect(True)
        self.root.configure(bg='black')

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.conv_manager = conv_manager
        self.input_handler = input_handler

        # Header for drag
        self.header = tk.Frame(self.root, bg='gray', height=20)
        self.header.grid(row=0, column=0, sticky='ew')
        self.header.bind("<Button-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.do_drag)

        self.toggle_button = tk.Button(self.header, text="^", command=self.toggle_collapse, bg='gray', fg='white')
        self.toggle_button.pack(side=tk.RIGHT)

        self.title_label = tk.Label(self.header, text="ArcaneEngine Overlay", bg='gray', fg='white')
        self.title_label.pack(side=tk.LEFT)

        self.text_frame = tk.Frame(self.root)
        self.text = tk.Text(self.text_frame, bg='black', fg='white', font=('Arial', 12), state='disabled', wrap='word')
        self.scrollbar = tk.Scrollbar(self.text_frame, orient="vertical", command=self.text.yview)
        self.text['yscrollcommand'] = self.scrollbar.set
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_frame.grid(row=1, column=0, sticky='nsew')

        self.bottom_frame = tk.Frame(self.root, bg='gray', height=30)  # Increased height for input
        self.bottom_frame.grid(row=2, column=0, sticky='ew')

        # Input entry
        self.entry = tk.Entry(self.bottom_frame, bg='black', fg='white', font=('Arial', 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.pack_forget()  # Hide initially

        # New Chat button
        self.new_chat_btn = tk.Button(self.bottom_frame, text="New Chat", command=self.new_chat, bg='gray', fg='white')
        self.new_chat_btn.pack(side=tk.LEFT)
        self.new_chat_btn.pack_forget()  # Hide initially

        # Resize handle
        self.resize_handle = tk.Label(self.bottom_frame, text="↘", bg='gray', width=3, height=2, relief='raised', bd=1, cursor='size_nw_se')
        self.resize_handle.pack(side=tk.RIGHT, anchor=tk.SE)
        self.resize_handle.bind("<Button-1>", self.start_resize)
        self.resize_handle.bind("<B1-Motion>", self.do_resize)

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.withdraw()

        self.collapsed = False
        self.expanded_height = None

    def show_response(self, response):
        self.root.after(0, lambda: self._show(response))

    def _show(self, response):
        self.text.config(state='normal')
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, response)
        self.text.see(tk.END)
        self.text.config(state='disabled')
        self.root.deiconify()
        self.root.update_idletasks()
        if self.expanded_height is None:
            self.expanded_height = self.root.winfo_height()

    def hide(self):
        self.root.after(0, self.root.withdraw)

    def toggle_collapse(self):
        if self.collapsed:
            self.text_frame.grid(row=1, column=0, sticky='nsew')
            self.bottom_frame.grid(row=2, column=0, sticky='ew')
            self.toggle_button.config(text="^")
            if self.expanded_height:
                self.root.geometry(f"{self.root.winfo_width()}x{self.expanded_height}")
        else:
            self.text_frame.grid_remove()
            self.bottom_frame.grid_remove()
            self.toggle_button.config(text="v")
            self.root.update_idletasks()
            collapsed_h = self.header.winfo_height()
            self.root.geometry(f"{self.root.winfo_width()}x{collapsed_h}")
        self.collapsed = not self.collapsed

    def start_drag(self, event):
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()

    def do_drag(self, event):
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.resize_start_w = self.root.winfo_width()
        self.resize_start_h = self.root.winfo_height()

    def do_resize(self, event):
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y
        w = max(200, self.resize_start_w + dx)
        h = max(100, self.resize_start_h + dy)
        self.root.geometry(f"{w}x{h}")

    def enable_input(self):
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.new_chat_btn.pack(side=tk.LEFT)
        self.entry.bind("<Return>", lambda e: self._handle_enter())

    def _handle_enter(self):
        user_input = self.entry.get().strip()
        if user_input:
            self.entry.delete(0, tk.END)
            self.input_handler(user_input)

    def new_chat(self):
        self.conv_manager.clear()
        self.clear_text()
        self.hide_input()
        self.show_ended_msg()

    def hide_input(self):
        self.entry.pack_forget()
        self.new_chat_btn.pack_forget()

    def show_ended_msg(self):
        self.text.config(state='normal')
        self.text.insert(tk.END, "\n\nConversation ended. Send new payload from game to start again.")
        self.text.see(tk.END)
        self.text.config(state='disabled')

    def append_response(self, user_content, asst_content):
        self.text.config(state='normal')
        self.text.insert(tk.END, f"\n\n--- User: {user_content}\n\n--- Assistant: {asst_content}\n")
        self.text.see(tk.END)
        self.text.config(state='disabled')
        self.root.deiconify()
        self.root.update_idletasks()
        if self.expanded_height is None:
            self.expanded_height = self.root.winfo_height()

    def clear_text(self):
        self.text.config(state='normal')
        self.text.delete(1.0, tk.END)
        self.text.config(state='disabled')

    def run(self):
        self.root.mainloop()
