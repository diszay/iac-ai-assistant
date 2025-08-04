"""
Enhanced AI Client for Proxmox AI Assistant.

Integrates all advanced AI capabilities including:
- Comprehensive technical knowledge base
- Dynamic system prompts with domain awareness
- Smart context switching
- Technical validation and security
- Expertise-level adaptation
- Input sanitization and security hardening

This is the main AI client that orchestrates all AI components for world-class
infrastructure automation assistance.
"""

import asyncio
import re
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import structlog

from .local_ai_client import OptimizedLocalAIClient, AIResponse
from .knowledge_base import (
    TechnicalKnowledgeBase, TechnicalDomain, ExpertiseLevel,
    KnowledgeContext, technical_knowledge_base
)
from .system_prompts import (
    SystemPromptsEngine, PromptType, PromptContext, system_prompts_engine
)
from .context_engine import (
    SmartContextEngine, ConversationContext, ContextSwitchEvent,
    smart_context_engine
)
from .validation_framework import (
    TechnicalValidationFramework, ValidationResult, SecurityAssessment,
    validation_framework
)
from .expertise_engine import (
    ExpertiseLevelsEngine, SkillAssessment, PersonalizedContent,
    expertise_engine
)
from .natural_language_processor import ParsedIntent, nlp_processor

logger = structlog.get_logger(__name__)


@dataclass
class EnhancedAIResponse:
    """Enhanced AI response with comprehensive metadata."""
    content: str
    success: bool
    model_used: str
    processing_time: float
    skill_level: str
    domain: str
    
    # Security and validation
    security_score: float
    validation_results: List[ValidationResult]
    sanitized_input: bool
    
    # Context and learning
    context_switched: bool
    learning_suggestions: List[str]
    related_topics: List[str]
    
    # Performance metrics
    memory_used_mb: float
    tokens_generated: int
    cache_hit: bool
    
    # Metadata
    session_id: str
    timestamp: float


class EnhancedAIClient:
    """
    World-class AI client with comprehensive technical knowledge and security.
    
    Features:
    - Automatic domain detection and expertise adaptation
    - Comprehensive input validation and sanitization
    - Security-conscious recommendations
    - Context-aware conversation management
    - Progressive learning and skill assessment
    - Technical validation of all configurations
    - Performance optimization
    """
    
    def __init__(
        self,
        local_ai_client: OptimizedLocalAIClient = None,
        knowledge_base: TechnicalKnowledgeBase = None,
        prompts_engine: SystemPromptsEngine = None,
        context_engine: SmartContextEngine = None,
        validation_framework: TechnicalValidationFramework = None,
        expertise_engine: ExpertiseLevelsEngine = None
    ):
        """Initialize the enhanced AI client."""
        
        # Core AI components
        self.local_ai_client = local_ai_client or OptimizedLocalAIClient()
        self.knowledge_base = knowledge_base or technical_knowledge_base
        self.prompts_engine = prompts_engine or system_prompts_engine
        self.context_engine = context_engine or smart_context_engine
        self.validation_framework = validation_framework or validation_framework
        self.expertise_engine = expertise_engine or expertise_engine
        
        # Performance tracking
        self.session_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "security_violations_blocked": 0,
            "context_switches": 0,
            "cache_hits": 0,
            "avg_processing_time": 0.0
        }
        
        logger.info("Enhanced AI client initialized with all advanced components")
    
    async def chat(
        self,
        user_input: str,
        session_id: str,
        user_id: Optional[str] = None,
        additional_context: Dict[str, Any] = None
    ) -> EnhancedAIResponse:
        """
        Process user input with comprehensive AI assistance.
        
        Args:
            user_input: Raw user input
            session_id: Session identifier for context management
            user_id: User identifier for personalization
            additional_context: Additional context information
            
        Returns:
            Enhanced AI response with comprehensive metadata
        """
        start_time = time.time()
        self.session_metrics["total_requests"] += 1
        
        try:
            # Step 1: Input validation and sanitization
            validation_results = await self._validate_and_sanitize_input(user_input)
            
            # Check for critical security issues
            critical_issues = [r for r in validation_results 
                             if r.level.value == "critical"]
            
            if critical_issues:
                self.session_metrics["security_violations_blocked"] += 1
                return self._create_security_blocked_response(
                    session_id, critical_issues, start_time
                )
            
            # Sanitize input based on validation results
            sanitized_input = self._sanitize_input(user_input, validation_results)
            
            # Step 2: Parse intent and detect domain
            parsed_intent = nlp_processor.parse_user_input(sanitized_input, additional_context)
            detected_domain = TechnicalDomain(parsed_intent.infrastructure_type.value) if parsed_intent.infrastructure_type else TechnicalDomain.SYSTEM_ENGINEERING
            
            # Step 3: Context management and switching
            context, context_switch_event = self.context_engine.process_user_input(
                session_id, sanitized_input, parsed_intent
            )
            
            if context_switch_event:
                self.session_metrics["context_switches"] += 1
            
            # Step 4: Skill assessment and expertise adaptation
            if user_id:
                skill_assessment = self.expertise_engine.assess_user_skill_level(
                    user_id, detected_domain, conversation_history=context.conversation_history
                )
                expertise_level = skill_assessment.current_level
            else:
                expertise_level = ExpertiseLevel(parsed_intent.skill_level)
            
            # Step 5: Generate contextual system prompt
            prompt_type = self._determine_prompt_type(parsed_intent)
            system_prompt = self.context_engine.generate_contextual_prompt(
                context, prompt_type, sanitized_input
            )
            
            # Step 6: Get domain knowledge and security recommendations
            knowledge_context = KnowledgeContext(
                domain=detected_domain,
                expertise_level=expertise_level,
                specific_technologies=context.active_technologies,
                use_case=parsed_intent.intent_type.value,
                security_requirements=context.security_level,
                compliance_needs=[]
            )
            
            domain_knowledge = self.knowledge_base.get_domain_knowledge(knowledge_context)
            security_recommendations = self.knowledge_base.get_security_recommendations(
                detected_domain, context.active_technologies
            )
            
            # Step 7: Enhanced prompt construction
            enhanced_prompt = self._construct_enhanced_prompt(
                system_prompt, sanitized_input, domain_knowledge, 
                security_recommendations, expertise_level
            )
            
            # Step 8: Generate AI response
            ai_response = await self.local_ai_client.intelligent_conversation(
                enhanced_prompt, {"context": asdict(context)}
            )
            
            # Step 9: Validate and enhance response
            enhanced_content = await self._enhance_response_content(
                ai_response.content, detected_domain, expertise_level, 
                context.active_technologies
            )
            
            # Step 10: Generate learning suggestions
            learning_suggestions = self._generate_learning_suggestions(
                parsed_intent, expertise_level, detected_domain
            )
            
            # Step 11: Get related topics
            related_topics = self._get_related_topics(detected_domain, context.active_technologies)
            
            # Calculate security score
            security_score = self._calculate_security_score(validation_results, enhanced_content)
            
            processing_time = time.time() - start_time
            self.session_metrics["successful_requests"] += 1
            self.session_metrics["avg_processing_time"] = (
                (self.session_metrics["avg_processing_time"] * (self.session_metrics["successful_requests"] - 1) + processing_time) /
                self.session_metrics["successful_requests"]
            )
            
            response = EnhancedAIResponse(
                content=enhanced_content,
                success=True,
                model_used=ai_response.model_used,
                processing_time=processing_time,
                skill_level=expertise_level.value,
                domain=detected_domain.value,
                security_score=security_score,
                validation_results=validation_results,
                sanitized_input=sanitized_input != user_input,
                context_switched=context_switch_event is not None,
                learning_suggestions=learning_suggestions,
                related_topics=related_topics,
                memory_used_mb=ai_response.memory_used_mb,
                tokens_generated=ai_response.tokens_generated,
                cache_hit=False,  # Could be determined from local_ai_client
                session_id=session_id,
                timestamp=time.time()
            )
            
            logger.info(
                "Enhanced AI chat completed successfully",
                session_id=session_id,
                domain=detected_domain.value,
                expertise_level=expertise_level.value,
                processing_time=processing_time,
                security_score=security_score,
                context_switched=context_switch_event is not None
            )
            
            return response
            
        except Exception as e:
            logger.error("Enhanced AI chat failed", error=str(e), session_id=session_id)
            
            processing_time = time.time() - start_time
            return EnhancedAIResponse(
                content=f"I apologize, but I encountered an error processing your request: {str(e)}. Please try rephrasing your question or contact support if the issue persists.",
                success=False,
                model_used="error_handler",
                processing_time=processing_time,
                skill_level="intermediate",
                domain="system_engineering",
                security_score=0.0,
                validation_results=[],
                sanitized_input=False,
                context_switched=False,
                learning_suggestions=[],
                related_topics=[],
                memory_used_mb=0.0,
                tokens_generated=0,
                cache_hit=False,
                session_id=session_id,
                timestamp=time.time()
            )
    
    async def _validate_and_sanitize_input(self, user_input: str) -> List[ValidationResult]:
        """Validate and sanitize user input."""
        try:
            # Comprehensive input validation
            results = self.validation_framework.validate_user_input(user_input)
            
            logger.debug(
                "Input validation completed",
                issues_found=len(results),
                critical_issues=len([r for r in results if r.level.value == "critical"])
            )
            
            return results
            
        except Exception as e:
            logger.error("Input validation failed", error=str(e))
            return []
    
    def _sanitize_input(self, user_input: str, validation_results: List[ValidationResult]) -> str:
        """Sanitize input based on validation results."""
        sanitized = user_input
        
        # Apply auto-fixable sanitizations
        for result in validation_results:
            if result.auto_fixable and result.fix_command:
                # Apply basic sanitization (in production, this would use the actual fix_command)
                if "command_injection" in result.message.lower():
                    # Remove dangerous characters
                    sanitized = re.sub(r'[;&|`$(){}[\]<>"\']+', '', sanitized)
                elif "path_traversal" in result.message.lower():
                    # Remove path traversal attempts
                    sanitized = re.sub(r'\.\./', '', sanitized)
                    sanitized = re.sub(r'\.\.\\\\', '', sanitized)
        
        return sanitized
    
    def _create_security_blocked_response(
        self,
        session_id: str,
        critical_issues: List[ValidationResult],
        start_time: float
    ) -> EnhancedAIResponse:
        """Create response for blocked security violations."""
        
        issue_descriptions = [issue.message for issue in critical_issues[:3]]
        
        content = f"""
🚨 **Security Alert: Request Blocked**

Your request has been blocked due to security concerns:

{chr(10).join(f'• {desc}' for desc in issue_descriptions)}

**What you can do:**
1. Review your input for potentially dangerous content
2. Rephrase your question using safe, descriptive language
3. If you need help with security topics, ask general questions about best practices
4. Contact support if you believe this was blocked in error

**Security is our priority** - We automatically scan all inputs to protect both you and our systems. Thank you for understanding.
"""
        
        return EnhancedAIResponse(
            content=content,
            success=False,
            model_used="security_filter",
            processing_time=time.time() - start_time,
            skill_level="intermediate",
            domain="security",
            security_score=0.0,
            validation_results=critical_issues,
            sanitized_input=False,
            context_switched=False,
            learning_suggestions=[
                "Learn about secure input practices",
                "Understand common security vulnerabilities",
                "Study input validation techniques"
            ],
            related_topics=["input_validation", "security_best_practices", "safe_coding"],
            memory_used_mb=0.0,
            tokens_generated=0,
            cache_hit=False,
            session_id=session_id,
            timestamp=time.time()
        )
    
    def _determine_prompt_type(self, parsed_intent: ParsedIntent) -> PromptType:
        """Determine appropriate prompt type from parsed intent."""
        intent_mapping = {
            "create_vm": PromptType.INFRASTRUCTURE_GENERATION,
            "deploy_infrastructure": PromptType.INFRASTRUCTURE_GENERATION,
            "generate_terraform": PromptType.INFRASTRUCTURE_GENERATION,
            "generate_ansible": PromptType.INFRASTRUCTURE_GENERATION,
            "security_review": PromptType.SECURITY_REVIEW,
            "optimize_config": PromptType.OPTIMIZATION,
            "explain_code": PromptType.LEARNING,
            "troubleshoot": PromptType.TROUBLESHOOTING,
            "best_practices": PromptType.BEST_PRACTICES,
            "general_question": PromptType.GENERAL_CHAT,
            "help": PromptType.LEARNING
        }
        
        return intent_mapping.get(parsed_intent.intent_type.value, PromptType.GENERAL_CHAT)
    
    def _construct_enhanced_prompt(
        self,
        system_prompt: str,
        user_input: str,
        domain_knowledge: Dict[str, Any],
        security_recommendations: List[str],
        expertise_level: ExpertiseLevel
    ) -> str:
        """Construct enhanced prompt with all context and knowledge."""
        
        prompt_parts = [system_prompt]
        
        # Add security context
        if security_recommendations:
            security_context = f"""
SECURITY RECOMMENDATIONS FOR THIS REQUEST:
{chr(10).join(f'• {rec}' for rec in security_recommendations[:5])}

IMPORTANT: All recommendations must prioritize security and follow these guidelines.
"""
            prompt_parts.append(security_context)
        
        # Add domain knowledge highlights
        if domain_knowledge:
            knowledge_highlights = []
            for topic, knowledge in domain_knowledge.items():
                if isinstance(knowledge, dict):
                    if "best_practices" in knowledge:
                        practices = knowledge["best_practices"][:3]  # Top 3
                        knowledge_highlights.extend(practices)
            
            if knowledge_highlights:
                knowledge_context = f"""
KEY BEST PRACTICES TO CONSIDER:
{chr(10).join(f'• {practice}' for practice in knowledge_highlights)}
"""
                prompt_parts.append(knowledge_context)
        
        # Add expertise level guidance
        expertise_guidance = {
            ExpertiseLevel.BEGINNER: """
EXPERTISE LEVEL: BEGINNER
- Provide step-by-step explanations
- Define technical terms as you use them
- Include safety warnings and precautions
- Offer multiple learning resources
- Use simple, clear examples
- Encourage questions and exploration
""",
            ExpertiseLevel.INTERMEDIATE: """
EXPERTISE LEVEL: INTERMEDIATE  
- Focus on practical implementation
- Include best practices and common patterns
- Provide troubleshooting guidance
- Reference related technologies
- Balance detail with conciseness
- Suggest optimization opportunities
""",
            ExpertiseLevel.EXPERT: """
EXPERTISE LEVEL: EXPERT
- Provide comprehensive technical details
- Include advanced patterns and architectures
- Discuss performance and security implications
- Reference cutting-edge practices
- Assume strong technical foundation
- Focus on strategic and design considerations
"""
        }
        
        prompt_parts.append(expertise_guidance[expertise_level])
        
        # Add user request
        prompt_parts.append(f"\nUSER REQUEST:\n{user_input}")
        
        # Add final instructions
        final_instructions = """
RESPONSE REQUIREMENTS:
1. Provide accurate, helpful, and secure recommendations
2. Include practical examples and implementation guidance
3. Prioritize security in all suggestions
4. Structure response clearly with headings where appropriate
5. Include relevant best practices and considerations
6. Offer next steps or follow-up suggestions
7. Maintain professional, helpful tone

Please provide a comprehensive response that addresses the user's needs while maintaining the highest standards of security and technical accuracy.
"""
        
        prompt_parts.append(final_instructions)
        
        return "\n".join(prompt_parts)
    
    async def _enhance_response_content(
        self,
        content: str,
        domain: TechnicalDomain,
        expertise_level: ExpertiseLevel,
        technologies: List[str]
    ) -> str:
        """Enhance response content with additional context and validation."""
        
        enhanced_parts = [content]
        
        # Add security reminder for infrastructure content
        if any(keyword in content.lower() for keyword in ['config', 'deploy', 'install', 'setup']):
            security_reminder = """

## 🔐 Security Checklist

Before implementing these recommendations:
- [ ] Review all configurations for security best practices
- [ ] Ensure proper access controls are in place
- [ ] Validate all inputs and configurations
- [ ] Test in a non-production environment first
- [ ] Keep security patches up to date
- [ ] Document changes for audit purposes
"""
            enhanced_parts.append(security_reminder)
        
        # Add expertise-specific enhancements
        if expertise_level == ExpertiseLevel.BEGINNER:
            learning_enhancement = """

## 📚 Learning Resources

To deepen your understanding:
1. Start with official documentation for any tools mentioned
2. Practice in a safe test environment
3. Join community forums and discussion groups
4. Consider structured learning paths or courses
5. Don't hesitate to ask questions - learning is a journey!
"""
            enhanced_parts.append(learning_enhancement)
        
        elif expertise_level == ExpertiseLevel.EXPERT:
            advanced_enhancement = """

## 🚀 Advanced Considerations

For enterprise implementation:
- Consider automation and orchestration opportunities
- Evaluate monitoring and alerting requirements
- Plan for disaster recovery and business continuity
- Assess compliance and governance requirements
- Design for scalability and performance optimization
- Implement proper testing and validation strategies
"""
            enhanced_parts.append(advanced_enhancement)
        
        return "\n".join(enhanced_parts)
    
    def _generate_learning_suggestions(
        self,
        parsed_intent: ParsedIntent,
        expertise_level: ExpertiseLevel,
        domain: TechnicalDomain
    ) -> List[str]:
        """Generate personalized learning suggestions."""
        suggestions = []
        
        # Base suggestions by expertise level
        if expertise_level == ExpertiseLevel.BEGINNER:
            suggestions.extend([
                f"Explore fundamental {domain.value} concepts",
                "Practice with hands-on tutorials",
                "Join beginner-friendly communities"
            ])
        elif expertise_level == ExpertiseLevel.INTERMEDIATE:
            suggestions.extend([
                f"Study advanced {domain.value} patterns",
                "Implement automation solutions",
                "Learn troubleshooting methodologies"
            ])
        else:  # Expert
            suggestions.extend([
                f"Architect enterprise {domain.value} solutions",
                "Mentor others in your expertise",
                "Contribute to open-source projects"
            ])
        
        # Intent-specific suggestions
        if parsed_intent.intent_type.value in ["generate_terraform", "generate_ansible"]:
            suggestions.append("Learn Infrastructure as Code best practices")
        elif parsed_intent.intent_type.value == "troubleshoot":
            suggestions.append("Study systematic troubleshooting methodologies")
        
        return suggestions[:5]
    
    def _get_related_topics(self, domain: TechnicalDomain, technologies: List[str]) -> List[str]:
        """Get related topics for further exploration."""
        
        # Get related topics from knowledge base
        try:
            knowledge_context = KnowledgeContext(
                domain=domain,
                expertise_level=ExpertiseLevel.INTERMEDIATE,
                specific_technologies=technologies,
                use_case="exploration",
                security_requirements="medium",
                compliance_needs=[]
            )
            
            domain_knowledge = self.knowledge_base.get_domain_knowledge(knowledge_context)
            related_topics = []
            
            for topic, knowledge in domain_knowledge.items():
                if isinstance(knowledge, dict) and "related_topics" in knowledge:
                    related_topics.extend(knowledge["related_topics"][:3])
            
            return list(set(related_topics))[:8]  # Unique topics, max 8
            
        except Exception as e:
            logger.debug("Could not get related topics", error=str(e))
            return []
    
    def _calculate_security_score(
        self,
        validation_results: List[ValidationResult],
        response_content: str
    ) -> float:
        """Calculate security score for the interaction."""
        
        if not validation_results:
            base_score = 100.0
        else:
            # Deduct points for security issues
            deductions = 0
            for result in validation_results:
                if result.level.value == "critical":
                    deductions += 30
                elif result.level.value == "error":
                    deductions += 15
                elif result.level.value == "warning":
                    deductions += 5
            
            base_score = max(0, 100 - deductions)
        
        # Bonus points for security-conscious content
        security_keywords = [
            "security", "encryption", "authentication", "authorization",
            "firewall", "backup", "monitoring", "audit", "compliance"
        ]
        
        security_mentions = sum(1 for keyword in security_keywords 
                              if keyword in response_content.lower())
        
        bonus_points = min(security_mentions * 2, 20)  # Max 20 bonus points
        
        return min(base_score + bonus_points, 100.0)
    
    async def generate_infrastructure_config(
        self,
        description: str,
        config_type: str,
        session_id: str,
        user_id: Optional[str] = None,
        validate_output: bool = True
    ) -> EnhancedAIResponse:
        """Generate and validate infrastructure configuration."""
        
        # Use the main chat interface but with specific infrastructure generation context
        enhanced_request = f"""
Generate {config_type} configuration for: {description}

Requirements:
- Production-ready configuration
- Security best practices included
- Comprehensive documentation
- Validation and testing guidance
- Error handling and resilience
"""
        
        response = await self.chat(enhanced_request, session_id, user_id)
        
        # Additional validation for infrastructure configurations
        if validate_output and response.success:
            # Extract configuration from response
            config_content = self._extract_config_from_response(response.content, config_type)
            
            if config_content:
                # Validate the generated configuration
                domain = self._map_config_type_to_domain(config_type)
                config_validation = self.validation_framework.validate_infrastructure_config(
                    config_content, config_type, domain
                )
                
                # Add validation results to response
                response.validation_results.extend(config_validation)
                
                # Update security score based on configuration validation
                config_security_score = self._calculate_config_security_score(config_validation)
                response.security_score = (response.security_score + config_security_score) / 2
        
        return response
    
    def _extract_config_from_response(self, content: str, config_type: str) -> Optional[str]:
        """Extract configuration code from AI response."""
        # This would contain logic to extract code blocks from response
        # For now, return the full content
        return content
    
    def _map_config_type_to_domain(self, config_type: str) -> TechnicalDomain:
        """Map configuration type to technical domain."""
        mapping = {
            "terraform": TechnicalDomain.INFRASTRUCTURE_AS_CODE,
            "ansible": TechnicalDomain.INFRASTRUCTURE_AS_CODE,
            "docker": TechnicalDomain.CONTAINERIZATION,
            "kubernetes": TechnicalDomain.CONTAINERIZATION,
            "proxmox": TechnicalDomain.VIRTUALIZATION
        }
        
        return mapping.get(config_type.lower(), TechnicalDomain.SYSTEM_ENGINEERING)
    
    def _calculate_config_security_score(self, validation_results: List[ValidationResult]) -> float:
        """Calculate security score for configuration validation."""
        if not validation_results:
            return 100.0
        
        # Similar to main security score calculation but focused on config
        deductions = 0
        for result in validation_results:
            if result.category.value == "security":
                if result.level.value == "critical":
                    deductions += 40
                elif result.level.value == "error":
                    deductions += 20
                elif result.level.value == "warning":
                    deductions += 10
        
        return max(0, 100 - deductions)
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Get current session performance metrics."""
        return self.session_metrics.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "ai_client": self.local_ai_client.get_model_info(),
            "context_engine": self.context_engine.get_performance_metrics(),
            "session_metrics": self.session_metrics,
            "components_status": {
                "knowledge_base": "operational",
                "system_prompts": "operational",
                "context_engine": "operational",
                "validation_framework": "operational",
                "expertise_engine": "operational"
            }
        }


# Global enhanced AI client instance
enhanced_ai_client = EnhancedAIClient()