import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox, filedialog
import threading
from datetime import datetime

# Environment Setup
os.environ["DISABLE_LOG_FILE"] = "true"
os.environ["WEBSITE_LOAD_TIMEOUT"] = "10"

# Add parent src directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from setup_driver import setup_driver
    from scrape_image import scrape_images
except ImportError:
    try:
        sys.path.append(os.path.join(os.getcwd(), 'src'))
        from setup_driver import setup_driver
        from scrape_image import scrape_images
    except ImportError as e:
        print(f"Import Error: {e}")

class AwesomeTheme:
    """Premium Modern Color Palette"""
    BG_APP = "#F3F4F6"         # Soft blue-grey background
    BG_CARD = "#FFFFFF"        # Pure white card
    PRIMARY = "#4F46E5"        # Indigo/Purple accent
    PRIMARY_HOVER = "#4338CA"  # Darker Indigo
    TEXT_MAIN = "#1F2937"      # Dark grey text
    TEXT_MUTED = "#6B7280"     # Muted text
    BORDER = "#E5E7EB"         # Light border
    INPUT_BG = "#F9FAFB"       # Very light grey input
    SUCCESS = "#10B981"        # Emerald green
    ERROR = "#EF4444"          # Red

class ImagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Imager Pro")
        self.root.geometry("700x750")
        self.root.configure(bg=AwesomeTheme.BG_APP)
        
        # Variables
        self.is_running = False
        self.driver = None
        
        # UI Setup
        self.setup_styles()
        self.create_layouts()
        self.center_window()
        
        self.log("🚀 System initialized and ready.", 'system')

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom Progress Bar
        style.configure("Modern.Horizontal.TProgressbar", 
                        background=AwesomeTheme.PRIMARY, 
                        troughcolor=AwesomeTheme.INPUT_BG,
                        borderwidth=0, thickness=6)

    def create_layouts(self):
        # --- HEADER SECTION ---
        header_frame = tk.Frame(self.root, bg=AwesomeTheme.PRIMARY, height=100)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Logo/Title Area
        tk.Label(header_frame, text="IMAGER PRO", 
                 font=("Helvetica", 22, "bold"),
                 bg=AwesomeTheme.PRIMARY, fg="white").pack(pady=(25, 0))
                 
        tk.Label(header_frame, text="The Ultimate High-Res Image Downloader", 
                 font=("Helvetica", 10, "normal"),
                 bg=AwesomeTheme.PRIMARY, fg="#E0E7FF").pack(pady=(2, 0))

        # --- MAIN CARD ---
        self.card = tk.Frame(self.root, bg=AwesomeTheme.BG_CARD, padx=40, pady=30,
                             highlightbackground=AwesomeTheme.BORDER, highlightthickness=1)
        self.card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 1. Search Section
        self.create_label("SEARCH QUERY", self.card)
        self.search_entry = self.create_input(self.card, "e.g. Cyberpunk City, 4K Nature, Portraits")
        
        # Spacing
        tk.Frame(self.card, bg=AwesomeTheme.BG_CARD, height=20).pack()

        # 2. Settings Grid (2 Columns)
        settings_grid = tk.Frame(self.card, bg=AwesomeTheme.BG_CARD)
        settings_grid.pack(fill=tk.X)

        # Col 1: Count
        col1 = tk.Frame(settings_grid, bg=AwesomeTheme.BG_CARD)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.create_label("IMAGE COUNT", col1)
        self.num_images_var = tk.StringVar(value="5")
        self.num_images_entry = self.create_input(col1, "5", var=self.num_images_var)

        # Col 2: Save Path
        col2 = tk.Frame(settings_grid, bg=AwesomeTheme.BG_CARD)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        self.create_label("SAVE LOCATION", col2)
        
        # Browse Group
        browse_frame = tk.Frame(col2, bg=AwesomeTheme.BG_CARD)
        browse_frame.pack(fill=tk.X)
        self.save_folder_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloaded_images"))
        
        self.save_folder_entry = tk.Entry(browse_frame, textvariable=self.save_folder_var,
                                         font=("Segoe UI", 11), bg=AwesomeTheme.INPUT_BG,
                                         relief=tk.FLAT, fg=AwesomeTheme.TEXT_MAIN)
        self.save_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(1, 0), pady=1)
        
        # Custom Browse Button
        self.browse_btn = tk.Button(browse_frame, text="Select Folder", 
                                   command=self.browse_folder,
                                   bg="#E0E7FF", fg=AwesomeTheme.PRIMARY,
                                   font=("Segoe UI", 9, "bold"),
                                   relief=tk.FLAT, cursor="hand2", padx=15)
        self.browse_btn.pack(side=tk.LEFT, padx=(10, 0), ipady=4)
        
        # Add bottom border to entry manually since relief=FLAT removes it
        tk.Frame(browse_frame, bg=AwesomeTheme.PRIMARY, height=2).pack(fill=tk.X, side=tk.BOTTOM)

        # Spacing
        tk.Frame(self.card, bg=AwesomeTheme.BG_CARD, height=30).pack()

        # 3. Big Action Button
        self.action_btn = tk.Button(self.card, text="START DOWNLOADING", 
                                    font=("Segoe UI", 12, "bold"),
                                    bg=AwesomeTheme.PRIMARY, 
                                    fg="white",
                                    activebackground=AwesomeTheme.PRIMARY_HOVER,
                                    activeforeground="white",
                                    relief=tk.FLAT,
                                    cursor="hand2",
                                    pady=12,
                                    command=self.toggle_scraping)
        self.action_btn.pack(fill=tk.X)

        # 4. Progress
        tk.Frame(self.card, bg=AwesomeTheme.BG_CARD, height=20).pack()
        self.progress = ttk.Progressbar(self.card, style="Modern.Horizontal.TProgressbar", mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 20))

        # 5. Log Area (Footer style)
        log_container = tk.Frame(self.card, bg=AwesomeTheme.INPUT_BG, padx=10, pady=10)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(log_container, text="ACTIVITY MONITOR", 
                 font=("Segoe UI", 8, "bold"),
                 bg=AwesomeTheme.INPUT_BG, fg=AwesomeTheme.TEXT_MUTED).pack(anchor=tk.W, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(log_container, height=6, 
                                                 font=("Consolas", 9),
                                                 bg=AwesomeTheme.INPUT_BG, 
                                                 fg=AwesomeTheme.TEXT_MAIN,
                                                 relief=tk.FLAT,
                                                 bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Setup Tags
        self.log_text.tag_config('info', foreground=AwesomeTheme.TEXT_MAIN)
        self.log_text.tag_config('success', foreground=AwesomeTheme.SUCCESS)
        self.log_text.tag_config('error', foreground=AwesomeTheme.ERROR)
        self.log_text.tag_config('system', foreground=AwesomeTheme.TEXT_MUTED)

    def create_label(self, text, parent):
        tk.Label(parent, text=text, 
                 font=("Segoe UI", 9, "bold"),
                 bg=AwesomeTheme.BG_CARD, 
                 fg=AwesomeTheme.TEXT_MUTED).pack(anchor=tk.W, pady=(0, 5))

    def create_input(self, parent, placeholder, var=None):
        frame = tk.Frame(parent, bg=AwesomeTheme.INPUT_BG)
        frame.pack(fill=tk.X, pady=(0, 5))
        
        entry = tk.Entry(frame, textvariable=var,
                         font=("Segoe UI", 11),
                         bg=AwesomeTheme.INPUT_BG,
                         fg=AwesomeTheme.TEXT_MAIN,
                         relief=tk.FLAT,
                         highlightthickness=0)
        entry.pack(fill=tk.X, ipady=8, padx=10)
        
        if not var: entry.insert(0, placeholder)
        
        # Bottom Border
        tk.Frame(parent, bg="#D1D5DB", height=1).pack(fill=tk.X, pady=(0, 15))
        
        return entry

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d: self.save_folder_var.set(d)

    def log(self, message, tag='info'):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def toggle_scraping(self):
        if self.is_running: self.stop_scraping()
        else: self.start_scraping()

    def start_scraping(self):
        query = self.search_entry.get().strip()
        if not query or query == "e.g. Cyberpunk City, 4K Nature, Portraits":
            messagebox.showwarning("Missing Input", "Please enter valid search terms.")
            return
            
        try:
            val = int(self.num_images_var.get())
            if val < 1: raise ValueError
        except:
            messagebox.showerror("Invalid Count", "Please enter a valid number (1-100).")
            return

        self.is_running = True
        self.action_btn.config(text="STOP DOWNLOADING", bg=AwesomeTheme.ERROR)
        self.progress.start(15)
        self.toggle_inputs(False)
        
        threading.Thread(target=self.run_process, daemon=True).start()

    def stop_scraping(self):
        self.is_running = False
        self.log("Stopping process...", 'system')

    def toggle_inputs(self, enable):
        state = 'normal' if enable else 'disabled'
        self.search_entry.config(state=state)
        self.num_images_entry.config(state=state)
        self.save_folder_entry.config(state=state)
        self.browse_btn.config(state=state)

    def run_process(self):
        try:
            path = self.save_folder_var.get().strip()
            os.environ['SAVE_FOLDER'] = path
            
            self.log(f"Config: Saving to {path}", 'info')
            self.log("Initializing WebDriver...", 'system')
            
            try:
                self.driver = setup_driver()
            except Exception as e:
                self.log(f"Driver Init Failed: {e}", 'error')
                return

            self.log("Browser connected. Starting batch job.", 'success')
            
            terms = [x.strip() for x in self.search_entry.get().split(',') if x.strip()]
            
            for i, term in enumerate(terms):
                if not self.is_running: break
                self.log(f"► Scraping: '{term}' ({i+1}/{len(terms)})", 'info')
                try:
                    scrape_images(self.driver, term, int(self.num_images_var.get()))
                    self.log(f"✓ Completed: '{term}'", 'success')
                except Exception as e:
                    self.log(f"✗ Failed: {e}", 'error')

            self.log("All operations completed.", 'success')

        except Exception as e:
            self.log(f"Critical Error: {e}", 'error')
        finally:
            if self.driver:
                self.log("Closing browser session...", 'system')
                try: self.driver.quit()
                except: pass
                self.driver = None
            self.finish()

    def finish(self):
        self.is_running = False
        self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.progress.stop()
        self.action_btn.config(text="START DOWNLOADING", bg=AwesomeTheme.PRIMARY)
        self.toggle_inputs(True)
        self.log("Ready for new task.", 'system')

if __name__ == "__main__":
    root = tk.Tk()
    app = ImagerGUI(root)
    root.mainloop()
