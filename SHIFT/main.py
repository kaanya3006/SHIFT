#!/usr/bin/env python3
"""SHIFT - Gothic Academia Edition.

A personal productivity and workspace manager built with Python and Tkinter.

This file contains:
  * the data / application-logic layer (the `Store` class), which keeps
    workspaces, tasks, notes, resources and settings in local JSON files, and
  * the program entry point, which starts the Tkinter interface in
    ui/frontend.py.

The `Store` class has no dependency on Tkinter, so it can be tested on its own.
"""

import json
import os
import sys
import uuid
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

TASK_FILTERS = ["All", "Today", "Upcoming", "Completed"]
PRIORITIES = ["Low", "Normal", "High"]
PRIORITY_RANK = {"Low": 0, "Normal": 1, "High": 2}
NOTE_CATEGORIES = ["General", "Lecture", "Ideas", "Project", "Personal"]
RESOURCE_CATEGORIES = ["Website", "Document", "Folder", "Other"]

DEFAULT_WORKSPACES = [
    ("College", "Classes, assignments and study-related activities.", "✎"),
    ("Coding", "Programming projects and experiments.", "⚙"),
    ("Research", "Research materials and collected information.", "❦"),
    ("Personal", "Personal tasks and everyday activities.", "☾"),
]

DEFAULT_THEME = "Gothic Academia"


def new_id():
    """Return a fresh unique identifier."""
    return uuid.uuid4().hex


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


class Store:
    """Loads, queries, changes and saves everything SHIFT remembers."""

    # Shared choice lists, so the interface can read them from the store.
    TASK_FILTERS = TASK_FILTERS
    PRIORITIES = PRIORITIES
    NOTE_CATEGORIES = NOTE_CATEGORIES
    RESOURCE_CATEGORIES = RESOURCE_CATEGORIES

    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.recovered = []  # names of files that were damaged and reset

        self.workspaces = self._load("workspaces", list)
        self.tasks = self._load("tasks", list)
        self.notes = self._load("notes", list)
        self.resources = self._load("resources", list)
        self.settings = self._load("settings", dict)

        if not self.workspaces:
            self.workspaces = [
                {"id": new_id(), "name": n, "description": d, "symbol": s}
                for n, d, s in DEFAULT_WORKSPACES
            ]
        self.settings.setdefault("theme", DEFAULT_THEME)
        self.settings.setdefault("focus_minutes", 25)
        self.settings.setdefault("name", "Scholar")
        self.settings.setdefault("intentions", {})
        if self.get_workspace(self.settings.get("workspace")) is None:
            self.settings["workspace"] = self.workspaces[0]["id"]

        for name in ("workspaces", "tasks", "notes", "resources", "settings"):
            self._save(name)

    # ------------------------------------------------------------------ files
    def _path(self, name):
        return os.path.join(self.data_dir, name + ".json")

    def _load(self, name, kind):
        path = self._path(name)
        if not os.path.exists(path):
            return kind()
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, kind):
                raise ValueError("unexpected structure")
            return data
        except (OSError, ValueError):
            # Keep the damaged file for the user instead of silently erasing it.
            try:
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                os.replace(path, "%s.damaged-%s.bak" % (path, stamp))
            except OSError:
                pass
            self.recovered.append(name + ".json")
            return kind()

    def _save(self, name):
        path = self._path(name)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(getattr(self, name), fh, indent=2, ensure_ascii=False)
        os.replace(tmp, path)

    # --------------------------------------------------------------- settings
    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self._save("settings")

    def get_intentions(self, ws_id):
        entry = self.settings.get("intentions", {}).get(ws_id)
        if entry and entry.get("date") == today_str():
            return entry.get("text", "")
        return ""

    def set_intentions(self, ws_id, text):
        intentions = self.settings.setdefault("intentions", {})
        text = text.strip()
        if text:
            intentions[ws_id] = {"date": today_str(), "text": text}
        else:
            intentions.pop(ws_id, None)
        self._save("settings")

    # ------------------------------------------------------------- workspaces
    def get_workspace(self, ws_id):
        for ws in self.workspaces:
            if ws["id"] == ws_id:
                return ws
        return None

    def workspace_name_exists(self, name):
        name = name.strip().lower()
        return any(w["name"].strip().lower() == name for w in self.workspaces)

    def add_workspace(self, name, description="", symbol=""):
        ws = {
            "id": new_id(),
            "name": name.strip(),
            "description": description.strip(),
            "symbol": (symbol.strip() or "✦")[:2],
        }
        self.workspaces.append(ws)
        self._save("workspaces")
        return ws

    def delete_workspace(self, ws_id):
        """Delete a workspace together with its tasks, notes and resources.

        The last remaining workspace cannot be deleted. Returns True on success.
        """
        if len(self.workspaces) <= 1 or self.get_workspace(ws_id) is None:
            return False
        self.workspaces = [w for w in self.workspaces if w["id"] != ws_id]
        self.tasks = [t for t in self.tasks if t["workspace_id"] != ws_id]
        self.notes = [n for n in self.notes if n["workspace_id"] != ws_id]
        self.resources = [r for r in self.resources if r["workspace_id"] != ws_id]
        self.settings.get("intentions", {}).pop(ws_id, None)
        if self.settings.get("workspace") == ws_id:
            self.settings["workspace"] = self.workspaces[0]["id"]
        for name in ("workspaces", "tasks", "notes", "resources", "settings"):
            self._save(name)
        return True

    def workspace_counts(self, ws_id):
        return {
            "tasks": sum(1 for t in self.tasks if t["workspace_id"] == ws_id),
            "notes": sum(1 for n in self.notes if n["workspace_id"] == ws_id),
            "resources": sum(1 for r in self.resources if r["workspace_id"] == ws_id),
        }

    # ------------------------------------------------------------------ tasks
    def add_task(self, ws_id, title, due="", priority="Normal"):
        if priority not in PRIORITIES:
            priority = "Normal"
        task = {
            "id": new_id(),
            "workspace_id": ws_id,
            "title": title.strip(),
            "due": due,
            "priority": priority,
            "done": False,
            "created": now_str(),
            "completed_at": "",
        }
        self.tasks.append(task)
        self._save("tasks")
        return task

    def toggle_task(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                t["completed_at"] = now_str() if t["done"] else ""
                self._save("tasks")
                return t
        return None

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save("tasks")

    def tasks_for(self, ws_id, flt="All", query=""):
        today = today_str()
        q = query.strip().lower()
        out = []
        for t in self.tasks:
            if t["workspace_id"] != ws_id:
                continue
            if q and q not in t["title"].lower():
                continue
            due = t.get("due") or ""
            if flt == "Today" and due != today:
                continue
            if flt == "Upcoming" and not (due and due > today and not t["done"]):
                continue
            if flt == "Completed" and not t["done"]:
                continue
            out.append(t)
        if flt == "Completed":
            out.sort(key=lambda t: t.get("completed_at") or "", reverse=True)
        else:
            out.sort(
                key=lambda t: (
                    t["done"],
                    t.get("due") or "9999-99-99",
                    -PRIORITY_RANK.get(t["priority"], 1),
                    t["created"],
                )
            )
        return out

    def pending_count(self, ws_id):
        return sum(1 for t in self.tasks if t["workspace_id"] == ws_id and not t["done"])

    def due_today_count(self, ws_id):
        today = today_str()
        return sum(
            1
            for t in self.tasks
            if t["workspace_id"] == ws_id and not t["done"] and t.get("due") == today
        )

    def overdue_count(self, ws_id):
        today = today_str()
        return sum(
            1
            for t in self.tasks
            if t["workspace_id"] == ws_id
            and not t["done"]
            and t.get("due")
            and t["due"] < today
        )

    def today_progress(self, ws_id):
        """Return (done, total) for tasks due today or completed today."""
        today = today_str()
        relevant = [
            t
            for t in self.tasks
            if t["workspace_id"] == ws_id
            and (t.get("due") == today or (t.get("completed_at") or "")[:10] == today)
        ]
        done = sum(1 for t in relevant if t["done"])
        return done, len(relevant)

    # ------------------------------------------------------------------ notes
    def add_note(self, ws_id, title, content, category="General", pinned=False):
        if category not in NOTE_CATEGORIES:
            category = "General"
        stamp = now_str()
        note = {
            "id": new_id(),
            "workspace_id": ws_id,
            "title": title.strip(),
            "content": content,
            "category": category,
            "pinned": bool(pinned),
            "created": stamp,
            "updated": stamp,
        }
        self.notes.append(note)
        self._save("notes")
        return note

    def get_note(self, note_id):
        for n in self.notes:
            if n["id"] == note_id:
                return n
        return None

    def update_note(self, note_id, touch=True, **fields):
        note = self.get_note(note_id)
        if note is None:
            return None
        for key in ("title", "content", "category", "pinned"):
            if key in fields:
                note[key] = fields[key]
        if touch:
            note["updated"] = now_str()
        self._save("notes")
        return note

    def delete_note(self, note_id):
        self.notes = [n for n in self.notes if n["id"] != note_id]
        self._save("notes")

    def notes_for(self, ws_id, query="", category="All"):
        q = query.strip().lower()
        out = []
        for n in self.notes:
            if n["workspace_id"] != ws_id:
                continue
            if category != "All" and n["category"] != category:
                continue
            if q and q not in n["title"].lower() and q not in n["content"].lower():
                continue
            out.append(n)
        out.sort(key=lambda n: n["updated"], reverse=True)
        out.sort(key=lambda n: not n["pinned"])  # stable: pinned notes first
        return out

    # -------------------------------------------------------------- resources
    def add_resource(self, ws_id, name, location, category="Website"):
        if category not in RESOURCE_CATEGORIES:
            category = "Other"
        res = {
            "id": new_id(),
            "workspace_id": ws_id,
            "name": name.strip(),
            "location": location.strip(),
            "category": category,
            "created": now_str(),
        }
        self.resources.append(res)
        self._save("resources")
        return res

    def delete_resource(self, res_id):
        self.resources = [r for r in self.resources if r["id"] != res_id]
        self._save("resources")

    def resources_for(self, ws_id):
        out = [r for r in self.resources if r["workspace_id"] == ws_id]
        out.sort(key=lambda r: r["name"].lower())
        return out

    # ----------------------------------------------------------------- search
    def search_all(self, query, limit=60):
        """Search task titles, note titles/content and resource names/locations
        across every workspace."""
        q = query.strip().lower()
        if not q:
            return []
        names = {w["id"]: w["name"] for w in self.workspaces}
        results = []
        for t in self.tasks:
            if q in t["title"].lower():
                detail = "Done" if t["done"] else (t.get("due") or "No due date")
                results.append(self._hit("task", t, t["title"], detail, names))
        for n in self.notes:
            if q in n["title"].lower() or q in n["content"].lower():
                results.append(self._hit("note", n, n["title"] or "Untitled note", n["category"], names))
        for r in self.resources:
            if q in r["name"].lower() or q in r["location"].lower():
                results.append(self._hit("resource", r, r["name"], r["category"], names))
        results.sort(key=lambda h: 0 if h["title"].lower().startswith(q) else 1)
        return results[:limit]

    @staticmethod
    def _hit(kind, item, title, detail, names):
        return {
            "kind": kind,
            "id": item["id"],
            "ws_id": item["workspace_id"],
            "ws_name": names.get(item["workspace_id"], "?"),
            "title": title,
            "detail": detail,
        }


# ------------------------------------------------------------------ start-up
def main():
    if sys.version_info < (3, 9):
        print("SHIFT needs Python 3.9 or later (you have %d.%d)." % sys.version_info[:2])
        sys.exit(1)
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("SHIFT needs Tkinter, which this Python installation does not include.")
        print("  Windows / macOS : reinstall Python from python.org (tick 'tcl/tk').")
        print("  Debian / Ubuntu : sudo apt install python3-tk")
        print("  Fedora          : sudo dnf install python3-tkinter")
        print("  Arch            : sudo pacman -S tk")
        sys.exit(1)

    from ui.frontend import ShiftApp

    store = Store()
    ShiftApp(store).run()


if __name__ == "__main__":
    main()
