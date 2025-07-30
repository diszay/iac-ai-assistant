"""
Natural Language Processing module for the Proxmox AI Assistant.

This module provides intelligent parsing and understanding of user prompts,
converting natural language requests into structured commands and recommendations.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class IntentType(Enum):
    """Types of user intents we can recognize."""
    CREATE_VM = "create_vm"
    DEPLOY_INFRASTRUCTURE = "deploy_infrastructure"
    GENERATE_TERRAFORM = "generate_terraform"
    GENERATE_ANSIBLE = "generate_ansible"
    SECURITY_REVIEW = "security_review"
    OPTIMIZE_CONFIG = "optimize_config"
    EXPLAIN_CODE = "explain_code"
    TROUBLESHOOT = "troubleshoot"
    BEST_PRACTICES = "best_practices"
    GENERAL_QUESTION = "general_question"
    SYSTEM_STATUS = "system_status"
    HELP = "help"


class InfrastructureType(Enum):
    """Types of infrastructure components."""
    WEB_SERVER = "web_server"
    DATABASE = "database"
    LOAD_BALANCER = "load_balancer"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    MONITORING = "monitoring"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"
    TESTING = "testing"


@dataclass
class ParsedIntent:
    """Structured representation of user intent."""
    intent_type: IntentType
    confidence: float
    infrastructure_type: Optional[InfrastructureType]
    parameters: Dict[str, Any]
    skill_level: str
    urgency: str
    entities: Dict[str, List[str]]


class NaturalLanguageProcessor:
    """
    Advanced natural language processor for infrastructure automation.
    
    Features:
    - Intent recognition from diverse user input patterns
    - Entity extraction (VM specs, network configs, etc.)
    - Context-aware parameter inference
    - Multi-language phrase matching
    - Confidence scoring for recommendations
    """
    
    def __init__(self):
        """Initialize the natural language processor."""
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        self.phrase_variations = self._load_phrase_variations()
        self.context_memory: List[ParsedIntent] = []
        
        logger.info("Natural language processor initialized")
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Load intent recognition patterns."""
        return {
            IntentType.CREATE_VM: [
                r"create.*(?:vm|virtual machine|server)",
                r"(?:spin up|deploy|provision).*(?:vm|machine|server)",
                r"need.*(?:new|fresh).*(?:vm|machine|server)",
                r"set up.*(?:vm|virtual machine)",
                r"build.*(?:vm|machine|server)",
                r"launch.*(?:vm|instance|machine)",
                r"i want.*(?:vm|machine|server)",
                r"can you.*(?:create|make|build).*(?:vm|machine)",
                r"help.*(?:create|setup).*(?:vm|machine)",
            ],
            
            IntentType.DEPLOY_INFRASTRUCTURE: [
                r"deploy.*(?:infrastructure|stack|environment)",
                r"set up.*(?:infrastructure|environment|platform)",
                r"create.*(?:infrastructure|environment|stack)",
                r"build.*(?:infrastructure|platform|environment)",
                r"provision.*(?:infrastructure|environment)",
                r"need.*(?:infrastructure|platform|stack)",
                r"want.*(?:deploy|setup).*(?:infrastructure|environment)",
                r"how.*deploy.*(?:infrastructure|stack)",
            ],
            
            IntentType.GENERATE_TERRAFORM: [
                r"(?:generate|create|write).*terraform",
                r"terraform.*(?:code|config|configuration)",
                r"need.*terraform.*(?:file|script|code)",
                r"help.*terraform",
                r"terraform.*(?:for|to)",
                r"iac.*terraform",
                r"infrastructure.*code.*terraform",
                r"tf.*(?:file|config)",
            ],
            
            IntentType.GENERATE_ANSIBLE: [
                r"(?:generate|create|write).*ansible",
                r"ansible.*(?:playbook|code|configuration)",
                r"need.*ansible.*(?:playbook|script|code)",
                r"help.*ansible",
                r"automation.*ansible",
                r"configuration.*management.*ansible",
                r"playbook.*(?:for|to)",
            ],
            
            IntentType.SECURITY_REVIEW: [
                r"security.*(?:review|audit|check|scan)",
                r"(?:check|review|audit).*security",
                r"secure.*(?:configuration|setup)",
                r"security.*(?:best practices|recommendations)",
                r"vulnerabilities.*(?:check|scan)",
                r"hardening.*(?:review|recommendations)",
                r"compliance.*(?:check|review)",
                r"is.*secure",
                r"security.*issues",
            ],
            
            IntentType.OPTIMIZE_CONFIG: [
                r"optimize.*(?:configuration|config|setup)",
                r"improve.*(?:performance|config|setup)",
                r"(?:tune|optimize).*(?:vm|server|infrastructure)",
                r"make.*(?:faster|better|efficient)",
                r"performance.*(?:optimization|tuning)",
                r"resource.*optimization",
                r"efficiency.*improvements",
                r"how.*(?:optimize|improve|tune)",
            ],
            
            IntentType.EXPLAIN_CODE: [
                r"explain.*(?:code|configuration|config)",
                r"what.*(?:does|is).*(?:code|config|configuration)",
                r"help.*understand.*(?:code|config)",
                r"(?:walk through|go through).*(?:code|config)",
                r"breakdown.*(?:code|configuration)",
                r"documentation.*(?:for|about)",
                r"how.*(?:works|does)",
                r"what.*(?:means|is)",
            ],
            
            IntentType.TROUBLESHOOT: [
                r"(?:troubleshoot|debug|fix|solve)",
                r"(?:error|problem|issue|trouble)",
                r"not.*working",
                r"fails?.*(?:to|with)",
                r"help.*(?:fix|solve|debug)",
                r"what.*wrong",
                r"why.*(?:not|doesn't|isn't)",
                r"broken.*(?:vm|infrastructure|deployment)",
            ],
            
            IntentType.BEST_PRACTICES: [
                r"best.*practices",
                r"recommendations.*(?:for|about)",
                r"what.*(?:should|recommended)",
                r"guidelines.*(?:for|about)",
                r"standards.*(?:for|about)",
                r"good.*(?:practices|approach|way)",
                r"proper.*(?:way|method|approach)",
                r"industry.*(?:standards|practices)",
            ],
            
            IntentType.SYSTEM_STATUS: [
                r"status.*(?:of|for).*(?:system|vm|infrastructure)",
                r"(?:check|show).*status",
                r"health.*(?:check|status)",
                r"monitoring.*(?:status|dashboard)",
                r"system.*(?:health|status|info)",
                r"is.*(?:running|working|up)",
                r"current.*(?:status|state)",
            ],
            
            IntentType.HELP: [
                r"help.*(?:me|with)",
                r"how.*(?:do|can).*i",
                r"what.*(?:can|should).*i",
                r"guide.*(?:me|to)",
                r"assistance.*(?:with|for)",
                r"support.*(?:for|with)",
                r"tutorial.*(?:for|on)",
                r"getting.*started",
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load entity extraction patterns."""
        return {
            "cpu_cores": [
                r"(\d+).*(?:cores?|cpus?|processors?)",
                r"(?:cores?|cpus?).*(\d+)",
                r"(\d+).*(?:core|cpu|processor)"
            ],
            "memory": [
                r"(\d+)(?:gb|mb).*(?:ram|memory)",
                r"(?:ram|memory).*(\d+)(?:gb|mb)",
                r"(\d+).*(?:gig|meg).*(?:ram|memory)"
            ],
            "disk_size": [
                r"(\d+)(?:gb|tb|mb).*(?:disk|storage|drive)",
                r"(?:disk|storage|drive).*(\d+)(?:gb|tb|mb)",
                r"(\d+).*(?:gig|terabyte|gigabyte).*(?:disk|storage)"
            ],
            "vm_count": [
                r"(\d+).*(?:vms?|virtual machines?|servers?|instances?)",
                r"(?:vms?|virtual machines?|servers?|instances?).*(\d+)",
                r"create.*(\d+).*(?:vm|machine|server)"
            ],
            "operating_system": [
                r"(?:ubuntu|debian|centos|rhel|fedora|alpine|windows)",
                r"(?:linux|unix|windows).*(?:server|desktop|vm)",
                r"(?:server|desktop).*(?:linux|windows|ubuntu|debian)"
            ],
            "application_type": [
                r"(?:web server|database|load balancer|nginx|apache|mysql|postgresql|redis|mongodb)",
                r"(?:docker|kubernetes|k8s|container|microservice)",
                r"(?:monitoring|prometheus|grafana|elasticsearch|jenkins)"
            ],
            "network_config": [
                r"(?:dhcp|static).*(?:ip|address)",
                r"(?:ip|address).*(?:dhcp|static)",
                r"(?:vlan|subnet|network).*(\d+)",
                r"port.*(\d+)"
            ],
            "security_features": [
                r"(?:firewall|ufw|iptables|security groups)",
                r"(?:ssl|tls|https|encryption)",
                r"(?:ssh|key|authentication|2fa|mfa)",
                r"(?:fail2ban|intrusion detection|ids)"
            ]
        }
    
    def _load_phrase_variations(self) -> Dict[str, List[str]]:
        """Load common phrase variations and synonyms."""
        return {
            "create_synonyms": [
                "create", "make", "build", "set up", "deploy", "provision", 
                "spin up", "launch", "establish", "initialize", "generate"
            ],
            "vm_synonyms": [
                "vm", "virtual machine", "server", "instance", "machine", 
                "node", "host", "container", "compute instance"
            ],
            "infrastructure_synonyms": [
                "infrastructure", "stack", "environment", "platform", 
                "setup", "deployment", "architecture", "system"
            ],
            "help_synonyms": [
                "help", "assist", "guide", "support", "show", "explain", 
                "walk through", "demonstrate", "teach", "tutorial"
            ],
            "optimization_synonyms": [
                "optimize", "improve", "enhance", "tune", "boost", 
                "speed up", "make better", "efficiency", "performance"
            ],
            "security_synonyms": [
                "secure", "harden", "protect", "safety", "compliance", 
                "audit", "review", "vulnerability", "threat"
            ]
        }
    
    def parse_user_input(self, user_input: str, context: Optional[Dict] = None) -> ParsedIntent:
        """
        Parse user input and extract intent, entities, and parameters.
        
        Args:
            user_input: Raw user input text
            context: Optional context from previous interactions
            
        Returns:
            ParsedIntent with structured information
        """
        # Normalize input
        normalized_input = self._normalize_input(user_input)
        
        # Detect intent
        intent_type, confidence = self._detect_intent(normalized_input)
        
        # Extract entities
        entities = self._extract_entities(normalized_input)
        
        # Infer parameters
        parameters = self._infer_parameters(normalized_input, entities, context)
        
        # Determine skill level from context
        skill_level = self._determine_skill_level(normalized_input, context)
        
        # Assess urgency
        urgency = self._assess_urgency(normalized_input)
        
        # Detect infrastructure type
        infrastructure_type = self._detect_infrastructure_type(normalized_input, entities)
        
        parsed_intent = ParsedIntent(
            intent_type=intent_type,
            confidence=confidence,
            infrastructure_type=infrastructure_type,
            parameters=parameters,
            skill_level=skill_level,
            urgency=urgency,
            entities=entities
        )
        
        # Update context memory
        self._update_context_memory(parsed_intent)
        
        logger.info(
            "Parsed user intent",
            intent=intent_type.value,
            confidence=confidence,
            skill_level=skill_level,
            entities=entities
        )
        
        return parsed_intent
    
    def _normalize_input(self, text: str) -> str:
        """Normalize user input for better pattern matching."""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Replace common abbreviations
        replacements = {
            "vm's": "virtual machines",
            "vms": "virtual machines", 
            "k8s": "kubernetes",
            "tf": "terraform",
            "infra": "infrastructure",
            "config": "configuration",
            "sec": "security",
            "perf": "performance",
            "db": "database",
            "lb": "load balancer",
            "nginx": "web server",
            "apache": "web server",
            "mysql": "database",
            "postgresql": "database",
            "redis": "database"
        }
        
        for abbrev, full_form in replacements.items():
            text = re.sub(r'\b' + abbrev + r'\b', full_form, text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\.\?\!]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _detect_intent(self, text: str) -> Tuple[IntentType, float]:
        """Detect user intent from normalized text."""
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
                    # Weight score by pattern specificity
                    pattern_weight = len(pattern.split()) / 10.0
                    score += (1.0 + pattern_weight)
            
            if matches > 0:
                # Normalize score by number of patterns
                intent_scores[intent_type] = score / len(patterns)
        
        if not intent_scores:
            return IntentType.GENERAL_QUESTION, 0.5
        
        # Get highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        return best_intent[0], min(best_intent[1], 1.0)
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using pattern matching."""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    matches.extend([match for match in found if match])
            
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities
    
    def _infer_parameters(self, text: str, entities: Dict[str, List[str]], context: Optional[Dict]) -> Dict[str, Any]:
        """Infer infrastructure parameters from text and entities."""
        parameters = {}
        
        # VM specifications
        if "cpu_cores" in entities:
            parameters["cpu_cores"] = int(entities["cpu_cores"][0])
        elif any(word in text for word in ["small", "minimal", "light"]):
            parameters["cpu_cores"] = 1
        elif any(word in text for word in ["medium", "standard", "normal"]):
            parameters["cpu_cores"] = 2
        elif any(word in text for word in ["large", "powerful", "high performance"]):
            parameters["cpu_cores"] = 4
        
        if "memory" in entities:
            memory_str = entities["memory"][0]
            if "gb" in memory_str.lower():
                parameters["memory_gb"] = int(re.findall(r'\d+', memory_str)[0])
            elif "mb" in memory_str.lower():
                parameters["memory_gb"] = int(re.findall(r'\d+', memory_str)[0]) / 1024
        
        if "disk_size" in entities:
            disk_str = entities["disk_size"][0]
            if "gb" in disk_str.lower():
                parameters["disk_size_gb"] = int(re.findall(r'\d+', disk_str)[0])
            elif "tb" in disk_str.lower():
                parameters["disk_size_gb"] = int(re.findall(r'\d+', disk_str)[0]) * 1024
        
        if "vm_count" in entities:
            parameters["vm_count"] = int(entities["vm_count"][0])
        
        # Operating system
        if "operating_system" in entities:
            parameters["os"] = entities["operating_system"][0]
        elif any(os_name in text for os_name in ["ubuntu", "debian", "centos", "rhel"]):
            for os_name in ["ubuntu", "debian", "centos", "rhel"]:
                if os_name in text:
                    parameters["os"] = os_name
                    break
        
        # Environment type
        if any(env in text for env in ["development", "dev", "testing", "test"]):
            parameters["environment"] = "development"
        elif any(env in text for env in ["staging", "stage", "uat"]):
            parameters["environment"] = "staging"
        elif any(env in text for env in ["production", "prod", "live"]):
            parameters["environment"] = "production"
        
        # Security level
        if any(sec in text for sec in ["high security", "secure", "hardened", "compliant"]):
            parameters["security_level"] = "high"
        elif any(sec in text for sec in ["basic security", "standard security"]):
            parameters["security_level"] = "medium"
        else:
            parameters["security_level"] = "medium"  # Default
        
        # Network configuration
        if any(net in text for net in ["static ip", "fixed ip", "static address"]):
            parameters["network_type"] = "static"
        elif "dhcp" in text:
            parameters["network_type"] = "dhcp"
        
        return parameters
    
    def _determine_skill_level(self, text: str, context: Optional[Dict]) -> str:
        """Determine user skill level from input patterns."""
        # Expert indicators
        expert_indicators = [
            "terraform", "ansible", "kubernetes", "docker", "cicd", "devops",
            "infrastructure as code", "automation", "orchestration", "helm",
            "prometheus", "grafana", "elk stack", "microservices"
        ]
        
        # Beginner indicators
        beginner_indicators = [
            "new to", "beginner", "first time", "don't know", "help me understand",
            "what is", "how do i", "step by step", "tutorial", "guide me"
        ]
        
        expert_score = sum(1 for indicator in expert_indicators if indicator in text)
        beginner_score = sum(1 for indicator in beginner_indicators if indicator in text)
        
        if expert_score > beginner_score and expert_score >= 2:
            return "expert"
        elif beginner_score > expert_score and beginner_score >= 1:
            return "beginner"
        else:
            return "intermediate"
    
    def _assess_urgency(self, text: str) -> str:
        """Assess urgency level from user input."""
        urgent_indicators = [
            "urgent", "asap", "immediately", "right now", "emergency",
            "critical", "production down", "broken", "not working"
        ]
        
        if any(indicator in text for indicator in urgent_indicators):
            return "high"
        elif any(word in text for word in ["soon", "today", "quickly"]):
            return "medium"
        else:
            return "low"
    
    def _detect_infrastructure_type(self, text: str, entities: Dict[str, List[str]]) -> Optional[InfrastructureType]:
        """Detect the type of infrastructure being requested."""
        type_mapping = {
            "web server": InfrastructureType.WEB_SERVER,
            "database": InfrastructureType.DATABASE,
            "load balancer": InfrastructureType.LOAD_BALANCER,
            "kubernetes": InfrastructureType.KUBERNETES,
            "docker": InfrastructureType.DOCKER,
            "monitoring": InfrastructureType.MONITORING,
            "development": InfrastructureType.DEVELOPMENT,
            "production": InfrastructureType.PRODUCTION,
            "staging": InfrastructureType.STAGING,
            "testing": InfrastructureType.TESTING
        }
        
        for keyword, infra_type in type_mapping.items():
            if keyword in text:
                return infra_type
        
        # Check entities for infrastructure type
        if "application_type" in entities:
            app_type = entities["application_type"][0].lower()
            for keyword, infra_type in type_mapping.items():
                if keyword in app_type:
                    return infra_type
        
        return None
    
    def _update_context_memory(self, parsed_intent: ParsedIntent):
        """Update context memory with recent interactions."""
        self.context_memory.append(parsed_intent)
        
        # Keep only last 10 interactions for context
        if len(self.context_memory) > 10:
            self.context_memory.pop(0)
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context for the AI model."""
        if not self.context_memory:
            return {}
        
        recent_intents = [intent.intent_type.value for intent in self.context_memory[-3:]]
        common_skill_level = max(set([intent.skill_level for intent in self.context_memory[-5:]]), 
                               key=[intent.skill_level for intent in self.context_memory[-5:]].count)
        
        context = {
            "recent_intents": recent_intents,
            "user_skill_level": common_skill_level,
            "conversation_flow": len(self.context_memory),
            "last_infrastructure_type": self.context_memory[-1].infrastructure_type.value if self.context_memory[-1].infrastructure_type else None
        }
        
        return context
    
    def generate_prompt_enhancement(self, parsed_intent: ParsedIntent) -> str:
        """Generate enhanced prompt for the AI model based on parsed intent."""
        context = self.get_conversation_context()
        
        base_prompt = f"""
        INFRASTRUCTURE REQUEST ANALYSIS:
        
        User Intent: {parsed_intent.intent_type.value}
        Confidence Level: {parsed_intent.confidence:.2f}
        Skill Level: {parsed_intent.skill_level}
        Urgency: {parsed_intent.urgency}
        
        Infrastructure Type: {parsed_intent.infrastructure_type.value if parsed_intent.infrastructure_type else 'Not specified'}
        
        Extracted Parameters:
        {json.dumps(parsed_intent.parameters, indent=2)}
        
        Detected Entities:
        {json.dumps(parsed_intent.entities, indent=2)}
        
        Conversation Context:
        {json.dumps(context, indent=2)}
        
        INSTRUCTIONS FOR AI RESPONSE:
        1. Provide response appropriate for {parsed_intent.skill_level} skill level
        2. Address the specific intent: {parsed_intent.intent_type.value}
        3. Include security best practices for {parsed_intent.parameters.get('security_level', 'medium')} security level
        4. If generating code, include comments and explanations suitable for {parsed_intent.skill_level} level
        5. Consider the urgency level: {parsed_intent.urgency}
        6. Maintain consistency with previous conversation context
        
        """
        
        return base_prompt.strip()


# Global instance for use throughout the application
nlp_processor = NaturalLanguageProcessor()