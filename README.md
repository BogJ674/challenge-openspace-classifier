# OpenSpace Organizer
[![forthebadge made-with-python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

## 🏢 Description

Your company moved to a new office at CEVI Ghent. It's an openspace with configurable tables and seating capacity. As many of you are new colleagues, you come up with the idea of changing seats everyday and get to know each other better by working side by side with your new colleagues.

This interactive application helps you organize and manage seating arrangements dynamically. You can adjust the room layout, handle late arrivals, set seating preferences, and re-organize seating at any time.

![coworking_img](https://media1.tenor.com/m/Z0GoLGN6GcwAAAAd/wwe-john-cena.gif)

## 📦 Repo structure

```
.
├── utils/
│   ├── openspace.py          # Openspace class - manages tables and seating
│   ├── table.py              # Table and Seat classes
│   └── file_utils.py         # CSV and JSON file operations
├── .gitignore
├── main.py                   # Interactive terminal application
├── new_colleagues.csv        # Input file with colleague names
├── openspace_state.json      # Saved session state (auto-generated)
├── output.csv                # Exported seating arrangement (optional)
├── config.json               # Room configuration (optional)
└── README.md
```

## 🛎️ Usage

1. Clone the repository to your local machine.

2. To run the script, you can execute the `main.py` file from your command line:

```bash
python main.py
````

3. The application launches an interactive terminal menu with the following features:

## 🎨 Interactive Terminal Interface

The terminal provides a color-coded menu system with real-time statistics:

![terminal_svg](https://file%2B.vscode-resource.vscode-cdn.net/Users/jensbogaert/Desktop/BeCode/challenge-openspace-classifier/termtosvg_qsip2q4m.svg?version%3D1761313606159)

### Menu Options

**Setup & Configuration**
- **Configure room**: Adjust number of tables and seating capacity
- **Organize initial seating**: Load colleagues from CSV and create first arrangement

**Dynamic Changes**
- **Add colleague**: Add late arrivals and automatically seat them
- **Add table**: Expand room capacity on the fly
- **Re-organize seating**: Shuffle all seated colleagues to new positions

**Seating Preferences**
- **Whitelist**: Set preferences for colleagues who want to sit together
- **Blacklist**: Keep certain colleagues apart

**View Information**
- **Current arrangement**: Visual display of all tables and seated colleagues
- **Room statistics**: Track seated/available/alone/unseated counts

### Statistics Footer

Every screen shows real-time stats at the bottom:
- **Seated**: Number of colleagues currently seated
- **Available**: Number of empty seats
- **Alone**: Number of people sitting at a table by themselves
- **Unseated**: People who couldn't be seated due to capacity

### State Persistence

The application automatically saves your session state to `openspace_state.json`, so you can close and resume without losing your seating arrangement or preferences.

## ⏱️ Timeline

This project took two days for completion.

## 📌 Personal Situation
This project was done as part of the AI Bootcamp at BeCode.org. 

Connect with me on [LinkedIn](https://www.linkedin.com/in/jens-bogaert-6b53b526a/).

