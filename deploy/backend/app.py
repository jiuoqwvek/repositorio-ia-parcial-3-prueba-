# Placeholder backend entrypoint inside deploy/ to match course layout.
# The real backend code is located at ../backend, this file simply imports it.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app import app as application  # type: ignore

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(application, host='0.0.0.0', port=8000)
