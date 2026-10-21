"""Headless GUI smoke test: open the real window briefly, then close it.

Run under a virtual display, e.g.  xvfb-run -a python tests/smoke_gui.py
"""
from skyline.ui import App

app = App()
app.after(1500, app.destroy)
app.mainloop()
print("GUI started OK")
