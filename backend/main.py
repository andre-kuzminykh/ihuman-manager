"""
main — uvicorn entrypoint бэкенд-сервиса.
"""

from core import app  # noqa: F401 — экспортируется для uvicorn main:app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
