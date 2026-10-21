# Skyline Weather

A small desktop weather app (Python) used to show a complete DevOps pipeline: from a code change to a
tested, built and downloadable app, all automatically.

**Download page:** https://anamaynarkar.github.io/devops_lab_ca/

## The app
Type a city and see the current weather and a 5-day forecast. Built with Python and CustomTkinter.
Weather data comes from the free [Open-Meteo](https://open-meteo.com) API (no key needed).

```bash
pip install -r requirements-dev.txt
python main.py     # run the app
pytest -q          # run the tests
```
On Linux the app needs Tk installed first (for example `sudo apt install python3-tk`).

## What we used, in simple words
| Tool | What it does here |
|---|---|
| **Git + GitHub** | Stores the code and its history. |
| **pytest** | Automatic unit tests that check the weather logic. |
| **Docker** | A clean, throwaway Linux machine. All Linux testing runs inside it, and it also proves the Linux build recipe works. |
| **GitHub Actions** | A robot that runs our steps on GitHub's computers whenever we push. This is our CI/CD. |
| **PyInstaller** | Packs the Python app into one file you can double-click, with no Python install needed. |
| **GitHub Releases** | Stores the finished download files. |
| **GitHub Pages** | Hosts the download website (`docs/index.html`). |

## How the pipeline works
There are two workflows. One checks every change, the other publishes a version.

### 1. Checking every push and pull request (`ci.yml`)
**What is tested?** The Python source code, not the finished app. Python runs straight from source, so
the tests never need a build. Building only wraps the same code into one file at the end. The tests are
unit tests (`tests/test_api.py`, 8 of them): they feed the weather code fake network replies and check
that it parses data, converts units and reports errors correctly. They never call the real internet.

The code is tested on both operating systems we ship for, in two parallel jobs:
- **Linux, inside Docker.** The `test` stage of the `Dockerfile` is a fresh Linux container. It runs the
  unit tests and then a GUI smoke test (opens the real window for 1.5 seconds on a virtual screen, to
  catch crashes the data tests cannot see). Because the container only has what `requirements.txt` and
  the `Dockerfile` install, a forgotten dependency fails here even if it works on our laptops.
- **Windows, directly on a Windows runner.** The same unit tests and GUI smoke test, without Docker.
  GitHub's Windows machines cannot run Linux containers, and Windows containers are huge and have no
  desktop, so Windows is tested natively instead.

A third job builds the Linux app inside Docker (the `build` and `artifact` stages) to check that the
Linux build recipe works. That app is only a check. It is not the file people download.

If anything fails, the run turns red and we know before anyone downloads a broken app.

### 2. Publishing a version (`release.yml`)
Starts when we push a tag like `v0.1.1`.
1. **Tests run first** (Linux in Docker, Windows natively). A tag push does not wait for CI, so the release re-checks the code itself.
2. **Four builds run at the same time, on GitHub's computers (not in Docker, not on our laptops).**
   Each one runs the same PyInstaller command. PyInstaller cannot build for another system: it packs the
   Python and libraries of the machine it runs on. So each target needs its own matching machine
   (a GitHub "runner"), not a different compiler:

   | Output | Runner machine |
   |---|---|
   | Linux, normal PC (x64) | `ubuntu-24.04` |
   | Linux, ARM chip (arm64) | `ubuntu-24.04-arm` |
   | Windows, normal PC (x64) | `windows-latest` |
   | Windows, ARM chip (arm64) | `windows-11-arm` |
3. **Publish.** The 4 files plus a checksum for each go to GitHub Releases.

The finished apps are not opened automatically in CI. They are the same tested code, packed by a tool
that has run on the real target system.

### 3. The website
It reads the newest release from GitHub, detects the visitor's system, and links to the right download.
A new release shows up on the website by itself.

```
push code  -> Linux tests in Docker + Windows tests + Docker build check
push tag   -> tests -> 4 builds on 4 machines -> GitHub Release -> website shows it
```

## Running the downloaded app
- **Windows:** double-click the `.exe`. It is unsigned, so SmartScreen may warn: choose "More info", then "Run anyway".
- **Linux:** downloads lose the executable flag, so run `chmod +x skyline-weather-linux-x64` once, then `./skyline-weather-linux-x64`.

## How to make a release
```bash
git tag v0.1.1
git push origin v0.1.1
```
Wait 2 to 3 minutes, then check the Releases page and the website.

## Folders
| Path | What is inside |
|---|---|
| `skyline/api.py` | Gets and parses weather data (no GUI, so it is easy to test) |
| `skyline/ui.py` | The app window |
| `tests/` | The unit tests (`test_api.py`) and the GUI smoke test (`smoke_gui.py`) |
| `Dockerfile` | `test` stage runs the unit tests and GUI smoke test, `build` stage makes the Linux app |
| `.github/workflows/` | `ci.yml` and `release.yml`, the pipeline |
| `docs/index.html` | The download website |
| `report/` | The project report |
