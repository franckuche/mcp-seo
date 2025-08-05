"""
Router pour l'interface chat MCP avec intégration OpenAI + Haloscan
"""
import json
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

logger = get_logger("chat")
router = APIRouter(tags=["chat"])

# Configuration OpenAI
openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

class ChatMessage(BaseModel):
    """Modèle pour un message de chat"""
    role: str = Field(..., description="Rôle du message: user, assistant, system")
    content: str = Field(..., description="Contenu du message")

class ChatRequest(BaseModel):
    """Modèle pour une requête de chat"""
    message: str = Field(..., description="Message de l'utilisateur")
    conversation_history: List[ChatMessage] = Field(default=[], description="Historique de conversation")

class ChatResponse(BaseModel):
    """Modèle pour une réponse de chat"""
    response: str = Field(..., description="Réponse de l'assistant")
    tools_used: List[Dict[str, Any]] = Field(default=[], description="Outils utilisés")
    conversation_history: List[ChatMessage] = Field(..., description="Historique mis à jour")

# Initialisation du registre MCP modulaire
def analyze_message_intent(message: str) -> List[str]:
    """Analyse le message utilisateur pour déterminer quels outils sont nécessaires"""
    message_lower = message.lower()
    needed_tools = []
    
    # Mots-clés et analyse de mots-clés
    if any(keyword in message_lower for keyword in ['mot-clé', 'keyword', 'analyse', 'recherche mot', 'seo']):
        needed_tools.extend(['analyze_keyword', 'find_similar_keywords', 'keywords_overview'])
    
    # Domaines et concurrents
    if any(keyword in message_lower for keyword in ['domaine', 'domain', 'concurrent', 'competitor', 'site']):
        needed_tools.extend(['analyze_domain', 'domains_overview', 'find_domain_competitors'])
    
    # Positions et classements
    if any(keyword in message_lower for keyword in ['position', 'classement', 'page 2', 'top 10', 'serp']):
        needed_tools.extend(['search_keywords_by_position', 'domains_positions'])
    
    # Analyse concurrentielle avancée
    if any(keyword in message_lower for keyword in ['différence', 'écart', 'comparaison', 'vs']):
        needed_tools.extend(['domains_competitors_keywords_diff'])
    
    # Crédits
    if any(keyword in message_lower for keyword in ['crédit', 'credit', 'solde', 'compte']):
        needed_tools.append('get_user_credits')
    
    # Historique et tendances
    if any(keyword in message_lower for keyword in ['historique', 'évolution', 'tendance', 'temps']):
        needed_tools.extend(['domains_history_positions', 'domains_visibility_trends'])
    
    # Backlinks et GMB
    if any(keyword in message_lower for keyword in ['backlink', 'lien', 'gmb', 'google my business']):
        needed_tools.extend(['domains_gmb_backlinks'])
    
    # Toujours inclure les outils de base
    base_tools = ['get_user_credits']
    needed_tools.extend(base_tools)
    
    # Supprimer les doublons
    return list(set(needed_tools))

def get_haloscan_tools(client: HaloscanClient, message: str = "") -> List[Dict[str, Any]]:
    """Récupère dynamiquement les outils Haloscan pertinents selon le message"""
    # Enregistrer les outils Haloscan si pas déjà fait
    if "haloscan" not in global_mcp_registry.registries:
        global_mcp_registry.register_haloscan_tools(client)
    
    # Analyser le message pour déterminer les outils nécessaires
    needed_tool_names = analyze_message_intent(message)
    
    # Récupérer toutes les définitions et filtrer selon les besoins
    all_tools = global_mcp_registry.get_all_tool_definitions()
    filtered_tools = []
    
    for tool in all_tools:
        tool_name = tool.get("function", {}).get("name", "")
        if tool_name in needed_tool_names:
            filtered_tools.append(tool)
    
    logger.info(f"🎯 Outils sélectionnés pour le message: {len(filtered_tools)} sur {len(all_tools)} disponibles")
    logger.info(f"📋 Outils: {[tool.get('function', {}).get('name', '') for tool in filtered_tools]}")
    
    return filtered_tools

async def execute_haloscan_tool(tool_name: str, arguments: Dict[str, Any], client: HaloscanClient) -> Dict[str, Any]:
    """Exécute un outil Haloscan via le registre modulaire"""
    logger.info(f"🔧 DÉBUT Exécution de l'outil modulaire: {tool_name}")
    logger.info(f"📝 Arguments reçus: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
    
    # Enregistrer les outils Haloscan si pas déjà fait
    if "haloscan" not in global_mcp_registry.registries:
        logger.info(f"🔄 Initialisation du registre Haloscan...")
        global_mcp_registry.register_haloscan_tools(client)
        logger.info(f"✅ Registre Haloscan initialisé avec {len(global_mcp_registry.list_all_tools())} outils")
    
    # Exécuter l'outil via le registre modulaire
    return await global_mcp_registry.execute_tool(tool_name, arguments)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_mcp(
    request: ChatRequest,
    client: HaloscanClient = Depends(get_haloscan_client)
) -> ChatResponse:
    """
    🤖 Interface chat MCP : Conversation avec OpenAI + outils Haloscan
    
    L'assistant peut automatiquement utiliser les outils Haloscan selon le contexte :
    - Analyse de mots-clés
    - Analyse de domaines
    - Recherche de concurrents
    - Recherche avancée par position
    - Et plus encore !
    """
    # Log simplifié - Format minimal et clean
    query_short = request.message[:50] + "..." if len(request.message) > 50 else request.message
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHAT: Nouvelle requête → \"{query_short}\"")
    
    try:
        # Construire l'historique de conversation
        messages = []
        
        # Message système pour définir le comportement de l'assistant
        system_message = {
            "role": "system",
            "content": """Tu es un assistant SEO expert qui utilise OBLIGATOIREMENT les outils Haloscan pour répondre aux questions.

Tu as accès aux outils suivants :
- analyze_keyword : Analyse complète d'un mot-clé (volume, difficulté, SERP, etc.)
- find_similar_keywords : Trouve des mots-clés similaires et suggestions
- analyze_domain : Analyse d'un domaine (trafic, autorité, mots-clés)
- find_domain_competitors : Trouve les concurrents d'un domaine
- search_keywords_by_position : Recherche avancée par plage de positions (ESSENTIEL pour page 2 = positions 11-20)
- get_user_credits : Vérifie les crédits disponibles

RÈGLES IMPORTANTES :
1. Tu DOIS utiliser les outils appropriés pour chaque demande
2. Pour "page 2" ou "positions 11-20", utilise OBLIGATOIREMENT search_keywords_by_position avec position_min=11, position_max=20
3. Pour "page 1" ou "top 10", utilise search_keywords_by_position avec position_min=1, position_max=10
4. Si l'utilisateur demande une analyse de domaine ET des positions spécifiques, utilise PLUSIEURS outils en séquence
5. IMPORTANT: Quand tu utilises des outils, tu reçois leurs résultats. Tu DOIS analyser et utiliser ces résultats dans ta réponse.
6. Ne dis JAMAIS que tu ne peux pas accéder aux outils - si tu les appelles, tu as accès à leurs résultats.
7. Explique toujours pourquoi tu utilises chaque outil et interprète les résultats obtenus.

Ne réponds JAMAIS sans avoir utilisé les outils appropriés et analysé leurs résultats."""
        }
        messages.append(system_message)
        
        # Ajouter l'historique de conversation
        for msg in request.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Ajouter le nouveau message utilisateur
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Première requête à OpenAI avec les outils disponibles
        logger.info("🤖 Envoi de la requête à OpenAI avec outils MCP")
        
        # Forcer l'utilisation d'outils pour certaines requêtes
        tool_choice = "auto"
        if any(keyword in request.message.lower() for keyword in ["page 2", "position", "11-20", "positions 11"]):
            # Forcer l'utilisation d'outils pour les requêtes de position
            tool_choice = "required"
        
        # Récupérer les outils dynamiquement depuis le registre modulaire
        haloscan_tools = get_haloscan_tools(client, request.message)
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] TOOLS: Sélection → {len(haloscan_tools)}/32 outils")
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=haloscan_tools,
            tool_choice=tool_choice,
            temperature=0.7,
            max_tokens=1500  # Réduit pour laisser plus de place au contexte
        )
        
        assistant_message = response.choices[0].message
        tools_used = []
        
        # Traiter les appels d'outils si nécessaire
        if assistant_message.tool_calls:
            # Log simplifié des outils utilisés
            tool_names = [tc.function.name for tc in assistant_message.tool_calls]
            logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] TOOLS: Exécution → {', '.join(tool_names)}")
            
            # Ajouter le message de l'assistant avec les tool_calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in assistant_message.tool_calls
                ]
            })
            
            # Exécuter chaque outil
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Exécuter l'outil Haloscan
                tool_result = await execute_haloscan_tool(function_name, function_args, client)
                tools_used.append(tool_result)
                
                # Log simplifié du résultat
                status = "✅" if tool_result.get('success', False) else "❌"
                result_info = ""
                if tool_result.get('success'):
                    data = tool_result.get('data', {})
                    if isinstance(data, dict):
                        if 'keywords_found' in data:
                            result_info = f" {data['keywords_found']} résultats"
                        elif 'competitors' in data:
                            result_info = f" {len(data.get('competitors', []))} concurrents"
                        elif 'total_keywords' in data:
                            result_info = f" {data['total_keywords']} mots-clés"
                logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] API: {function_name} → {status}{result_info}")
                
                # Ajouter le résultat de l'outil aux messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # Vérifier si d'autres outils sont nécessaires
            needs_more_tools = False
            if any(keyword in request.message.lower() for keyword in ["page 2", "positions 11-20", "business centric"]):
                # Vérifier si search_keywords_by_position a été utilisé
                position_tool_used = any(tool["tool"] == "search_keywords_by_position" for tool in tools_used)
                if not position_tool_used:
                    logger.info("🎯 Requête de position détectée mais outil position non utilisé - Ajout d'un message de guidage")
                    
                    # Ajouter un message pour guider l'assistant
                    guidance_message = {
                        "role": "user",
                        "content": "Maintenant, utilise l'outil search_keywords_by_position pour trouver les mots-clés en page 2 (positions 11-20) pour ce domaine."
                    }
                    messages.append(guidance_message)
                    
                    # Nouvelle requête avec guidage
                    guided_response = await openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        tools=haloscan_tools,
                        tool_choice="required",
                        temperature=0.7,
                        max_tokens=2000
                    )
                    
                    # Traiter les nouveaux outils si nécessaire
                    if guided_response.choices[0].message.tool_calls:
                        logger.info(f"🔧 L'assistant utilise maintenant {len(guided_response.choices[0].message.tool_calls)} outil(s) supplémentaire(s)")
                        
                        # Ajouter le message de l'assistant avec les nouveaux tool_calls
                        messages.append({
                            "role": "assistant",
                            "content": guided_response.choices[0].message.content,
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": tool_call.type,
                                    "function": {
                                        "name": tool_call.function.name,
                                        "arguments": tool_call.function.arguments
                                    }
                                }
                                for tool_call in guided_response.choices[0].message.tool_calls
                            ]
                        })
                        
                        # Exécuter les nouveaux outils
                        for tool_call in guided_response.choices[0].message.tool_calls:
                            function_name = tool_call.function.name
                            function_args = json.loads(tool_call.function.arguments)
                            
                            logger.info(f"🔧 Exécution supplémentaire de {function_name} avec {function_args}")
                            
                            # Exécuter l'outil Haloscan
                            tool_result = await execute_haloscan_tool(function_name, function_args, client)
                            tools_used.append(tool_result)
                            
                            # Ajouter le résultat de l'outil aux messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(tool_result, ensure_ascii=False)
                            })
            
            # Deuxième requête à OpenAI avec les résultats des outils
            
            final_response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            final_content = final_response.choices[0].message.content
        else:
            final_content = assistant_message.content
        
        # Construire l'historique mis à jour
        updated_history = []
        for msg in request.conversation_history:
            updated_history.append(msg)
        
        # Ajouter le message utilisateur
        updated_history.append(ChatMessage(role="user", content=request.message))
        
        # Ajouter la réponse de l'assistant
        updated_history.append(ChatMessage(role="assistant", content=final_content))
        
        # Log final simplifié
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] RESPONSE: ✅ Réponse générée ({len(tools_used)} outils utilisés)")
        
        return ChatResponse(
            response=final_content,
            tools_used=tools_used,
            conversation_history=updated_history
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chat MCP: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chat: {str(e)}")

@router.get("/chat/tools")
async def list_available_tools(
    client: HaloscanClient = Depends(get_haloscan_client)
) -> Dict[str, Any]:
    """
    📋 Liste tous les outils MCP disponibles pour le chat
    """
    # Récupérer tous les outils disponibles
    all_tools = get_haloscan_tools(client, "")
    
    return {
        "tools": all_tools,
        "description": "Outils Haloscan disponibles pour l'assistant IA (sélection dynamique selon le message)",
        "total_tools": len(all_tools),
        "note": "Les outils sont sélectionnés dynamiquement selon le contenu du message utilisateur"
    }
