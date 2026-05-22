import uvicorn
from app.application.api.main import app


def main():
    uvicorn.run("app.application.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
