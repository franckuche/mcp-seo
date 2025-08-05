"""
Service de chunking intelligent pour contourner les limites de tokens OpenAI
Permet des analyses SEO complètes en divisant les données en chunks logiques
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from ..logging_config import get_logger

logger = get_logger("chunking")

@dataclass
class ChunkContext:
    """Contexte maintenu entre les chunks"""
    analysis_id: str
    user_query: str
    domain: str
    total_chunks: int
    current_chunk: int
    accumulated_insights: List[str]
    chunk_summaries: List[str]
    start_time: datetime
    
class ChunkingStrategy:
    """Stratégies de découpage selon le type d'analyse"""
    
    @staticmethod
    def competitor_analysis(competitors: List[str], chunk_size: int = 3) -> List[List[str]]:
        """Découpe les concurrents en chunks logiques"""
        chunks = []
        for i in range(0, len(competitors), chunk_size):
            chunks.append(competitors[i:i + chunk_size])
        return chunks
    
    @staticmethod
    def keyword_analysis(keywords: List[Dict], chunk_size: int = 20) -> List[List[Dict]]:
        """Découpe les mots-clés par importance/volume"""
        # Trier par volume décroissant puis découper
        sorted_keywords = sorted(keywords, key=lambda k: k.get('volume', 0), reverse=True)
        chunks = []
        for i in range(0, len(sorted_keywords), chunk_size):
            chunks.append(sorted_keywords[i:i + chunk_size])
        return chunks
    
    @staticmethod
    def position_analysis(positions: List[Dict], chunk_size: int = 50) -> List[List[Dict]]:
        """Découpe les positions par plages (1-10, 11-20, etc.)"""
        # Grouper par plages de positions
        position_ranges = {}
        for pos in positions:
            position = pos.get('position', 0)
            range_key = f"{((position-1)//10)*10 + 1}-{((position-1)//10 + 1)*10}"
            if range_key not in position_ranges:
                position_ranges[range_key] = []
            position_ranges[range_key].append(pos)
        
        return list(position_ranges.values())

class ChunkingService:
    """Service principal de chunking intelligent"""
    
    def __init__(self):
        self.active_contexts: Dict[str, ChunkContext] = {}
    
    def create_analysis_context(self, user_query: str, domain: str, total_chunks: int) -> str:
        """Crée un nouveau contexte d'analyse"""
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(user_query) % 10000}"
        
        context = ChunkContext(
            analysis_id=analysis_id,
            user_query=user_query,
            domain=domain,
            total_chunks=total_chunks,
            current_chunk=0,
            accumulated_insights=[],
            chunk_summaries=[],
            start_time=datetime.now()
        )
        
        self.active_contexts[analysis_id] = context
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Nouvelle analyse → {analysis_id} ({total_chunks} chunks)")
        
        return analysis_id
    
    def get_context(self, analysis_id: str) -> Optional[ChunkContext]:
        """Récupère le contexte d'une analyse"""
        return self.active_contexts.get(analysis_id)
    
    def update_context(self, analysis_id: str, chunk_summary: str, insights: List[str]) -> None:
        """Met à jour le contexte avec les résultats d'un chunk"""
        context = self.active_contexts.get(analysis_id)
        if not context:
            return
        
        context.current_chunk += 1
        context.chunk_summaries.append(chunk_summary)
        context.accumulated_insights.extend(insights)
        
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Chunk {context.current_chunk}/{context.total_chunks} terminé")
    
    def is_analysis_complete(self, analysis_id: str) -> bool:
        """Vérifie si l'analyse est terminée"""
        context = self.active_contexts.get(analysis_id)
        if not context:
            return True
        
        return context.current_chunk >= context.total_chunks
    
    def get_synthesis_prompt(self, analysis_id: str) -> str:
        """Génère le prompt de synthèse finale"""
        context = self.active_contexts.get(analysis_id)
        if not context:
            return ""
        
        duration = (datetime.now() - context.start_time).total_seconds()
        
        prompt = f"""Tu viens de terminer une analyse SEO complète en {context.total_chunks} étapes pour le domaine {context.domain}.

REQUÊTE ORIGINALE: {context.user_query}

RÉSUMÉS DES ÉTAPES:
{chr(10).join([f"Étape {i+1}: {summary}" for i, summary in enumerate(context.chunk_summaries)])}

INSIGHTS ACCUMULÉS:
{chr(10).join([f"• {insight}" for insight in context.accumulated_insights])}

MISSION: Synthétise maintenant tous ces éléments en une analyse complète et cohérente qui répond parfaitement à la requête originale. 

Inclus:
1. Un résumé exécutif des découvertes principales
2. Les opportunités prioritaires identifiées
3. Un plan d'action concret et priorisé
4. Les métriques clés à surveiller

Durée d'analyse: {duration:.1f}s sur {context.total_chunks} chunks."""

        return prompt
    
    def cleanup_context(self, analysis_id: str) -> None:
        """Nettoie le contexte après synthèse"""
        if analysis_id in self.active_contexts:
            context = self.active_contexts[analysis_id]
            duration = (datetime.now() - context.start_time).total_seconds()
            logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] CHUNKING: Analyse {analysis_id} terminée en {duration:.1f}s")
            del self.active_contexts[analysis_id]

class ChunkProcessor:
    """Processeur spécialisé pour différents types de chunks"""
    
    @staticmethod
    def create_competitor_chunk_prompt(competitors: List[str], domain: str, chunk_num: int, total_chunks: int) -> str:
        """Crée le prompt pour un chunk de concurrents"""
        return f"""Analyse SEO - Étape {chunk_num}/{total_chunks}

DOMAINE ANALYSÉ: {domain}
CONCURRENTS À ANALYSER: {', '.join(competitors)}

MISSION: Analyse ces {len(competitors)} concurrents et identifie:

1. MOTS-CLÉS UNIQUES: Quels mots-clés ces concurrents ciblent-ils que {domain} ne cible pas ?
2. STRATÉGIES DIFFÉRENCIANTES: Quelles approches SEO utilisent-ils ?
3. OPPORTUNITÉS: Quels gaps peut exploiter {domain} ?
4. FORCES/FAIBLESSES: Points forts et vulnérabilités de chaque concurrent

IMPORTANT: 
- Sois concis mais précis
- Focus sur les insights actionnables
- Cette analyse sera combinée avec d'autres étapes
- Termine par 3-5 insights clés pour la synthèse finale"""
    
    @staticmethod
    def create_keyword_chunk_prompt(keywords: List[Dict], domain: str, chunk_num: int, total_chunks: int) -> str:
        """Crée le prompt pour un chunk de mots-clés"""
        return f"""Analyse SEO - Étape {chunk_num}/{total_chunks}

DOMAINE ANALYSÉ: {domain}
MOTS-CLÉS À ANALYSER: {len(keywords)} mots-clés

DONNÉES:
{json.dumps(keywords[:10], indent=2, ensure_ascii=False)}
{"... et " + str(len(keywords)-10) + " autres" if len(keywords) > 10 else ""}

MISSION: Analyse ces mots-clés et identifie:

1. OPPORTUNITÉS PRIORITAIRES: Mots-clés à fort potentiel (volume élevé, difficulté modérée)
2. GAPS DE CONTENU: Sujets non couverts par {domain}
3. SAISONNALITÉ: Tendances temporelles importantes
4. CLUSTERING: Groupes thématiques cohérents

IMPORTANT:
- Priorise par impact business potentiel
- Cette analyse sera combinée avec d'autres étapes
- Termine par 3-5 recommandations concrètes"""

# Instance globale du service de chunking
chunking_service = ChunkingService()
