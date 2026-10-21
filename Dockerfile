# syntax=docker/dockerfile:1
# All automated testing happens in the "test" stage of this file.
# Stage "test":     unit tests + headless GUI smoke test.
# Stage "build":    builds the Linux executable with PyInstaller.
# Stage "artifact": exports only the executable.
FROM python:3.12-slim AS base
WORKDIR /app
# libtk8.6: Tk runtime for the GUI; xvfb, xauth: virtual screen; binutils: needed by PyInstaller
RUN apt-get update && apt-get install -y --no-install-recommends binutils libtk8.6 xvfb xauth \
    && rm -rf /var/lib/apt/lists/*
COPY requirements-dev.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .

FROM base AS test
RUN pytest -q
RUN PYTHONPATH=. xvfb-run -a python tests/smoke_gui.py

FROM base AS build
RUN python -c "import tkinter" \
    && pyinstaller --onefile --windowed --name skyline-weather \
    --collect-all customtkinter main.py

FROM scratch AS artifact
COPY --from=build /app/dist/skyline-weather /skyline-weather
