# syntax=docker/dockerfile:1
# Stage "test": runs the unit tests in a clean, reproducible container.
# Stage "build": produces the Linux executable with PyInstaller.
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements-dev.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .

FROM base AS test
RUN pytest -q

FROM base AS build
RUN apt-get update && apt-get install -y --no-install-recommends binutils libtk8.6 \
    && rm -rf /var/lib/apt/lists/*
RUN python -c "import tkinter" \
    && pyinstaller --onefile --windowed --name skyline-weather \
    --collect-all customtkinter main.py

FROM scratch AS artifact
COPY --from=build /app/dist/skyline-weather /skyline-weather
