"""
Advanced Natural Language Processor with Enterprise-Grade Features.

This module provides state-of-the-art NLP capabilities including semantic similarity,
advanced entity recognition, context-aware parsing, and multi-turn conversation
support, optimized for Intel N150 hardware constraints.
"""

import re
import json
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import math

import structlog

# Advanced NLP libraries
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    ADVANCED_NLP_AVAILABLE = True
except ImportError:
    ADVANCED_NLP_AVAILABLE = False

# Optional spaCy for advanced entity recognition
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from .natural_language_processor import (
    IntentType, InfrastructureType, ComplexityLevel, ConfidenceLevel,
    ParsedIntent, EntityExtraction, SemanticSimilarity
)
from ..core.hardware_detector import hardware_detector

logger = structlog.get_logger(__name__)


@dataclass
class AdvancedNLPConfig:
    """Configuration for advanced NLP processing."""
    
    # Model settings optimized for Intel N150
    use_semantic_similarity: bool = True
    semantic_model_name: str = "all-MiniLM-L6-v2"  # Lightweight model
    similarity_threshold: float = 0.7
    
    # Entity recognition
    use_spacy_ner: bool = True
    spacy_model: str = "en_core_web_sm"
    custom_entity_patterns: bool = True
    
    # Performance optimization
    max_text_length: int = 2048  # Conservative for memory
    batch_processing: bool = False  # Disable for N150
    cache_embeddings: bool = True
    cache_size: int = 100  # Small cache for memory constraints
    
    # Context management
    conversation_memory_turns: int = 5
    context_window_size: int = 500
    
    def __post_init__(self):
        """Adjust settings based on hardware."""
        available_memory = hardware_detector.specs.available_memory_gb
        
        if available_memory < 4.0:
            self.use_semantic_similarity = False
            self.use_spacy_ner = False
            self.cache_size = 50
            self.max_text_length = 1024
        elif available_memory < 6.0:
            self.semantic_model_name = "all-MiniLM-L6-v2"  # Keep lightweight
            self.cache_size = 75
        
        logger.info(
            "Advanced NLP config optimized for hardware",
            config=self.__dict__,
            available_memory_gb=available_memory
        )


class AdvancedEntityRecognizer:
    """Advanced entity recognition with custom patterns and ML models."""
    
    def __init__(self, config: AdvancedNLPConfig):
        self.config = config
        self.spacy_nlp = None
        self.custom_patterns = self._load_custom_patterns()
        
        # Initialize spaCy if available and enabled
        if SPACY_AVAILABLE and config.use_spacy_ner:
            try:
                self.spacy_nlp = spacy.load(config.spacy_model)
                logger.info("spaCy model loaded successfully")
            except Exception as e:
                logger.warning("Failed to load spaCy model", error=str(e))
                self.spacy_nlp = None
    
    def _load_custom_patterns(self) -> Dict[str, List[str]]:
        """Load custom patterns for infrastructure entities."""
        return {
            'memory_size': [
                r'(\d+)\s*(?:gb|gigabytes?|g)\s*(?:of\s+)?(?:ram|memory)',
                r'(\d+)\s*(?:mb|megabytes?|m)\s*(?:of\s+)?(?:ram|memory)',
                r'memory.*?(\d+)\s*(?:gb|mb|g|m)',
                r'ram.*?(\d+)\s*(?:gb|mb|g|m)'
            ],
            'cpu_cores': [
                r'(\d+)\s*(?:cores?|cpus?|processors?|vcpus?)',
                r'(\d+)[-\s]*core',
                r'cpu.*?(\d+)',
                r'processor.*?(\d+)'
            ],
            'storage_size': [
                r'(\d+)\s*(?:gb|tb|gigabytes?|terabytes?|g|t)\s*(?:of\s+)?(?:storage|disk|ssd|hdd)',
                r'storage.*?(\d+)\s*(?:gb|tb|g|t)',
                r'disk.*?(\d+)\s*(?:gb|tb|g|t)'
            ],
            'vm_count': [
                r'(\d+)\s*(?:vms?|virtual\s+machines?|servers?|instances?)',
                r'(\d+)\s*node[s]?',
                r'cluster.*?(\d+)',
                r'deploy.*?(\d+)'
            ],
            'port_numbers': [
                r'port\s*(\d+)',
                r':(\d{2,5})',
                r'listening.*?(\d{2,5})',
                r'service.*?(\d{2,5})'
            ],
            'ip_addresses': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}/\d{1,2}\b'
            ],
            'network_segments': [
                r'vlan\s*(\d+)',
                r'subnet.*?(\d+)',
                r'network.*?(\d+)'
            ],
            'versions': [
                r'version\s*(\d+(?:\.\d+)*)',
                r'v(\d+(?:\.\d+)*)',
                r'(\d+(?:\.\d+)+)'
            ]
        }
    
    async def extract_entities(self, text: str) -> List[EntityExtraction]:
        """Extract entities using both custom patterns and ML models."""
        entities = []
        
        # Custom pattern extraction
        for entity_type, patterns in self.custom_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    entities.append(EntityExtraction(
                        entity_type=entity_type,
                        value=value,
                        confidence=0.8,  # High confidence for pattern matches
                        position=match.span(),
                        context=text[max(0, match.start()-20):match.end()+20]
                    ))
        
        # spaCy NER if available
        if self.spacy_nlp:
            doc = self.spacy_nlp(text)
            for ent in doc.ents:
                # Map spaCy labels to our entity types
                mapped_type = self._map_spacy_label(ent.label_)
                if mapped_type:
                    entities.append(EntityExtraction(
                        entity_type=mapped_type,
                        value=ent.text,
                        confidence=0.9,  # High confidence for spaCy
                        position=(ent.start_char, ent.end_char),
                        context=str(ent.sent) if ent.sent else None
                    ))
        
        # Remove duplicates and sort by confidence
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda x: x.confidence, reverse=True)
        
        return entities
    
    def _map_spacy_label(self, spacy_label: str) -> Optional[str]:
        """Map spaCy entity labels to our custom types."""
        mapping = {
            'CARDINAL': 'number',
            'ORDINAL': 'ordinal_number',
            'PERCENT': 'percentage',
            'MONEY': 'cost',
            'QUANTITY': 'quantity',
            'ORG': 'organization',
            'PRODUCT': 'product',
            'TIME': 'time',
            'DATE': 'date',
            'GPE': 'location'
        }
        return mapping.get(spacy_label)
    
    def _deduplicate_entities(self, entities: List[EntityExtraction]) -> List[EntityExtraction]:
        """Remove duplicate entities based on overlap and confidence."""
        if not entities:
            return entities
        
        # Sort by position
        entities.sort(key=lambda x: x.position[0])
        
        deduplicated = []
        for entity in entities:
            # Check for overlap with existing entities
            overlap = False
            for existing in deduplicated:
                if self._entities_overlap(entity, existing):
                    # Keep the one with higher confidence
                    if entity.confidence > existing.confidence:
                        deduplicated.remove(existing)
                        deduplicated.append(entity)
                    overlap = True
                    break
            
            if not overlap:
                deduplicated.append(entity)
        
        return deduplicated
    
    def _entities_overlap(self, entity1: EntityExtraction, entity2: EntityExtraction) -> bool:
        """Check if two entities overlap in position."""
        start1, end1 = entity1.position
        start2, end2 = entity2.position
        
        return not (end1 <= start2 or end2 <= start1)


class SemanticSimilarityEngine:
    """Semantic similarity analysis using sentence transformers."""
    
    def __init__(self, config: AdvancedNLPConfig):
        self.config = config
        self.model = None
        self.embedding_cache = {}
        self.knowledge_base = self._load_infrastructure_knowledge_base()
        
        # Initialize semantic model if available
        if ADVANCED_NLP_AVAILABLE and config.use_semantic_similarity:
            try:
                self.model = SentenceTransformer(config.semantic_model_name)
                logger.info(
                    "Semantic similarity model loaded",
                    model=config.semantic_model_name
                )
            except Exception as e:
                logger.warning("Failed to load semantic model", error=str(e))
    
    def _load_infrastructure_knowledge_base(self) -> Dict[str, List[str]]:
        """Load knowledge base of infrastructure-related terms."""
        return {
            'virtualization': [
                'create virtual machine', 'deploy vm', 'provision server',
                'hypervisor setup', 'virtual infrastructure', 'vm deployment'
            ],
            'containerization': [
                'docker container', 'kubernetes cluster', 'container orchestration',
                'microservices deployment', 'pod management', 'helm charts'
            ],
            'networking': [
                'network configuration', 'firewall rules', 'load balancer',
                'network security', 'vlan setup', 'network topology'
            ],
            'storage': [
                'storage configuration', 'disk management', 'backup strategy',
                'distributed storage', 'ceph cluster', 'nfs setup'
            ],
            'monitoring': [
                'system monitoring', 'metrics collection', 'alerting setup',
                'prometheus configuration', 'grafana dashboard', 'log analysis'
            ],
            'security': [
                'security hardening', 'access control', 'ssl certificates',
                'vulnerability assessment', 'compliance check', 'security audit'
            ],
            'automation': [
                'infrastructure as code', 'configuration management', 'ci/cd pipeline',
                'automated deployment', 'terraform scripts', 'ansible playbooks'
            ]
        }
    
    async def find_semantic_matches(self, query: str, 
                                  top_k: int = 5) -> List[SemanticSimilarity]:
        """Find semantically similar infrastructure concepts."""
        if not self.model:
            return []
        
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            if query_embedding is None:
                return []
            
            matches = []
            
            # Compare with knowledge base
            for category, concepts in self.knowledge_base.items():
                for concept in concepts:
                    concept_embedding = self._get_embedding(concept)
                    if concept_embedding is not None:
                        similarity = cosine_similarity(
                            query_embedding.reshape(1, -1),
                            concept_embedding.reshape(1, -1)
                        )[0][0]
                        
                        if similarity >= self.config.similarity_threshold:
                            matches.append((concept, float(similarity)))
            
            # Sort by similarity and return top-k
            matches.sort(key=lambda x: x[1], reverse=True)
            
            result = SemanticSimilarity(
                query=query,
                matches=matches[:top_k],
                best_match=matches[0][0] if matches else None,
                confidence=matches[0][1] if matches else 0.0
            )
            
            return [result]
            
        except Exception as e:
            logger.error("Semantic similarity search failed", error=str(e))
            return []
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text with caching."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            embedding = self.model.encode(text)
            
            # Cache if under limit
            if len(self.embedding_cache) < self.config.cache_size:
                self.embedding_cache[text] = embedding
            
            return embedding
            
        except Exception as e:
            logger.warning("Failed to get embedding", text=text[:50], error=str(e))
            return None


class AdvancedNaturalLanguageProcessor:
    """Enterprise-grade natural language processor with advanced features."""
    
    def __init__(self, config: Optional[AdvancedNLPConfig] = None):
        self.config = config or AdvancedNLPConfig()
        self.entity_recognizer = AdvancedEntityRecognizer(self.config)
        self.semantic_engine = SemanticSimilarityEngine(self.config)
        
        # Enhanced pattern matching
        self.intent_patterns = self._load_enhanced_intent_patterns()
        self.complexity_indicators = self._load_complexity_indicators()
        self.skill_level_indicators = self._load_skill_level_indicators()
        
        # Conversation context
        self.conversation_history = []
        self.context_embeddings = []
        
        logger.info(
            "Advanced NLP processor initialized",
            config=self.config.__dict__
        )
    
    def _load_enhanced_intent_patterns(self) -> Dict[IntentType, Dict[str, Any]]:
        """Load enhanced intent patterns with confidence weights."""
        return {
            IntentType.CREATE_VM: {
                'patterns': [
                    (r'create.*(?:vm|virtual machine|server)', 0.9),
                    (r'(?:spin up|deploy|provision).*(?:vm|machine|server)', 0.8),
                    (r'need.*(?:new|fresh).*(?:vm|machine|server)', 0.7),
                    (r'set up.*(?:vm|virtual machine)', 0.8),
                    (r'launch.*(?:vm|instance|machine)', 0.8),
                    (r'build.*(?:vm|machine|server)', 0.7),
                ],
                'keywords': ['vm', 'virtual', 'machine', 'server', 'create', 'deploy'],
                'complexity_hints': ['simple', 'basic', 'single'] 
            },
            
            IntentType.GENERATE_KUBERNETES: {
                'patterns': [
                    (r'(?:create|generate|build).*(?:kubernetes|k8s).*(?:cluster|deployment)', 0.9),
                    (r'(?:deploy|setup).*(?:kubernetes|k8s)', 0.8),
                    (r'(?:orchestrate|manage).*containers?', 0.7),
                    (r'(?:helm|kubectl).*(?:install|deploy)', 0.8),
                ],
                'keywords': ['kubernetes', 'k8s', 'cluster', 'pods', 'helm', 'kubectl'],
                'complexity_hints': ['complex', 'enterprise', 'scalable', 'distributed']
            },
            
            IntentType.SECURITY_REVIEW: {
                'patterns': [
                    (r'(?:security|secure).*(?:review|audit|check)', 0.9),
                    (r'(?:vulnerability|vuln).*(?:scan|assessment)', 0.8),
                    (r'(?:harden|secure).*(?:configuration|setup)', 0.8),
                    (r'security.*(?:best practices|recommendations)', 0.7),
                ],
                'keywords': ['security', 'audit', 'vulnerability', 'hardening', 'compliance'],
                'complexity_hints': ['enterprise', 'production', 'compliance']
            },
            
            IntentType.PERFORMANCE_ANALYSIS: {
                'patterns': [
                    (r'(?:performance|perf).*(?:analysis|review|optimization)', 0.9),
                    (r'(?:optimize|tune|improve).*(?:performance|speed)', 0.8),
                    (r'(?:bottleneck|slow|latency).*(?:analysis|investigation)', 0.8),
                    (r'(?:benchmark|load test|stress test)', 0.7),
                ],
                'keywords': ['performance', 'optimization', 'bottleneck', 'benchmark', 'latency'],
                'complexity_hints': ['advanced', 'enterprise', 'optimization']
            },
            
            IntentType.COST_ANALYSIS: {
                'patterns': [
                    (r'(?:cost|price|budget).*(?:analysis|optimization|reduction)', 0.9),
                    (r'(?:save|reduce).*(?:cost|money|budget)', 0.8),
                    (r'(?:billing|expense).*(?:review|analysis)', 0.7),
                    (r'resource.*(?:utilization|efficiency)', 0.7),
                ],
                'keywords': ['cost', 'budget', 'pricing', 'billing', 'optimization', 'savings'],
                'complexity_hints': ['enterprise', 'optimization', 'analysis']
            }
        }
    
    def _load_complexity_indicators(self) -> Dict[ComplexityLevel, List[str]]:
        """Load complexity level indicators."""
        return {
            ComplexityLevel.SIMPLE: [
                'simple', 'basic', 'easy', 'single', 'one', 'quick', 'minimal'
            ],
            ComplexityLevel.MODERATE: [
                'moderate', 'standard', 'typical', 'normal', 'regular', 'few'
            ],
            ComplexityLevel.COMPLEX: [
                'complex', 'advanced', 'multiple', 'several', 'many', 'sophisticated'
            ],
            ComplexityLevel.ENTERPRISE: [
                'enterprise', 'production', 'scalable', 'distributed', 'cluster',
                'high availability', 'fault tolerant', 'multi-region', 'ha'
            ]
        }
    
    def _load_skill_level_indicators(self) -> Dict[str, List[str]]:
        """Load skill level indicators."""
        return {
            'beginner': [
                'beginner', 'new', 'first time', 'learning', 'tutorial',
                'help', 'guide', 'simple', 'easy', 'basic'
            ],
            'intermediate': [
                'intermediate', 'some experience', 'familiar', 'understand',
                'know', 'worked with', 'used before'
            ],
            'expert': [
                'expert', 'advanced', 'experienced', 'professional', 'production',
                'enterprise', 'complex', 'optimize', 'performance', 'scale'
            ]
        }
    
    async def parse_user_input(self, 
                             user_input: str, 
                             context: Optional[Dict[str, Any]] = None) -> ParsedIntent:
        """Parse user input with advanced NLP capabilities."""
        start_time = time.time()
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(user_input)
            
            # Intent recognition
            intent_result = await self._recognize_intent(processed_text)
            
            # Entity extraction
            entities = await self.entity_recognizer.extract_entities(processed_text)
            
            # Semantic similarity analysis
            semantic_matches = await self.semantic_engine.find_semantic_matches(processed_text)
            
            # Extract parameters
            parameters = self._extract_parameters(processed_text, entities)
            
            # Determine complexity level
            complexity = self._determine_complexity(processed_text)
            
            # Determine skill level
            skill_level = self._determine_skill_level(processed_text, context)
            
            # Detect infrastructure type
            infra_type = self._detect_infrastructure_type(processed_text, entities)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(processed_text)
            
            # Extract technical terms
            technical_terms = self._extract_technical_terms(processed_text)
            
            # Check if clarification is needed
            clarification_needed, questions = self._check_clarification_needs(
                intent_result['intent'], parameters
            )
            
            # Create parsed intent
            parsed_intent = ParsedIntent(
                intent_type=intent_result['intent'],
                confidence=intent_result['confidence'],
                infrastructure_type=infra_type,
                parameters=parameters,
                skill_level=skill_level,
                urgency="normal",  # Could be enhanced with urgency detection
                entities={entity.entity_type: [entity.value] for entity in entities},
                
                # Enhanced features
                complexity_level=complexity,
                extracted_entities=entities,
                semantic_matches=semantic_matches,
                context_keywords=self._extract_keywords(processed_text),
                technical_terms=technical_terms,
                confidence_breakdown=intent_result['confidence_breakdown'],
                processing_time=time.time() - start_time,
                sentiment=sentiment,
                requires_clarification=clarification_needed,
                clarification_questions=questions,
                previous_context=context.get('previous_context') if context else None
            )
            
            # Add to conversation history
            self._update_conversation_history(parsed_intent)
            
            logger.info(
                "Advanced NLP parsing completed",
                intent=intent_result['intent'].value,
                confidence=intent_result['confidence'],
                entities_count=len(entities),
                processing_time=parsed_intent.processing_time
            )
            
            return parsed_intent
            
        except Exception as e:
            logger.error("Advanced NLP parsing failed", error=str(e))
            
            # Return fallback intent
            return ParsedIntent(
                intent_type=IntentType.GENERAL_QUESTION,
                confidence=0.1,
                infrastructure_type=None,
                parameters={},
                skill_level="intermediate",
                urgency="normal",
                entities={},
                processing_time=time.time() - start_time
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        # Truncate if too long
        if len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length]
        
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    async def _recognize_intent(self, text: str) -> Dict[str, Any]:
        """Recognize intent with confidence scoring."""
        text_lower = text.lower()
        intent_scores = defaultdict(float)
        confidence_breakdown = {}
        
        # Pattern matching
        for intent_type, intent_data in self.intent_patterns.items():
            pattern_score = 0.0
            pattern_matches = 0
            
            for pattern, weight in intent_data['patterns']:
                if re.search(pattern, text_lower):
                    pattern_score += weight
                    pattern_matches += 1
            
            # Keyword matching
            keyword_score = 0.0
            for keyword in intent_data['keywords']:
                if keyword in text_lower:
                    keyword_score += 0.1
            
            # Combine scores
            total_score = pattern_score + keyword_score
            if pattern_matches > 0:
                total_score = total_score / max(1, pattern_matches)  # Normalize
            
            intent_scores[intent_type] = total_score
            confidence_breakdown[intent_type.value] = {
                'pattern_score': pattern_score,
                'keyword_score': keyword_score,
                'total_score': total_score
            }
        
        # Find best match
        if intent_scores:
            best_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
            best_confidence = min(1.0, intent_scores[best_intent])
        else:
            best_intent = IntentType.GENERAL_QUESTION
            best_confidence = 0.1
        
        return {
            'intent': best_intent,
            'confidence': best_confidence,
            'confidence_breakdown': confidence_breakdown
        }
    
    def _extract_parameters(self, text: str, entities: List[EntityExtraction]) -> Dict[str, Any]:
        """Extract parameters from text and entities."""
        parameters = {}
        
        # Extract from entities
        for entity in entities:
            if entity.entity_type == 'memory_size':
                try:
                    value = int(re.search(r'\d+', entity.value).group())
                    unit = 'GB' if 'gb' in entity.value.lower() else 'MB'
                    parameters['memory'] = {'value': value, 'unit': unit}
                except:
                    pass
            
            elif entity.entity_type == 'cpu_cores':
                try:
                    parameters['cpu_cores'] = int(re.search(r'\d+', entity.value).group())
                except:
                    pass
            
            elif entity.entity_type == 'storage_size':
                try:
                    value = int(re.search(r'\d+', entity.value).group())
                    unit = 'TB' if 'tb' in entity.value.lower() else 'GB'
                    parameters['storage'] = {'value': value, 'unit': unit}
                except:
                    pass
            
            elif entity.entity_type == 'vm_count':
                try:
                    parameters['vm_count'] = int(re.search(r'\d+', entity.value).group())
                except:
                    pass
        
        # Extract environment type
        text_lower = text.lower()
        for env in ['production', 'staging', 'development', 'testing']:
            if env in text_lower:
                parameters['environment'] = env
                break
        
        return parameters
    
    def _determine_complexity(self, text: str) -> ComplexityLevel:
        """Determine complexity level from text."""
        text_lower = text.lower()
        complexity_scores = defaultdict(int)
        
        for level, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    complexity_scores[level] += 1
        
        if complexity_scores:
            return max(complexity_scores.keys(), key=lambda k: complexity_scores[k])
        
        return ComplexityLevel.MODERATE
    
    def _determine_skill_level(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """Determine user skill level."""
        text_lower = text.lower()
        skill_scores = defaultdict(int)
        
        for level, indicators in self.skill_level_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    skill_scores[level] += 1
        
        # Use context if available
        if context and 'user_skill_level' in context:
            return context['user_skill_level']
        
        if skill_scores:
            return max(skill_scores.keys(), key=lambda k: skill_scores[k])
        
        return "intermediate"
    
    def _detect_infrastructure_type(self, text: str, 
                                  entities: List[EntityExtraction]) -> Optional[InfrastructureType]:
        """Detect infrastructure type from text and entities."""
        text_lower = text.lower()
        
        # Infrastructure type mapping
        type_keywords = {
            InfrastructureType.KUBERNETES: ['kubernetes', 'k8s', 'kubectl', 'helm', 'pod'],
            InfrastructureType.DOCKER: ['docker', 'container', 'dockerfile'],
            InfrastructureType.AWS: ['aws', 'amazon', 'ec2', 's3', 'lambda'],
            InfrastructureType.AZURE: ['azure', 'microsoft', 'vm', 'storage account'],
            InfrastructureType.GCP: ['gcp', 'google cloud', 'compute engine'],
            InfrastructureType.TERRAFORM: ['terraform', 'hcl', 'tf'],
            InfrastructureType.ANSIBLE: ['ansible', 'playbook', 'yaml'],
            InfrastructureType.MONITORING: ['prometheus', 'grafana', 'monitoring', 'metrics'],
            InfrastructureType.DATABASE: ['database', 'mysql', 'postgresql', 'mongodb'],
            InfrastructureType.WEB_SERVER: ['nginx', 'apache', 'web server', 'http'],
            InfrastructureType.PROXMOX: ['proxmox', 've', 'pve']
        }
        
        type_scores = defaultdict(int)
        
        for infra_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    type_scores[infra_type] += 1
        
        if type_scores:
            return max(type_scores.keys(), key=lambda k: type_scores[k])
        
        return None
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'awesome', 'perfect', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'problem', 'issue', 'error', 'fail']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text."""
        technical_terms = [
            'vm', 'virtual machine', 'container', 'kubernetes', 'docker',
            'terraform', 'ansible', 'prometheus', 'grafana', 'nginx',
            'apache', 'mysql', 'postgresql', 'redis', 'mongodb',
            'ssl', 'tls', 'https', 'api', 'rest', 'json', 'yaml',
            'cpu', 'ram', 'memory', 'storage', 'disk', 'network',
            'firewall', 'load balancer', 'proxy', 'cache'
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in technical_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple keyword extraction (could be enhanced with TF-IDF)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
            'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has',
            'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two',
            'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she',
            'too', 'use'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return top keywords by frequency
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    def _check_clarification_needs(self, intent: IntentType, 
                                 parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if clarification is needed for the request."""
        questions = []
        
        # Check for missing critical parameters based on intent
        if intent == IntentType.CREATE_VM:
            if 'memory' not in parameters:
                questions.append("How much memory should the VM have?")
            if 'cpu_cores' not in parameters:
                questions.append("How many CPU cores do you need?")
            if 'storage' not in parameters:
                questions.append("How much storage space do you need?")
        
        elif intent == IntentType.DEPLOY_INFRASTRUCTURE:
            if 'environment' not in parameters:
                questions.append("Which environment is this for (development, staging, production)?")
        
        elif intent in [IntentType.GENERATE_KUBERNETES, IntentType.GENERATE_DOCKER]:
            if 'vm_count' not in parameters:
                questions.append("How many nodes do you need in the cluster?")
        
        return len(questions) > 0, questions
    
    def _update_conversation_history(self, parsed_intent: ParsedIntent):
        """Update conversation history for context."""
        self.conversation_history.append(parsed_intent)
        
        # Keep only recent history
        if len(self.conversation_history) > self.config.conversation_memory_turns:
            self.conversation_history = self.conversation_history[-self.config.conversation_memory_turns:]
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context."""
        if not self.conversation_history:
            return {}
        
        recent_intents = [intent.intent_type.value for intent in self.conversation_history[-3:]]
        recent_topics = []
        
        for intent in self.conversation_history[-3:]:
            if intent.infrastructure_type:
                recent_topics.append(intent.infrastructure_type.value)
            recent_topics.extend(intent.technical_terms[:3])
        
        return {
            'recent_intents': recent_intents,
            'recent_topics': list(set(recent_topics)),
            'conversation_length': len(self.conversation_history),
            'last_complexity': self.conversation_history[-1].complexity_level.value if self.conversation_history else None
        }


# Global enhanced NLP processor
enhanced_nlp_processor = None

def get_enhanced_nlp_processor(config: Optional[AdvancedNLPConfig] = None) -> AdvancedNaturalLanguageProcessor:
    """Get global enhanced NLP processor instance."""
    global enhanced_nlp_processor
    
    if enhanced_nlp_processor is None:
        enhanced_nlp_processor = AdvancedNaturalLanguageProcessor(config)
    
    return enhanced_nlp_processor


# Export main classes and functions
__all__ = [
    'AdvancedNLPConfig',
    'AdvancedEntityRecognizer',
    'SemanticSimilarityEngine', 
    'AdvancedNaturalLanguageProcessor',
    'get_enhanced_nlp_processor'
]