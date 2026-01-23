import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime

from setup_driver import setup_driver
from scrape_image import scrape_images


def app_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = app_base_path()


class AwesomeTheme:
    BG_APP = "#F3F4F6"
    BG_CARD = "#FFFFFF"
    PRIMARY = "#4F46E5"
    PRIMARY_HOVER = "#4338CA"
    TEXT_MAIN = "#1F2937"
    TEXT_MUTED = "#6B7280"
    BORDER = "#E5E7EB"
    INPUT_BG = "#F9FAFB"
    SUCCESS = "#10B981"
    ERROR = "#EF4444"


class ImagerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Imager Pro")
        self.root.geometry("1200x720")
        self.root.configure(bg=AwesomeTheme.BG_APP)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Thread control
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.ui_queue = queue.Queue()

        # Driver
        self.driver = None

        self.setup_styles()
        self.create_layout()
        self.center_window()

        # UI queue polling
        self.root.after(100, self.process_ui_queue)

        self.log("System ready.", "system")

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=AwesomeTheme.PRIMARY,
            troughcolor=AwesomeTheme.INPUT_BG,
            borderwidth=0,
            thickness=6,
        )

    def create_layout(self):
        header = tk.Frame(self.root, bg=AwesomeTheme.PRIMARY, height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="IMAGER PRO",
            font=("Segoe UI", 22, "bold"),
            bg=AwesomeTheme.PRIMARY,
            fg="white",
        ).pack(pady=(25, 0))

        tk.Label(
            header,
            text="High-Resolution Image Downloader",
            font=("Segoe UI", 10),
            bg=AwesomeTheme.PRIMARY,
            fg="#E0E7FF",
        ).pack()

        self.card = tk.Frame(
            self.root,
            bg=AwesomeTheme.BG_CARD,
            padx=40,
            pady=30,
            highlightbackground=AwesomeTheme.BORDER,
            highlightthickness=1,
        )
        self.card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.create_label("SEARCH QUERY")
        self.search_entry = self.create_input("e.g. Cyberpunk City, 4K Nature")

        self.create_label("IMAGE COUNT")
        self.count_var = tk.StringVar(value="5")
        self.count_entry = self.create_input("5", self.count_var)

        self.create_label("SAVE LOCATION")
        path_frame = tk.Frame(self.card, bg=AwesomeTheme.BG_CARD)
        path_frame.pack(fill=tk.X)

        self.save_var = tk.StringVar(value=os.path.join(BASE_DIR, "downloaded_images"))

        self.save_entry = tk.Entry(
            path_frame,
            textvariable=self.save_var,
            font=("Segoe UI", 11),
            bg=AwesomeTheme.INPUT_BG,
            relief=tk.FLAT,
        )
        self.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

        tk.Button(
            path_frame,
            text="Browse",
            command=self.browse_folder,
            bg="#E0E7FF",
            fg=AwesomeTheme.PRIMARY,
            relief=tk.FLAT,
        ).pack(side=tk.LEFT, padx=10)

        self.action_btn = tk.Button(
            self.card,
            text="START DOWNLOADING",
            font=("Segoe UI", 12, "bold"),
            bg=AwesomeTheme.PRIMARY,
            fg="white",
            relief=tk.FLAT,
            command=self.toggle,
            pady=12,
        )
        self.action_btn.pack(fill=tk.X, pady=20)

        self.progress = ttk.Progressbar(
            self.card,
            style="Modern.Horizontal.TProgressbar",
            mode="indeterminate",
        )
        self.progress.pack(fill=tk.X)

        self.log_text = scrolledtext.ScrolledText(
            self.card,
            height=8,
            font=("Consolas", 9),
            bg=AwesomeTheme.INPUT_BG,
            relief=tk.FLAT,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=15)
        self.log_text.config(state=tk.DISABLED)

        for tag, color in {
            "info": AwesomeTheme.TEXT_MAIN,
            "success": AwesomeTheme.SUCCESS,
            "error": AwesomeTheme.ERROR,
            "system": AwesomeTheme.TEXT_MUTED,
        }.items():
            self.log_text.tag_config(tag, foreground=color)

    def create_label(self, text):
        tk.Label(
            self.card,
            text=text,
            font=("Segoe UI", 9, "bold"),
            bg=AwesomeTheme.BG_CARD,
            fg=AwesomeTheme.TEXT_MUTED,
        ).pack(anchor=tk.W, pady=(10, 4))

    def create_input(self, placeholder, var=None):
        entry = tk.Entry(
            self.card,
            textvariable=var,
            font=("Segoe UI", 11),
            bg=AwesomeTheme.INPUT_BG,
            relief=tk.FLAT,
        )
        entry.pack(fill=tk.X, ipady=8)
        if not var:
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END))
        return entry

    def log(self, msg, tag="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def queue_log(self, msg, tag="info"):
        self.ui_queue.put(("log", msg, tag))

    def process_ui_queue(self):
        try:
            while True:
                item = self.ui_queue.get_nowait()
                if item[0] == "log":
                    _, msg, tag = item
                    self.log(msg, tag)
                elif item[0] == "done":
                    self.finish()
        except queue.Empty:
            pass
        self.root.after(100, self.process_ui_queue)

    def toggle(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.stop_event.set()
            self.queue_log("Stopping process...", "system")
            # Disable STOP to avoid spam clicks
            self.action_btn.config(state=tk.DISABLED)
        else:
            self.start()

    def start(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Required", "Enter search terms.")
            return

        try:
            count = int(self.count_var.get())
            if count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Count", "Enter a valid number.")
            return

        os.makedirs(self.save_var.get(), exist_ok=True)

        self.stop_event.clear()
        self.progress.start(15)
        self.action_btn.config(text="STOP", bg=AwesomeTheme.ERROR)

        self.worker_thread = threading.Thread(
            target=self.worker,
            args=(query, count),
            daemon=True,
        )
        self.worker_thread.start()

    def worker(self, query, count):
        try:
            self.queue_log("Initializing browser...", "system")
            self.driver = setup_driver()

            terms = [t.strip() for t in query.split(",") if t.strip()]

            for term in terms:
                if self.stop_event.is_set():
                    self.queue_log("Stopping current job...", "system")
                    break

                self.queue_log(f"Scraping: {term}", "info")

                scrape_images(self.driver, term, count)

                if self.stop_event.is_set():
                    break

                self.queue_log(f"Completed: {term}", "success")

        except Exception as e:
            self.queue_log(f"Error: {e}", "error")

        finally:
            self.cleanup_driver()
            self.ui_queue.put(("done",))

    def on_close(self):
        if self.worker_thread and self.worker_thread.is_alive():
            if not messagebox.askyesno(
                "Exit", "A download is still running.\nDo you want to stop and exit?"
            ):
                return

            self.stop_event.set()

            # Give Selenium a moment to shut down
            try:
                if self.driver:
                    self.driver.quit()
            except Exception:
                pass

        self.root.destroy()

    def cleanup_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def finish(self):
        self.progress.stop()
        self.action_btn.config(
            text="START DOWNLOADING", bg=AwesomeTheme.PRIMARY, state=tk.NORMAL
        )
        self.queue_log("Ready.", "system")

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.save_var.set(d)


if __name__ == "__main__":
    root = tk.Tk()
    ImagerGUI(root)
    root.mainloop()
