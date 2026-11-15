"""SHIFT - Gothic Academia Edition: the Tkinter user interface.

Layers (see README.txt):
  * this file  - presentation: windows, pages, themes, shortcuts
  * main.Store - application logic and local JSON storage
"""

import math
import os
import subprocess
import sys
import time
import traceback
import webbrowser
import tkinter as tk
import tkinter.font as tkfont
from datetime import date, datetime, timedelta
from tkinter import colorchooser, filedialog, messagebox, ttk

FOCUS_PRESETS = (15, 25, 45, 60)
DEFAULT_THEME = "Gothic Academia"

# --------------------------------------------------------------------- themes
THEMES = {
    "Gothic Academia": dict(
        bg="#15121a", panel="#1f1b27", panel2="#2a2535", fg="#ebe2d0",
        muted="#a0947f", accent="#c2a05a", border="#3b3347",
        danger="#c4616b", success="#86a77a"),
    "Midnight": dict(
        bg="#0d1117", panel="#161b22", panel2="#212936", fg="#e6edf3",
        muted="#8b98a8", accent="#58a6ff", border="#30363d",
        danger="#f0646f", success="#56d364"),
    "Lavender Dreams": dict(
        bg="#f1ecf9", panel="#faf7ff", panel2="#e4dbf1", fg="#2f2640",
        muted="#6f6486", accent="#8a63c7", border="#cdbfe3",
        danger="#c24b6b", success="#4f9a6a"),
    "Forest": dict(
        bg="#0f1a14", panel="#17261d", panel2="#203528", fg="#e0ebe0",
        muted="#8fa896", accent="#72b87d", border="#2f4a38",
        danger="#d1706a", success="#8fcf8a"),
    "Sunset": dict(
        bg="#22141a", panel="#2f1c23", panel2="#3d252d", fg="#f7e5d8",
        muted="#c39d8c", accent="#f28c52", border="#573740",
        danger="#e0596b", success="#9bc27a"),
    "Soft Light": dict(
        bg="#f6f2ea", panel="#fffdf9", panel2="#ebe5d8", fg="#2b2a28",
        muted="#7b766b", accent="#a8792f", border="#d8d0bf",
        danger="#b8434b", success="#5b8a5b"),
}


# ------------------------------------------------------------ colour helpers
def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in rgb)


def mix(a, b, t):
    """Blend colour a towards colour b by fraction t."""
    ra, rb = _rgb(a), _rgb(b)
    return _hex([x + (y - x) * t for x, y in zip(ra, rb)])


def luminance(h):
    r, g, b = _rgb(h)
    return 0.299 * r + 0.587 * g + 0.114 * b


def on_color(h):
    """A readable text colour (dark or light) for text drawn on colour h."""
    return "#16121a" if luminance(h) > 150 else "#ffffff"


def build_colors(theme_name, custom_accent=None):
    c = dict(THEMES.get(theme_name, THEMES[DEFAULT_THEME]))
    if custom_accent:
        c["accent"] = custom_accent
    dark = luminance(c["bg"]) < 128
    c["dark"] = dark
    c["accent_fg"] = on_color(c["accent"])
    c["accent_hover"] = mix(c["accent"], "#ffffff" if dark else "#000000", 0.18)
    c["sidebar"] = mix(c["bg"], "#000000", 0.28) if dark else mix(c["bg"], c["fg"], 0.07)
    c["entry_bg"] = mix(c["panel"], c["bg"], 0.5)
    c["hover"] = mix(c["panel2"], c["fg"], 0.08)
    c["tint"] = mix(c["panel"], c["accent"], 0.22)
    return c


# ------------------------------------------------------------- small helpers
def parse_due(text):
    """Turn what the user typed into an ISO date. Returns (iso, ok)."""
    s = text.strip().lower()
    if not s:
        return "", True
    if s in ("today", "tod"):
        return date.today().isoformat(), True
    if s in ("tomorrow", "tom", "tmr"):
        return (date.today() + timedelta(days=1)).isoformat(), True
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat(), True
        except ValueError:
            pass
    return "", False


def fmt_ts(stamp):
    try:
        return datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y, %H:%M")
    except (ValueError, TypeError):
        return stamp or ""


def fmt_clock(seconds):
    minutes, secs = divmod(max(0, int(seconds)), 60)
    return "%02d:%02d" % (minutes, secs)


def open_path(path):
    """Open a file or folder with the operating system's default application."""
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa: S606 (Windows only)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def draw_axolotl(cv, x, y, s=1.0):
    """Draw the SHIFT axolotl mascot on canvas cv, centred near (x, y)."""
    pink, shade, deep = "#f6b8c6", "#eea0b5", "#e0708f"
    cheek, dark = "#f08fa8", "#2b1b2c"

    def oval(cx, cy, rx, ry, **kw):
        return cv.create_oval(x + (cx - rx) * s, y + (cy - ry) * s,
                              x + (cx + rx) * s, y + (cy + ry) * s, **kw)

    def pts(seq):
        out = []
        for px_, py_ in seq:
            out += [x + px_ * s, y + py_ * s]
        return out

    cv.create_polygon(pts([(18, 20), (44, 20), (62, 25), (66, 31), (54, 35), (26, 36)]),
                      fill=shade, outline="", smooth=True)           # tail
    oval(0, 18, 32, 15, fill=pink, outline="")                         # body
    oval(-22, 32, 7, 4, fill=shade, outline="")                        # feet
    oval(22, 32, 7, 4, fill=shade, outline="")
    for side in (-1, 1):                                               # gills
        for sx, sy, ex, ey in ((20, -6, 42, -24), (22, 0, 48, -6), (20, 6, 42, 12)):
            cv.create_line(x + side * sx * s, y + sy * s, x + side * ex * s, y + ey * s,
                           fill=deep, width=max(2, int(3 * s)), capstyle="round")
            oval(side * ex, ey, 5, 5, fill=deep, outline="")
    oval(0, 0, 27, 22, fill=pink, outline="")                          # head
    oval(-18, 7, 5, 3, fill=cheek, outline="")                         # cheeks
    oval(18, 7, 5, 3, fill=cheek, outline="")
    oval(-10, -3, 3.4, 3.8, fill=dark, outline="")                     # eyes
    oval(10, -3, 3.4, 3.8, fill=dark, outline="")
    oval(-9, -4.5, 1.1, 1.1, fill="#ffffff", outline="")
    oval(11, -4.5, 1.1, 1.1, fill="#ffffff", outline="")
    cv.create_arc(x - 7 * s, y - 2 * s, x + 7 * s, y + 10 * s, start=210, extent=120,
                  style="arc", outline=dark, width=max(1, int(1.6 * s)))   # smile


# -------------------------------------------------------------- custom widgets
class Btn(tk.Label):
    """A flat button made from a Label, so colours work the same on every OS."""

    def __init__(self, parent, text, command, bg, fg, hover, font, padx=14, pady=6):
        tk.Label.__init__(self, parent, text=text, bg=bg, fg=fg, font=font,
                          padx=padx, pady=pady, cursor="hand2")
        self._command = command
        self._bg = bg
        self._hover = hover
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))
        self.bind("<Button-1>", self._click)

    def _click(self, _event):
        if self._command:
            self._command()

    def restyle(self, bg, fg, hover):
        self._bg, self._hover = bg, hover
        self.configure(bg=bg, fg=fg)


class Bar(tk.Canvas):
    """A simple horizontal progress bar."""

    def __init__(self, parent, trough, fill, height=10, width=100):
        tk.Canvas.__init__(self, parent, width=width, height=height, bg=trough,
                           highlightthickness=0, bd=0)
        self._fill = fill
        self._fraction = 0.0
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, fraction):
        self._fraction = max(0.0, min(1.0, fraction))
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if self._fraction > 0:
            self.create_rectangle(0, 0, w * self._fraction, h, fill=self._fill, width=0)


class ScrollFrame(tk.Frame):
    """A vertically scrolling area. Put content in `.inner`."""

    def __init__(self, parent, bg):
        tk.Frame.__init__(self, parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, yscrollincrement=20)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self._win, width=e.width))

    def clear(self):
        """Remove all content; returns the scroll position so it can be restored."""
        pos = self.canvas.yview()[0]
        for w in self.inner.winfo_children():
            w.destroy()
        return pos

    def restore(self, pos):
        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(pos)

    def scroll_to(self, widget):
        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        total = max(self.inner.winfo_reqheight(), 1)
        self.canvas.yview_moveto(max(0.0, (widget.winfo_y() - 10) / float(total)))

    def scroll(self, event):
        lo, hi = self.canvas.yview()
        if lo <= 0.0 and hi >= 1.0:
            return
        if getattr(event, "num", None) == 4:
            step = -1
        elif getattr(event, "num", None) == 5:
            step = 1
        else:
            step = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(step * 2, "units")


# ============================================================== the application
class ShiftApp:
    NAV = [
        ("dashboard", "Dashboard", "⌂"),
        ("tasks", "Tasks", "✓"),
        ("focus", "Focus Room", "◔"),
        ("notes", "Notes", "✎"),
        ("resources", "Resources", "❖"),
        ("workspaces", "Workspaces", "▦"),
        ("appearance", "Appearance", "✦"),
    ]

    # ------------------------------------------------------------------ setup
    def __init__(self, store):
        self.store = store
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        self.root = tk.Tk()
        self.root.title("SHIFT — Gothic Academia")

        # Scale pixel sizes on high-resolution screens; enlarge fonts a little on macOS.
        try:
            self.scale = max(1.0, self.root.winfo_fpixels("1i") / 96.0)
        except tk.TclError:
            self.scale = 1.0
        self.fscale = 1.2 if sys.platform == "darwin" else 1.0
        self.root.geometry("%dx%d" % (self.px(1200), self.px(760)))
        self.root.minsize(self.px(1000), self.px(640))

        families = dict((f.lower(), f) for f in tkfont.families(self.root))
        self.f_serif = self._pick_font(families, [
            "Georgia", "Palatino Linotype", "Book Antiqua", "Cambria",
            "Times New Roman", "DejaVu Serif", "Liberation Serif"], "Times")
        self.f_sans = self._pick_font(families, [
            "Segoe UI", "Helvetica Neue", "Helvetica", "Arial",
            "DejaVu Sans", "Liberation Sans"], "Helvetica")

        theme = store.get_setting("theme", DEFAULT_THEME)
        self.theme_name = theme if theme in THEMES else DEFAULT_THEME
        self.custom_accent = None            # session only, never saved
        self.c = build_colors(self.theme_name, self.custom_accent)

        ws = store.get_setting("workspace")
        self.ws_id = ws if store.get_workspace(ws) else store.workspaces[0]["id"]
        self.page = "dashboard"

        # focus timer state lives here so it survives page changes
        minutes = store.get_setting("focus_minutes", 25)
        if minutes not in FOCUS_PRESETS:
            minutes = 25
        self.timer_total = minutes * 60
        self.timer_remaining = self.timer_total
        self.timer_running = False
        self.timer_end = 0.0
        self.timer_job = None
        self.distraction = False
        self._dist_hint = None

        # page state
        self.task_filter = "All"
        self.task_query = ""
        self.note_query = ""
        self.note_cat = "All"
        self.current_note_id = None
        self.pending_highlight = None
        self.note_text = None
        self._note_snapshot = ("", "", "General", False)
        self.note_pinned = False
        self._intent_text = None
        self._intent_ws = None
        self._qs = None
        self._qs_entry = None
        self._reporting_error = False

        self.root.report_callback_exception = self._on_callback_error
        self._setup_style()
        self._bind_shortcuts()
        self._build_shell()
        self.show_page("dashboard")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self):
        if self.store.recovered:
            names = ", ".join(self.store.recovered)
            self.root.after(300, lambda: messagebox.showwarning(
                "Data file reset",
                "These data files could not be read and were set aside "
                "(renamed with a .bak ending) so SHIFT could start:\n\n%s" % names,
                parent=self.root))
        self.root.mainloop()

    def px(self, n):
        return int(round(n * self.scale))

    @staticmethod
    def _pick_font(available, wanted, fallback):
        for name in wanted:
            if name.lower() in available:
                return available[name.lower()]
        return fallback

    def font(self, size=11, bold=False, italic=False, serif=False, extra=""):
        style = " ".join(s for s in ("bold" if bold else "", "italic" if italic else "", extra) if s)
        family = self.f_serif if serif else self.f_sans
        size = max(7, int(round(size * self.fscale)))
        return (family, size, style) if style else (family, size)

    def _on_callback_error(self, exc, val, tb):
        traceback.print_exception(exc, val, tb)
        if self._reporting_error:
            return
        self._reporting_error = True
        try:
            messagebox.showerror(
                "SHIFT hit a problem",
                "Something unexpected happened:\n\n%s: %s\n\nYour saved data is safe. "
                "If this keeps happening, restart SHIFT." % (exc.__name__, val),
                parent=self.root)
        finally:
            self._reporting_error = False

    # ------------------------------------------------------------- widget kit
    def lbl(self, parent, text="", size=11, bold=False, italic=False, serif=False,
            color="fg", bg=None, **kw):
        return tk.Label(parent, text=text, font=self.font(size, bold, italic, serif),
                        fg=self.c.get(color, color), bg=bg or parent.cget("bg"), **kw)

    def card(self, parent):
        c = self.c
        return tk.Frame(parent, bg=c["panel"], highlightthickness=1,
                        highlightbackground=c["border"], highlightcolor=c["border"])

    def entry(self, parent, var=None, width=24, size=11):
        c = self.c
        return tk.Entry(parent, textvariable=var, width=width, font=self.font(size),
                        bg=c["entry_bg"], fg=c["fg"], insertbackground=c["fg"],
                        relief="flat", highlightthickness=1,
                        highlightbackground=c["border"], highlightcolor=c["accent"],
                        selectbackground=c["accent"], selectforeground=c["accent_fg"])

    def combo(self, parent, values, var, width=12):
        return ttk.Combobox(parent, values=list(values), textvariable=var,
                            state="readonly", width=width, font=self.font(10))

    def btn(self, parent, text, command, kind="primary", size=10):
        c = self.c
        if kind == "primary":
            bg, fg, hover = c["accent"], c["accent_fg"], c["accent_hover"]
        elif kind == "danger":
            bg, fg, hover = c["danger"], "#ffffff", mix(c["danger"], "#000000", 0.18)
        else:
            bg, fg, hover = c["panel2"], c["fg"], c["hover"]
        return Btn(parent, text, command, bg, fg, hover, self.font(size, bold=(kind == "primary")))

    def textbox(self, parent, height=5, size=11):
        c = self.c
        return tk.Text(parent, height=height, wrap="word", font=self.font(size),
                       bg=c["entry_bg"], fg=c["fg"], insertbackground=c["fg"],
                       relief="flat", highlightthickness=1, highlightbackground=c["border"],
                       highlightcolor=c["accent"], padx=10, pady=8, undo=True,
                       selectbackground=c["accent"], selectforeground=c["accent_fg"])

    def _click_all(self, widget, fn):
        """Make a widget and everything inside it clickable."""
        widget.bind("<Button-1>", lambda e: fn())
        try:
            widget.configure(cursor="hand2")
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._click_all(child, fn)

    def _empty(self, parent, text):
        self.lbl(parent, text, 11, italic=True, serif=True, color="muted").pack(pady=30)

    def _setup_style(self):
        c = self.c
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", fieldbackground=c["entry_bg"], background=c["panel2"],
                        foreground=c["fg"], arrowcolor=c["accent"], bordercolor=c["border"],
                        lightcolor=c["border"], darkcolor=c["border"],
                        selectbackground=c["entry_bg"], selectforeground=c["fg"], padding=4)
        style.map("TCombobox",
                  fieldbackground=[("readonly", c["entry_bg"])],
                  foreground=[("readonly", c["fg"])],
                  background=[("active", c["hover"]), ("readonly", c["panel2"])],
                  selectbackground=[("readonly", c["entry_bg"])],
                  selectforeground=[("readonly", c["fg"])])
        style.configure("Vertical.TScrollbar", background=c["panel2"], troughcolor=c["bg"],
                        bordercolor=c["bg"], lightcolor=c["panel2"], darkcolor=c["panel2"],
                        arrowcolor=c["muted"])
        style.map("Vertical.TScrollbar", background=[("active", c["hover"])])
        for opt, val in (("background", c["entry_bg"]), ("foreground", c["fg"]),
                         ("selectBackground", c["accent"]), ("selectForeground", c["accent_fg"])):
            self.root.option_add("*TCombobox*Listbox." + opt, val)

    # -------------------------------------------------------------- shortcuts
    def _bind_shortcuts(self):
        r = self.root
        for letter, handler in (("k", self._sc_search), ("n", self._sc_note), ("t", self._sc_task)):
            for key in (letter, letter.upper()):
                seq = "<Control-%s>" % key
                r.bind_all(seq, handler)
                # Entry/Text widgets have their own Ctrl+K/N/T editing keys;
                # replace them so SHIFT's shortcuts win while typing.
                for cls in ("Entry", "Text", "TEntry", "TCombobox"):
                    r.bind_class(cls, seq, handler)
        r.bind("<Escape>", self._on_escape)
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            r.bind_all(seq, self._on_wheel)

    def _sc_search(self, _event=None):
        self.open_quick_search()
        return "break"

    def _sc_note(self, _event=None):
        if self.distraction:
            return "break"
        self._close_qs()
        if self.page != "notes":
            if not self._confirm_discard_note():
                return "break"
            self.show_page("notes")
        self._new_note()
        return "break"

    def _sc_task(self, _event=None):
        if self.distraction:
            return "break"
        self._close_qs()
        if self.page != "tasks":
            if not self._confirm_discard_note():
                return "break"
            self.show_page("tasks")
        self.task_title_entry.focus_set()
        return "break"

    def _on_escape(self, _event=None):
        if self.distraction:
            self.exit_distraction()

    def _on_wheel(self, event):
        try:
            w = self.root.winfo_containing(event.x_root, event.y_root)
        except (KeyError, tk.TclError):
            return
        while w is not None:
            if isinstance(w, ScrollFrame):
                w.scroll(event)
                return
            if isinstance(w, (tk.Text, tk.Listbox)):
                return
            w = getattr(w, "master", None)

    # ------------------------------------------------------------------ shell
    def _build_shell(self):
        c = self.c
        for w in self.root.winfo_children():
            w.destroy()
        self._qs = None
        self.root.configure(bg=c["bg"])
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self.root, bg=c["sidebar"], width=self.px(236))
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.pack_propagate(False)
        self.main = tk.Frame(self.root, bg=c["bg"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)
        self.header = tk.Frame(self.main, bg=c["bg"])
        self.header.grid(row=0, column=0, sticky="ew")
        self.content = tk.Frame(self.main, bg=c["bg"])
        self.content.grid(row=1, column=0, sticky="nsew")
        self._build_sidebar()
        self._build_header()

    def _build_sidebar(self):
        c, sb = self.c, self.sidebar
        cv = tk.Canvas(sb, width=self.px(200), height=self.px(84), bg=c["sidebar"],
                       highlightthickness=0)
        cv.pack(pady=(self.px(22), 0))
        draw_axolotl(cv, self.px(92), self.px(46), self.scale)
        self.lbl(sb, "SHIFT", 26, bold=True, serif=True, color="accent").pack(pady=(4, 0))
        self.lbl(sb, "gothic academia", 10, italic=True, serif=True, color="muted").pack(pady=(0, 14))
        tk.Frame(sb, bg=c["border"], height=1).pack(fill="x", padx=20, pady=(0, 12))
        self.nav_labels = {}
        for key, name, icon in self.NAV:
            lab = tk.Label(sb, text="  %s   %s" % (icon, name), anchor="w", font=self.font(11),
                           fg=c["fg"], bg=c["sidebar"], padx=14, pady=9, cursor="hand2")
            lab.pack(fill="x", padx=10, pady=1)
            lab.bind("<Button-1>", lambda e, k=key: self.nav_to(k))
            lab.bind("<Enter>", lambda e, k=key: self._nav_hover(k, True))
            lab.bind("<Leave>", lambda e, k=key: self._nav_hover(k, False))
            self.nav_labels[key] = lab
        tk.Frame(sb, bg=c["sidebar"]).pack(fill="both", expand=True)
        self.lbl(sb, "Ctrl+K  search\nCtrl+N  new note\nCtrl+T  new task", 9, color="muted",
                 bg=c["sidebar"], justify="center").pack(pady=(0, 18))

    def _style_nav(self):
        c = self.c
        for key, lab in self.nav_labels.items():
            if key == self.page:
                lab.configure(bg=c["panel2"], fg=c["accent"], font=self.font(11, bold=True))
            else:
                lab.configure(bg=c["sidebar"], fg=c["fg"], font=self.font(11))

    def _nav_hover(self, key, inside):
        if key == self.page:
            return
        self.nav_labels[key].configure(bg=self.c["panel"] if inside else self.c["sidebar"])

    def _build_header(self):
        c, h = self.c, self.header
        h.grid_columnconfigure(0, weight=1)
        left = tk.Frame(h, bg=c["bg"])
        left.grid(row=0, column=0, sticky="w", padx=(28, 0), pady=(18, 4))
        self.title_lbl = self.lbl(left, "", 24, bold=True, serif=True)
        self.title_lbl.pack(anchor="w")
        self.sub_lbl = self.lbl(left, "", 10, italic=True, serif=True, color="muted")
        self.sub_lbl.pack(anchor="w")
        right = tk.Frame(h, bg=c["bg"])
        right.grid(row=0, column=1, sticky="e", padx=28)
        self.lbl(right, "Workspace", 10, color="muted").pack(side="left", padx=(0, 8))
        self.ws_var = tk.StringVar()
        self.ws_combo = self.combo(right, [], self.ws_var, width=18)
        self.ws_combo.pack(side="left")
        self.ws_combo.bind("<<ComboboxSelected>>", self._on_ws_combo)
        self.btn(right, "Search  Ctrl+K", self.open_quick_search, "ghost").pack(side="left", padx=(12, 0))
        tk.Frame(h, bg=c["border"], height=1).grid(row=1, column=0, columnspan=2,
                                                   sticky="ew", padx=28, pady=(8, 0))
        self._sync_ws_combo()

    def _sync_ws_combo(self):
        spaces = self.store.workspaces
        self.ws_combo.configure(values=["%s  %s" % (w["symbol"], w["name"]) for w in spaces])
        for i, w in enumerate(spaces):
            if w["id"] == self.ws_id:
                self.ws_combo.current(i)
                break

    def _on_ws_combo(self, _event=None):
        idx = self.ws_combo.current()
        if idx < 0 or idx >= len(self.store.workspaces):
            return
        target = self.store.workspaces[idx]["id"]
        if target == self.ws_id:
            return
        if not self._confirm_discard_note():
            self._sync_ws_combo()
            return
        self.set_workspace(target)

    def _refresh_header_title(self):
        name = dict((k, n) for k, n, _ in self.NAV)[self.page]
        ws = self.store.get_workspace(self.ws_id)
        self.title_lbl.configure(text=name)
        self.sub_lbl.configure(text="%s  %s   ·   %s" % (
            ws["symbol"], ws["name"], date.today().strftime("%A, %d %B %Y")))

    # ------------------------------------------------------------- navigation
    def nav_to(self, key):
        if not self._confirm_discard_note():
            return
        self.show_page(key)

    def show_page(self, key):
        self._flush_intentions()
        if key != "focus":
            self.exit_distraction()
        self.page = key
        if key != "notes":
            self.note_text = None
        for w in self.content.winfo_children():
            w.destroy()
        self._intent_text = None
        self._style_nav()
        self._refresh_header_title()
        getattr(self, "_page_" + key)()
        self.pending_highlight = None

    def set_workspace(self, ws_id, page=None):
        self._flush_intentions()
        self.ws_id = ws_id
        self.store.set_setting("workspace", ws_id)
        self.current_note_id = None
        self.task_query = ""
        self.note_query = ""
        self.note_cat = "All"
        self._sync_ws_combo()
        self.show_page(page or self.page)

    def _recolor(self, page):
        self._flush_intentions()
        self._close_qs()
        self.c = build_colors(self.theme_name, self.custom_accent)
        self._setup_style()
        self._build_shell()
        self.show_page(page)

    def _on_close(self):
        if not self._confirm_discard_note():
            return
        if self.timer_running and not messagebox.askyesno(
                "Quit SHIFT", "A focus session is still running.\n\nQuit anyway?", parent=self.root):
            return
        self._flush_intentions()
        self._timer_cancel_job()
        self.root.destroy()

    # =============================================================== DASHBOARD
    def _page_dashboard(self):
        c, st, ws = self.c, self.store, self.ws_id
        page = tk.Frame(self.content, bg=c["bg"])
        page.pack(fill="both", expand=True, padx=28, pady=(14, 22))
        page.grid_columnconfigure(0, weight=1, uniform="dash")
        page.grid_columnconfigure(1, weight=1, uniform="dash")

        # welcome
        wel = self.card(page)
        wel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        inner = tk.Frame(wel, bg=c["panel"])
        inner.pack(fill="x", padx=22, pady=16)
        left = tk.Frame(inner, bg=c["panel"])
        left.pack(side="left", fill="x", expand=True)
        hour = datetime.now().hour
        greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
        name = st.get_setting("name", "Scholar") or "Scholar"
        self.lbl(left, "%s, %s." % (greet, name), 22, bold=True, serif=True,
                 bg=c["panel"]).pack(anchor="w")
        wsr = st.get_workspace(ws)
        self.lbl(left, "Your %s workspace is open. Choose one thing, then begin." % wsr["name"],
                 11, italic=True, serif=True, color="muted", bg=c["panel"]).pack(anchor="w", pady=(4, 0))
        cv = tk.Canvas(inner, width=self.px(200), height=self.px(84), bg=c["panel"],
                       highlightthickness=0)
        cv.pack(side="right")
        draw_axolotl(cv, self.px(92), self.px(46), self.scale)

        # numbers
        overdue = st.overdue_count(ws)
        stats = [
            ("Pending tasks", st.pending_count(ws),
             "%d overdue" % overdue if overdue else "none overdue", "danger" if overdue else "muted"),
            ("Due today", st.due_today_count(ws), "tasks to finish today", "muted"),
            ("Notes", len([n for n in st.notes if n["workspace_id"] == ws]), "saved notes", "muted"),
            ("Resources", len([r for r in st.resources if r["workspace_id"] == ws]),
             "saved links and files", "muted"),
        ]
        row = tk.Frame(page, bg=c["bg"])
        row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        for i, (label, value, caption, cap_color) in enumerate(stats):
            row.grid_columnconfigure(i, weight=1, uniform="stat")
            box = self.card(row)
            box.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 7, 0 if i == 3 else 7))
            self.lbl(box, str(value), 30, bold=True, serif=True, color="accent").pack(anchor="w", padx=16, pady=(12, 0))
            self.lbl(box, label, 11, bold=True).pack(anchor="w", padx=16)
            self.lbl(box, caption, 9, color=cap_color).pack(anchor="w", padx=16, pady=(0, 12))

        # intentions
        ic = self.card(page)
        ic.grid(row=2, column=0, sticky="nsew", padx=(0, 7), pady=(0, 14))
        self.lbl(ic, "Today's intentions", 14, bold=True, serif=True).pack(anchor="w", padx=18, pady=(14, 0))
        self.lbl(ic, "What deserves your attention today?", 10, italic=True,
                 color="muted").pack(anchor="w", padx=18)
        txt = self.textbox(ic, height=5)
        txt.pack(fill="both", expand=True, padx=18, pady=(8, 16))
        txt.insert("1.0", st.get_intentions(ws))
        txt.bind("<FocusOut>", lambda e: self._flush_intentions())
        self._intent_text, self._intent_ws = txt, ws

        # focus room shortcut
        fc = self.card(page)
        fc.grid(row=2, column=1, sticky="nsew", padx=(7, 0), pady=(0, 14))
        self.lbl(fc, "Focus Room", 14, bold=True, serif=True).pack(anchor="w", padx=18, pady=(14, 0))
        self.lbl(fc, "Silence the noise. One timed session at a time.", 10, italic=True,
                 color="muted").pack(anchor="w", padx=18)
        if self.timer_running:
            status = "Session running — %s left" % fmt_clock(self.timer_remaining)
        elif 0 < self.timer_remaining < self.timer_total:
            status = "Session paused at %s" % fmt_clock(self.timer_remaining)
        else:
            status = "Ready for a %d-minute session" % (self.timer_total // 60)
        self.lbl(fc, status, 12, serif=True).pack(anchor="w", padx=18, pady=(16, 0))
        self.btn(fc, "Enter the Focus Room", lambda: self.nav_to("focus")).pack(
            anchor="w", padx=18, pady=(12, 16))

        # recent notes
        rc = self.card(page)
        rc.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.lbl(rc, "Recently saved notes", 14, bold=True, serif=True).pack(anchor="w", padx=18, pady=(14, 6))
        recent = sorted(st.notes_for(ws), key=lambda n: n["updated"], reverse=True)[:4]
        if not recent:
            self.lbl(rc, "No notes yet — press Ctrl+N to write your first.", 10, italic=True,
                     color="muted").pack(anchor="w", padx=18, pady=(0, 16))
        for n in recent:
            nr = tk.Frame(rc, bg=c["panel"])
            nr.pack(fill="x", padx=18, pady=2)
            self.lbl(nr, ("★ " if n["pinned"] else "") + (n["title"] or "Untitled note"),
                     11, bold=True, bg=c["panel"]).pack(side="left")
            self.lbl(nr, "%s · %s" % (n["category"], fmt_ts(n["updated"])), 9, color="muted",
                     bg=c["panel"]).pack(side="right")
            self._click_all(nr, lambda i=n["id"]: self._goto_note(i))
        tk.Frame(rc, bg=c["panel"], height=10).pack()

    def _flush_intentions(self):
        t = self._intent_text
        if t is None:
            return
        try:
            text = t.get("1.0", "end-1c")
        except tk.TclError:
            self._intent_text = None
            return
        if text.strip() != self.store.get_intentions(self._intent_ws).strip():
            self.store.set_intentions(self._intent_ws, text)

    def _goto_note(self, note_id):
        if not self._confirm_discard_note():
            return
        self.current_note_id = note_id
        self.show_page("notes")

    # ==================================================================== TASKS
    def _page_tasks(self):
        c = self.c
        page = tk.Frame(self.content, bg=c["bg"])
        page.pack(fill="both", expand=True, padx=28, pady=(14, 18))

        add = self.card(page)
        add.pack(fill="x")
        f = tk.Frame(add, bg=c["panel"])
        f.pack(fill="x", padx=16, pady=14)
        f.grid_columnconfigure(0, weight=1)
        self.lbl(f, "New task", 10, color="muted", bg=c["panel"]).grid(row=0, column=0, sticky="w")
        self.lbl(f, "Due date", 10, color="muted", bg=c["panel"]).grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.lbl(f, "Priority", 10, color="muted", bg=c["panel"]).grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.task_title_var = tk.StringVar()
        self.task_due_var = tk.StringVar()
        self.task_prio_var = tk.StringVar(value="Normal")
        self.task_title_entry = self.entry(f, self.task_title_var, width=30)
        self.task_title_entry.grid(row=1, column=0, sticky="ew", ipady=5)
        due_entry = self.entry(f, self.task_due_var, width=14)
        due_entry.grid(row=1, column=1, padx=(10, 0), ipady=5)
        self.combo(f, self.store.PRIORITIES, self.task_prio_var, width=9).grid(
            row=1, column=2, padx=(10, 0))
        self.btn(f, "Add task", self._add_task).grid(row=1, column=3, padx=(10, 0))
        self.lbl(f, "Due date: 2026-11-30, 30/11/2026, today or tomorrow — or leave blank.",
                 9, color="muted", bg=c["panel"]).grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        for w in (self.task_title_entry, due_entry):
            w.bind("<Return>", lambda e: self._add_task())

        bar = tk.Frame(page, bg=c["bg"])
        bar.pack(fill="x", pady=(14, 8))
        self.filter_btns = {}
        for flt in self.store.TASK_FILTERS:
            b = self.btn(bar, flt, lambda f=flt: self._set_task_filter(f), "ghost")
            b.pack(side="left", padx=(0, 6))
            self.filter_btns[flt] = b
        self.task_query_var = tk.StringVar(value=self.task_query)
        self.entry(bar, self.task_query_var, width=26).pack(side="right", ipady=4)
        self.lbl(bar, "Search tasks", 10, color="muted").pack(side="right", padx=(0, 8))
        self.task_query_var.trace_add("write", lambda *a: self._on_task_query())

        pr = tk.Frame(page, bg=c["bg"])
        pr.pack(fill="x", pady=(0, 8))
        self.progress_lbl = self.lbl(pr, "", 10, color="muted")
        self.progress_lbl.pack(anchor="w")
        self.progress_bar = Bar(pr, c["panel2"], c["accent"], height=8)
        self.progress_bar.pack(fill="x", pady=(4, 0))

        self.task_scroll = ScrollFrame(page, c["bg"])
        self.task_scroll.pack(fill="both", expand=True)
        self._style_filter_buttons()
        self._render_tasks()

    def _style_filter_buttons(self):
        c = self.c
        for flt, b in self.filter_btns.items():
            if flt == self.task_filter:
                b.restyle(c["accent"], c["accent_fg"], c["accent_hover"])
                b.configure(font=self.font(10, bold=True))
            else:
                b.restyle(c["panel2"], c["fg"], c["hover"])
                b.configure(font=self.font(10))

    def _set_task_filter(self, flt):
        self.task_filter = flt
        self._style_filter_buttons()
        self._render_tasks()

    def _on_task_query(self):
        self.task_query = self.task_query_var.get()
        self._render_tasks()

    def _add_task(self):
        title = self.task_title_var.get().strip()
        if not title:
            messagebox.showinfo("New task", "Please give the task a title.", parent=self.root)
            self.task_title_entry.focus_set()
            return
        due, ok = parse_due(self.task_due_var.get())
        if not ok:
            messagebox.showwarning(
                "Due date", "That date could not be read.\n\nTry 2026-11-30, 30/11/2026, "
                "today or tomorrow — or leave it blank.", parent=self.root)
            return
        self.store.add_task(self.ws_id, title, due, self.task_prio_var.get())
        self.task_title_var.set("")
        self.task_due_var.set("")
        self.task_title_entry.focus_set()
        self._render_tasks()

    def _toggle_task(self, task_id):
        self.store.toggle_task(task_id)
        self._render_tasks()

    def _delete_task(self, task_id):
        self.store.delete_task(task_id)
        self._render_tasks()

    def _render_tasks(self):
        st, sf = self.store, self.task_scroll
        pos = sf.clear()
        done, total = st.today_progress(self.ws_id)
        if total:
            self.progress_lbl.configure(text="Today's progress — %d of %d task%s complete" % (
                done, total, "" if total == 1 else "s"))
            self.progress_bar.set(done / float(total))
        else:
            self.progress_lbl.configure(text="Today's progress — no tasks due today")
            self.progress_bar.set(0)
        tasks = st.tasks_for(self.ws_id, self.task_filter, self.task_query)
        if not tasks:
            if self.task_query.strip():
                msg = "No tasks match your search."
            else:
                msg = {"All": "No tasks yet — add your first one above.",
                       "Today": "Nothing is due today.",
                       "Upcoming": "No upcoming tasks.",
                       "Completed": "Nothing completed yet."}[self.task_filter]
            self._empty(sf.inner, msg)
        target = None
        for t in tasks:
            lit = self.pending_highlight == ("task", t["id"])
            row = self._task_row(sf.inner, t, lit)
            row.pack(fill="x", pady=3, padx=(0, 6))
            if lit:
                target = row
        if target is not None:
            sf.scroll_to(target)
        else:
            sf.restore(pos)

    def _task_row(self, parent, t, lit):
        c = self.c
        bg = c["tint"] if lit else c["panel"]
        row = tk.Frame(parent, bg=bg, highlightthickness=1,
                       highlightbackground=c["accent"] if lit else c["border"])
        row.grid_columnconfigure(1, weight=1)
        chk = tk.Label(row, text="☑" if t["done"] else "☐", font=self.font(18),
                       fg=c["accent"] if t["done"] else c["muted"], bg=bg, cursor="hand2", padx=12)
        chk.grid(row=0, column=0, rowspan=2, sticky="ns", pady=6)
        chk.bind("<Button-1>", lambda e, i=t["id"]: self._toggle_task(i))
        title_font = self.font(12, extra="overstrike") if t["done"] else self.font(12)
        tk.Label(row, text=t["title"], anchor="w", justify="left", font=title_font,
                 fg=c["muted"] if t["done"] else c["fg"], bg=bg,
                 wraplength=self.px(560)).grid(row=0, column=1, sticky="w", pady=(8, 0))
        text, color = self._fmt_due(t)
        tk.Label(row, text=text, font=self.font(9), fg=c[color], bg=bg).grid(
            row=1, column=1, sticky="w", pady=(0, 8))
        pcolor = {"High": c["danger"], "Normal": c["accent"], "Low": c["muted"]}.get(t["priority"], c["accent"])
        tk.Label(row, text=t["priority"], font=self.font(9, bold=True), fg=pcolor,
                 bg=mix(bg, pcolor, 0.2), padx=8, pady=2).grid(row=0, column=2, rowspan=2, padx=8)
        x = tk.Label(row, text="✕", font=self.font(12), fg=c["muted"], bg=bg, cursor="hand2", padx=10)
        x.grid(row=0, column=3, rowspan=2)
        x.bind("<Button-1>", lambda e, i=t["id"]: self._delete_task(i))
        x.bind("<Enter>", lambda e, w=x: w.configure(fg=c["danger"]))
        x.bind("<Leave>", lambda e, w=x: w.configure(fg=c["muted"]))
        return row

    @staticmethod
    def _fmt_due(t):
        due = t.get("due") or ""
        if not due:
            return "No due date", "muted"
        try:
            d = datetime.strptime(due, "%Y-%m-%d").date()
        except ValueError:
            return due, "muted"
        label = d.strftime("%a %d %b %Y")
        if t["done"]:
            return "Due " + label, "muted"
        delta = (d - date.today()).days
        if delta < 0:
            return "Overdue · " + label, "danger"
        if delta == 0:
            return "Due today", "accent"
        if delta == 1:
            return "Due tomorrow · " + label, "accent"
        return "Due " + label, "muted"

    # ================================================================ FOCUS ROOM
    def _page_focus(self):
        c = self.c
        page = tk.Frame(self.content, bg=c["bg"])
        page.pack(fill="both", expand=True)
        box = tk.Frame(page, bg=c["bg"])
        box.place(relx=0.5, rely=0.46, anchor="center")
        self.lbl(box, "One task. One session. Nothing else.", 14, italic=True, serif=True,
                 color="muted").pack()
        presets = tk.Frame(box, bg=c["bg"])
        presets.pack(pady=(18, 4))
        self.preset_btns = {}
        for m in FOCUS_PRESETS:
            b = self.btn(presets, "%d min" % m, lambda m=m: self.set_preset(m), "ghost", size=11)
            b.pack(side="left", padx=5)
            self.preset_btns[m] = b
        self.timer_label = tk.Label(box, text="", font=self.font(88, bold=True, serif=True),
                                    fg=c["fg"], bg=c["bg"])
        self.timer_label.pack(pady=(10, 0))
        self.timer_status = self.lbl(box, "", 12, italic=True, serif=True, color="muted")
        self.timer_status.pack()
        self.timer_bar = Bar(box, c["panel2"], c["accent"], height=self.px(10), width=self.px(520))
        self.timer_bar.pack(pady=(16, 18))
        ctr = tk.Frame(box, bg=c["bg"])
        ctr.pack()
        self.timer_btn = self.btn(ctr, "Start", self.timer_toggle, "primary", size=12)
        self.timer_btn.pack(side="left", padx=6)
        self.btn(ctr, "Reset", self.timer_reset, "ghost", size=12).pack(side="left", padx=6)
        self.dist_btn = self.btn(ctr, "Distraction-free", self.toggle_distraction, "ghost", size=12)
        self.dist_btn.pack(side="left", padx=6)
        self._style_presets()
        self._timer_update_ui()

    def _style_presets(self):
        c = self.c
        try:
            for m, b in self.preset_btns.items():
                if m * 60 == self.timer_total:
                    b.restyle(c["accent"], c["accent_fg"], c["accent_hover"])
                else:
                    b.restyle(c["panel2"], c["fg"], c["hover"])
        except (tk.TclError, AttributeError):
            pass

    def set_preset(self, minutes):
        started = self.timer_running or (0 < self.timer_remaining < self.timer_total)
        if started and not messagebox.askyesno(
                "Change length", "This will end the current session.\n\nContinue?", parent=self.root):
            return
        self._timer_cancel_job()
        self.timer_running = False
        self.timer_total = minutes * 60
        self.timer_remaining = self.timer_total
        self.store.set_setting("focus_minutes", minutes)
        self._style_presets()
        self._timer_update_ui()

    def timer_toggle(self):
        if self.timer_running:
            self._timer_pause()
        else:
            self._timer_start()

    def _timer_start(self):
        if self.timer_remaining <= 0:
            self.timer_remaining = self.timer_total
        self.timer_running = True
        self.timer_end = time.monotonic() + self.timer_remaining
        self._timer_tick()

    def _timer_pause(self):
        self._timer_cancel_job()
        self.timer_remaining = max(0, int(math.ceil(self.timer_end - time.monotonic())))
        self.timer_running = False
        self._timer_update_ui()

    def timer_reset(self):
        self._timer_cancel_job()
        self.timer_running = False
        self.timer_remaining = self.timer_total
        self._timer_update_ui()

    def _timer_cancel_job(self):
        if self.timer_job is not None:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None
        self.root.title("SHIFT — Gothic Academia")

    def _timer_tick(self):
        self.timer_job = None
        if not self.timer_running:
            return
        left = self.timer_end - time.monotonic()
        if left <= 0:
            self._timer_complete()
            return
        self.timer_remaining = int(math.ceil(left))
        self.root.title("%s — SHIFT" % fmt_clock(self.timer_remaining))
        self._timer_update_ui()
        self.timer_job = self.root.after(200, self._timer_tick)

    def _timer_complete(self):
        self.timer_running = False
        self.timer_remaining = 0
        self.timer_job = None
        self.root.title("SHIFT — Gothic Academia")
        self._timer_update_ui()
        self.exit_distraction()
        self.root.bell()
        messagebox.showinfo(
            "Focus session complete",
            "Well done — your %d-minute session is complete.\n\nTake a short break." % (
                self.timer_total // 60), parent=self.root)

    def _timer_update_ui(self):
        if self.page != "focus":
            return
        try:
            self.timer_label.configure(text=fmt_clock(self.timer_remaining))
            self.timer_bar.set(1 - self.timer_remaining / float(self.timer_total))
            if self.timer_running:
                status, button = "In session — stay with it", "Pause"
            elif self.timer_remaining <= 0:
                status, button = "Session complete", "Start"
            elif self.timer_remaining < self.timer_total:
                status, button = "Paused", "Resume"
            else:
                status, button = "Ready when you are", "Start"
            self.timer_status.configure(text=status)
            self.timer_btn.configure(text=button)
        except (tk.TclError, AttributeError):
            pass

    def toggle_distraction(self):
        if self.distraction:
            self.exit_distraction()
        else:
            self.enter_distraction()

    def enter_distraction(self):
        if self.distraction:
            return
        self.distraction = True
        self._close_qs()
        self.sidebar.grid_remove()
        self.header.grid_remove()
        self._dist_hint = self.lbl(self.content, "Press Esc to leave distraction-free mode",
                                   10, italic=True, color="muted")
        self._dist_hint.place(relx=0.5, rely=0.97, anchor="s")
        try:
            self.dist_btn.configure(text="Leave distraction-free")
        except (tk.TclError, AttributeError):
            pass

    def exit_distraction(self):
        if not self.distraction:
            return
        self.distraction = False
        self.sidebar.grid()
        self.header.grid()
        try:
            self._dist_hint.destroy()
        except (tk.TclError, AttributeError):
            pass
        self._dist_hint = None
        try:
            self.dist_btn.configure(text="Distraction-free")
        except (tk.TclError, AttributeError):
            pass

    # ===================================================================== NOTES
    def _page_notes(self):
        c = self.c
        page = tk.Frame(self.content, bg=c["bg"])
        page.pack(fill="both", expand=True, padx=28, pady=(14, 18))
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(0, weight=1)

        left = tk.Frame(page, bg=c["bg"], width=self.px(330))
        left.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        left.pack_propagate(False)
        self.btn(left, "+  New note   (Ctrl+N)", self._new_note).pack(fill="x")
        self.lbl(left, "Search notes", 10, color="muted").pack(anchor="w", pady=(12, 2))
        self.note_query_var = tk.StringVar(value=self.note_query)
        self.entry(left, self.note_query_var, width=10).pack(fill="x", ipady=5)
        self.lbl(left, "Category", 10, color="muted").pack(anchor="w", pady=(10, 2))
        self.note_filter_var = tk.StringVar(value=self.note_cat)
        self.combo(left, ["All"] + list(self.store.NOTE_CATEGORIES), self.note_filter_var,
                   width=10).pack(fill="x", pady=(0, 10))
        self.note_query_var.trace_add("write", lambda *a: self._on_note_filter())
        self.note_filter_var.trace_add("write", lambda *a: self._on_note_filter())
        self.note_scroll = ScrollFrame(left, c["bg"])
        self.note_scroll.pack(fill="both", expand=True)

        ed = self.card(page)
        ed.grid(row=0, column=1, sticky="nsew")
        top = tk.Frame(ed, bg=c["panel"])
        top.pack(fill="x", padx=18, pady=(16, 8))
        top.grid_columnconfigure(0, weight=1)
        self.note_title_var = tk.StringVar()
        title_entry = self.entry(top, self.note_title_var, width=20, size=16)
        title_entry.configure(font=self.font(16, bold=True, serif=True))
        title_entry.grid(row=0, column=0, sticky="ew", ipady=6)
        self.note_title_entry = title_entry
        self.note_cat_var = tk.StringVar(value="General")
        self.combo(top, self.store.NOTE_CATEGORIES, self.note_cat_var, width=11).grid(
            row=0, column=1, padx=(10, 0))
        self.pin_btn = self.btn(top, "☆  Pin", self._toggle_pin, "ghost")
        self.pin_btn.grid(row=0, column=2, padx=(10, 0))

        body = tk.Frame(ed, bg=c["panel"])
        body.pack(fill="both", expand=True, padx=18)
        self.note_text = self.textbox(body, height=10, size=12)
        sb = ttk.Scrollbar(body, orient="vertical", command=self.note_text.yview)
        self.note_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.note_text.pack(side="left", fill="both", expand=True)

        foot = tk.Frame(ed, bg=c["panel"])
        foot.pack(fill="x", padx=18, pady=(10, 14))
        self.note_stamp = self.lbl(foot, "", 9, color="muted", bg=c["panel"], justify="left")
        self.note_stamp.pack(side="left")
        self.btn(foot, "Delete", self._delete_note, "ghost").pack(side="right")
        self.btn(foot, "Save   (Ctrl+S)", self._save_note).pack(side="right", padx=(0, 8))
        for w in (title_entry, self.note_text):
            w.bind("<Control-s>", self._ctrl_s)
            w.bind("<Control-S>", self._ctrl_s)

        note = self.store.get_note(self.current_note_id) if self.current_note_id else None
        if note is None or note["workspace_id"] != self.ws_id:
            self.current_note_id = None
            note = None
        self._fill_editor(note)
        self._render_note_list()

    def _ctrl_s(self, _event=None):
        self._save_note()
        return "break"

    def _on_note_filter(self):
        self.note_query = self.note_query_var.get()
        self.note_cat = self.note_filter_var.get()
        self._render_note_list()

    def _fill_editor(self, note):
        if note:
            title, content, cat, pinned = note["title"], note["content"], note["category"], note["pinned"]
        else:
            title, content, cat, pinned = "", "", "General", False
        self.note_title_var.set(title)
        self.note_cat_var.set(cat)
        self.note_pinned = bool(pinned)
        self.note_text.delete("1.0", "end")
        self.note_text.insert("1.0", content)
        self.note_text.edit_reset()
        self._note_snapshot = (title.strip(), content, cat, bool(pinned))
        self._update_pin_btn()
        self._update_note_stamp(note)

    def _update_pin_btn(self):
        c = self.c
        if self.note_pinned:
            self.pin_btn.configure(text="★  Pinned")
            self.pin_btn.restyle(c["accent"], c["accent_fg"], c["accent_hover"])
        else:
            self.pin_btn.configure(text="☆  Pin")
            self.pin_btn.restyle(c["panel2"], c["fg"], c["hover"])

    def _update_note_stamp(self, note):
        if note:
            self.note_stamp.configure(text="Created %s\nUpdated %s" % (
                fmt_ts(note["created"]), fmt_ts(note["updated"])))
        else:
            self.note_stamp.configure(text="New note — not saved yet")

    def _note_current(self):
        return (self.note_title_var.get().strip(), self.note_text.get("1.0", "end-1c"),
                self.note_cat_var.get(), self.note_pinned)

    def _note_dirty(self):
        if self.page != "notes" or self.note_text is None:
            return False
        try:
            return self._note_current() != self._note_snapshot
        except tk.TclError:
            return False

    def _confirm_discard_note(self):
        """True if it is fine to leave the editor (nothing unsaved, or the user chose)."""
        if not self._note_dirty():
            return True
        answer = messagebox.askyesnocancel(
            "Unsaved note", "This note has unsaved changes.\n\nSave them first?", parent=self.root)
        if answer is None:
            return False
        if answer:
            return self._save_note(from_prompt=True)
        return True

    def _new_note(self):
        if not self._confirm_discard_note():
            return
        self.current_note_id = None
        self._fill_editor(None)
        self._render_note_list()
        self.note_title_entry.focus_set()

    def _open_note(self, note_id):
        if note_id == self.current_note_id:
            return
        if not self._confirm_discard_note():
            return
        self.current_note_id = note_id
        self._fill_editor(self.store.get_note(note_id))
        self._render_note_list()

    def _save_note(self, from_prompt=False):
        if self.note_text is None or self.page != "notes":
            return False
        title, content, cat, pinned = self._note_current()
        if not title and not content.strip():
            if from_prompt:
                return True
            messagebox.showinfo("Save note", "A note needs a title or some text.", parent=self.root)
            return False
        if not title:
            title = content.strip().splitlines()[0][:50]
        if self.current_note_id and self.store.get_note(self.current_note_id):
            note = self.store.update_note(self.current_note_id, title=title, content=content,
                                          category=cat, pinned=pinned)
        else:
            note = self.store.add_note(self.ws_id, title, content, cat, pinned)
            self.current_note_id = note["id"]
        if self.note_title_var.get().strip() != note["title"]:
            self.note_title_var.set(note["title"])
        self._note_snapshot = (note["title"].strip(), content, cat, pinned)
        self._update_note_stamp(note)
        self._render_note_list()
        return True

    def _toggle_pin(self):
        self.note_pinned = not self.note_pinned
        if self.current_note_id and self.store.get_note(self.current_note_id):
            self.store.update_note(self.current_note_id, touch=False, pinned=self.note_pinned)
            s = self._note_snapshot
            self._note_snapshot = (s[0], s[1], s[2], self.note_pinned)
            self._render_note_list()
        self._update_pin_btn()

    def _delete_note(self):
        saved = self.current_note_id and self.store.get_note(self.current_note_id)
        if saved:
            if not messagebox.askyesno("Delete note", "Delete this note permanently?", parent=self.root):
                return
            self.store.delete_note(self.current_note_id)
        elif self._note_dirty():
            if not messagebox.askyesno("Discard note", "Discard this unsaved note?", parent=self.root):
                return
        self.current_note_id = None
        self._fill_editor(None)
        self._render_note_list()

    def _render_note_list(self):
        c, sf = self.c, self.note_scroll
        pos = sf.clear()
        notes = self.store.notes_for(self.ws_id, self.note_query, self.note_cat)
        if not notes:
            filtered = self.note_query.strip() or self.note_cat != "All"
            self._empty(sf.inner, "No notes match." if filtered else "No notes yet.")
        for n in notes:
            sel = n["id"] == self.current_note_id
            bg = c["panel2"] if sel else c["panel"]
            row = tk.Frame(sf.inner, bg=bg, highlightthickness=1,
                           highlightbackground=c["accent"] if sel else c["border"])
            row.pack(fill="x", pady=3, padx=(0, 6))
            tk.Label(row, text=("★ " if n["pinned"] else "") + (n["title"] or "Untitled note"),
                     anchor="w", justify="left", wraplength=self.px(270),
                     font=self.font(11, bold=True), fg=c["accent"] if sel else c["fg"],
                     bg=bg).pack(fill="x", padx=12, pady=(8, 0))
            tk.Label(row, text="%s · %s" % (n["category"], fmt_ts(n["updated"])), anchor="w",
                     font=self.font(9), fg=c["muted"], bg=bg).pack(fill="x", padx=12, pady=(0, 8))
            self._click_all(row, lambda i=n["id"]: self._open_note(i))
        sf.restore(pos)

    # ================================================================= RESOURCES
    def _page_resources(self):
        c = self.c
        page = tk.Frame(self.content, bg=c["bg"])
        page.pack(fill="both", expand=True, padx=28, pady=(14, 18))

        add = self.card(page)
        add.pack(fill="x")
        f = tk.Frame(add, bg=c["panel"])
        f.pack(fill="x", padx=16, pady=14)
        f.grid_columnconfigure(1, weight=1)
        self.lbl(f, "Name", 10, color="muted", bg=c["panel"]).grid(row=0, column=0, sticky="w")
        self.lbl(f, "Website address, or file / folder path", 10, color="muted",
                 bg=c["panel"]).grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.lbl(f, "Type", 10, color="muted", bg=c["panel"]).grid(row=0, column=3, sticky="w", padx=(10, 0))
        self.res_name_var = tk.StringVar()
        self.res_loc_var = tk.StringVar()
        self.res_cat_var = tk.StringVar(value="Website")
        name_e = self.entry(f, self.res_name_var, width=22)
        name_e.grid(row=1, column=0, ipady=5)
        loc_e = self.entry(f, self.res_loc_var, width=30)
        loc_e.grid(row=1, column=1, sticky="ew", padx=(10, 0), ipady=5)
        self.btn(f, "Browse…", self._browse_resource, "ghost").grid(row=1, column=2, padx=(8, 0))
        self.combo(f, self.store.RESOURCE_CATEGORIES, self.res_cat_var, width=10).grid(
            row=1, column=3, padx=(10, 0))
        self.btn(f, "Add", self._add_resource).grid(row=1, column=4, padx=(10, 0))
        for w in (name_e, loc_e):
            w.bind("<Return>", lambda e: self._add_resource())

        self.lbl(page, "Saved resources", 14, bold=True, serif=True).pack(anchor="w", pady=(16, 6))
        self.res_scroll = ScrollFrame(page, c["bg"])
        self.res_scroll.pack(fill="both", expand=True)
        self._render_resources()

    def _browse_resource(self):
        cat = self.res_cat_var.get()
        if cat == "Folder":
            path = filedialog.askdirectory(parent=self.root, title="Choose a folder")
        else:
            path = filedialog.askopenfilename(parent=self.root, title="Choose a file")
        if not path:
            return
        self.res_loc_var.set(path)
        if not self.res_name_var.get().strip():
            self.res_name_var.set(os.path.basename(path.rstrip("/\\")) or path)
        if cat == "Website":
            self.res_cat_var.set("Document")

    def _add_resource(self):
        name = self.res_name_var.get().strip()
        loc = self.res_loc_var.get().strip()
        if not loc:
            messagebox.showinfo("New resource", "Please enter a web address or choose a file or folder.",
                                parent=self.root)
            return
        if not name:
            name = loc
        self.store.add_resource(self.ws_id, name, loc, self.res_cat_var.get())
        self.res_name_var.set("")
        self.res_loc_var.set("")
        self._render_resources()

    def _delete_resource(self, res_id):
        self.store.delete_resource(res_id)
        self._render_resources()

    def _open_resource(self, res):
        loc = res["location"].strip()
        path = os.path.expanduser(loc)
        low = loc.lower()
        try:
            if low.startswith(("http://", "https://", "ftp://")):
                webbrowser.open(loc)
            elif os.path.exists(path):
                open_path(path)
            elif res["category"] == "Website" or low.startswith("www."):
                webbrowser.open("https://" + loc)
            else:
                messagebox.showerror("Cannot open", "This file or folder could not be found:\n\n%s" % loc,
                                     parent=self.root)
        except Exception as exc:  # opening is done by the OS; report any failure plainly
            messagebox.showerror("Cannot open", "Could not open:\n\n%s\n\n%s" % (loc, exc),
                                 parent=self.root)

    def _render_resources(self):
        c, sf = self.c, self.res_scroll
        pos = sf.clear()
        items = self.store.resources_for(self.ws_id)
        if not items:
            self._empty(sf.inner, "No resources yet — save a website, document or folder above.")
        target = None
        for r in items:
            lit = self.pending_highlight == ("resource", r["id"])
            bg = c["tint"] if lit else c["panel"]
            row = tk.Frame(sf.inner, bg=bg, highlightthickness=1,
                           highlightbackground=c["accent"] if lit else c["border"])
            row.pack(fill="x", pady=3, padx=(0, 6))
            row.grid_columnconfigure(0, weight=1)
            info = tk.Frame(row, bg=bg)
            info.grid(row=0, column=0, sticky="ew", padx=14, pady=8)
            head = tk.Frame(info, bg=bg)
            head.pack(anchor="w")
            tk.Label(head, text=r["name"], font=self.font(12, bold=True), fg=c["fg"], bg=bg).pack(side="left")
            tk.Label(head, text=r["category"], font=self.font(9, bold=True), fg=c["accent"],
                     bg=mix(bg, c["accent"], 0.2), padx=8, pady=1).pack(side="left", padx=10)
            tk.Label(info, text=r["location"], anchor="w", justify="left", font=self.font(9),
                     fg=c["muted"], bg=bg, wraplength=self.px(620)).pack(anchor="w", pady=(2, 0))
            self.btn(row, "Open", lambda res=r: self._open_resource(res), "primary").grid(
                row=0, column=1, padx=6)
            x = tk.Label(row, text="✕", font=self.font(12), fg=c["muted"], bg=bg,
                         cursor="hand2", padx=10)
            x.grid(row=0, column=2)
            x.bind("<Button-1>", lambda e, i=r["id"]: self._delete_resource(i))
            x.bind("<Enter>", lambda e, w=x: w.configure(fg=c["danger"]))
            x.bind("<Leave>", lambda e, w=x: w.configure(fg=c["muted"]))
            if lit:
                target = row
        if target is not None:
            sf.scroll_to(target)
        else:
            sf.restore(pos)

    # ================================================================ WORKSPACES
    def _page_workspaces(self):
        c = self.c
        page = tk.Frame(self.content, bg=c["bg"])
        page.pack(fill="both", expand=True, padx=28, pady=(14, 18))

        add = self.card(page)
        add.pack(fill="x")
        f = tk.Frame(add, bg=c["panel"])
        f.pack(fill="x", padx=16, pady=14)
        f.grid_columnconfigure(1, weight=1)
        self.lbl(f, "New workspace", 10, color="muted", bg=c["panel"]).grid(row=0, column=0, sticky="w")
        self.lbl(f, "Description", 10, color="muted", bg=c["panel"]).grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.lbl(f, "Symbol", 10, color="muted", bg=c["panel"]).grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.ws_name_var = tk.StringVar()
        self.ws_desc_var = tk.StringVar()
        self.ws_sym_var = tk.StringVar()
        name_e = self.entry(f, self.ws_name_var, width=20)
        name_e.grid(row=1, column=0, ipady=5)
        desc_e = self.entry(f, self.ws_desc_var, width=30)
        desc_e.grid(row=1, column=1, sticky="ew", padx=(10, 0), ipady=5)
        sym_e = self.entry(f, self.ws_sym_var, width=4)
        sym_e.grid(row=1, column=2, padx=(10, 0), ipady=5)
        self.btn(f, "Create", self._add_workspace).grid(row=1, column=3, padx=(10, 0))
        self.lbl(f, "Symbol: one or two characters, such as ✦, ⚒ or a letter.", 9,
                 color="muted", bg=c["panel"]).grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        for w in (name_e, desc_e, sym_e):
            w.bind("<Return>", lambda e: self._add_workspace())

        sf = ScrollFrame(page, c["bg"])
        sf.pack(fill="both", expand=True, pady=(14, 0))
        sf.inner.grid_columnconfigure(0, weight=1, uniform="ws")
        sf.inner.grid_columnconfigure(1, weight=1, uniform="ws")
        for i, w in enumerate(self.store.workspaces):
            active = w["id"] == self.ws_id
            card = tk.Frame(sf.inner, bg=c["panel"], highlightthickness=2 if active else 1,
                            highlightbackground=c["accent"] if active else c["border"])
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
            head = tk.Frame(card, bg=c["panel"])
            head.pack(fill="x", padx=16, pady=(14, 0))
            self.lbl(head, w["symbol"], 26, serif=True, color="accent", bg=c["panel"]).pack(side="left")
            self.lbl(head, w["name"], 16, bold=True, serif=True, bg=c["panel"]).pack(side="left", padx=10)
            if active:
                self.lbl(head, "● active", 9, bold=True, color="accent", bg=c["panel"]).pack(side="right")
            self.lbl(card, w["description"] or "No description.", 10, italic=True, color="muted",
                     bg=c["panel"], wraplength=self.px(330), justify="left").pack(anchor="w", padx=16, pady=(4, 0))
            n = self.store.workspace_counts(w["id"])
            self.lbl(card, "%d tasks  ·  %d notes  ·  %d resources" % (
                n["tasks"], n["notes"], n["resources"]), 10, bg=c["panel"]).pack(anchor="w", padx=16, pady=(8, 0))
            btns = tk.Frame(card, bg=c["panel"])
            btns.pack(anchor="w", padx=16, pady=(10, 14))
            if not active:
                self.btn(btns, "Switch to this", lambda i=w["id"]: self._switch_from_page(i)).pack(side="left")
            else:
                self.btn(btns, "Open dashboard", lambda: self.nav_to("dashboard")).pack(side="left")
            self.btn(btns, "Delete", lambda i=w["id"]: self._delete_workspace(i), "ghost").pack(
                side="left", padx=(8, 0))

    def _add_workspace(self):
        name = self.ws_name_var.get().strip()
        if not name:
            messagebox.showinfo("New workspace", "Please give the workspace a name.", parent=self.root)
            return
        if self.store.workspace_name_exists(name):
            messagebox.showinfo("New workspace", "A workspace called “%s” already exists." % name,
                                parent=self.root)
            return
        self.store.add_workspace(name, self.ws_desc_var.get(), self.ws_sym_var.get())
        self._sync_ws_combo()
        self.show_page("workspaces")

    def _switch_from_page(self, ws_id):
        self.set_workspace(ws_id, page="dashboard")

    def _delete_workspace(self, ws_id):
        st = self.store
        if len(st.workspaces) <= 1:
            messagebox.showinfo("Delete workspace", "SHIFT needs at least one workspace.", parent=self.root)
            return
        w = st.get_workspace(ws_id)
        n = st.workspace_counts(ws_id)
        if not messagebox.askyesno(
                "Delete workspace",
                "Delete “%s” together with its %d tasks, %d notes and %d resources?\n\n"
                "This cannot be undone." % (w["name"], n["tasks"], n["notes"], n["resources"]),
                icon="warning", parent=self.root):
            return
        st.delete_workspace(ws_id)
        if ws_id == self.ws_id:
            self.set_workspace(st.get_setting("workspace"), page="workspaces")
        else:
            self._sync_ws_combo()
            self.show_page("workspaces")

    # ================================================================ APPEARANCE
    def _page_appearance(self):
        c = self.c
        sf = ScrollFrame(self.content, c["bg"])
        sf.pack(fill="both", expand=True, padx=(28, 22), pady=(10, 14))
        page = sf.inner
        self.lbl(page, "Theme", 16, bold=True, serif=True).pack(anchor="w", pady=(4, 0))
        self.lbl(page, "Your choice is remembered the next time SHIFT opens.", 10, italic=True,
                 color="muted").pack(anchor="w", pady=(0, 8))
        grid = tk.Frame(page, bg=c["bg"])
        grid.pack(fill="x")
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1, uniform="theme")
        for i, name in enumerate(THEMES):
            t = build_colors(name)
            sel = name == self.theme_name
            card = tk.Frame(grid, bg=t["bg"], highlightthickness=3 if sel else 1,
                            highlightbackground=c["accent"] if sel else c["border"])
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            tk.Frame(card, bg=t["accent"], height=6).pack(fill="x")
            tk.Label(card, text="Aa  Quiet study", font=self.font(15, serif=True), fg=t["fg"],
                     bg=t["panel"], pady=14).pack(fill="x", padx=12, pady=(12, 0))
            tk.Label(card, text="a calm place to think", font=self.font(9, italic=True), fg=t["muted"],
                     bg=t["panel"]).pack(fill="x", padx=12)
            tk.Label(card, text=name + ("   ✓" if sel else ""), font=self.font(11, bold=True),
                     fg=t["fg"], bg=t["bg"], pady=10).pack(fill="x")
            self._click_all(card, lambda n=name: self.apply_theme(n))

        self.lbl(page, "Accent colour", 16, bold=True, serif=True).pack(anchor="w", pady=(22, 0))
        self.lbl(page, "A custom accent lasts for this session only; the theme above is what is saved.",
                 10, italic=True, color="muted").pack(anchor="w", pady=(0, 8))
        arow = tk.Frame(page, bg=c["bg"])
        arow.pack(anchor="w")
        tk.Label(arow, text="      ", bg=c["accent"], highlightthickness=1,
                 highlightbackground=c["border"]).pack(side="left", ipady=6)
        self.btn(arow, "Choose colour…", self._choose_accent).pack(side="left", padx=(12, 0))
        self.btn(arow, "Reset to theme accent", self._reset_accent, "ghost").pack(side="left", padx=(8, 0))

        self.lbl(page, "Your name", 16, bold=True, serif=True).pack(anchor="w", pady=(22, 0))
        self.lbl(page, "Used for the greeting on your dashboard.", 10, italic=True,
                 color="muted").pack(anchor="w", pady=(0, 8))
        nrow = tk.Frame(page, bg=c["bg"])
        nrow.pack(anchor="w", pady=(0, 20))
        self.name_var = tk.StringVar(value=self.store.get_setting("name", "Scholar"))
        name_e = self.entry(nrow, self.name_var, width=24)
        name_e.pack(side="left", ipady=5)
        self.btn(nrow, "Save name", self._save_name).pack(side="left", padx=(10, 0))
        self.name_status = self.lbl(nrow, "", 10, color="success")
        self.name_status.pack(side="left", padx=10)
        name_e.bind("<Return>", lambda e: self._save_name())

    def apply_theme(self, name):
        self.theme_name = name
        self.store.set_setting("theme", name)
        self._recolor("appearance")

    def _choose_accent(self):
        result = colorchooser.askcolor(color=self.c["accent"], parent=self.root,
                                       title="Choose an accent colour")
        if result and result[1]:
            self.custom_accent = result[1]
            self._recolor("appearance")

    def _reset_accent(self):
        self.custom_accent = None
        self._recolor("appearance")

    def _save_name(self):
        self.store.set_setting("name", self.name_var.get().strip() or "Scholar")
        self.name_status.configure(text="Saved.")
        self.root.after(2000, lambda: self._clear_label(self.name_status))

    @staticmethod
    def _clear_label(label):
        try:
            label.configure(text="")
        except tk.TclError:
            pass

    # =============================================================== QUICK SEARCH
    def _close_qs(self):
        if self._qs is not None:
            try:
                self._qs.destroy()
            except tk.TclError:
                pass
        self._qs = None

    def open_quick_search(self, _event=None):
        if self.distraction:
            return
        if self._qs is not None:
            try:
                if self._qs.winfo_exists():
                    self._qs.lift()
                    self._qs_entry.focus_set()
                    return
            except tk.TclError:
                pass
        c = self.c
        top = tk.Toplevel(self.root)
        self._qs = top
        top.title("Quick Search")
        top.configure(bg=c["bg"])
        top.transient(self.root)
        w, h = self.px(640), self.px(460)
        x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - w) // 2)
        y = self.root.winfo_rooty() + self.px(80)
        top.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.lbl(top, "Quick search", 16, bold=True, serif=True).pack(anchor="w", padx=20, pady=(16, 0))
        self.lbl(top, "Tasks, notes and resources from every workspace", 10, italic=True,
                 color="muted").pack(anchor="w", padx=20)
        var = tk.StringVar()
        entry = self.entry(top, var, width=40, size=12)
        entry.pack(fill="x", padx=20, pady=(10, 8), ipady=6)
        self._qs_entry = entry
        frame = tk.Frame(top, bg=c["border"], padx=1, pady=1)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        listbox = tk.Listbox(frame, activestyle="none", font=self.font(11), bg=c["panel"],
                             fg=c["fg"], selectbackground=c["accent"], selectforeground=c["accent_fg"],
                             highlightthickness=0, relief="flat", bd=0)
        vsb = ttk.Scrollbar(frame, command=listbox.yview)
        listbox.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        listbox.pack(fill="both", expand=True)
        info = self.lbl(top, "Start typing.   ↑ ↓ choose · Enter open · Esc close", 9,
                        color="muted")
        info.pack(anchor="w", padx=20, pady=(0, 12))
        hits = []
        tags = {"task": "Task", "note": "Note", "resource": "Resource"}

        def refresh(*_args):
            hits[:] = self.store.search_all(var.get())
            listbox.delete(0, "end")
            for hit in hits:
                listbox.insert("end", "%s   %s    —  %s · %s" % (
                    tags[hit["kind"]], hit["title"], hit["ws_name"], hit["detail"]))
            if hits:
                listbox.selection_set(0)
                info.configure(text="%d result%s   ↑ ↓ choose · Enter open · Esc close" % (
                    len(hits), "" if len(hits) == 1 else "s"))
            elif var.get().strip():
                info.configure(text="Nothing found.")
            else:
                info.configure(text="Start typing.   ↑ ↓ choose · Enter open · Esc close")

        def move(delta):
            n = listbox.size()
            if n:
                sel = listbox.curselection()
                idx = ((sel[0] if sel else -1) + delta) % n
                listbox.selection_clear(0, "end")
                listbox.selection_set(idx)
                listbox.activate(idx)
                listbox.see(idx)
            return "break"

        def choose(_event=None):
            sel = listbox.curselection()
            if hits and (sel or listbox.size()):
                hit = hits[sel[0] if sel else 0]
                self._close_qs()
                self._goto_hit(hit)
            return "break"

        var.trace_add("write", refresh)
        entry.bind("<Down>", lambda e: move(1))
        entry.bind("<Up>", lambda e: move(-1))
        entry.bind("<Return>", choose)
        listbox.bind("<Double-Button-1>", choose)
        listbox.bind("<Return>", choose)
        top.bind("<Escape>", lambda e: self._close_qs())
        entry.focus_set()

    def _goto_hit(self, hit):
        if not self._confirm_discard_note():
            return
        if hit["ws_id"] != self.ws_id:
            self._flush_intentions()
            self.ws_id = hit["ws_id"]
            self.store.set_setting("workspace", self.ws_id)
            self.task_query = ""
            self.note_query = ""
            self.note_cat = "All"
            self._sync_ws_combo()
        if hit["kind"] == "note":
            self.current_note_id = hit["id"]
            self.show_page("notes")
        elif hit["kind"] == "task":
            self.task_filter = "All"
            self.task_query = ""
            self.pending_highlight = ("task", hit["id"])
            self.show_page("tasks")
        else:
            self.pending_highlight = ("resource", hit["id"])
            self.show_page("resources")
