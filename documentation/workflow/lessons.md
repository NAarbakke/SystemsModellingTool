
- **Python deps go in `.venv` + `requirements.txt`, never global.** Create/use `.venv` (`python -m venv .venv`, install via `.venv/Scripts/python -m pip install -r requirements.txt`) and record pinned top-level packages in `requirements.txt`. Never `pip install` into the system Python.
