
- **Python deps go in `.venv` + `documentation/requirements.txt`, never global.** Create/use `.venv` (`python -m venv .venv`, install via `.venv/Scripts/python -m pip install -r documentation/requirements.txt`) and record packages in `documentation/requirements.txt`. Never `pip install` into the system Python.
- **Check for an existing file before creating one.** I created a root `requirements.txt` while `docs/requirements.txt` already existed (visible in `git status`). Search the repo (`**/requirements*.txt`, etc.) before adding config/dependency files.
