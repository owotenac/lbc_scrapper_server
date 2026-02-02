from ollama import chat
from ollama import ChatResponse
from flask import request, jsonify
import re

system_prompt = """Tu es un analyste immobilier spécialisé en investissement locatif.
Ta mission est d’analyser une annonce immobilière brute en texte 
et d’en extraire des informations STRICTEMENT FACTUELLES.
Règles impératives :
- N’invente jamais de chiffres
- Ne fais aucune estimation implicite 
- Ne complète jamais une information absente 
- Si une donnée n’est pas explicitement mentionnée, indique 'NON PRÉCISÉ'
- Ignore les phrases marketing non chiffrées ('bon rendement', 'fort potentiel', etc.) 
- Distingue clairement les données certaines, absentes ou ambiguës 
- Detail les éventuels travaux à réaliser
- Fournis un résumé des loyers potentiels 
- Si tu trouve les Revenus annuels, utilise les pour calculer le total des loyers mensuels en divisant par 12 et fournis le sous la forme : TOTAL_LOYERS_MENSUELS_EUR: <montant en euros>
- fournis le total des loyers mensuels sous la forme : TOTAL_LOYERS_MENSUELS_EUR: <montant en euros sans virgule>
- La réponse doit être exclusivement en Markdown.
- Aucun texte hors Markdown n’est autorisé.
INTERDICTIONS FORMELLES :
- Il est STRICTEMENT INTERDIT d'utiliser des blocs de code
- Ne pas entourer la réponse par ``` ou ```markdown
- Toute sortie contenant ``` est invalide
- Le premier caractère de la réponse doit être '#'

"""


def getDescription(text: str) -> str:
    response: ChatResponse = chat(model='qwen2.5', 
        messages=[
            {
            'role': 'system',
            'content': system_prompt
            },
        {
            'role': 'user',
            'content': f"""Voici l\'annonce à analyser:\n\n{text}""",
        },
    ],
    options={
            "temperature": 0.0
        }

    )
    return response['message']['content']


def ai_analysis():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing 'data' in request body"}), 400
    
    if 'description' not in data:
        return jsonify({"error": "Missing 'description' in request body"}), 400
    description = data['description']
    
    if 'features' not in data:
        return jsonify({"error": "Missing 'features' in request body"}), 400
    features = data['features']

    response = ai_analysisWithData(description, features)
    return jsonify({
        "analysis": response['analysis'], 
         "financials": response['financials']
         })


def ai_analysisWithData(description: str, features: dict):
    
    #RUN AI analysis
    analysis = getDescription(description)

    #get computer rent_value
    total_rent = 1500.0 #default value
    default_rent = True
    regex = "TOTAL_LOYERS_MENSUELS_EUR:\s*([\d\s]+)"
    match = re.search(regex, analysis)
    if match:
        t = match.group(1).replace(' ','').replace('\xa0', '').strip()
        if len(t) != 0:
            total_rent = float(t)
            default_rent = False
            print(f"Extracted total monthly rent: {total_rent} €")

    group_financial = []
    financial = {}
    financial['total_monthly_rent'] = total_rent
    financial['default_monthly_rent'] = default_rent

    #we need to find the exact price
    for f in features:
        if f.get('key') == 'price_euros':
            financial['price'] = f.get('value_label', 0)
            break
    
    price = float(financial['price'] )
    #extrat financials with price
    financials_result = computeFinancialsWithPrice(financial)
    group_financial.append(financials_result)    
    #extract financiales with 10% nego
    financial_nego = {
        'total_monthly_rent': total_rent,
        'price': price - (price * 0.1),
        'default_monthly_rent' : default_rent
    }
    financials_result = computeFinancialsWithPrice(financial_nego)
    group_financial.append(financials_result)   

    return {
        "analysis": analysis, 
         "financials": group_financial
         }


def computeFinancials(features: dict, financial: dict):

    for f in features:
        #we need to find the exact price
        if f.get('key') == 'price_euros':
            financial['price'] = f.get('value_label', 0)
        if f.get('key') == 'estimated_notary_fees':
            financial['notary_fees'] = float(f.get('value_label', '0').replace('€', '').replace(',', '').strip())
        if f.get('key') == 'estimated_total_property_price':
            financial['total_price'] = float(f.get('value_label', '0').replace('€', '').replace(',', '').strip())


    return computeFinancialsWithPrice(financial)

def computeFinancialsWithPrice(financial: dict):
    price = float(financial['price'] )
    if not financial.get('notary_fees'): financial['notary_fees']= price * 0.08
    if not financial.get('total_price'): financial['total_price'] = price + financial['notary_fees']
    financial['mensualite'] = getEstimatedMensualite(financial['total_price'])
    financial['total_yearly_rent'] = financial['total_monthly_rent'] * 12
    financial['annual_charge'] = 2000
    financial['raw_rentability'] = financial['total_yearly_rent'] / financial['price'] * 100
    financial['net_rentability'] = (financial['total_yearly_rent'] - financial['annual_charge']) / financial['price'] * 100
    financial['annual_cash_flow'] = financial['total_yearly_rent'] - financial['annual_charge'] - ( financial['mensualite'] * 12)
    financial['monthly_cash_flow'] = financial['annual_cash_flow'] / 12

    return financial


def getEstimatedMensualite(amount : int, taux_annuel : float = 3.5, duree_annees : int = 25) -> float:
    taux_mensuel = taux_annuel / 100 / 12
    nombre_paiements = duree_annees * 12
    mensualite = amount * (taux_mensuel * (1 + taux_mensuel) ** nombre_paiements) / ((1 + taux_mensuel) ** nombre_paiements - 1)
    return mensualite
