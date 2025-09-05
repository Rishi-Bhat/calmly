from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change to your frontend domain(s) in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )