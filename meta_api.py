import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv('META_APP_ID')
APP_SECRET = os.getenv('META_APP_SECRET')
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

def init_meta_api():
    if ACCESS_TOKEN and APP_ID and APP_SECRET:
        FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)
        return True
    return False

def inject_campaign_draft(ai_campaign_data: dict, business_name: str = "Campaña Generada por IA"):
    """
    Inyecta la campaña sugerida a Facebook en modo PAUSADO.
    Si faltan credenciales, simula la inyección (Modo Seguro).
    """
    if not init_meta_api():
        print("⚠️ Credenciales de Meta no detectadas. Entrando en Modo Simulación.")
        return {
            "status": "simulated", 
            "message": "Campaña inyectada con éxito (Simulación). Para una inyección real, configura tu archivo .env con las llaves de Meta."
        }
    
    try:
        account = AdAccount(AD_ACCOUNT_ID)
        
        # 1. Creamos la campaña en Facebook
        campaign = account.create_campaign(
            fields=[],
            params={
                'name': f'{business_name}',
                # Simplificado: En prod se mapearía exactamente al tipo de objetivo
                'objective': 'OUTCOME_TRAFFIC', 
                'status': Campaign.Status.paused,
                'special_ad_categories': [],
            }
        )
        campaign_id = campaign.get('id')
        print(f"✅ Campaña {campaign_id} inyectada en estado PAUSADO.")
        
        return {
            "status": "success", 
            "message": f"Campaña inyectada con éxito a Meta Ads. ID: {campaign_id}",
            "campaign_id": campaign_id
        }
    except Exception as e:
        print(f"❌ Error API Meta: {str(e)}")
        return {"status": "error", "message": f"Error al enviar a Facebook: {str(e)}"}
