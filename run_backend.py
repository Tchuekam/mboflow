"""
Mboa Finance AI — Application Server Runner.
Launches FastAPI and mounts the simulated Cameroon financial portal.
"""

import uvicorn
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("=" * 70)
    print("  Starting Mboa Finance AI Backend Service")
    print("  Interactive Banking Portal: http://127.0.0.1:8000/bank")
    print("  Interactive OpenAPI Docs:   http://127.0.0.1:8000/docs")
    print("  WebSocket Voice Stream:     ws://127.0.0.1:8000/api/v1/ws/voice")
    print("=" * 70)
    uvicorn.run(
        "apps.backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

