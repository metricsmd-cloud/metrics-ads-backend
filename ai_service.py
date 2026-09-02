import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Usaremos un modelo rápido y barato ideal para razonamiento lógico
model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_ad_performance(ad_metrics):
    """
    Pide a Gemini evaluar las métricas de un anuncio.
    Retorna: {"action": "...", "reason": "..."}
    """
    if not API_KEY:
        # Modo Demo si no hay API Key: Devolver acciones aleatorias para ver el UI funcionando
        import random
        demo_action = random.choice(["PAUSE", "INCREASE_BUDGET", "KEEP"])
        demo_reason = (
            "Gasto alto sin retorno. Pausado por protección." if demo_action == "PAUSE" 
            else "ROAS excelente detectado. Escale presupuesto." if demo_action == "INCREASE_BUDGET" 
            else "Métricas estables. Mantener sin cambios."
        )
        return {"action": demo_action, "reason": f"[MODO DEMO SIN API KEY] {demo_reason}"}
    
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
    
    Devuelve estrictamente un JSON válido con dos claves:
    "action": una de las tres acciones permitidas.
    "reason": una explicación muy breve (1 oración) del porqué.
    No incluyas markdown de bloques de código en tu respuesta, solo el objeto JSON puro (ej: {{"action": "PAUSE", "reason": "Gasto alto sin retorno"}}).
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Limpiar markdown de json si Gemini lo agrega
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text)
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return {"action": "KEEP", "reason": f"Error de IA: {str(e)}"}

def generate_campaign_structure(tipo_negocio: str, estrategia: str, description: str):
    """
    Genera la estructura de la campaña adaptándose dinámicamente al tipo de negocio.
    """
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
    - Tipo de Negocio: {tipo_negocio} (ej: ecommerce=tienda online, servicios=B2B, local=restaurante/físico)
    - Estrategia Elegida: {estrategia}
    - Descripción de la Oferta: {description}
    
    TUS TAREAS:
    1. Define el 'Buyer Persona' exacto para este caso.
    2. Redacta el copy ('primaryText') enfocado 100% en el tipo de negocio. Si es local, apela a la cercanía/reservas. Si es ecommerce, apela a envío/compra directa. Si es B2B, apela a autoridad/leads.
    3. Define el Objetivo Técnico recomendado para Meta Ads (ej. CONVERSIONES, MENSAJES, TRAFICO, RECONOCIMIENTO).
    4. Sugiere presupuesto/estructura (ej. CBO Advantage+, o ABO Geográfico).
    5. Sugiere la Segmentación (Broad, Intereses, Lookalike, Radio Geográfico).
    
    Devuelve estrictamente un JSON válido con esta estructura exacta:
    {{
      "technical": {{
        "objective": "Objetivo sugerido",
        "budget": "Presupuesto y estructura",
        "audience": "Segmentación sugerida"
      }},
      "creative": {{
        "buyerPersona": "Descripción del cliente ideal en 2 líneas",
        "primaryText": "Texto persuasivo del anuncio (con emojis y espacios)",
        "headline": "Título corto y llamativo",
        "callToAction": "Boton sugerido (ej. Comprar, Enviar Mensaje, Más info)",
        "imagePrompt": "Prompt en inglés para generar la imagen en Dalle/Midjourney"
      }}
    }}
    NO agregues comillas invertidas (```) ni texto adicional fuera del JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Parseo robusto: buscar el primer '{' y el último '}'
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            clean_json = text[start_idx:end_idx+1]
            return json.loads(clean_json)
        else:
            raise ValueError("No se encontró JSON válido en la respuesta de Gemini")
    except Exception as e:
        print(f"Error generando campaña: {e}")
        return {"error": "No se pudo generar la campaña"}
