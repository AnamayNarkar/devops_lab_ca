"""CustomTkinter GUI."""
from __future__ import annotations

import threading

import customtkinter as ctk

from . import __version__
from .api import Weather, WeatherError, format_temp, describe, get_weather

BG = "#0b1a14"
CARD = "#12261d"
CARD_2 = "#1a3528"
ACCENT = "#34d399"
TEXT = "#eef1ff"
MUTED = "#8a93b8"
FONT = "Segoe UI"


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color=BG)
        ctk.set_appearance_mode("dark")
        self.title(f"Skyline Weather {__version__}")
        self.geometry("460x720")
        self.minsize(420, 680)
        self.unit = "C"
        self.weather: Weather | None = None
        self._build()
        self._search("London")

    # ---------- layout ----------
    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        bar.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            bar, placeholder_text="Search city…", height=44, corner_radius=22,
            fg_color=CARD, border_width=0, text_color=TEXT,
            font=ctk.CTkFont(FONT, 14),
        )
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", lambda _e: self._search(self.entry.get()))
        ctk.CTkButton(
            bar, text="Go", width=56, height=44, corner_radius=22,
            fg_color=ACCENT, hover_color="#10b981", font=ctk.CTkFont(FONT, 14, "bold"),
            command=lambda: self._search(self.entry.get()),
        ).grid(row=0, column=1, padx=(8, 0))

        hero = ctk.CTkFrame(self, fg_color=CARD, corner_radius=28)
        hero.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
        hero.grid_columnconfigure(0, weight=1)
        self.city = ctk.CTkLabel(hero, text="", text_color=TEXT,
                                 font=ctk.CTkFont(FONT, 20, "bold"))
        self.city.grid(row=0, column=0, pady=(24, 0))
        self.icon = ctk.CTkLabel(hero, text="", font=ctk.CTkFont("Segoe UI Emoji", 64))
        self.icon.grid(row=1, column=0, pady=(4, 0))
        self.temp = ctk.CTkLabel(hero, text="--°", text_color=TEXT,
                                 font=ctk.CTkFont(FONT, 72, "bold"))
        self.temp.grid(row=2, column=0)
        self.desc = ctk.CTkLabel(hero, text="", text_color=MUTED,
                                 font=ctk.CTkFont(FONT, 16))
        self.desc.grid(row=3, column=0, pady=(0, 20))

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=2, column=0, sticky="ew", padx=24, pady=8)
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1, uniform="s")
        self.stat_feels = self._stat(stats, 0, "Feels like")
        self.stat_hum = self._stat(stats, 1, "Humidity")
        self.stat_wind = self._stat(stats, 2, "Wind")

        ctk.CTkLabel(self, text="5-DAY FORECAST", text_color=MUTED, anchor="w",
                     font=ctk.CTkFont(FONT, 12, "bold")
                     ).grid(row=3, column=0, sticky="ew", padx=30, pady=(12, 0))
        self.forecast = ctk.CTkFrame(self, fg_color=CARD, corner_radius=24)
        self.forecast.grid(row=4, column=0, sticky="ew", padx=24, pady=8)
        self.forecast.grid_columnconfigure(0, weight=1)

        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=5, column=0, sticky="ew", padx=24, pady=(4, 16))
        foot.grid_columnconfigure(0, weight=1)
        self.status = ctk.CTkLabel(foot, text="", text_color=MUTED, anchor="w",
                                   font=ctk.CTkFont(FONT, 12))
        self.status.grid(row=0, column=0, sticky="w")
        self.unit_btn = ctk.CTkSegmentedButton(
            foot, values=["°C", "°F"], command=self._set_unit, fg_color=CARD,
            selected_color=ACCENT, unselected_color=CARD, selected_hover_color=ACCENT,
        )
        self.unit_btn.set("°C")
        self.unit_btn.grid(row=0, column=1)

    def _stat(self, parent, col: int, title: str) -> ctk.CTkLabel:
        box = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=20)
        box.grid(row=0, column=col, sticky="ew", padx=4)
        ctk.CTkLabel(box, text=title, text_color=MUTED,
                     font=ctk.CTkFont(FONT, 11)).pack(pady=(12, 0))
        val = ctk.CTkLabel(box, text="--", text_color=TEXT,
                           font=ctk.CTkFont(FONT, 16, "bold"))
        val.pack(pady=(0, 12))
        return val

    # ---------- behaviour ----------
    def _set_unit(self, value: str) -> None:
        self.unit = value[-1]
        if self.weather:
            self._render(self.weather)

    def _search(self, query: str) -> None:
        self.status.configure(text="Loading…", text_color=MUTED)
        threading.Thread(target=self._worker, args=(query,), daemon=True).start()

    def _worker(self, query: str) -> None:
        try:
            result = get_weather(query)
        except WeatherError as exc:
            self.after(0, lambda: self.status.configure(text=str(exc), text_color="#ff7b8a"))
            return
        self.after(0, lambda: self._render(result))

    def _render(self, w: Weather) -> None:
        self.weather = w
        u = self.unit
        self.city.configure(text=w.place.label)
        self.icon.configure(text=w.icon)
        self.temp.configure(text=format_temp(w.temperature, u))
        self.desc.configure(text=w.description)
        self.stat_feels.configure(text=format_temp(w.feels_like, u))
        self.stat_hum.configure(text=f"{w.humidity}%")
        self.stat_wind.configure(text=f"{round(w.wind_speed)} km/h")
        for child in self.forecast.winfo_children():
            child.destroy()
        for i, d in enumerate(w.days[1:6]):
            row = ctk.CTkFrame(self.forecast, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", padx=18, pady=(12 if i == 0 else 4, 12 if i == 4 else 4))
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=d.weekday, text_color=TEXT, anchor="w", width=60,
                         font=ctk.CTkFont(FONT, 14, "bold")).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(row, text=describe(d.code)[1],
                         font=ctk.CTkFont("Segoe UI Emoji", 20)).grid(row=0, column=1, padx=12)
            ctk.CTkLabel(row, text=f"{format_temp(d.high, u)}  /  {format_temp(d.low, u)}",
                         text_color=MUTED, font=ctk.CTkFont(FONT, 14)
                         ).grid(row=0, column=2, sticky="e")
        self.status.configure(text="Data: Open-Meteo", text_color=MUTED)


def run() -> None:
    App().mainloop()
