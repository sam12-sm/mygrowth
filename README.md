# 🌱 MyGrowth — Habit Tracker App

A full-featured personal habit tracking app built with **Python + Streamlit**, inspired by the MyGrowth workbook by Internsoft.

## Features

| Page | What it does |
|------|-------------|
| 🏠 Dashboard | Overview: today's habits, goals, challenge progress, daily quote |
| 🎯 Goal Setting | Set goals from 1 week all the way to 10 years |
| ✅ Weekly Tracker | Tick habits daily, track streaks, see weekly % |
| 🔥 30-Day Challenge | Commit to one habit for 30 days with a visual streak calendar |
| 🌀 Wheel of Growth | Score yourself in 6 life areas, visualize with a radar chart |

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

## Data Storage
All your data is saved locally in `habit_data.json` — no account needed, no internet required.

## Tech Stack
- **Python 3.x**
- **Streamlit** — UI framework
- **Plotly** — Radar chart visualization
- **JSON** — Local data persistence

## Project Structure
```
habit_tracker/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── habit_data.json     # Your saved data (auto-created)
└── README.md           # This file
```

## Portfolio Notes
This project demonstrates:
- Building a multi-page web app in pure Python
- Working with JSON for local data persistence
- Interactive UI components (sliders, buttons, progress bars)
- Data visualization with Plotly radar charts
- Clean, modular code structure

---
Built with ❤️ using Python & Streamlit
