# Skyline Weather

A clean desktop weather app (Python + CustomTkinter, data from Open-Meteo) used as the subject of an
end-to-end DevOps delivery pipeline.

**Download page:** https://anamaynarkar.github.io/devops_lab_ca/

## Run from source
```bash
pip install -r requirements-dev.txt
python main.py
pytest -q
```

## Docker
```bash
docker build --target test -t skyline-weather:test .          # run tests in a container
docker build --target artifact --output dist . # build the Linux executable
```

## Pipeline
| Stage | Where |
|---|---|
| Version control | Git + GitHub |
| Automated tests | `pytest`, run in `.github/workflows/ci.yml` (Linux + Windows) and in Docker |
| Containerization | `Dockerfile` (test and build stages) |
| Build | PyInstaller for Windows/Linux on x64 and ARM64, `.github/workflows/release.yml` |
| Deploy | GitHub Releases (executables) and GitHub Pages (`docs/`) |

Release: `git tag v0.1.0 && git push origin v0.1.0`
