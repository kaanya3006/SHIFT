# SHIFT – A Personal Productivity and Workspace Management Application

SHIFT is a desktop-based productivity application developed using Python and Tkinter. It is designed to help users manage their daily tasks, organise notes and resources, and maintain focus while working.

The application brings different productivity tools together in one place, making it easier to organise everyday activities without switching between multiple applications.

SHIFT also features a Gothic Academia-inspired interface with custom themes and a simple, user-friendly layout.

## About the Project

The main idea behind SHIFT is to provide a single platform where users can manage their work and personal activities more efficiently.

Whether it is keeping track of college assignments, saving useful study materials, writing notes, or setting aside time for focused work, SHIFT provides tools to manage these activities in an organised way.

The application uses local JSON files to store information, so users can access their saved data without requiring an internet connection or an external database.

## Features

### 1. Dashboard
- Displays an overview of tasks and productivity.
- Shows pending and completed task information.
- Provides quick access to different application sections.

### 2. Task Management
- Add, edit, and delete tasks.
- Set task priorities such as Low, Medium, and High.
- Add due dates to tasks.
- Mark tasks as completed.
- Search and filter tasks.

### 3. Focus Room
- Includes timer presets of 15, 25, 45, and 60 minutes.
- Start, pause, and reset timer options.
- Helps users manage focused working sessions.
- Includes a distraction-free mode.

### 4. Notes
- Create, edit, and delete notes.
- Organise notes using categories.
- Pin important notes.
- Search for saved notes.

### 5. Resources Library
- Save useful website links.
- Store local file and folder paths.
- Organise resources into categories.
- Open saved resources whenever needed.

### 6. Workspace Management
- Includes default workspaces such as College, Coding, Research, and Personal.
- Create and manage additional workspaces.
- Switch between workspaces.
- Keep tasks, notes, and resources organised.

### 7. Themes and Appearance
- Includes multiple themes to customise the application.
- Provides a consistent Gothic Academia-inspired design.
- Allows users to choose an appearance they prefer.

### 8. Quick Search
- Quickly search for saved tasks, notes, and resources.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Tkinter | Creating the graphical user interface |
| ttk | Styled interface components |
| JSON | Storing application data locally |
| UUID | Generating unique identifiers |
| datetime | Handling dates and time |
| os | File and folder operations |
| subprocess | System-level operations |
| webbrowser | Opening saved website links |

## Getting Started

Follow these steps to run SHIFT on your computer.

### Prerequisites

- Python installed on your system.
- A code editor such as VS Code (optional).

Tkinter is included with many standard Python installations. Make sure it is available in your Python environment.

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/kaanya3006/SHIFT.git
```

**2. Open the project folder**

```bash
cd SHIFT
```

**3. Run the application**

```bash
python main.py
```

### Alternative Run Methods

- **Windows:** Run `run.bat`.
- **Linux/macOS:** Run `bash run.sh`.

## Project Structure

```text
SHIFT/
│
├── main.py
├── run.bat
├── run.sh
├── README.md
│
├── ui/
│   ├── __init__.py
│   └── frontend.py
│
├── data/
│   ├── workspaces.json
│   ├── tasks.json
│   ├── notes.json
│   ├── resources.json
│   └── settings.json
│
└── assets/
    └── README.txt
```

## Data Storage

SHIFT uses JSON files to store application information locally.

Each file is used for a particular purpose:

- `workspaces.json` – Stores workspace information.
- `tasks.json` – Stores task details.
- `notes.json` – Stores saved notes.
- `resources.json` – Stores saved resources.
- `settings.json` – Stores application preferences and theme settings.

This approach keeps the storage simple and allows the application to work without an external database.

## Future Enhancements

Some features that can be added in future versions include:

- Calendar integration.
- Task reminders and notifications.
- Recurring tasks.
- Cloud backup and synchronisation.
- Productivity reports and analytics.
- More advanced note-taking options.

## Team Members

**Project: SHIFT – A Personal Productivity and Workspace Management Application**

1. **Kaanya** – RA2511003011682
2. **V Srishty** – RA2511003011712
3. **Dinesh Kanna SM** – RA2511003011723

## Acknowledgement

This project was developed as part of our academic work. Through SHIFT, we got the opportunity to work with Python, GUI development, file handling, and local data storage while building an application that addresses everyday productivity needs.

---

**SHIFT – Organise your world. Focus on what matters.**