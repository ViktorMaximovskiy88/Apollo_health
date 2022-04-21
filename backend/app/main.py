from pathlib import Path
import sys
import uvicorn

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
