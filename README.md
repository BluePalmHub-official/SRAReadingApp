# SRA Reading Progress Tracker

A desktop app for teachers to record each student's reading progress on the **SRA Reading Laboratory** and see it as charts. Keep a roster, log comprehension and reading-rate scores after each session, and generate individual and whole-class reports.

Built with Python, Tkinter and Matplotlib.

> SRA Reading Laboratory is a product of its publisher. This is an independent teacher's tool and is not affiliated with or endorsed by them.

## Features

- **Student management:** add, update and delete students with name, date of birth and grade level. Age is calculated automatically.
- **Progress tracking:** log each session with the date, SRA colour level, comprehension score (%), reading rate (words per minute) and notes, with a full history per student.
- **Analytics and reports:** a chart report for one student, and a class overview to compare everyone.
- **Level reference built in:** the SRA colour levels from Pre-Primary through Red 3B are mapped to Lexile range, grade level and reading age.

## Requirements

- Python 3 (developed and tested on 3.13)
- Tkinter, which comes with the standard Python installers for Windows and macOS. On Debian or Ubuntu Linux, install it with `sudo apt install python3-tk`.
- Matplotlib and NumPy:

```bash
pip install -r requirements.txt
```

## Run it

```bash
git clone https://github.com/BluePalmHub-official/SRAReadingApp.git
cd SRAReadingApp
pip install -r requirements.txt
python3 main.py
```

`main.py` starts the app. The code itself is in `SRAReadingApp.py`, in the `SRAReadingTracker` class.

## Your data and privacy

Student records are saved to a file called `sra_students.json` in the folder you run the app from. It stays on your computer. Because it holds student names and birth dates, it is listed in `.gitignore` so it cannot be committed by accident. Please keep it that way if you fork this project, and back the file up yourself.

## Build a standalone app

```bash
pip install pyinstaller
pyinstaller SRAReadingApp.spec
```

The program appears in `dist/`. Build on the system you want to run it on.

## Project layout

```
main.py              Starts the app
SRAReadingApp.py     The whole application: roster, progress log, charts
SRAReadingApp.spec   PyInstaller build recipe
requirements.txt     Python packages needed
```

## Contributing and reuse

This is a free, open project. Read it, learn from it and adapt it for your own classroom or project under the MIT License. Issues and suggestions are welcome.

## License

[MIT](LICENSE) © 2026 Dennis Quijano

Made by [BluePalm Hub](https://bluepalmhub.com), custom software for businesses and schools.
