import os
import sys
import uvicorn
from backend import app

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        os.system("streamlit run dashboard.py")
    else:
        uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True, workers=1)
