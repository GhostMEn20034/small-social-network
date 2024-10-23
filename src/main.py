from .core.app_factory import create_app
from .core.database import create_database

app = create_app()

@app.on_event('startup')
async def create_all_db_metadata():
    await create_database()
