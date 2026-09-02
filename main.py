import contextlib
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from mock_metrics import get_mock_campaign_metrics
from ai_service import analyze_ad_performance

models.Base.metadata.create_all(bind=engine)

def run_ai_analysis():
    print("Ejecutando ciclo de análisis con IA...")
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        metrics = get_mock_campaign_metrics()
        for ad_data in metrics:
            decision = analyze_ad_performance(ad_data)
            
            # Solo guardamos si la IA decide hacer una optimización
            if decision.get("action") in ["PAUSE", "INCREASE_BUDGET"]:
                new_suggestion = models.AdSuggestion(
                    campaign_id=ad_data["campaign_id"],
                    ad_id=ad_data["ad_id"],
                    suggested_action=decision["action"],
                    reason=decision.get("reason", "")
                )
                db.add(new_suggestion)
        db.commit()
        print("Ciclo de análisis finalizado. Sugerencias nuevas guardadas (si las hubo).")
    except Exception as e:
        print(f"Error en el ciclo de análisis: {e}")
    finally:
        db.close()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar el Cron Job para correr en segundo plano
    scheduler = BackgroundScheduler()
    # Configurado para correr cada 1 minuto en ambiente de desarrollo
    scheduler.add_job(run_ai_analysis, 'interval', minutes=1)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="Metrics Ads API",
    description="Backend for Meta Ads Automation (Hybrid System)",
    version="1.0.0",
    lifespan=lifespan
)

# Habilitar CORS para conectar con Next.js (abierto para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Metrics Ads API is running."}

@app.get("/api/suggestions")
def get_suggestions(db: Session = Depends(get_db)):
    suggestions = db.query(models.AdSuggestion).filter(models.AdSuggestion.status == "PENDING").all()
    return {"data": suggestions}

@app.post("/api/suggestions/{suggestion_id}/approve")
def approve_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    suggestion = db.query(models.AdSuggestion).filter(models.AdSuggestion.id == suggestion_id).first()
    if suggestion:
        suggestion.status = "APPROVED"
        db.commit()
        return {"status": "success", "message": "Acción aprobada"}
    return {"status": "error", "message": "Sugerencia no encontrada"}

@app.get("/auth/facebook")
def facebook_login():
    return {"message": "Redirecting to Facebook OAuth..."}

@app.get("/auth/facebook/callback")
def facebook_callback(code: str = None):
    if code:
        return {"status": "success", "message": "Authenticated with Meta successfully."}
    return {"status": "error", "message": "No code provided by Meta."}

class CampaignRequest(BaseModel):
    tipo_negocio: str
    estrategia: str
    descripcion: str

@app.post("/api/campaigns/generate")
def generate_campaign(req: CampaignRequest):
    import ai_service
    result = ai_service.generate_campaign_structure(req.tipo_negocio, req.estrategia, req.descripcion)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

class InjectRequest(BaseModel):
    campaign_data: dict

@app.post("/api/campaigns/inject")
def inject_campaign(req: InjectRequest):
    import meta_api
    result = meta_api.inject_campaign_draft(req.campaign_data)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
