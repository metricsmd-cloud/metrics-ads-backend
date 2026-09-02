import random

def get_mock_campaign_metrics():
    """
    Simula la lectura de métricas de Meta Graph API.
    Retorna una lista de anuncios con sus métricas clave.
    """
    ads = []
    
    for i in range(1, 6):
        spend = round(random.uniform(10.0, 150.0), 2)
        purchases = random.randint(0, 10)
        cpa = round(spend / purchases, 2) if purchases > 0 else spend
        revenue = purchases * random.uniform(20.0, 50.0)
        roas = round(revenue / spend, 2) if spend > 0 else 0
        
        ad = {
            "campaign_id": f"camp_{random.randint(100, 999)}",
            "ad_id": f"ad_{1000 + i}",
            "ad_name": f"Creativo de Prueba {i}",
            "status": "ACTIVE",
            "spend_today": spend,
            "purchases": purchases,
            "cpa": cpa,
            "roas": roas,
            "clicks": random.randint(10, 500)
        }
        ads.append(ad)
        
    return ads
