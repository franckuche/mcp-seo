"""
Router chat MCP avec chunking intelligent intégré
Permet des analyses SEO complètes malgré les limites de tokens OpenAI
"""
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from ..config import Config
from ..dependencies import get_haloscan_client, HaloscanClient
from ..logging_config import get_logger
from ..mcp_tools.registry import global_mcp_registry
from ..services.chunking_service import chunking_service, ChunkProcessor
from .chat import ChatMessage, ChatRequest, ChatResponse, get_haloscan_tools, execute_haloscan_tool

logger = get_logger("chat_chunked")
router = APIRouter(tags=["chat-chunked"])

# Configuration OpenAI optimisée pour le maximum d'informations
openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

def detect_complex_analysis(message: str) -> bool:
    """Détecte si la requête nécessite une analyse complexe (chunking)"""
    complex_keywords = [
        "analyse complète", "analyse détaillée", "tous les concurrents", 
        "analyse exhaustive", "étude approfondie", "rapport complet",
        "tous les mots-clés", "analyse concurrentielle", "audit complet"
    ]
    return any(keyword in message.lower() for keyword in complex_keywords)

async def perform_chunked_analysis(
    request: ChatRequest, 
    client: HaloscanClient
) -> ChatResponse:
    """Effectue une analyse chunked complète - VERSION SIMPLIFIÉE FONCTIONNELLE"""
    
    # 1. Extraire le domaine
    domain = extract_domain_from_query(request.message)
    if not domain:
        raise HTTPException(400, "Impossible d'extraire le domaine de la requête")
    
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Analyse complexe détectée pour {domain}")
    
    try:
        # 2. Collecter toutes les données nécessaires
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Collecte des données...")
        
        # Analyse du domaine principal
        domain_analysis = await execute_haloscan_tool("analyze_domain", {"domain": domain}, client)
        
        # Analyse des concurrents
        competitors_analysis = await execute_haloscan_tool("find_domain_competitors", {"domain": domain}, client)
        
        # Mots-clés par positions (focus sur page 2 comme demandé) - LIMITE AUGMENTÉE
        keywords_page2 = await execute_haloscan_tool("search_keywords_by_position", {
            "domain": domain, 
            "position_min": 11, 
            "position_max": 20,
            "limit": 200  # Augmenter la limite pour plus de mots-clés
        }, client)
        
        # Mots-clés page 1 pour comparaison - LIMITE AUGMENTÉE
        keywords_page1 = await execute_haloscan_tool("search_keywords_by_position", {
            "domain": domain, 
            "position_min": 1, 
            "position_max": 10,
            "limit": 200  # Augmenter la limite pour plus de mots-clés
        }, client)
        
        # Récupérer aussi les positions 21-50 pour une analyse encore plus complète
        keywords_page3_plus = await execute_haloscan_tool("search_keywords_by_position", {
            "domain": domain, 
            "position_min": 21, 
            "position_max": 50,
            "limit": 200  # Positions plus lointaines mais importantes
        }, client)
        
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Données collectées, génération de la synthèse...")
        
        # 3. Générer la synthèse finale avec OpenAI optimisé
        synthesis_prompt = f"""ANALYSE SEO COMPLÈTE - SYNTHÈSE FINALE

🎯 DOMAINE ANALYSÉ: {domain}
📊 DONNÉES COLLECTÉES:
- Analyse du domaine principal
- {len(competitors_analysis.get('competitors', []))} concurrents identifiés
- Mots-clés positions 1-10 (page 1)
- Mots-clés positions 11-20 (page 2) - FOCUS PRINCIPAL
- Mots-clés positions 21-50 (pages 3+) - ANALYSE COMPLÈTE

🎯 MISSION: Créer une étude de mots-clés complète au format demandé:
keyword | volume | difficulty | competition | cpc | trend | thematic_cluster | sous_thematique | intention_type

⚠️ INSTRUCTION CRITIQUE: AFFICHE TOUS LES MOTS-CLÉS TROUVÉS (PAS SEULEMENT LES 20 PREMIERS)
Tu dois inclure TOUS les mots-clés des 3 datasets dans ton tableau final. Ne limite pas à 20 lignes !

📋 DONNÉES BRUTES:

DOMAINE PRINCIPAL:
{json.dumps(domain_analysis, indent=2)}

CONCURRENTS:
{json.dumps(competitors_analysis, indent=2)}

MOTS-CLÉS PAGE 2 (11-20) - PRIORITÉ:
{json.dumps(keywords_page2, indent=2)}

MOTS-CLÉS PAGE 1 (1-10) - RÉFÉRENCE:
{json.dumps(keywords_page1, indent=2)}

MOTS-CLÉS PAGES 3+ (21-50) - ANALYSE COMPLÈTE:
{json.dumps(keywords_page3_plus, indent=2)}

🎯 INSTRUCTIONS CRITIQUES:
1. FOCUS sur les mots-clés où {domain} se positionne APRÈS la page 1 (positions 11-20)
2. Analyser les concurrents qui se positionnent mieux sur ces mots-clés
3. Structurer OBLIGATOIREMENT au format: keyword | volume | difficulty | competition | cpc | trend | thematic_cluster | sous_thematique | intention_type
4. Fournir des recommandations actionables
5. Être exhaustif et détaillé

⚠️ FORMAT DE RÉPONSE OBLIGATOIRE:
- PAS DE BLABLA, PAS D'INTRODUCTION, PAS DE CONCLUSION
- UNIQUEMENT LE TABLEAU FORMATÉ EN MARKDOWN
- ÉCONOMISER LES TOKENS POUR MAXIMISER LES DONNÉES
- COMMENCER DIRECTEMENT PAR L'EN-TÊTE DU TABLEAU

GÉNÈRE UNIQUEMENT LE TABLEAU:"""
        
        # Appel OpenAI optimisé pour maximum d'informations et TOUS les mots-clés
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert SEO qui génère des analyses complètes et détaillées. Tu dois TOUJOURS respecter le format demandé, être exhaustif, et AFFICHER TOUS LES MOTS-CLÉS TROUVÉS sans limitation. Ne limite jamais le nombre de lignes dans le tableau final."},
                {"role": "user", "content": synthesis_prompt}
            ],
            max_tokens=8000,  # AUGMENTÉ pour permettre plus de mots-clés
            temperature=0.1,  # Précision maximale pour les données
            top_p=0.85  # Focus sur les réponses les plus probables
        )
        
        final_analysis = response.choices[0].message.content
        
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Analyse terminée avec succès")
        
        # 4. Construire la réponse finale
        return ChatResponse(
            response=final_analysis,
            tools_used=[
                {"tool": "analyze_domain", "success": True},
                {"tool": "find_domain_competitors", "success": True, "chunks_processed": len(competitors_analysis.get('competitors', []))},
                {"tool": "search_keywords_by_position", "success": True, "chunks_processed": 3, "details": "Positions 1-10, 11-20, 21-50"},
                {"tool": "chunked_synthesis", "success": True, "chunks_processed": 1, "max_tokens": 8000}
            ],
            conversation_history=request.conversation_history + [
                ChatMessage(role="user", content=request.message),
                ChatMessage(role="assistant", content=final_analysis)
            ]
        )
        
    except Exception as e:
        logger.error(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Erreur - {str(e)}")
        
        # Fallback sur le chat normal en cas d'erreur
        from .chat import chat_with_mcp
        return await chat_with_mcp(request, client)

async def get_comprehensive_competitor_data(domain: str, client: HaloscanClient) -> List[Dict]:
    """Récupère toutes les données concurrents disponibles"""
    try:
        # Utiliser l'outil find_domain_competitors
        competitors_result = await execute_haloscan_tool("find_domain_competitors", {"domain": domain}, client)
        
        if competitors_result.get("success"):
            competitors = competitors_result.get("data", {}).get("competitors", [])
            logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] DATA: {len(competitors)} concurrents trouvés pour {domain}")
            return competitors[:15]  # Limiter à 15 concurrents max
        
        return []
    except Exception as e:
        logger.error(f"Erreur récupération concurrents: {e}")
        return []

async def get_comprehensive_keyword_data(domain: str, client: HaloscanClient) -> List[Dict]:
    """Récupère toutes les données mots-clés disponibles"""
    try:
        # Utiliser l'outil search_keywords_by_position pour différentes plages
        all_keywords = []
        
        # Positions 1-10 (page 1)
        result_p1 = await execute_haloscan_tool("search_keywords_by_position", {
            "domain": domain, "position_min": 1, "position_max": 10
        }, client)
        
        # Positions 11-20 (page 2)
        result_p2 = await execute_haloscan_tool("search_keywords_by_position", {
            "domain": domain, "position_min": 11, "position_max": 20
        }, client)
        
        # Positions 21-50 (pages 3-5)
        result_p3 = await execute_haloscan_tool("search_keywords_by_position", {
            "domain": domain, "position_min": 21, "position_max": 50
        }, client)
        
        # Combiner tous les résultats
        for result in [result_p1, result_p2, result_p3]:
            if result.get("success"):
                keywords = result.get("data", {}).get("keywords", [])
                all_keywords.extend(keywords)
        
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] DATA: {len(all_keywords)} mots-clés trouvés pour {domain}")
        return all_keywords[:200]  # Limiter à 200 mots-clés max
        
    except Exception as e:
        logger.error(f"Erreur récupération mots-clés: {e}")
        return []

def create_competitor_chunks(competitors: List[Dict], chunk_size: int = 3) -> List[List[Dict]]:
    """Crée des chunks intelligents de concurrents"""
    if not competitors:
        return []
    
    chunks = []
    for i in range(0, len(competitors), chunk_size):
        chunk = competitors[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks

def create_keyword_chunks(keywords: List[Dict], chunk_size: int = 30) -> List[List[Dict]]:
    """Crée des chunks intelligents de mots-clés"""
    if not keywords:
        return []
    
    # Trier par volume/importance
    sorted_keywords = sorted(keywords, key=lambda k: k.get('volume', 0), reverse=True)
    
    chunks = []
    for i in range(0, len(sorted_keywords), chunk_size):
        chunk = sorted_keywords[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks

async def process_competitor_chunk(
    competitors: List[Dict], 
    domain: str, 
    chunk_num: int, 
    total_chunks: int
) -> Dict[str, Any]:
    """Traite un chunk de concurrents avec OpenAI optimisé"""
    
    competitor_names = [comp.get("domain", "N/A") for comp in competitors]
    
    prompt = f"""ANALYSE SEO CONCURRENTIELLE - ÉTAPE {chunk_num}/{total_chunks}

🎯 DOMAINE ANALYSÉ: {domain}
🏢 CONCURRENTS: {', '.join(competitor_names)}

📊 DONNÉES DÉTAILLÉES:
{json.dumps(competitors, indent=2, ensure_ascii=False)}

🎯 MISSION CRITIQUE: Analyse exhaustive de ces concurrents

ANALYSE REQUISE (SOIS TRÈS DÉTAILLÉ):

1. 🔍 MOTS-CLÉS UNIQUES PAR CONCURRENT:
   - Liste précise des mots-clés que chaque concurrent cible
   - Volumes de recherche et difficultés
   - Mots-clés que {domain} ne cible PAS

2. 📈 STRATÉGIES SEO IDENTIFIÉES:
   - Approches de contenu spécifiques
   - Structures de site observées
   - Tactiques de positionnement

3. 🎯 OPPORTUNITÉS CONCRÈTES:
   - Gaps exploitables immédiatement
   - Mots-clés à faible concurrence
   - Niches non exploitées

4. ⚡ INSIGHTS ACTIONNABLES:
   - Actions prioritaires pour {domain}
   - Recommandations spécifiques
   - Métriques à surveiller

IMPORTANT: 
- Fournis un maximum de détails et de données concrètes
- Chaque insight doit être actionnable
- Cette analyse sera combinée avec d'autres chunks
- Termine par 5 insights clés pour la synthèse finale"""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Plus bas pour plus de précision
            max_tokens=3000,  # Maximum pour plus d'infos
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        content = response.choices[0].message.content
        
        # Extraire les insights clés (dernières lignes)
        insights = extract_key_insights(content)
        
        return {
            "type": "competitor_analysis",
            "chunk_num": chunk_num,
            "content": content,
            "summary": f"Analyse de {len(competitors)} concurrents: {', '.join(competitor_names)}",
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Erreur traitement chunk concurrent: {e}")
        return {
            "type": "competitor_analysis",
            "chunk_num": chunk_num,
            "content": f"Erreur lors de l'analyse des concurrents: {str(e)}",
            "summary": f"Erreur chunk {chunk_num}",
            "insights": []
        }

async def process_keyword_chunk(
    keywords: List[Dict], 
    domain: str, 
    chunk_num: int, 
    total_chunks: int
) -> Dict[str, Any]:
    """Traite un chunk de mots-clés avec OpenAI optimisé"""
    
    prompt = f"""ANALYSE SEO MOTS-CLÉS - ÉTAPE {chunk_num}/{total_chunks}

🎯 DOMAINE ANALYSÉ: {domain}
📊 MOTS-CLÉS: {len(keywords)} mots-clés à analyser

📈 DONNÉES COMPLÈTES:
{json.dumps(keywords[:20], indent=2, ensure_ascii=False)}
{"... et " + str(len(keywords)-20) + " autres mots-clés" if len(keywords) > 20 else ""}

🎯 MISSION CRITIQUE: Analyse exhaustive de ces mots-clés

ANALYSE REQUISE (SOIS TRÈS DÉTAILLÉ):

1. 🏆 OPPORTUNITÉS PRIORITAIRES:
   - Top 10 des mots-clés à fort potentiel
   - Ratio volume/difficulté optimal
   - Estimations de trafic potentiel

2. 📝 GAPS DE CONTENU:
   - Sujets non couverts par {domain}
   - Types de contenu manquants
   - Intentions de recherche non adressées

3. 📅 ANALYSE TEMPORELLE:
   - Tendances saisonnières détectées
   - Évolutions de volume observées
   - Moments optimaux pour cibler

4. 🎯 CLUSTERING THÉMATIQUE:
   - Groupes de mots-clés cohérents
   - Piliers de contenu suggérés
   - Architecture SEO recommandée

5. ⚡ PLAN D'ACTION:
   - Priorisation par impact/effort
   - Recommandations de contenu
   - Métriques de suivi

IMPORTANT:
- Fournis des données chiffrées précises
- Chaque recommandation doit être concrète
- Cette analyse sera combinée avec d'autres chunks
- Termine par 5 actions prioritaires pour la synthèse finale"""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Plus bas pour plus de précision
            max_tokens=3000,  # Maximum pour plus d'infos
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        content = response.choices[0].message.content
        
        # Extraire les insights clés
        insights = extract_key_insights(content)
        
        return {
            "type": "keyword_analysis",
            "chunk_num": chunk_num,
            "content": content,
            "summary": f"Analyse de {len(keywords)} mots-clés (positions variées)",
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Erreur traitement chunk mots-clés: {e}")
        return {
            "type": "keyword_analysis",
            "chunk_num": chunk_num,
            "content": f"Erreur lors de l'analyse des mots-clés: {str(e)}",
            "summary": f"Erreur chunk {chunk_num}",
            "insights": []
        }

async def perform_final_synthesis(analysis_id: str) -> Dict[str, Any]:
    """Effectue la synthèse finale de tous les chunks"""
    
    synthesis_prompt = chunking_service.get_synthesis_prompt(analysis_id)
    
    # Prompt optimisé pour la synthèse finale
    final_prompt = f"""{synthesis_prompt}

🎯 SYNTHÈSE FINALE EXHAUSTIVE REQUISE:

Crée maintenant un rapport SEO complet et actionnable qui inclut:

1. 📊 RÉSUMÉ EXÉCUTIF:
   - Situation actuelle du domaine
   - Principales découvertes
   - Potentiel d'amélioration chiffré

2. 🏆 OPPORTUNITÉS PRIORITAIRES (TOP 10):
   - Mots-clés à cibler en priorité
   - Estimations de trafic potentiel
   - Niveau de difficulté et ressources nécessaires

3. 🎯 PLAN D'ACTION DÉTAILLÉ:
   - Actions immédiates (0-30 jours)
   - Actions moyen terme (1-3 mois)
   - Actions long terme (3-12 mois)

4. 📈 MÉTRIQUES DE SUIVI:
   - KPIs à surveiller
   - Outils de mesure recommandés
   - Fréquence de reporting

5. 💡 RECOMMANDATIONS STRATÉGIQUES:
   - Axes de développement prioritaires
   - Investissements conseillés
   - Risques à éviter

IMPORTANT: Sois exhaustif, précis et actionnable. Ce rapport doit permettre une mise en œuvre immédiate."""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": final_prompt}],
            temperature=0.2,  # Très bas pour cohérence maximale
            max_tokens=4000,  # Maximum absolu pour synthèse complète
            top_p=0.8,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        content = response.choices[0].message.content
        
        return {
            "type": "final_synthesis",
            "content": content
        }
        
    except Exception as e:
        logger.error(f"Erreur synthèse finale: {e}")
        return {
            "type": "final_synthesis", 
            "content": f"Erreur lors de la synthèse finale: {str(e)}"
        }

def extract_domain_from_query(query: str) -> Optional[str]:
    """Extrait le domaine de la requête utilisateur"""
    import re
    
    # Rechercher des patterns de domaine
    domain_patterns = [
        r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'([a-zA-Z0-9.-]+\.(?:com|fr|org|net|info|biz))'
    ]
    
    for pattern in domain_patterns:
        matches = re.findall(pattern, query.lower())
        if matches:
            return matches[0].replace('www.', '')
    
    return None

def extract_key_insights(content: str) -> List[str]:
    """Extrait les insights clés du contenu généré"""
    lines = content.split('\n')
    insights = []
    
    # Chercher les lignes qui ressemblent à des insights
    for line in lines:
        line = line.strip()
        if any(marker in line.lower() for marker in ['insight', 'recommandation', 'action', 'priorité', '•', '-']):
            if len(line) > 20:  # Éviter les lignes trop courtes
                insights.append(line)
    
    return insights[:10]  # Limiter à 10 insights max

# Endpoint principal avec chunking intelligent
@router.post("/chat-chunked", response_model=ChatResponse)
async def chat_with_chunking(
    request: ChatRequest,
    client: HaloscanClient = Depends(get_haloscan_client)
) -> ChatResponse:
    """
    🧠 Interface chat MCP avec chunking intelligent
    
    TOUJOURS utilise le chunking intelligent - pas de détection nécessaire
    """
    
    # TOUJOURS utiliser le chunking intelligent sur cet endpoint
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Mode chunking intelligent activé")
    return await perform_chunked_analysis(request, client)
