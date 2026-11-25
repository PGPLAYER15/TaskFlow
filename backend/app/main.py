from sys import prefix
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.database import engine, Base, SessionLocal
from app.api.v1 import auth, boards, lists, cards , tag
from app.domain.entities.board import Board
from app.domain.entities.list import List
from app.domain.entities.card import Card
from app.domain.entities.user import User

app = FastAPI(title="Trello Clone API", version="2.0.0")

from app.core.middleware import JWTAuthMiddleware

# Se añade antes que CORS para que CORS quede como capa externa (también cubre los 401)
app.add_middleware(JWTAuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

    # Migración ligera: añade cards.position si la BD ya existía sin esa columna
    from sqlalchemy import inspect, text
    if "position" not in [c["name"] for c in inspect(engine).get_columns("cards")]:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE cards ADD COLUMN position INTEGER NOT NULL DEFAULT 0"))

    # Migración ligera: tags pasa de nombre único global a único por usuario (user_id).
    # SQLite no puede quitar el UNIQUE de una columna, así que se reconstruye la tabla.
    if "user_id" not in [c["name"] for c in inspect(engine).get_columns("tags")]:
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            conn.execute(text("ALTER TABLE tags RENAME TO tags_old"))
            conn.execute(text("DROP INDEX IF EXISTS ix_tags_id"))
        Base.metadata.tables["tags"].create(bind=engine)
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO tags (id, name, color) SELECT id, name, color FROM tags_old"))
            conn.execute(text("DROP TABLE tags_old"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
    
    db = SessionLocal()
    try:
        if not db.query(Board).first():
            demo_board = Board(
                title="Mi Primer Tablero",
                description="Tablero de ejemplo creado automáticamente",
                color="#0079BF"
            )
            db.add(demo_board)
            db.commit()
            db.refresh(demo_board)
            
            lista_todo = List(title="Por Hacer", board_id=demo_board.id)
            lista_progreso = List(title="En Progreso", board_id=demo_board.id)
            lista_hecho = List(title="Hecho", board_id=demo_board.id)
            
            db.add_all([lista_todo, lista_progreso, lista_hecho])
            db.commit()
            
            tarjeta_1 = Card(title="Configurar proyecto", list_id=lista_todo.id)
            tarjeta_2 = Card(title="Diseñar interfaz", list_id=lista_todo.id)
            
            db.add_all([tarjeta_1, tarjeta_2])
            db.commit()
                        
    except Exception as e:
        print(f" Error al crear datos iniciales: {str(e)}")
        db.rollback()
    finally:
        db.close()

# Auth routes
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"]
)

# Board routes
app.include_router(
    boards.router, 
    prefix="/api/boards",
    tags=["boards"]
)

app.include_router(
    lists.router, 
    prefix="/api/boards/{board_id}/lists",
    tags=["lists"]
)

app.include_router(
    cards.router, 
    prefix="/api/boards/{board_id}/lists/{list_id}/cards",
    tags=["cards"]
)

app.include_router(
    tag.router,
    prefix="/api/tags",
    tags=["tags"]
)

@app.get("/")
def read_root():
    return {"message": "API de Trello Clone - Clean Architecture v2.0"}
