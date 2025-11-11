from fastapi import FastAPI
from app.database import init_session
from app.middleware.cors import add_cors_middleware
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.moods import router as moods_router
from app.routes.journals import router as journals_router
from app.routes.resources import router as resources_router

init_session()

app = FastAPI()

# Add CORS middleware
add_cors_middleware(app)

# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(moods_router)
app.include_router(journals_router)
app.include_router(resources_router)