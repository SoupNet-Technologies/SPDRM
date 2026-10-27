import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "site_data.json"
BUILD_SCRIPT = BASE_DIR / "build.py"

class JSONEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("SPDRM Site Editor")
        # Colors
        self.bg_color = "#320227"
        self.fg_color = "#ffffff"
        self.accent_color = "#cd52e2"
        self.secondary_bg = "#6e0051"
        self.text_color = "#e0e0e0"

        #self.root.geometry("1000x800")
        self.root.attributes('-zoomed', True)
        self.root.configure(bg=self.bg_color)

        icon_path = BASE_DIR.parent / "assets" / "icon.png"
        self.ico = tk.PhotoImage(file=str(icon_path))
        self.root.iconphoto(True, self.ico)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.apply_styles()

        self.data = {}
        self.current_card_index = None
        self.current_route_slug = None
        self.load_data()
        
        self.setup_ui()
        self.populate_all()
        
        self.root.bind("<Control-s>", lambda e: self.save_data())

    def apply_styles(self):
        self.style.configure(".", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TButton", background=self.secondary_bg, foreground=self.fg_color, borderwidth=1, font=('Times New Roman', 12))
        self.style.map("TButton", background=[("active", self.accent_color)])
        
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.secondary_bg, foreground=self.fg_color, padding=[10, 2], font=('Times New Roman', 16))
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_color)])
        
        self.style.configure("TLabelframe", background=self.bg_color, foreground=self.accent_color)
        self.style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.accent_color, font=("Arial", 10, "bold"))

        self.style.configure("Treeview", background=self.secondary_bg, foreground=self.fg_color, fieldbackground=self.secondary_bg)
        self.style.map("Treeview", background=[("selected", self.accent_color)])

        self.style.configure("TEntry", fieldbackground=self.secondary_bg, foreground=self.fg_color, insertcolor=self.fg_color)
        self.style.configure("TCombobox", fieldbackground=self.secondary_bg, foreground=self.fg_color, insertcolor=self.fg_color)
        self.style.map("TCombobox", fieldbackground=[("readonly", self.secondary_bg)])

        self.style.configure("TCheckbutton", background=self.bg_color, foreground=self.fg_color)
        self.style.map("TCheckbutton", 
            indicatorcolor=[("selected", self.accent_color), ("pressed", self.accent_color)],
            background=[("active", self.bg_color)]
        )

        self.style.configure("Vertical.TScrollbar", gripcount=0, background=self.secondary_bg, troughcolor=self.bg_color, bordercolor=self.bg_color, arrowcolor=self.accent_color)

        self.style.configure("Text", font=('Arial', 16))

    def load_data(self):
        try:
            if JSON_PATH.exists():
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            else:
                self.data = {"site":{}, "meta":{}, "layout":{}, "routes":{}, "nav":[], "ads":[], "pwa":{}}
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Failed to load JSON: {e}\n\nTo prevent data loss, the editor will exit. Please fix the JSON syntax issue in site_data.json first.")
            import sys
            sys.exit(1)

    def save_data(self):
        try:
            self.gather_all()
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            messagebox.showinfo("Success", "Data saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON: {e}")

    def run_build(self):
        self.save_data()
        try:
            result = subprocess.run(["python3", str(BUILD_SCRIPT)], capture_output=True, text=True)
            if result.returncode == 0:
                msg = result.stdout
                if result.stderr.strip():
                    msg += f"\n\nWarnings:\n{result.stderr.strip()}"
                messagebox.showinfo("Build Success", msg)
            else:
                messagebox.showerror("Build Failed", result.stderr)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run build: {e}")

    def setup_ui(self):
        # Main Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Build Site", command=self.run_build).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reload", command=self.reload).pack(side=tk.LEFT, padx=2)

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_global = ttk.Frame(self.notebook)
        self.tab_routes = ttk.Frame(self.notebook)
        self.tab_nav = ttk.Frame(self.notebook)
        self.tab_ads_pwa = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_global, text="Global Settings")
        self.notebook.add(self.tab_routes, text="Routes")
        self.notebook.add(self.tab_nav, text="Navigation")
        self.notebook.add(self.tab_ads_pwa, text="Ads & PWA")

        self.setup_global_tab()
        self.setup_routes_tab()
        self.setup_nav_tab()
        self.setup_ads_pwa_tab()

    def reload(self):
        if messagebox.askyesno("Reload", "Unsaved changes will be lost. Reload?"):
            self.current_route_slug = None
            self.current_card_index = None
            for child in self.right_route_frame.winfo_children():
                child.destroy()
            self.load_data()
            self.populate_all()

    # MARK: --- Global Tab ---
    def setup_global_tab(self):
        # Using a simple canvas + frame for scrolling
        canvas = tk.Canvas(self.tab_global, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_global, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Global basic fields
        f = ttk.LabelFrame(self.scrollable_frame, text="Basic Info")
        f.pack(fill=tk.X, padx=10, pady=5)
        self.fields_global = {}
        for i, (label, key) in enumerate([("Site URL", "url"), ("Last Modified", "lastmod")]):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ent = ttk.Entry(f, width=100)
            ent.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.fields_global[key] = ent

        # Site Section
        f = ttk.LabelFrame(self.scrollable_frame, text="Site Identity")
        f.pack(fill=tk.X, padx=10, pady=5)
        self.fields_site = {}
        for i, (label, key) in enumerate([("Title", "title"), ("SEO Title", "seo_title"), ("Tagline", "tagline")]):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ent = ttk.Entry(f, width=100)
            ent.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.fields_site[key] = ent

        # Meta Section
        f = ttk.LabelFrame(self.scrollable_frame, text="Meta Tags")
        f.pack(fill=tk.X, padx=10, pady=5)
        self.fields_meta = {}
        for i, (label, key) in enumerate([("Description", "description"), ("Keywords", "keywords"), ("Author", "author"), ("Theme Color", "theme_color")]):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ent = ttk.Entry(f, width=100)
            ent.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.fields_meta[key] = ent

        # Layout Section
        f = ttk.LabelFrame(self.scrollable_frame, text="Layout Assets")
        f.pack(fill=tk.X, padx=10, pady=5)
        self.fields_layout = {}
        for i, (label, key) in enumerate([("Header Image", "header_img"), ("Nav Image", "nav_img"), ("Footer HTML", "footer_html")]):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ent = ttk.Entry(f, width=100)
            ent.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.fields_layout[key] = ent

    # MARK: --- Routes Tab ---
    def setup_routes_tab(self):
        paned = ttk.PanedWindow(self.tab_routes, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        self.route_list = tk.Listbox(left_frame, bg=self.secondary_bg, fg=self.fg_color, selectbackground=self.accent_color, borderwidth=0, highlightthickness=0, exportselection=False)
        self.route_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.route_list.bind("<<ListboxSelect>>", self.on_route_select)

        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Add", command=self.add_route).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Del", command=self.delete_route, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Rename", command=self.rename_route).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Up", command=lambda: self.move_route(-1), width=4).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Dn", command=lambda: self.move_route(1), width=4).pack(side=tk.LEFT, padx=2)

        self.right_route_frame = ttk.Frame(paned)
        paned.add(self.right_route_frame, weight=10)
        
        self.current_route_slug = None

    def on_route_select(self, event):
        selection = self.route_list.curselection()
        if not selection: return
        slug = self.route_list.get(selection[0])
        if slug == self.current_route_slug: return
        self.load_route_editor(slug)

    def load_route_editor(self, slug):
        if self.current_route_slug:
            self.save_current_route()
        
        self.current_route_slug = slug
        self.current_card_index = None
        for child in self.right_route_frame.winfo_children():
            child.destroy()

        route = self.data["routes"][slug]
        
        # General Route Fields
        f = ttk.LabelFrame(self.right_route_frame, text=f"Route: {slug}")
        f.pack(fill=tk.X, padx=10, pady=5)
        
        self.route_fields = {}
        
        row = 0
        ttk.Label(f, text="Type").grid(row=row, column=0, sticky=tk.W)
        self.route_type_var = tk.StringVar(value=route.get("type", "content"))
        cb = ttk.Combobox(f, textvariable=self.route_type_var, values=["content", "iframe", "404", "abyss", "interactive"])
        cb.grid(row=row, column=1, sticky=tk.W)
        cb.bind("<<ComboboxSelected>>", lambda e: self.load_route_editor(slug))
        row += 1

        fields = [("Title", "title"), ("Ads", "ads"), ("Sitemap", "sitemap"), ("Priority", "priority"), ("BG Image", "bg_image")]
        # Some types don't use all fields
        rtype = self.route_type_var.get()
        
        for label, key in fields:
            if rtype in ("404", "abyss") and key in ("title", "bg_image"): continue
            if rtype == "iframe" and key == "title": continue
            
            ttk.Label(f, text=label).grid(row=row, column=0, sticky=tk.W)
            if key in ("ads", "sitemap"):
                var = tk.BooleanVar(value=route.get(key, True))
                ttk.Checkbutton(f, variable=var).grid(row=row, column=1, sticky=tk.W)
                self.route_fields[key] = var
            else:
                ent = ttk.Entry(f, width=40)
                ent.insert(0, str(route.get(key, "")))
                ent.grid(row=row, column=1, sticky=tk.W)
                self.route_fields[key] = ent
            row += 1

        # Meta (list of 3 strings)
        f_meta = ttk.LabelFrame(self.right_route_frame, text="Meta [Title Suffix, Desc, Keywords]")
        f_meta.pack(fill=tk.X, padx=10, pady=5)
        self.route_meta_fields = []
        meta = route.get("meta", ["", "", ""])
        for i in range(3):
            ent = ttk.Entry(f_meta, width=60)
            val = meta[i] if i < len(meta) else ""
            ent.insert(0, val)
            ent.pack(fill=tk.X, padx=5, pady=2)
            self.route_meta_fields.append(ent)

        # Type Specific
        if rtype == "content":
            self.setup_cards_editor(route)
        elif rtype == "iframe":
            f_spec = ttk.LabelFrame(self.right_route_frame, text="Iframe URL")
            f_spec.pack(fill=tk.X, padx=10, pady=5)
            self.route_iframe_ent = ttk.Entry(f_spec, width=80)
            self.route_iframe_ent.insert(0, route.get("iframe", ""))
            self.route_iframe_ent.pack(padx=5, pady=5)
        elif rtype == "404":
            f_spec = ttk.LabelFrame(self.right_route_frame, text="404 Body HTML")
            f_spec.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.route_body_text = tk.Text(f_spec, height=10, bg=self.secondary_bg, fg=self.text_color, insertbackground=self.fg_color)
            self.route_body_text.insert("1.0", route.get("body", ""))
            self.route_body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        elif rtype == "interactive":
            f_spec = ttk.LabelFrame(self.right_route_frame, text="Interactive Content")
            f_spec.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            self.backtick_warn = ttk.Label(f_spec, text="⚠️ Warning: Backticks (`) might break rendering if not careful.", foreground="orange")
            
            ttk.Label(f_spec, text="HTML:").pack(anchor=tk.W)
            self.route_html_text = tk.Text(f_spec, height=10, bg=self.secondary_bg, fg=self.text_color, insertbackground=self.fg_color)
            self.route_html_text.insert("1.0", route.get("html", ""))
            self.route_html_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
            self.route_html_text.bind("<KeyRelease>", self.check_backticks)
            
            ttk.Label(f_spec, text="Onload JS:").pack(anchor=tk.W)
            self.route_onload_ent = ttk.Entry(f_spec, width=80)
            self.route_onload_ent.insert(0, route.get("onload", ""))
            self.route_onload_ent.pack(fill=tk.X, padx=5, pady=2)
            self.route_onload_ent.bind("<KeyRelease>", self.check_backticks)
            
            self.check_backticks(None)

    def check_backticks(self, event):
        if not hasattr(self, "route_html_text"): return
        html = self.route_html_text.get("1.0", tk.END)
        js = self.route_onload_ent.get()
        if "`" in html or "`" in js:
            self.backtick_warn.pack(anchor=tk.W, padx=5)
        else:
            self.backtick_warn.pack_forget()

    # MARK: Card Editor
    def setup_cards_editor(self, route):
        f_cards = ttk.LabelFrame(self.right_route_frame, text="Cards")
        f_cards.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        paned = ttk.PanedWindow(f_cards, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        self.card_list = tk.Listbox(left, bg=self.secondary_bg, fg=self.fg_color, selectbackground=self.accent_color, borderwidth=0, highlightthickness=0, exportselection=False)
        self.card_list.pack(fill=tk.BOTH, expand=True)
        self.card_list.bind("<<ListboxSelect>>", self.on_card_select)
        
        btn_f = ttk.Frame(left)
        btn_f.pack(fill=tk.X)
        ttk.Button(btn_f, text="+", width=3, command=self.add_card).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="-", width=3, command=self.delete_card).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="Up", width=4, command=lambda: self.move_card(-1)).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="Dn", width=4, command=lambda: self.move_card(1)).pack(side=tk.LEFT)

        self.card_detail = ttk.Frame(paned)
        paned.add(self.card_detail, weight=2)
        
        ttk.Label(self.card_detail, text="Card Title").pack(anchor=tk.W)
        self.card_title_ent = ttk.Entry(self.card_detail)
        self.card_title_ent.pack(fill=tk.X, padx=5)
        ttk.Label(self.card_detail, text="Card Body (HTML)").pack(anchor=tk.W)
        self.card_body_text = tk.Text(self.card_detail, height=10, bg=self.secondary_bg, fg=self.text_color, insertbackground=self.fg_color, wrap=tk.WORD, font=('DejaVu Serif', 14))
        self.card_body_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        self.current_cards = route.get("cards", [])
        self.current_card_index = None
        self.update_card_list()

    def update_card_list(self):
        self.card_list.delete(0, tk.END)
        for i, card in enumerate(self.current_cards):
            title = card.get("title", "")
            if not title: 
                body_snippet = card.get('body', '').strip()[:20]
                title = f"[No Title] {body_snippet}..." if body_snippet else f"Card {i+1}"
            self.card_list.insert(tk.END, title)

    def on_card_select(self, event):
        selection = self.card_list.curselection()
        # Save previous card if index is valid
        if self.current_card_index is not None and self.current_card_index < len(self.current_cards):
            self.save_current_card(update_list=False)
        
        if not selection: 
            # We don't clear the index here anymore to avoid losing state on focus loss
            return
        
        idx = selection[0]
        self.current_card_index = idx
        card = self.current_cards[idx]
        self.card_title_ent.delete(0, tk.END)
        self.card_title_ent.insert(0, card.get("title", ""))
        self.card_body_text.delete("1.0", tk.END)
        self.card_body_text.insert("1.0", card.get("body", ""))

    def save_current_card(self, update_list=True):
        if self.current_card_index is not None and self.current_card_index < len(self.current_cards):
            title = self.card_title_ent.get()
            body = self.card_body_text.get("1.0", tk.END).strip()
            self.current_cards[self.current_card_index]["title"] = title
            self.current_cards[self.current_card_index]["body"] = body
            if update_list:
                # Update just this item in listbox
                display_title = title if title else f"[No Title] {body[:20]}..."
                if not title and not body: display_title = f"Card {self.current_card_index + 1}"
                self.card_list.delete(self.current_card_index)
                self.card_list.insert(self.current_card_index, display_title)
                self.card_list.selection_set(self.current_card_index)

    def add_card(self):
        self.save_current_card()
        self.current_cards.append({"title": "New Card", "body": ""})
        self.update_card_list()
        last_idx = len(self.current_cards) - 1
        self.card_list.selection_clear(0, tk.END)
        self.card_list.selection_set(last_idx)
        self.card_list.see(last_idx)
        self.on_card_select(None)

    def delete_card(self):
        selection = self.card_list.curselection()
        if not selection: return
        idx = selection[0]
        if messagebox.askyesno("Delete", "Are you sure you want to delete this card?"):
            del self.current_cards[idx]
            self.current_card_index = None
            self.card_title_ent.delete(0, tk.END)
            self.card_body_text.delete("1.0", tk.END)
            self.update_card_list()

    def move_card(self, delta):
        selection = self.card_list.curselection()
        if not selection: return
        idx = selection[0]
        new_idx = idx + delta
        if 0 <= new_idx < len(self.current_cards):
            self.save_current_card(update_list=False)
            item = self.current_cards.pop(idx)
            self.current_cards.insert(new_idx, item)
            self.update_card_list()
            self.card_list.selection_set(new_idx)
            self.current_card_index = new_idx
            self.card_list.see(new_idx)

    def move_route(self, delta):
        selection = self.route_list.curselection()
        if not selection: return
        idx = selection[0]
        new_idx = idx + delta
        keys = list(self.data["routes"].keys())
        if 0 <= new_idx < len(keys):
            self.save_current_route()
            slug = keys[idx]
            # Reorder dictionary
            new_routes = {}
            keys.pop(idx)
            keys.insert(new_idx, slug)
            for k in keys:
                new_routes[k] = self.data["routes"][k]
            self.data["routes"] = new_routes
            self.populate_routes()
            self.route_list.selection_set(new_idx)
            self.load_route_editor(slug)

    def add_route(self):
        name = simpledialog.askstring("Add Route", "Enter slug for new route:")
        if name:
            if name in self.data["routes"]:
                messagebox.showerror("Error", "Route already exists")
                return
            self.data["routes"][name] = {"type": "content", "title": name, "cards": []}
            self.populate_routes()
            idx = list(self.data["routes"].keys()).index(name)
            self.route_list.selection_set(idx)
            self.load_route_editor(name)

    def delete_route(self):
        selection = self.route_list.curselection()
        if not selection: return
        slug = self.route_list.get(selection[0])
        if messagebox.askyesno("Delete", f"Are you sure you want to delete route '{slug}'?"):
            del self.data["routes"][slug]
            self.current_route_slug = None
            self.populate_routes()
            for child in self.right_route_frame.winfo_children():
                child.destroy()

    def rename_route(self):
        selection = self.route_list.curselection()
        if not selection: return
        old_slug = self.route_list.get(selection[0])
        new_slug = simpledialog.askstring("Rename Route", f"Enter new slug for '{old_slug}':", initialvalue=old_slug)
        if new_slug and new_slug != old_slug:
            if new_slug in self.data["routes"]:
                messagebox.showerror("Error", "New slug already exists")
                return
            
            # Save current route before renaming if it's the one we're renaming
            if self.current_route_slug == old_slug:
                self.save_current_route()
            
            # Preserve order by creating a new dict
            new_routes = {}
            for k, v in self.data["routes"].items():
                if k == old_slug:
                    new_routes[new_slug] = v
                else:
                    new_routes[k] = v
            self.data["routes"] = new_routes
            
            if self.current_route_slug == old_slug:
                self.current_route_slug = new_slug
            
            # Update Nav if it uses this slug
            def update_nav_slugs(items):
                for item in items:
                    if item.get("slug") == old_slug: item["slug"] = new_slug
                    if "children" in item: update_nav_slugs(item["children"])
            update_nav_slugs(self.data.get("nav", []))
            
            self.populate_routes()
            self.populate_nav()
            idx = list(self.data["routes"].keys()).index(new_slug)
            self.route_list.selection_set(idx)
            self.load_route_editor(new_slug)

    def save_current_route(self):
        if not self.current_route_slug: return
        route = self.data["routes"][self.current_route_slug]
        route["type"] = self.route_type_var.get()
        
        for key, widget in self.route_fields.items():
            if isinstance(widget, tk.BooleanVar):
                route[key] = widget.get()
            else:
                val = widget.get()
                if key == "priority":
                    try: route[key] = float(val)
                    except: route[key] = 0.8
                else:
                    route[key] = val
        
        route["meta"] = [ent.get() for ent in self.route_meta_fields]
        
        rtype = route["type"]
        if rtype == "content":
            self.save_current_card()
            route["cards"] = self.current_cards
        elif rtype == "iframe":
            route["iframe"] = self.route_iframe_ent.get()
        elif rtype == "404":
            route["body"] = self.route_body_text.get("1.0", tk.END).strip()
        elif rtype == "interactive":
            route["html"] = self.route_html_text.get("1.0", tk.END).strip()
            route["onload"] = self.route_onload_ent.get()

    # MARK: --- Nav Tab ---
    def setup_nav_tab(self):
        paned = ttk.PanedWindow(self.tab_nav, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        
        self.nav_tree = ttk.Treeview(left, columns=("slug"), show="tree headings")
        self.nav_tree.heading("#0", text="Label")
        self.nav_tree.heading("slug", text="Slug")
        self.nav_tree.pack(fill=tk.BOTH, expand=True)
        self.nav_tree.bind("<<TreeviewSelect>>", self.on_nav_select)
        
        btn_f = ttk.Frame(left)
        btn_f.pack(fill=tk.X)
        ttk.Button(btn_f, text="Add Top", command=self.add_nav_top).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="Add Child", command=self.add_nav_child).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="Delete", command=self.delete_nav).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="Up", command=lambda: self.move_nav(-1)).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="Dn", command=lambda: self.move_nav(1)).pack(side=tk.LEFT)

        right = ttk.Frame(paned)
        paned.add(right, weight=1)
        
        ttk.Label(right, text="Label").pack(anchor=tk.W)
        self.nav_label_ent = ttk.Entry(right)
        self.nav_label_ent.pack(fill=tk.X, padx=5)
        self.nav_label_ent.bind("<KeyRelease>", self.update_nav_item)
        
        ttk.Label(right, text="Slug").pack(anchor=tk.W)
        self.nav_slug_cb = ttk.Combobox(right)
        self.nav_slug_cb.pack(fill=tk.X, padx=5)
        self.nav_slug_cb.bind("<<ComboboxSelected>>", self.update_nav_item)

    def on_nav_select(self, event):
        sel = self.nav_tree.selection()
        if not sel: return
        item = self.nav_tree.item(sel[0])
        self.nav_label_ent.delete(0, tk.END)
        self.nav_label_ent.insert(0, item["text"])
        
        slugs = list(self.data.get("routes", {}).keys())
        self.nav_slug_cb["values"] = slugs
        self.nav_slug_cb.set(item["values"][0] if item["values"] else "")

    def update_nav_item(self, event):
        sel = self.nav_tree.selection()
        if not sel: return
        label = self.nav_label_ent.get()
        slug = self.nav_slug_cb.get()
        self.nav_tree.item(sel[0], text=label, values=(slug,))
        self.save_nav_from_tree()

    def add_nav_top(self):
        item = self.nav_tree.insert("", tk.END, text="New Item", values=("",))
        self.nav_tree.selection_set(item)
        self.save_nav_from_tree()

    def add_nav_child(self):
        sel = self.nav_tree.selection()
        if not sel: return
        # Check depth (only 1 level of children supported by SPDRM)
        parent = self.nav_tree.parent(sel[0])
        if parent != "":
            messagebox.showwarning("Warning", "SPDRM only supports 1 level of children in navigation.")
            return
        
        item = self.nav_tree.insert(sel[0], tk.END, text="New Child", values=("",))
        self.nav_tree.item(sel[0], open=True)
        self.nav_tree.selection_set(item)
        self.save_nav_from_tree()

    def delete_nav(self):
        sel = self.nav_tree.selection()
        if not sel: return
        self.nav_tree.delete(sel[0])
        self.save_nav_from_tree()

    def move_nav(self, delta):
        sel = self.nav_tree.selection()
        if not sel: return
        node = sel[0]
        parent = self.nav_tree.parent(node)
        idx = self.nav_tree.index(node)
        self.nav_tree.move(node, parent, idx + delta)
        self.save_nav_from_tree()

    def save_nav_from_tree(self):
        new_nav = []
        for top_id in self.nav_tree.get_children(""):
            item = self.nav_tree.item(top_id)
            entry = {"label": item["text"], "slug": item["values"][0]}
            children = self.nav_tree.get_children(top_id)
            if children:
                entry["children"] = []
                for child_id in children:
                    citem = self.nav_tree.item(child_id)
                    entry["children"].append({"label": citem["text"], "slug": citem["values"][0]})
            new_nav.append(entry)
        self.data["nav"] = new_nav

    # MARK: --- Ads & PWA Tab ---
    def setup_ads_pwa_tab(self):
        paned = ttk.PanedWindow(self.tab_ads_pwa, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Ads
        f_ads = ttk.LabelFrame(paned, text="Ads")
        paned.add(f_ads, weight=1)
        
        self.ads_tree = ttk.Treeview(f_ads, columns=("src", "url"), show="headings")
        self.ads_tree.heading("src", text="Image Path")
        self.ads_tree.heading("url", text="Target URL")
        self.ads_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ads_tree.bind("<<TreeviewSelect>>", self.on_ad_select)
        
        scrollbar = ttk.Scrollbar(f_ads, orient="vertical", command=self.ads_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ads_tree.configure(yscrollcommand=scrollbar.set)
        
        f_ad_edit = ttk.Frame(paned)
        paned.add(f_ad_edit, weight=0)
        
        ttk.Label(f_ad_edit, text="Src:").grid(row=0, column=0)
        self.ad_src_ent = ttk.Entry(f_ad_edit, width=40)
        self.ad_src_ent.grid(row=0, column=1)
        ttk.Button(f_ad_edit, text="Browse", command=self.browse_ad_img).grid(row=0, column=2)
        
        ttk.Label(f_ad_edit, text="URL:").grid(row=1, column=0)
        self.ad_url_ent = ttk.Entry(f_ad_edit, width=40)
        self.ad_url_ent.grid(row=1, column=1)
        
        ttk.Button(f_ad_edit, text="Update Ad", command=self.update_ad).grid(row=2, column=1)
        ttk.Button(f_ad_edit, text="Add New", command=self.add_ad).grid(row=2, column=2)
        ttk.Button(f_ad_edit, text="Delete", command=self.delete_ad).grid(row=2, column=0)

        # PWA
        f_pwa = ttk.LabelFrame(paned, text="PWA Settings")
        paned.add(f_pwa, weight=1)
        self.fields_pwa = {}
        pwa_fields = [
            ("Short Name", "short_name"),
            ("Background Color", "background_color"),
            ("Theme Color", "theme_color"),
            ("Icon Path", "icon"),
            ("Icon Sizes", "icon_sizes")
        ]
        for i, (label, key) in enumerate(pwa_fields):
            ttk.Label(f_pwa, text=label).grid(row=i, column=0, sticky=tk.W)
            ent = ttk.Entry(f_pwa, width=40)
            ent.grid(row=i, column=1, sticky=tk.W)
            self.fields_pwa[key] = ent

    def on_ad_select(self, event):
        sel = self.ads_tree.selection()
        if not sel: return
        item = self.ads_tree.item(sel[0])
        self.ad_src_ent.delete(0, tk.END)
        self.ad_src_ent.insert(0, item["values"][0])
        self.ad_url_ent.delete(0, tk.END)
        self.ad_url_ent.insert(0, item["values"][1])

    def browse_ad_img(self):
        f = filedialog.askopenfilename(initialdir=BASE_DIR.parent / "assets/ads")
        if f:
            try:
                rel = os.path.relpath(f, BASE_DIR.parent)
                self.ad_src_ent.delete(0, tk.END)
                self.ad_src_ent.insert(0, rel)
            except:
                self.ad_src_ent.delete(0, tk.END)
                self.ad_src_ent.insert(0, f)

    def update_ad(self):
        sel = self.ads_tree.selection()
        if not sel: return
        self.ads_tree.item(sel[0], values=(self.ad_src_ent.get(), self.ad_url_ent.get()))
        self.save_ads_from_tree()

    def add_ad(self):
        item = self.ads_tree.insert("", tk.END, values=(self.ad_src_ent.get(), self.ad_url_ent.get()))
        self.ads_tree.selection_set(item)
        self.save_ads_from_tree()

    def delete_ad(self):
        sel = self.ads_tree.selection()
        if not sel: return
        self.ads_tree.delete(sel[0])
        self.save_ads_from_tree()

    def save_ads_from_tree(self):
        self.data["ads"] = []
        for child in self.ads_tree.get_children():
            v = self.ads_tree.item(child)["values"]
            self.data["ads"].append({"src": v[0], "url": v[1]})

    # MARK: --- Populate & Gather ---
    def populate_all(self):
        # Global
        for key, ent in self.fields_global.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(self.data.get(key, "")))
        
        site = self.data.get("site", {})
        for key, ent in self.fields_site.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(site.get(key, "")))
            
        meta = self.data.get("meta", {})
        for key, ent in self.fields_meta.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(meta.get(key, "")))
            
        layout = self.data.get("layout", {})
        for key, ent in self.fields_layout.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(layout.get(key, "")))
            
        # PWA
        pwa = self.data.get("pwa", {})
        for key, ent in self.fields_pwa.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(pwa.get(key, "")))
            
        # Routes
        self.populate_routes()
        
        # Nav
        self.populate_nav()
        
        # Ads
        self.populate_ads()

    def populate_routes(self):
        self.route_list.delete(0, tk.END)
        for slug in self.data.get("routes", {}).keys():
            self.route_list.insert(tk.END, slug)

    def populate_nav(self):
        self.nav_tree.delete(*self.nav_tree.get_children())
        for item in self.data.get("nav", []):
            parent = self.nav_tree.insert("", tk.END, text=item.get("label", ""), values=(item.get("slug", ""),))
            for child in item.get("children", []):
                self.nav_tree.insert(parent, tk.END, text=child.get("label", ""), values=(child.get("slug", ""),))

    def populate_ads(self):
        self.ads_tree.delete(*self.ads_tree.get_children())
        for ad in self.data.get("ads", []):
            self.ads_tree.insert("", tk.END, values=(ad.get("src", ""), ad.get("url", "")))

    def gather_all(self):
        # Site/Meta/Global
        for key, ent in self.fields_global.items():
            self.data[key] = ent.get()
        
        if "site" not in self.data: self.data["site"] = {}
        for key, ent in self.fields_site.items():
            self.data["site"][key] = ent.get()
            
        if "meta" not in self.data: self.data["meta"] = {}
        for key, ent in self.fields_meta.items():
            self.data["meta"][key] = ent.get()
            
        if "layout" not in self.data: self.data["layout"] = {}
        for key, ent in self.fields_layout.items():
            self.data["layout"][key] = ent.get()
            
        if "pwa" not in self.data: self.data["pwa"] = {}
        for key, ent in self.fields_pwa.items():
            self.data["pwa"][key] = ent.get()

        self.save_current_route()
        self.save_nav_from_tree()
        self.save_ads_from_tree()

if __name__ == "__main__":
    root = tk.Tk()
    # Simple ScrollableFrame implementation if missing
    app = JSONEditor(root)
    
    root.mainloop()
