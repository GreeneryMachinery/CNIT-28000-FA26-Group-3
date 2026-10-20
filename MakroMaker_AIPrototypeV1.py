from __future__ import annotations
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""KeyLaunch - one-file Windows global shortcut launcher.

Requirements: Windows 10/11, Python 3.9+ with Tkinter (standard library).
No third-party Python packages are used.

Run: python KeyLaunch.py
Optional: pythonw KeyLaunch.py --minimized

Settings: %LOCALAPPDATA%\\KeyLaunch\\macros.json
Each shortcut launches one file, folder, URL or executable. The application
must remain running (it may be minimized) for shortcuts to work.
"""

"""
THIS FILE CONTAINS 100% AI GENERATED CODE. DO NOT SUBMIT FOR ANY CLASS CREDIT. THIS IS ONLY FOR TESTING PURPOSES.
"""

"""
AI Disclosure
ChatGPT V6.0 Sol
"I need to make a program that launches programs or opens files using user defined keyboard macros. The program should be based on Python, and ideally use a single python file. It can import libraries that are open-source with permissive use, as the program will be under the Apache 2.0 license."
The goal of the code is to create a quick prototype as a proof of concept, and provide guidance in development direction for the project.
AI was used to get a rough mock up to verify viability prior to manually beginning to write code.
"""

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import queue
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import uuid

if sys.platform == "win32":
    import winreg

APP_NAME = "KeyLaunch"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP_NAME
DATA_FILE = DATA_DIR / "macros.json"
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_VALUE = "KeyLaunch"

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_APP_WAKE = 0x8001
PM_NOREMOVE = 0x0000

KEYS = {chr(code): code for code in range(ord("A"), ord("Z") + 1)}
KEYS.update({str(n): ord(str(n)) for n in range(10)})
KEYS.update({f"F{n}": 0x6F + n for n in range(1, 12)})  # F12 reserved by Windows
KEYS.update({
    "Space": 0x20,
    "PageUp": 0x21,
    "PageDown": 0x22,
    "End": 0x23,
    "Home": 0x24,
    "Left": 0x25,
    "Up": 0x26,
    "Right": 0x27,
    "Down": 0x28,
    "Insert": 0x2D,
    "Delete": 0x2E,
})
MOD_NAMES = (("Ctrl", MOD_CONTROL), ("Alt", MOD_ALT), ("Shift", MOD_SHIFT), ("Win", MOD_WIN))
ALIASES = {
    "CONTROL": "Ctrl", "CTRL": "Ctrl", "ALT": "Alt",
    "SHIFT": "Shift", "WIN": "Win", "WINDOWS": "Win", "SUPER": "Win",
    "PGUP": "PageUp", "PAGEUP": "PageUp", "PRIOR": "PageUp",
    "PGDN": "PageDown", "PAGEDOWN": "PageDown", "NEXT": "PageDown",
    "DEL": "Delete", "DELETE": "Delete", "INS": "Insert", "INSERT": "Insert",
    "SPACE": "Space", "LEFT": "Left", "RIGHT": "Right", "UP": "Up",
    "DOWN": "Down", "HOME": "Home", "END": "End",
}


def parse_hotkey(hotkey: str) -> tuple[str, int, int]:
    """Return (canonical display text, Windows modifier bits, Windows VK)."""
    words = [part.strip() for part in hotkey.split("+")]
    if not words or any(not part for part in words):
        raise ValueError("Use a shortcut such as Ctrl+Alt+K.")
    modifiers: set[str] = set()
    primary = None
    for word in words:
        token = ALIASES.get(word.upper(), word.upper())
        if token in {"Ctrl", "Alt", "Shift", "Win"}:
            if token in modifiers:
                raise ValueError(f"Repeated modifier: {token}.")
            modifiers.add(token)
        else:
            candidate = next((k for k in KEYS if k.upper() == token.upper()), None)
            if candidate is None:
                raise ValueError(f"Unsupported shortcut key: {word}. Use A-Z, 0-9, F1-F11 or navigation keys.")
            if primary is not None:
                raise ValueError("A shortcut can have only one non-modifier key.")
            primary = candidate
    if primary is None:
        raise ValueError("Add a letter, digit, F-key, or navigation key.")
    if not ({"Ctrl", "Alt", "Win"} & modifiers):
        raise ValueError("Include Ctrl, Alt, or Win to avoid triggering shortcuts while typing.")
    bits = sum(bit for name, bit in MOD_NAMES if name in modifiers)
    canonical = "+".join([name for name, _ in MOD_NAMES if name in modifiers] + [primary])
    return canonical, bits, KEYS[primary]


def load_macros() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("macros"), list):
        raise ValueError("Configuration should contain a 'macros' array.")
    cleaned = []
    used_ids = set()
    for item in data["macros"]:
        if not isinstance(item, dict):
            continue
        uid = str(item.get("id") or uuid.uuid4().hex)
        if uid in used_ids:
            uid = uuid.uuid4().hex
        used_ids.add(uid)
        cleaned.append({
            "id": uid,
            "name": str(item.get("name", "Unnamed")),
            "hotkey": str(item.get("hotkey", "")),
            "target": str(item.get("target", "")),
            "args": str(item.get("args", "")),
            "cwd": str(item.get("cwd", "")),
            "enabled": bool(item.get("enabled", True)),
        })
    return cleaned


def save_macros(macros: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=DATA_DIR, suffix=".tmp", delete=False
        ) as file:
            temp_name = file.name
            json.dump({"schema": 1, "macros": macros}, file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temp_name, DATA_FILE)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def startup_command() -> str:
    # subprocess.list2cmdline handles Windows argument quoting without launching a process.
    import subprocess
    if getattr(sys, "frozen", False):
        args = [sys.executable, "--minimized"]
    else:
        interpreter = Path(sys.executable)
        if interpreter.name.lower() == "python.exe":
            gui_interpreter = interpreter.with_name("pythonw.exe")
            if gui_interpreter.exists():
                interpreter = gui_interpreter
        args = [str(interpreter), str(Path(__file__).resolve()), "--minimized"]
    return subprocess.list2cmdline(args)


def startup_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY) as key:
            winreg.QueryValueEx(key, STARTUP_VALUE)
            return True
    except FileNotFoundError:
        return False


def set_startup(enabled: bool) -> None:
    if enabled:
        command = startup_command()
        if len(command) > 260:
            raise ValueError("The startup command is too long for the Windows Run registry key.")
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, STARTUP_VALUE, 0, winreg.REG_SZ, command)
    else:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, STARTUP_VALUE)
        except FileNotFoundError:
            pass


def launch_macro(macro: dict) -> None:
    """Use the user's Windows file associations to open apps, files and URLs."""
    raw = macro["target"].strip()
    if not raw:
        raise ValueError("This macro has no target.")
    is_url = raw.lower().startswith(("https://", "http://"))
    target = raw if is_url else os.path.expanduser(os.path.expandvars(raw.strip('"')))
    arguments = macro.get("args", "").strip()
    directory = os.path.expanduser(os.path.expandvars(macro.get("cwd", "").strip().strip('"')))
    directory = directory or None
    if directory and not os.path.isdir(directory):
        raise FileNotFoundError(f"Working directory does not exist:\n{directory}")
    if not is_url:
        # A simple command like 'notepad.exe' can be resolved by Windows.
        # Explicit paths are checked to make typos immediately visible.
        explicit_path = os.path.isabs(target) or any(sep in target for sep in ("\\", "/"))
        if explicit_path and not os.path.exists(target):
            raise FileNotFoundError(f"Target does not exist:\n{target}")
    executable = not is_url and Path(target).suffix.lower() in {".exe", ".com", ".bat", ".cmd"}
    if arguments and not executable:
        raise ValueError("Arguments are supported for executable programs (.exe, .com, .bat, .cmd) only.")
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    shell.ShellExecuteW.argtypes = [
        wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR,
        wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_int,
    ]
    shell.ShellExecuteW.restype = ctypes.c_void_p
    code = shell.ShellExecuteW(None, "open", target, arguments or None, directory, 1)
    if int(code or 0) <= 32:
        raise OSError(f"Windows could not open {target!r} (ShellExecute error {int(code or 0)}).")


class HotkeyService:
    """Owns a dedicated native message loop; Tk and hotkeys never fight over messages."""

    def __init__(self) -> None:
        self.commands: queue.Queue = queue.Queue()
        self.events: queue.Queue = queue.Queue()
        self.ready = threading.Event()
        self.thread_id: int | None = None
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
        self.user32.RegisterHotKey.restype = wintypes.BOOL
        self.user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        self.user32.UnregisterHotKey.restype = wintypes.BOOL
        self.user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
        self.user32.GetMessageW.restype = ctypes.c_int
        self.user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
        self.user32.PeekMessageW.restype = wintypes.BOOL
        self.user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self.user32.PostThreadMessageW.restype = wintypes.BOOL
        self.kernel32.GetCurrentThreadId.argtypes = []
        self.kernel32.GetCurrentThreadId.restype = wintypes.DWORD
        self.thread = threading.Thread(target=self._run, daemon=True, name="KeyLaunchHotkeys")
        self.thread.start()
        if not self.ready.wait(3):
            raise RuntimeError("Windows hotkey listener could not initialize.")

    def _wake(self) -> None:
        if self.thread_id and self.thread.is_alive():
            if not self.user32.PostThreadMessageW(self.thread_id, WM_APP_WAKE, 0, 0):
                self.events.put(("error", "Unable to notify the global hotkey listener."))

    def update(self, macros: list[dict]) -> None:
        self.commands.put(("update", [dict(m) for m in macros]))
        self._wake()

    def stop(self) -> None:
        self.commands.put(("stop", None))
        self._wake()
        self.thread.join(timeout=1.5)

    def _run(self) -> None:
        registered: dict[int, str] = {}
        msg = wintypes.MSG()
        try:
            self.thread_id = int(self.kernel32.GetCurrentThreadId())
            # Forces Windows to create this thread's message queue before PostThreadMessage.
            self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_NOREMOVE)
            self.ready.set()
            while True:
                value = self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if value <= 0:
                    break
                if msg.message == WM_HOTKEY:
                    uid = registered.get(int(msg.wParam))
                    if uid:
                        self.events.put(("launch", uid))
                elif msg.message == WM_APP_WAKE:
                    while True:
                        try:
                            action, payload = self.commands.get_nowait()
                        except queue.Empty:
                            break
                        if action == "stop":
                            return
                        if action != "update":
                            continue
                        for hid in registered:
                            self.user32.UnregisterHotKey(None, hid)
                        registered.clear()
                        states: dict[str, str] = {}
                        seen: set[str] = set()
                        for macro in payload:
                            uid = macro["id"]
                            if not macro.get("enabled", True):
                                states[uid] = "Disabled"
                                continue
                            try:
                                canonical, bits, vk = parse_hotkey(macro["hotkey"])
                            except ValueError as exc:
                                states[uid] = f"Invalid: {exc}"
                                continue
                            if canonical in seen:
                                states[uid] = "Duplicate shortcut"
                                continue
                            seen.add(canonical)
                            hotkey_id = len(registered) + 1
                            # Advance past successful IDs only; each registered ID is unique.
                            if self.user32.RegisterHotKey(None, hotkey_id, bits | MOD_NOREPEAT, vk):
                                registered[hotkey_id] = uid
                                states[uid] = "Active"
                            else:
                                err = ctypes.get_last_error()
                                states[uid] = f"Unavailable (Windows error {err})"
                        self.events.put(("states", states))
        except Exception as exc:
            self.events.put(("error", f"Global hotkey listener stopped: {exc}"))
        finally:
            for hid in registered:
                self.user32.UnregisterHotKey(None, hid)
            self.ready.set()


class ShortcutRecorder:
    """Captures a combination using Win32 polling; never installs a keyboard hook."""

    def __init__(self, parent: tk.Toplevel, on_done) -> None:
        self.on_done = on_done
        self.window = tk.Toplevel(parent)
        self.window.title("Record shortcut")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.geometry("420x155")
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.finish(None))
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Press your shortcut now", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Hold Ctrl, Alt or Win, then press a letter, digit, F1-F11\nor navigation key. Press Escape to cancel.").pack(anchor="w", pady=(12, 12))
        ttk.Button(frame, text="Cancel", command=lambda: self.finish(None)).pack(anchor="e")
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.user32.GetAsyncKeyState.restype = ctypes.c_short
        self.watch_keys = list(KEYS.values()) + [0x1B]
        self.previous = self.pressed_keys()
        self.window.grab_set()
        self.window.focus_force()
        self.window.after(70, self.poll)

    def down(self, vk: int) -> bool:
        return bool(self.user32.GetAsyncKeyState(vk) & 0x8000)

    def pressed_keys(self) -> set[int]:
        return {vk for vk in self.watch_keys if self.down(vk)}

    def poll(self) -> None:
        if not self.window.winfo_exists():
            return
        current = self.pressed_keys()
        fresh = current - self.previous
        self.previous = current
        if 0x1B in fresh:
            self.finish(None)
            return
        mod_names = []
        if self.down(0x11):
            mod_names.append("Ctrl")
        if self.down(0x12):
            mod_names.append("Alt")
        if self.down(0x10):
            mod_names.append("Shift")
        if self.down(0x5B) or self.down(0x5C):
            mod_names.append("Win")
        if fresh and ("Ctrl" in mod_names or "Alt" in mod_names or "Win" in mod_names):
            vk = next(iter(sorted(fresh)))
            key = next((name for name, code in KEYS.items() if code == vk), None)
            if key:
                self.finish("+".join(mod_names + [key]))
                return
        self.window.after(35, self.poll)

    def finish(self, hotkey: str | None) -> None:
        if self.window.winfo_exists():
            self.window.grab_release()
            self.window.destroy()
        self.on_done(hotkey)


class MacroDialog:
    def __init__(self, app: "KeyLaunchApp", original: dict | None = None) -> None:
        self.app = app
        self.original = original
        self.result = None
        self.top = tk.Toplevel(app.root)
        self.top.title("Edit shortcut" if original else "Add shortcut")
        self.top.geometry("680x385")
        self.top.minsize(650, 385)
        self.top.transient(app.root)
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)
        wrapper = ttk.Frame(self.top, padding=18)
        wrapper.pack(fill="both", expand=True)
        wrapper.columnconfigure(1, weight=1)
        row = 0
        def add_row(label: str, variable: tk.StringVar, browse_command=None):
            nonlocal row
            ttk.Label(wrapper, text=label).grid(row=row, column=0, sticky="w", pady=7, padx=(0, 12))
            field = ttk.Entry(wrapper, textvariable=variable)
            field.grid(row=row, column=1, sticky="ew", pady=7)
            if browse_command:
                ttk.Button(wrapper, text="Browse...", command=browse_command).grid(
                    row=row, column=2, padx=(8, 0), pady=7
                )
            row += 1
            return field
        self.name_var = tk.StringVar(value=original.get("name", "") if original else "")
        self.key_var = tk.StringVar(value=original.get("hotkey", "") if original else "")
        self.target_var = tk.StringVar(value=original.get("target", "") if original else "")
        self.args_var = tk.StringVar(value=original.get("args", "") if original else "")
        self.cwd_var = tk.StringVar(value=original.get("cwd", "") if original else "")
        self.enabled_var = tk.BooleanVar(value=original.get("enabled", True) if original else True)
        first = add_row("Name", self.name_var)
        add_row("Shortcut", self.key_var, self.record)
        add_row("Program / file / URL", self.target_var, self.browse_target)
        add_row("Program arguments", self.args_var)
        add_row("Working folder", self.cwd_var, self.browse_cwd)
        ttk.Checkbutton(wrapper, text="Enabled", variable=self.enabled_var).grid(
            row=row, column=1, sticky="w", pady=(6, 4)
        )
        row += 1
        ttk.Label(wrapper, text="Example: Ctrl+Alt+K. Arguments apply to .exe/.com/.bat/.cmd files only.",
                  foreground="#59677a").grid(row=row, column=0, columnspan=3, sticky="w", pady=8)
        row += 1
        controls = ttk.Frame(wrapper)
        controls.grid(row=row, column=0, columnspan=3, sticky="e", pady=(8, 0))
        ttk.Button(controls, text="Cancel", command=self.cancel).pack(side="right", padx=(8, 0))
        ttk.Button(controls, text="Save", command=self.save).pack(side="right")
        first.focus_set()
        self.top.grab_set()
        self.top.wait_window()

    def browse_target(self) -> None:
        path = filedialog.askopenfilename(parent=self.top, title="Choose program or file", filetypes=[
            ("All files", "*.*"), ("Applications", "*.exe *.com *.bat *.cmd"),
        ])
        if path:
            self.target_var.set(path)
        # Folders and URLs may be entered directly.

    def browse_cwd(self) -> None:
        path = filedialog.askdirectory(parent=self.top, title="Choose working directory")
        if path:
            self.cwd_var.set(path)

    def record(self) -> None:
        self.app.suspend_hotkeys = True
        self.app.publish_hotkeys()
        self.top.grab_release()
        def done(hotkey):
            if hotkey:
                self.key_var.set(hotkey)
            self.top.grab_set()
            self.app.suspend_hotkeys = False
            self.app.publish_hotkeys()
        ShortcutRecorder(self.top, done)

    def save(self) -> None:
        name = self.name_var.get().strip()
        target = self.target_var.get().strip()
        if not name or not target:
            messagebox.showerror("Missing information", "Give this shortcut a name and a target.", parent=self.top)
            return
        try:
            canonical, _, _ = parse_hotkey(self.key_var.get())
        except ValueError as exc:
            messagebox.showerror("Invalid shortcut", str(exc), parent=self.top)
            return
        for other in self.app.macros:
            if self.original and other["id"] == self.original["id"]:
                continue
            try:
                same = parse_hotkey(other["hotkey"])[0] == canonical
            except ValueError:
                same = False
            if same:
                messagebox.showerror("Duplicate shortcut", f"{canonical} is already assigned to {other['name']}.", parent=self.top)
                return
        args = self.args_var.get().strip()
        suffix = Path(target.strip('"')).suffix.lower()
        if args and suffix not in {".exe", ".com", ".bat", ".cmd"}:
            messagebox.showerror("Invalid arguments", "Program arguments are supported for .exe, .com, .bat and .cmd files only.", parent=self.top)
            return
        self.result = {
            "id": self.original["id"] if self.original else uuid.uuid4().hex,
            "name": name,
            "hotkey": canonical,
            "target": target,
            "args": args,
            "cwd": self.cwd_var.get().strip(),
            "enabled": self.enabled_var.get(),
        }
        self.top.grab_release()
        self.top.destroy()

    def cancel(self) -> None:
        self.top.grab_release()
        self.top.destroy()


class KeyLaunchApp:
    def __init__(self, root: tk.Tk, macros: list[dict]) -> None:
        self.root = root
        self.macros = macros
        self.suspend_hotkeys = False
        self.states: dict[str, str] = {}
        self.service = HotkeyService()
        self.setup_ui()
        self.refresh()
        self.publish_hotkeys()
        self.root.after(80, self.check_events)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def setup_ui(self) -> None:
        self.root.title("KeyLaunch - Shortcut Manager")
        self.root.geometry("990x570")
        self.root.minsize(770, 460)
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        shell = ttk.Frame(self.root, padding=20)
        shell.pack(fill="both", expand=True)
        ttk.Label(shell, text="KeyLaunch", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(shell, text="Global keyboard shortcuts for programs, files, folders, and websites.",
                  foreground="#637083").pack(anchor="w", pady=(1, 15))
        toolbar = ttk.Frame(shell)
        toolbar.pack(fill="x", pady=(0, 12))
        for text, handler in [
            ("+ Add", self.add), ("Edit", self.edit), ("Delete", self.delete),
            ("Enable / Disable", self.toggle), ("Run now", self.run_selected),
        ]:
            ttk.Button(toolbar, text=text, command=handler).pack(side="left", padx=(0, 7))
        container = ttk.Frame(shell)
        container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(container, columns=("name", "hotkey", "target", "state"),
                                 show="headings", selectmode="browse")
        for col, label, width, stretch in [
            ("name", "Name", 180, True), ("hotkey", "Keyboard shortcut", 152, False),
            ("target", "Program / file / URL", 385, True), ("state", "Status", 160, False),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, stretch=stretch, minwidth=90)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda event: self.edit())
        self.tree.bind("<Delete>", lambda event: self.delete())
        self.tree.bind("<Return>", lambda event: self.edit())
        options = ttk.Frame(shell)
        options.pack(fill="x", pady=(15, 6))
        self.startup_var = tk.BooleanVar(value=startup_enabled())
        ttk.Checkbutton(options, text="Run minimized when I sign in to Windows",
                        variable=self.startup_var, command=self.change_startup).pack(side="left")
        ttk.Button(options, text="Open settings folder", command=self.open_settings_folder).pack(side="right")
        self.info = tk.StringVar(value="Ready")
        ttk.Label(shell, textvariable=self.info, foreground="#526279").pack(anchor="w", pady=(10, 4))
        ttk.Label(shell, text="Shortcuts work while this window is minimized. Closing KeyLaunch stops all shortcuts.",
                  foreground="#748195").pack(anchor="w")

    def selected(self) -> dict | None:
        items = self.tree.selection()
        return next((m for m in self.macros if items and m["id"] == items[0]), None)

    def refresh(self, select_id: str | None = None) -> None:
        previous = select_id or (self.tree.selection()[0] if self.tree.selection() else None)
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for item in self.macros:
            status = self.states.get(item["id"], "Checking..." if item["enabled"] else "Disabled")
            self.tree.insert("", "end", iid=item["id"], values=(
                item["name"], item["hotkey"], item["target"], status,
            ))
        if previous and self.tree.exists(previous):
            self.tree.selection_set(previous)
            self.tree.see(previous)
        active = sum(1 for value in self.states.values() if value == "Active")
        self.info.set(f"{len(self.macros)} shortcuts configured  |  {active} active")

    def commit(self, select_id: str | None = None) -> None:
        try:
            save_macros(self.macros)
        except Exception as exc:
            messagebox.showerror("Unable to save", str(exc), parent=self.root)
        self.publish_hotkeys()
        self.refresh(select_id)

    def publish_hotkeys(self) -> None:
        self.service.update([] if self.suspend_hotkeys else self.macros)

    def add(self) -> None:
        dialog = MacroDialog(self)
        if dialog.result:
            self.macros.append(dialog.result)
            self.commit(dialog.result["id"])

    def edit(self) -> None:
        macro = self.selected()
        if not macro:
            messagebox.showinfo("Select a shortcut", "Choose a shortcut to edit.", parent=self.root)
            return
        dialog = MacroDialog(self, macro)
        if dialog.result:
            macro.update(dialog.result)
            self.commit(macro["id"])

    def delete(self) -> None:
        macro = self.selected()
        if not macro:
            return
        if messagebox.askyesno("Delete shortcut", f"Delete '{macro['name']}'?", parent=self.root):
            self.macros.remove(macro)
            self.commit()

    def toggle(self) -> None:
        macro = self.selected()
        if macro:
            macro["enabled"] = not macro["enabled"]
            self.commit(macro["id"])

    def run_selected(self) -> None:
        macro = self.selected()
        if macro:
            self.run(macro)

    def run(self, macro: dict) -> None:
        try:
            launch_macro(macro)
            self.info.set(f"Launched: {macro['name']}")
        except Exception as exc:
            messagebox.showerror("Could not launch shortcut", f"{macro['name']}\n\n{exc}", parent=self.root)

    def check_events(self) -> None:
        try:
            while True:
                kind, payload = self.service.events.get_nowait()
                if kind == "states":
                    self.states = payload
                    self.refresh()
                elif kind == "launch":
                    macro = next((m for m in self.macros if m["id"] == payload and m["enabled"]), None)
                    if macro and not self.suspend_hotkeys:
                        self.run(macro)
                elif kind == "error":
                    self.info.set(str(payload))
        except queue.Empty:
            pass
        self.root.after(80, self.check_events)

    def change_startup(self) -> None:
        try:
            set_startup(self.startup_var.get())
        except Exception as exc:
            self.startup_var.set(not self.startup_var.get())
            messagebox.showerror("Startup setting failed", str(exc), parent=self.root)

    def open_settings_folder(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        os.startfile(str(DATA_DIR))

    def close(self) -> None:
        self.service.stop()
        self.root.destroy()


def main() -> None:
    if sys.platform != "win32":
        print("KeyLaunch currently supports Windows 10 and 11 only.", file=sys.stderr)
        raise SystemExit(1)
    # Avoid competing copies using the same shortcuts and settings file.
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    mutex = kernel.CreateMutexW(None, False, "Local\\KeyLaunch_MacroShortcutManager_v1")
    if not mutex:
        raise OSError("Could not create application instance mutex.")
    if ctypes.get_last_error() == 183:
        if "--minimized" not in sys.argv:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(APP_NAME, "KeyLaunch is already running. Check the taskbar.")
            root.destroy()
        kernel.CloseHandle(mutex)
        return
    try:
        root = tk.Tk()
        try:
            macros = load_macros()
        except Exception as exc:
            messagebox.showerror("Settings could not be loaded", f"{DATA_FILE}\n\n{exc}\n\n"
                                 "Existing settings have not been overwritten.", parent=root)
            root.destroy()
            return
        try:
            KeyLaunchApp(root, macros)
        except Exception as exc:
            messagebox.showerror("Could not start KeyLaunch", str(exc), parent=root)
            root.destroy()
            return
        if "--minimized" in sys.argv:
            root.after(250, root.iconify)
        root.mainloop()
    finally:
        kernel.CloseHandle(mutex)


if __name__ == "__main__":
    main()

# End of AI Generated Code Segment