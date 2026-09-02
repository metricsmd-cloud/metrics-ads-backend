import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

def analyze_ad_performance(ad_metrics):
    if not API_KEY:
        import random
        demo_action = random.choice(["PAUSE", "INCREASE_BUDGET", "KEEP"])
        demo_reason = "Métricas estables. Mantener sin cambios."
        return {"action": demo_action, "reason": f"[MODO DEMO] {demo_reason}"}
    
    prompt = f"""
    Eres un Media Buyer experto. Analiza las métricas de este anuncio de Facebook Ads de hoy:
    - Gasto: ${ad_metrics['spend_today']}
    - Compras: {ad_metrics['purchases']}
    - Costo por Adquisición (CPA): ${ad_metrics['cpa']}
    - Retorno de Inversión (ROAS): {ad_metrics['roas']}
    
    Reglas estrictas de optimización:
    1. Si el ROAS es >= 3.0, la acción debe ser "INCREASE_BUDGET".
    2. Si el ROAS es < 1.0 y el gasto es > $20, la acción debe ser "PAUSE".
    3. En cualquier otro caso, la acción es "KEEP".
    
    Devuelve estrictamente un JSON válido con dos claves: "action" y "reason".
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=payload)
        data = res.json()
        if "error" in data:
            return {"error": f"Detalle Técnico Google: {data['error']['message']}"}
            
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            return json.loads(text[start_idx:end_idx+1])
        return {"action": "KEEP", "reason": "No se pudo parsear el JSON."}
    except Exception as e:
        return {"error": f"Error de conexión: {str(e)}"}


def generate_campaign_structure(tipo_negocio: str, estrategia: str, description: str):
    if not API_KEY:
        import time
        time.sleep(1.5)
        return {
            "technical": {
                "objective": "AUTOMÁTICO",
                "budget": f"Campaña Optimizada para {estrategia}",
                "audience": "Broad o Segmentado según IA"
            },
            "creative": {
                "buyerPersona": "Perfil de cliente dinámico",
                "primaryText": f"Promoción para {tipo_negocio}: {description}",
                "headline": "¡No te lo pierdas!",
                "callToAction": "Más Información",
                "imagePrompt": "Imagen publicitaria"
            }
        }

    prompt = f"""
    Eres un Trafficker Digital Experto y un Copywriter persuasivo. 
    
    INFORMACIÓN DEL CLIENTE:
    - Tipo de Negocio: {tipo_negocio}
    - Estrategia Elegida: {estrategia}
    - Descripción de la Oferta: {description}
    
    TUS TAREAS:
    1. Define el 'Buyer Persona' exacto para este caso.
    2. Redacta el copy ('primaryText') enfocado 100% en el tipo de negocio.
    3. Define el Objetivo Técnico recomendado para Meta Ads.
    4. Sugiere presupuesto/estructura.
    5. Sugiere la Segmentación.
    
    Devuelve estrictamente un JSON válido con esta estructura exacta:
    {{
      "technical": {{
        "objective": "...",
        "budget": "...",
        "audience": "..."
      }},
      "creative": {{
        "buyerPersona": "...",
        "primaryText": "...",
        "headline": "...",
        "callToAction": "...",
        "imagePrompt": "..."
      }}
    }}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=payload)
        data = res.json()
        if "error" in data:
            return {"error": f"Detalle Técnico Google: {data['error']['message']}"}
            
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            return json.loads(text[start_idx:end_idx+1])
        return {"error": "JSON devuelto por Google era inválido."}
    except Exception as e:
        return {"error": f"Error de conexión HTTP: {str(e)}"}
