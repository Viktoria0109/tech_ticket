
from pathlib import Path
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, JSONResponse
import os
from app.db.base import Base, engine
from app.db.session import get_db
from app.api.v1 import tickets, auth, users
from app import models, schemas
from app.models import user, Ticket, Comment
from app.core.security import get_current_user
from app.core.config import settings


app = FastAPI()


Base.metadata.create_all(bind=engine)



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontent')

app.mount("/static", StaticFiles(directory= os.path.join(FRONTEND_DIR, "static")), name="static")
templates = Jinja2Templates(directory= os.path.join(FRONTEND_DIR, "templates"))

app.include_router(users.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
   
    if request.headers.get("accept") == "application/json":
        return JSONResponse(content={"ok": True})
    
   
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/session-info")
def session_info(current_user: user = Depends(get_current_user)):
    return {
        "message": f"Вы авторизованы как {current_user.username}",
        "session_valid_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }

                                      
@app.post("/tickets", response_model=schemas.TicketBase)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = models.Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@app.get("/tickets", response_model=list[schemas.TicketBase])
def read_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()


@app.get("/tickets/{ticket_id}", response_model=schemas.TicketBase)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted"}
