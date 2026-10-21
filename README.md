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

## What we used, in simple words
| Tool | What it does here |
|---|---|
| **Git + GitHub** | Stores the code and its history. |
| **pytest** | Automatic tests. They check the weather logic without needing the internet. |
| **Docker** | Runs the tests (and builds the Linux app) in a clean container, so results are the same everywhere. |
| **GitHub Actions** | A robot that runs our steps on GitHub's computers whenever we push. This is our CI/CD. |
| **PyInstaller** | Turns the Python app into one file you can double-click, with no Python install needed. |
| **GitHub Releases** | Stores the finished download files. |
| **GitHub Pages** | Hosts the download website (`docs/index.html`). |

## How the pipeline works
**1. Every push or pull request** runs `ci.yml`:
- runs the tests on Linux and Windows
- opens the app window on a fake screen to check it starts
- builds the Docker image, which runs the tests again and builds the Linux app

If anything fails, the run turns red and we know before anyone downloads a broken app.

**2. Pushing a version tag** (like `v0.1.1`) runs `release.yml`:
- runs the tests first
- builds the app 4 times at once, each on a matching computer: Windows and Linux, each for normal
  PCs (x64) and ARM chips (arm64). An app only runs on the system it was built on, so all four are needed.
- publishes the 4 files, plus a checksum for each, to GitHub Releases

**3. The website** reads the newest release from GitHub, detects the visitor's system, and links to the
right download. A new release shows up on the website by itself.

```
push code  -> tests + Docker check (CI)
push tag   -> tests -> 4 builds -> GitHub Release -> website shows it
```

## How to make a release
```bash
git tag v0.1.1
git push origin v0.1.1
```
Wait about 2 minutes, then check the Releases page and the website.

## Folders
| Path | What is inside |
|---|---|
| `skyline/api.py` | Gets and parses weather data (no GUI, so it is easy to test) |
| `skyline/ui.py` | The app window |
| `tests/` | The automatic tests |
| `Dockerfile` | Docker steps: `test` runs tests, `build` makes the Linux app |
| `.github/workflows/` | `ci.yml` and `release.yml`, the pipeline |
| `docs/index.html` | The download website |
| `report/` | The project report |
