"""
Smart Context Switching Engine for Proxmox AI Assistant.

Provides intelligent context switching that automatically adapts to technical domains,
user expertise levels, and conversation flow. Integrates with knowledge base and
system prompts for seamless domain expertise transitions.

Features:
- Automatic domain detection and switching
- Expertise level adaptation
- Conversation context preservation
- Security context awareness
- Performance optimization
- Session state management
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

from .knowledge_base import (
    TechnicalKnowledgeBase, TechnicalDomain, ExpertiseLevel,
    KnowledgeContext, technical_knowledge_base
)
from .system_prompts import (
    SystemPromptsEngine, PromptType, PromptContext, system_prompts_engine
)
from .natural_language_processor import ParsedIntent, nlp_processor

logger = structlog.get_logger(__name__)


class ContextSwitchTrigger(Enum):
    """Triggers for context switching."""
    DOMAIN_CHANGE = "domain_change"
    EXPERTISE_SHIFT = "expertise_shift"
    SECURITY_ESCALATION = "security_escalation"
    TECHNOLOGY_FOCUS = "technology_focus"
    CONVERSATION_FLOW = "conversation_flow"
    USER_REQUEST = "user_request"


@dataclass
class ConversationContext:
    """Current conversation context state."""
    session_id: str
    current_domain: TechnicalDomain
    expertise_level: ExpertiseLevel
    active_technologies: List[str]
    security_level: str
    conversation_history: List[Dict[str, Any]]
    knowledge_cache: Dict[str, Any]
    prompt_history: List[str]
    context_switches: List[Dict[str, Any]]
    last_updated: float
    performance_metrics: Dict[str, float]


@dataclass
class ContextSwitchEvent:
    """Context switch event record."""
    timestamp: float
    trigger: ContextSwitchTrigger
    previous_context: Dict[str, Any]
    new_context: Dict[str, Any]
    confidence: float
    reason: str
    user_confirmed: bool = False


class SmartContextEngine:
    """
    Smart context switching engine with domain expertise adaptation.
    
    Features:
    - Automatic domain detection from user input
    - Expertise level adaptation based on user behavior
    - Context preservation across conversation turns
    - Performance optimization with caching
    - Security context awareness
    - Conversation flow analysis
    """
    
    def __init__(
        self,
        knowledge_base: TechnicalKnowledgeBase = None,
        prompts_engine: SystemPromptsEngine = None
    ):
        """Initialize the smart context engine."""
        self.knowledge_base = knowledge_base or technical_knowledge_base
        self.prompts_engine = prompts_engine or system_prompts_engine
        
        # Active conversation contexts by session
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        # Context switching rules and patterns
        self.domain_keywords = self._initialize_domain_keywords()
        self.expertise_indicators = self._initialize_expertise_indicators()
        self.security_triggers = self._initialize_security_triggers()
        
        # Performance tracking
        self.context_switch_metrics = {
            "total_switches": 0,
            "automatic_switches": 0,
            "user_confirmed_switches": 0,
            "avg_switch_confidence": 0.0,
            "cache_hit_rate": 0.0
        }
        
        logger.info("Smart context engine initialized")
    
    def _initialize_domain_keywords(self) -> Dict[TechnicalDomain, List[str]]:
        """Initialize domain detection keywords."""
        return {
            TechnicalDomain.VIRTUALIZATION: [
                "proxmox", "vm", "virtual machine", "hypervisor", "kvm", "qemu", "lxc",
                "cluster", "node", "migration", "snapshot", "template", "backup",
                "storage", "ceph", "zfs", "high availability", "ha", "fencing"
            ],
            TechnicalDomain.INFRASTRUCTURE_AS_CODE: [
                "terraform", "ansible", "playbook", "iac", "infrastructure as code",
                "pulumi", "cloudformation", "arm template", "helm", "state", "module",
                "provider", "resource", "variable", "output", "plan", "apply", "destroy"
            ],
            TechnicalDomain.CONTAINERIZATION: [
                "docker", "kubernetes", "k8s", "container", "pod", "service", "deployment",
                "namespace", "ingress", "helm", "istio", "service mesh", "microservice",
                "compose", "dockerfile", "image", "registry", "orchestration"
            ],
            TechnicalDomain.CLOUD_COMPUTING: [
                "aws", "azure", "gcp", "cloud", "ec2", "s3", "lambda", "serverless",
                "multi-cloud", "hybrid", "saas", "paas", "iaas", "api gateway",
                "load balancer", "auto scaling", "cdn", "vpc", "subnet"
            ],
            TechnicalDomain.SYSTEM_ENGINEERING: [
                "linux", "ubuntu", "centos", "rhel", "systemd", "bash", "shell",
                "performance", "tuning", "monitoring", "logging", "cron", "ssh",
                "firewall", "iptables", "selinux", "sudo", "user management"
            ],
            TechnicalDomain.NETWORKING: [
                "network", "vlan", "subnet", "routing", "switching", "firewall",
                "vpn", "dns", "dhcp", "tcp", "udp", "ip", "ethernet", "bridge",
                "bonding", "load balancing", "proxy", "nginx", "haproxy"
            ],
            TechnicalDomain.SECURITY: [
                "security", "encryption", "tls", "ssl", "certificate", "authentication",
                "authorization", "rbac", "iam", "vulnerability", "compliance",
                "audit", "logging", "monitoring", "incident", "threat", "zero trust"
            ],
            TechnicalDomain.MONITORING: [
                "monitoring", "metrics", "logs", "tracing", "observability",
                "prometheus", "grafana", "elk", "elasticsearch", "kibana", "logstash",
                "alerting", "dashboard", "sla", "slo", "sli", "uptime", "performance"
            ]
        }
    
    def _initialize_expertise_indicators(self) -> Dict[ExpertiseLevel, Dict[str, List[str]]]:
        """Initialize expertise level detection indicators."""
        return {
            ExpertiseLevel.BEGINNER: {
                "keywords": [
                    "how to", "what is", "explain", "tutorial", "guide", "help me",
                    "beginner", "new to", "first time", "don't know", "learning",
                    "basic", "simple", "easy", "step by step", "getting started"
                ],
                "patterns": [
                    r"what (?:is|are|does)",
                    r"how (?:to|do|can) i",
                    r"(?:i'm|i am) (?:new|beginner)",
                    r"(?:first time|getting started)",
                    r"(?:don't know|not sure) (?:how|what|where)"
                ]
            },
            ExpertiseLevel.INTERMEDIATE: {
                "keywords": [
                    "best practice", "optimization", "configuration", "setup",
                    "implementation", "deployment", "automation", "integration",
                    "troubleshoot", "debug", "performance", "scaling", "monitoring"
                ],
                "patterns": [
                    r"(?:best|recommended) (?:practice|approach|way)",
                    r"how (?:to|can) (?:optimize|improve|configure)",
                    r"(?:implement|deploy|setup) (?:a|an|the)",
                    r"(?:troubleshoot|debug|fix) (?:issue|problem)"
                ]
            },
            ExpertiseLevel.EXPERT: {
                "keywords": [
                    "architecture", "design patterns", "enterprise", "scalability",
                    "high availability", "disaster recovery", "security hardening",
                    "compliance", "governance", "automation", "orchestration",
                    "advanced", "custom", "extension", "plugin", "api integration"
                ],
                "patterns": [
                    r"(?:architect|design) (?:a|an|the) (?:system|solution|platform)",
                    r"(?:enterprise|production) (?:grade|ready|deployment)",
                    r"(?:advanced|complex|sophisticated) (?:setup|configuration)",
                    r"(?:custom|extend|integrate) (?:with|into)"
                ]
            }
        }
    
    def _initialize_security_triggers(self) -> List[str]:
        """Initialize security context triggers."""
        return [
            "security", "secure", "vulnerability", "exploit", "attack", "breach",
            "compliance", "audit", "encryption", "authentication", "authorization",
            "firewall", "intrusion", "threat", "risk", "hardening", "penetration",
            "certificate", "key management", "access control", "privilege"
        ]
    
    def get_or_create_context(
        self,
        session_id: str,
        initial_input: str = "",
        user_preferences: Dict[str, Any] = None
    ) -> ConversationContext:
        """Get existing context or create new one for session."""
        if session_id in self.active_contexts:
            context = self.active_contexts[session_id]
            context.last_updated = time.time()
            return context
        
        # Create new context
        initial_domain, confidence = self._detect_domain(initial_input)
        initial_expertise = self._detect_expertise_level(initial_input, user_preferences)
        
        context = ConversationContext(
            session_id=session_id,
            current_domain=initial_domain,
            expertise_level=initial_expertise,
            active_technologies=self._extract_technologies(initial_input),
            security_level=self._detect_security_level(initial_input),
            conversation_history=[],
            knowledge_cache={},
            prompt_history=[],
            context_switches=[],
            last_updated=time.time(),
            performance_metrics={"context_switches": 0, "cache_hits": 0, "total_requests": 0}
        )
        
        self.active_contexts[session_id] = context
        
        logger.info(
            "Created new conversation context",
            session_id=session_id,
            domain=initial_domain.value,
            expertise=initial_expertise.value,
            confidence=confidence
        )
        
        return context
    
    def process_user_input(
        self,
        session_id: str,
        user_input: str,
        parsed_intent: Optional[ParsedIntent] = None
    ) -> Tuple[ConversationContext, Optional[ContextSwitchEvent]]:
        """
        Process user input and determine if context switching is needed.
        
        Args:
            session_id: Session identifier
            user_input: Raw user input
            parsed_intent: Pre-parsed intent from NLP processor
            
        Returns:
            Tuple of (updated_context, context_switch_event)
        """
        context = self.get_or_create_context(session_id, user_input)
        context.performance_metrics["total_requests"] += 1
        
        # Parse intent if not provided
        if parsed_intent is None:
            parsed_intent = nlp_processor.parse_user_input(user_input)
        
        # Add to conversation history
        context.conversation_history.append({
            "timestamp": time.time(),
            "user_input": user_input,
            "parsed_intent": asdict(parsed_intent),
            "context_snapshot": {
                "domain": context.current_domain.value,
                "expertise": context.expertise_level.value,
                "technologies": context.active_technologies.copy()
            }
        })
        
        # Keep conversation history manageable
        if len(context.conversation_history) > 50:
            context.conversation_history = context.conversation_history[-50:]
        
        # Detect potential context switches
        switch_event = self._analyze_context_switch_need(context, user_input, parsed_intent)
        
        if switch_event:
            # Apply context switch
            self._apply_context_switch(context, switch_event)
            context.context_switches.append(asdict(switch_event))
            
            logger.info(
                "Context switch applied",
                session_id=session_id,
                trigger=switch_event.trigger.value,
                confidence=switch_event.confidence,
                reason=switch_event.reason
            )
        
        context.last_updated = time.time()
        return context, switch_event
    
    def _detect_domain(self, text: str) -> Tuple[TechnicalDomain, float]:
        """Detect technical domain from text input."""
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword in text_lower:
                    matches += 1
                    # Weight longer keywords more heavily
                    score += len(keyword.split()) * 1.5
            
            if matches > 0:
                # Normalize score by keyword count
                domain_scores[domain] = score / len(keywords)
        
        if not domain_scores:
            # Default to general infrastructure if no specific domain detected
            return TechnicalDomain.SYSTEM_ENGINEERING, 0.5
        
        # Get highest scoring domain
        best_domain = max(domain_scores.items(), key=lambda x: x[1])
        confidence = min(best_domain[1] * 2, 1.0)  # Scale confidence
        
        return best_domain[0], confidence
    
    def _detect_expertise_level(
        self,
        text: str,
        user_preferences: Dict[str, Any] = None
    ) -> ExpertiseLevel:
        """Detect user expertise level from text and preferences."""
        # Check user preferences first
        if user_preferences and "expertise_level" in user_preferences:
            try:
                return ExpertiseLevel(user_preferences["expertise_level"])
            except ValueError:
                pass
        
        text_lower = text.lower()
        level_scores = {}
        
        for level, indicators in self.expertise_indicators.items():
            score = 0
            
            # Check keywords
            for keyword in indicators["keywords"]:
                if keyword in text_lower:
                    score += 1
            
            # Check patterns
            import re
            for pattern in indicators["patterns"]:
                if re.search(pattern, text_lower):
                    score += 2  # Patterns weighted more heavily
            
            level_scores[level] = score
        
        if not any(level_scores.values()):
            return ExpertiseLevel.INTERMEDIATE  # Default
        
        return max(level_scores.items(), key=lambda x: x[1])[0]
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technology mentions from text."""
        technologies = []
        text_lower = text.lower()
        
        # Common technology terms
        tech_terms = [
            "proxmox", "terraform", "ansible", "docker", "kubernetes", "k8s",
            "aws", "azure", "gcp", "vmware", "hyper-v", "nginx", "apache",
            "mysql", "postgresql", "redis", "elasticsearch", "prometheus",
            "grafana", "jenkins", "gitlab", "github", "linux", "ubuntu",
            "centos", "rhel", "debian", "python", "bash", "powershell"
        ]
        
        for tech in tech_terms:
            if tech in text_lower:
                # Find the actual case from original text
                import re
                match = re.search(rf'\b{re.escape(tech)}\b', text, re.IGNORECASE)
                if match:
                    technologies.append(match.group())
        
        return list(set(technologies))  # Remove duplicates
    
    def _detect_security_level(self, text: str) -> str:
        """Detect security context level."""
        text_lower = text.lower()
        
        # High security indicators
        high_security_terms = [
            "production", "enterprise", "compliance", "audit", "security",
            "encryption", "vulnerability", "threat", "breach", "attack"
        ]
        
        # Count security-related terms
        security_score = sum(1 for term in high_security_terms if term in text_lower)
        
        if security_score >= 3:
            return "high"
        elif security_score >= 1:
            return "medium"
        else:
            return "medium"  # Default to medium security
    
    def _analyze_context_switch_need(
        self,
        context: ConversationContext,
        user_input: str,
        parsed_intent: ParsedIntent
    ) -> Optional[ContextSwitchEvent]:
        """Analyze if context switch is needed."""
        current_time = time.time()
        
        # Detect new domain from current input
        new_domain, domain_confidence = self._detect_domain(user_input)
        
        # Detect expertise shift
        new_expertise = self._detect_expertise_level(user_input)
        
        # Extract new technologies
        new_technologies = self._extract_technologies(user_input)
        
        # Check for domain switch
        if new_domain != context.current_domain and domain_confidence > 0.7:
            return ContextSwitchEvent(
                timestamp=current_time,
                trigger=ContextSwitchTrigger.DOMAIN_CHANGE,
                previous_context={
                    "domain": context.current_domain.value,
                    "technologies": context.active_technologies.copy()
                },
                new_context={
                    "domain": new_domain.value,
                    "technologies": new_technologies
                },
                confidence=domain_confidence,
                reason=f"Detected domain shift from {context.current_domain.value} to {new_domain.value}"
            )
        
        # Check for expertise level shift (only if significant change and confidence)
        if (new_expertise != context.expertise_level and 
            abs(list(ExpertiseLevel).index(new_expertise) - 
                list(ExpertiseLevel).index(context.expertise_level)) > 0):
            
            # Look for strong expertise indicators in recent conversation
            recent_history = context.conversation_history[-3:] if context.conversation_history else []
            expertise_consistency = sum(
                1 for entry in recent_history 
                if self._detect_expertise_level(entry.get("user_input", "")) == new_expertise
            )
            
            if expertise_consistency >= 2:  # Consistent over multiple turns
                return ContextSwitchEvent(
                    timestamp=current_time,
                    trigger=ContextSwitchTrigger.EXPERTISE_SHIFT,
                    previous_context={
                        "expertise_level": context.expertise_level.value
                    },
                    new_context={
                        "expertise_level": new_expertise.value
                    },
                    confidence=0.8,
                    reason=f"Detected expertise shift from {context.expertise_level.value} to {new_expertise.value}"
                )
        
        # Check for new technology focus
        significant_new_tech = [tech for tech in new_technologies 
                              if tech.lower() not in [t.lower() for t in context.active_technologies]]
        
        if significant_new_tech and len(significant_new_tech) >= 2:
            return ContextSwitchEvent(
                timestamp=current_time,
                trigger=ContextSwitchTrigger.TECHNOLOGY_FOCUS,
                previous_context={
                    "technologies": context.active_technologies.copy()
                },
                new_context={
                    "technologies": context.active_technologies + significant_new_tech
                },
                confidence=0.9,
                reason=f"Detected focus on new technologies: {', '.join(significant_new_tech)}"
            )
        
        return None
    
    def _apply_context_switch(self, context: ConversationContext, switch_event: ContextSwitchEvent):
        """Apply context switch to conversation context."""
        previous_state = {
            "domain": context.current_domain,
            "expertise_level": context.expertise_level,
            "technologies": context.active_technologies.copy(),
            "security_level": context.security_level
        }
        
        # Apply changes based on switch trigger
        if switch_event.trigger == ContextSwitchTrigger.DOMAIN_CHANGE:
            new_domain_str = switch_event.new_context["domain"]
            context.current_domain = TechnicalDomain(new_domain_str)
            
            # Update technologies for new domain
            if "technologies" in switch_event.new_context:
                context.active_technologies = switch_event.new_context["technologies"]
        
        elif switch_event.trigger == ContextSwitchTrigger.EXPERTISE_SHIFT:
            new_expertise_str = switch_event.new_context["expertise_level"]
            context.expertise_level = ExpertiseLevel(new_expertise_str)
        
        elif switch_event.trigger == ContextSwitchTrigger.TECHNOLOGY_FOCUS:
            new_technologies = switch_event.new_context["technologies"]
            # Merge new technologies, keeping most recent 10
            all_technologies = list(set(context.active_technologies + new_technologies))
            context.active_technologies = all_technologies[-10:]
        
        # Update performance metrics
        context.performance_metrics["context_switches"] += 1
        
        # Clear relevant cache entries after context switch
        self._invalidate_context_cache(context, switch_event.trigger)
        
        logger.debug(
            "Applied context switch",
            session_id=context.session_id,
            trigger=switch_event.trigger.value,
            previous_state=previous_state,
            new_state={
                "domain": context.current_domain.value,
                "expertise_level": context.expertise_level.value,
                "technologies": context.active_technologies
            }
        )
    
    def _invalidate_context_cache(self, context: ConversationContext, trigger: ContextSwitchTrigger):
        """Invalidate relevant cache entries after context switch."""
        cache_keys_to_remove = []
        
        if trigger == ContextSwitchTrigger.DOMAIN_CHANGE:
            # Remove domain-specific cache entries
            cache_keys_to_remove = [k for k in context.knowledge_cache.keys() 
                                   if k.startswith("domain_") or k.startswith("knowledge_")]
        
        elif trigger == ContextSwitchTrigger.EXPERTISE_SHIFT:
            # Remove expertise-level specific cache entries
            cache_keys_to_remove = [k for k in context.knowledge_cache.keys() 
                                   if "expertise" in k or "prompt" in k]
        
        elif trigger == ContextSwitchTrigger.TECHNOLOGY_FOCUS:
            # Remove technology-specific cache entries
            cache_keys_to_remove = [k for k in context.knowledge_cache.keys() 
                                   if "tech_" in k or "guidance" in k]
        
        for key in cache_keys_to_remove:
            context.knowledge_cache.pop(key, None)
    
    def generate_contextual_prompt(
        self,
        context: ConversationContext,
        prompt_type: PromptType,
        specific_request: str = ""
    ) -> str:
        """Generate context-aware system prompt."""
        # Check cache first
        cache_key = f"prompt_{prompt_type.value}_{context.current_domain.value}_{context.expertise_level.value}"
        
        if cache_key in context.knowledge_cache:
            context.performance_metrics["cache_hits"] += 1
            cached_prompt = context.knowledge_cache[cache_key]
            
            # Add specific request context if provided
            if specific_request:
                return cached_prompt + f"\n\nSPECIFIC REQUEST CONTEXT:\n{specific_request}"
            
            return cached_prompt
        
        # Generate new prompt
        prompt_context = PromptContext(
            prompt_type=prompt_type,
            domain=context.current_domain,
            expertise_level=context.expertise_level,
            technologies=context.active_technologies,
            security_level=context.security_level,
            environment_type="production"  # Default to production for safety
        )
        
        base_prompt = self.prompts_engine.generate_system_prompt(prompt_context)
        
        # Add conversation context
        if context.conversation_history:
            recent_context = self._build_conversation_context(context)
            if recent_context:
                base_prompt += f"\n\nCONVERSATION CONTEXT:\n{recent_context}"
        
        # Cache the generated prompt
        context.knowledge_cache[cache_key] = base_prompt
        
        # Add specific request context if provided
        if specific_request:
            return base_prompt + f"\n\nSPECIFIC REQUEST CONTEXT:\n{specific_request}"
        
        return base_prompt
    
    def _build_conversation_context(self, context: ConversationContext) -> str:
        """Build conversation context summary."""
        if not context.conversation_history:
            return ""
        
        # Get recent conversation turns (last 5)
        recent_turns = context.conversation_history[-5:]
        
        context_summary = []
        
        # Add domain evolution
        domains_mentioned = set()
        for turn in recent_turns:
            snapshot = turn.get("context_snapshot", {})
            if "domain" in snapshot:
                domains_mentioned.add(snapshot["domain"])
        
        if len(domains_mentioned) > 1:
            context_summary.append(f"Conversation spans multiple domains: {', '.join(domains_mentioned)}")
        
        # Add technology focus
        all_technologies = set()
        for turn in recent_turns:
            snapshot = turn.get("context_snapshot", {})
            technologies = snapshot.get("technologies", [])
            all_technologies.update(technologies)
        
        if all_technologies:
            context_summary.append(f"Technologies discussed: {', '.join(list(all_technologies)[:5])}")
        
        # Add recent intents
        recent_intents = []
        for turn in recent_turns:
            parsed_intent = turn.get("parsed_intent", {})
            intent_type = parsed_intent.get("intent_type")
            if intent_type:
                recent_intents.append(intent_type)
        
        if recent_intents:
            unique_intents = list(set(recent_intents))
            context_summary.append(f"Recent user intents: {', '.join(unique_intents[:3])}")
        
        return "\n".join(context_summary) if context_summary else ""
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of current conversation context."""
        if session_id not in self.active_contexts:
            return {"error": "Session not found"}
        
        context = self.active_contexts[session_id]
        
        return {
            "session_id": session_id,
            "current_domain": context.current_domain.value,
            "expertise_level": context.expertise_level.value,
            "active_technologies": context.active_technologies,
            "security_level": context.security_level,
            "conversation_turns": len(context.conversation_history),
            "context_switches": len(context.context_switches),
            "last_updated": context.last_updated,
            "performance_metrics": context.performance_metrics,
            "cache_size": len(context.knowledge_cache)
        }
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Clean up inactive conversation contexts."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        inactive_sessions = [
            session_id for session_id, context in self.active_contexts.items()
            if (current_time - context.last_updated) > max_age_seconds
        ]
        
        for session_id in inactive_sessions:
            del self.active_contexts[session_id]
            logger.info("Cleaned up inactive session", session_id=session_id)
        
        return len(inactive_sessions)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics."""
        total_sessions = len(self.active_contexts)
        total_switches = sum(len(ctx.context_switches) for ctx in self.active_contexts.values())
        total_cache_hits = sum(ctx.performance_metrics.get("cache_hits", 0) 
                              for ctx in self.active_contexts.values())
        total_requests = sum(ctx.performance_metrics.get("total_requests", 0) 
                            for ctx in self.active_contexts.values())
        
        cache_hit_rate = (total_cache_hits / total_requests) if total_requests > 0 else 0.0
        
        return {
            "active_sessions": total_sessions,
            "total_context_switches": total_switches,
            "cache_hit_rate": cache_hit_rate,
            "avg_switches_per_session": total_switches / total_sessions if total_sessions > 0 else 0,
            "total_requests": total_requests,
            "total_cache_hits": total_cache_hits
        }


# Global context engine instance
smart_context_engine = SmartContextEngine()