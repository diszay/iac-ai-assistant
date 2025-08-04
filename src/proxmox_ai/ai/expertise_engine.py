"""
Expertise Levels Engine for Proxmox AI Assistant.

Provides adaptive learning modes with appropriate technical depth for different
user expertise levels. Automatically adjusts response complexity, examples,
and guidance based on user skill level and learning progression.

Features:
- Dynamic expertise level detection and adaptation
- Progressive learning path generation
- Skill assessment and tracking
- Personalized content delivery
- Learning objective alignment
- Interactive tutorial generation
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

from .knowledge_base import (
    TechnicalDomain, TechnicalKnowledgeBase, ExpertiseLevel,
    KnowledgeContext, technical_knowledge_base
)

logger = structlog.get_logger(__name__)


class LearningObjective(Enum):
    """Learning objectives for different expertise levels."""
    UNDERSTAND_BASICS = "understand_basics"
    APPLY_CONCEPTS = "apply_concepts"
    ANALYZE_SYSTEMS = "analyze_systems"
    DESIGN_SOLUTIONS = "design_solutions"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    TEACH_OTHERS = "teach_others"


class LearningStyle(Enum):
    """Different learning style preferences."""
    VISUAL = "visual"
    HANDS_ON = "hands_on"
    THEORETICAL = "theoretical"
    EXAMPLE_DRIVEN = "example_driven"
    PROBLEM_SOLVING = "problem_solving"


@dataclass
class LearningPath:
    """Structured learning path for a domain."""
    domain: TechnicalDomain
    start_level: ExpertiseLevel
    target_level: ExpertiseLevel
    prerequisites: List[str]
    learning_modules: List[Dict[str, Any]]
    estimated_duration: str
    success_criteria: List[str]
    resources: List[str]


@dataclass
class SkillAssessment:
    """User skill assessment results."""
    domain: TechnicalDomain
    current_level: ExpertiseLevel
    confidence_level: float  # 0.0 to 1.0
    strengths: List[str]
    knowledge_gaps: List[str]
    recommended_topics: List[str]
    next_objectives: List[LearningObjective]
    assessment_date: float


@dataclass
class PersonalizedContent:
    """Personalized content for user's expertise level."""
    content_type: str
    title: str
    description: str
    difficulty_level: ExpertiseLevel
    prerequisites: List[str]
    learning_objectives: List[str]
    content: str
    examples: List[Dict[str, Any]]
    exercises: List[Dict[str, Any]]
    references: List[str]
    estimated_time: str


class ExpertiseLevelsEngine:
    """
    Expertise levels engine with adaptive learning capabilities.
    
    Features:
    - Automatic expertise level detection from user interactions
    - Personalized content generation based on skill level
    - Progressive learning path creation
    - Skill gap analysis and recommendations
    - Interactive tutorial and exercise generation
    - Learning progress tracking
    """
    
    def __init__(self, knowledge_base: TechnicalKnowledgeBase = None):
        """Initialize the expertise levels engine."""
        self.knowledge_base = knowledge_base or technical_knowledge_base
        
        # Learning content templates by expertise level
        self.content_templates = self._initialize_content_templates()
        
        # Learning paths for different domains
        self.learning_paths = self._initialize_learning_paths()
        
        # Skill assessment criteria
        self.assessment_criteria = self._initialize_assessment_criteria()
        
        # User learning profiles (in production, this would be persistent storage)
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Expertise levels engine initialized")
    
    def _initialize_content_templates(self) -> Dict[ExpertiseLevel, Dict[str, Any]]:
        """Initialize content templates for different expertise levels."""
        return {
            ExpertiseLevel.BEGINNER: {
                "introduction_style": "Start with fundamental concepts and build gradually",
                "explanation_depth": "Detailed step-by-step explanations with context",
                "example_complexity": "Simple, real-world examples with complete code",
                "terminology": "Define technical terms as they are introduced",
                "assumptions": "Assume minimal prior knowledge in the domain",
                "guidance_level": "Provide explicit guidance and safety warnings",
                "learning_pace": "Slower pace with repetition and reinforcement",
                "content_structure": [
                    "Overview and context",
                    "Prerequisites check",
                    "Core concepts explanation",
                    "Simple examples",
                    "Hands-on practice",
                    "Common mistakes to avoid",
                    "Next steps and resources"
                ],
                "interaction_style": "Encouraging, patient, comprehensive",
                "error_handling": "Extensive troubleshooting guides and common solutions"
            },
            
            ExpertiseLevel.INTERMEDIATE: {
                "introduction_style": "Quick overview then dive into practical applications",
                "explanation_depth": "Balanced detail with focus on practical implementation",
                "example_complexity": "Realistic scenarios with some complexity",
                "terminology": "Use standard terminology with brief clarifications",
                "assumptions": "Basic familiarity with domain concepts",
                "guidance_level": "Provide best practices and alternatives",
                "learning_pace": "Moderate pace with practical exercises",
                "content_structure": [
                    "Brief context and objectives",
                    "Key concepts review",
                    "Implementation examples",
                    "Best practices",
                    "Common patterns",
                    "Troubleshooting tips",
                    "Advanced topics preview"
                ],
                "interaction_style": "Professional, solution-focused, informative",
                "error_handling": "Focused troubleshooting with root cause analysis"
            },
            
            ExpertiseLevel.EXPERT: {
                "introduction_style": "Concise overview focusing on advanced aspects",
                "explanation_depth": "High-level concepts with implementation details",
                "example_complexity": "Complex, enterprise-grade scenarios",
                "terminology": "Full technical vocabulary without simplification",
                "assumptions": "Strong foundation in domain and related technologies",
                "guidance_level": "Focus on optimization and advanced patterns",
                "learning_pace": "Fast pace with comprehensive coverage",
                "content_structure": [
                    "Advanced concepts and architecture",
                    "Enterprise patterns and practices",
                    "Performance optimization",
                    "Security considerations",
                    "Integration strategies",
                    "Troubleshooting complex issues",
                    "Future trends and technologies"
                ],
                "interaction_style": "Technical, detailed, consultative",
                "error_handling": "Advanced diagnostics and system-level troubleshooting"
            }
        }
    
    def _initialize_learning_paths(self) -> Dict[TechnicalDomain, Dict[str, LearningPath]]:
        """Initialize structured learning paths for different domains."""
        return {
            TechnicalDomain.VIRTUALIZATION: {
                "beginner_to_intermediate": LearningPath(
                    domain=TechnicalDomain.VIRTUALIZATION,
                    start_level=ExpertiseLevel.BEGINNER,
                    target_level=ExpertiseLevel.INTERMEDIATE,
                    prerequisites=[
                        "Basic Linux command line knowledge",
                        "Understanding of networking concepts",
                        "Familiarity with server hardware"
                    ],
                    learning_modules=[
                        {
                            "title": "Virtualization Fundamentals",
                            "topics": ["What is virtualization", "Types of hypervisors", "Benefits and use cases"],
                            "duration": "2 hours",
                            "hands_on": ["Install VirtualBox", "Create first VM"]
                        },
                        {
                            "title": "Proxmox VE Introduction",
                            "topics": ["Proxmox architecture", "Web interface navigation", "Basic VM management"],
                            "duration": "4 hours",
                            "hands_on": ["Proxmox installation", "Create VM from ISO", "Basic networking"]
                        },
                        {
                            "title": "Storage and Networking",
                            "topics": ["Storage types", "Network configuration", "VLANs and bridges"],
                            "duration": "6 hours",
                            "hands_on": ["Configure storage pools", "Set up VLANs", "Network troubleshooting"]
                        },
                        {
                            "title": "VM Lifecycle Management",
                            "topics": ["Templates", "Cloning", "Snapshots", "Backup strategies"],
                            "duration": "4 hours",
                            "hands_on": ["Create templates", "Automated backups", "Disaster recovery"]
                        }
                    ],
                    estimated_duration="2-3 weeks",
                    success_criteria=[
                        "Can install and configure Proxmox VE",
                        "Can create and manage VMs independently",
                        "Understands storage and networking concepts",
                        "Can implement basic backup strategies"
                    ],
                    resources=[
                        "Proxmox VE Official Documentation",
                        "Virtualization fundamentals course",
                        "Hands-on lab environment"
                    ]
                ),
                "intermediate_to_expert": LearningPath(
                    domain=TechnicalDomain.VIRTUALIZATION,
                    start_level=ExpertiseLevel.INTERMEDIATE,
                    target_level=ExpertiseLevel.EXPERT,
                    prerequisites=[
                        "Solid Proxmox VE administration experience",
                        "Understanding of enterprise storage solutions",
                        "Network administration knowledge",
                        "Scripting and automation skills"
                    ],
                    learning_modules=[
                        {
                            "title": "High Availability and Clustering",
                            "topics": ["Cluster architecture", "Quorum and fencing", "Live migration", "HA management"],
                            "duration": "8 hours",
                            "hands_on": ["Build 3-node cluster", "Configure fencing", "Test failover scenarios"]
                        },
                        {
                            "title": "Advanced Storage Solutions",
                            "topics": ["Ceph configuration", "ZFS optimization", "Storage replication", "Performance tuning"],
                            "duration": "12 hours",
                            "hands_on": ["Deploy Ceph cluster", "Configure replication", "Performance benchmarking"]
                        },
                        {
                            "title": "Automation and Integration",
                            "topics": ["API automation", "Infrastructure as Code", "Monitoring integration", "Custom tooling"],
                            "duration": "10 hours",
                            "hands_on": ["Terraform integration", "Ansible automation", "Custom monitoring"]
                        },
                        {
                            "title": "Enterprise Operations",
                            "topics": ["Capacity planning", "Security hardening", "Compliance", "Disaster recovery"],
                            "duration": "8 hours",
                            "hands_on": ["Security audit", "DR testing", "Capacity analysis"]
                        }
                    ],
                    estimated_duration="6-8 weeks",
                    success_criteria=[
                        "Can design and implement HA clusters",
                        "Can optimize storage and network performance",
                        "Can automate infrastructure operations",
                        "Can plan and execute enterprise deployments"
                    ],
                    resources=[
                        "Enterprise virtualization architecture guides",
                        "Proxmox clustering best practices",
                        "Performance tuning documentation",
                        "Security hardening guides"
                    ]
                )
            },
            
            TechnicalDomain.INFRASTRUCTURE_AS_CODE: {
                "beginner_to_intermediate": LearningPath(
                    domain=TechnicalDomain.INFRASTRUCTURE_AS_CODE,
                    start_level=ExpertiseLevel.BEGINNER,
                    target_level=ExpertiseLevel.INTERMEDIATE,
                    prerequisites=[
                        "Basic command line skills",
                        "Understanding of infrastructure concepts",
                        "Version control basics (Git)"
                    ],
                    learning_modules=[
                        {
                            "title": "IaC Fundamentals",
                            "topics": ["What is Infrastructure as Code", "Benefits and challenges", "Tools comparison"],
                            "duration": "3 hours",
                            "hands_on": ["Compare manual vs automated deployment"]
                        },
                        {
                            "title": "Terraform Basics",
                            "topics": ["HCL syntax", "Providers and resources", "State management", "Variables and outputs"],
                            "duration": "8 hours",
                            "hands_on": ["First Terraform deployment", "State exploration", "Variable usage"]
                        },
                        {
                            "title": "Ansible Fundamentals",
                            "topics": ["Playbooks and roles", "Inventory management", "Task execution", "Error handling"],
                            "duration": "8 hours",
                            "hands_on": ["System configuration", "Multi-host deployment", "Error recovery"]
                        },
                        {
                            "title": "Best Practices and Workflows",
                            "topics": ["Code organization", "Testing strategies", "CI/CD integration", "Security practices"],
                            "duration": "6 hours",
                            "hands_on": ["Modular code structure", "Automated testing", "Pipeline integration"]
                        }
                    ],
                    estimated_duration="3-4 weeks",
                    success_criteria=[
                        "Can write and deploy Terraform configurations",
                        "Can create and execute Ansible playbooks",
                        "Understands state management and workflows",
                        "Can implement basic testing and validation"
                    ],
                    resources=[
                        "Terraform and Ansible official documentation",
                        "IaC best practices guides",
                        "Hands-on tutorial platforms"
                    ]
                )
            },
            
            TechnicalDomain.CONTAINERIZATION: {
                "beginner_to_intermediate": LearningPath(
                    domain=TechnicalDomain.CONTAINERIZATION,
                    start_level=ExpertiseLevel.BEGINNER,
                    target_level=ExpertiseLevel.INTERMEDIATE,
                    prerequisites=[
                        "Linux command line proficiency",
                        "Understanding of application deployment",
                        "Basic networking knowledge"
                    ],
                    learning_modules=[
                        {
                            "title": "Container Fundamentals",
                            "topics": ["What are containers", "Containers vs VMs", "Docker architecture", "Images and layers"],
                            "duration": "4 hours",
                            "hands_on": ["Install Docker", "Run first container", "Explore images"]
                        },
                        {
                            "title": "Docker Deep Dive",
                            "topics": ["Dockerfile creation", "Multi-stage builds", "Networking", "Volume management"],
                            "duration": "8 hours",
                            "hands_on": ["Build custom images", "Configure networking", "Data persistence"]
                        },
                        {
                            "title": "Container Orchestration",
                            "topics": ["Docker Compose", "Kubernetes basics", "Service discovery", "Load balancing"],
                            "duration": "10 hours",
                            "hands_on": ["Multi-container apps", "Kubernetes deployment", "Service configuration"]
                        },
                        {
                            "title": "Production Considerations",
                            "topics": ["Security practices", "Monitoring", "Logging", "Performance optimization"],
                            "duration": "6 hours",
                            "hands_on": ["Security scanning", "Monitoring setup", "Performance tuning"]
                        }
                    ],
                    estimated_duration="4-5 weeks",
                    success_criteria=[
                        "Can containerize applications effectively",
                        "Can deploy multi-container applications",
                        "Understands Kubernetes fundamentals",
                        "Can implement security and monitoring"
                    ],
                    resources=[
                        "Docker and Kubernetes documentation",
                        "Container security guides",
                        "Orchestration best practices"
                    ]
                )
            }
        }
    
    def _initialize_assessment_criteria(self) -> Dict[TechnicalDomain, Dict[ExpertiseLevel, List[str]]]:
        """Initialize skill assessment criteria for different domains and levels."""
        return {
            TechnicalDomain.VIRTUALIZATION: {
                ExpertiseLevel.BEGINNER: [
                    "Can explain what virtualization is and its benefits",
                    "Can navigate Proxmox web interface",
                    "Can create and start/stop VMs",
                    "Understands basic VM configuration options",
                    "Can create simple backups"
                ],
                ExpertiseLevel.INTERMEDIATE: [
                    "Can configure storage pools and understand different storage types",
                    "Can set up VM templates and use them for deployment",
                    "Can configure network bridges and VLANs",
                    "Can troubleshoot common VM and network issues",
                    "Can implement automated backup strategies",
                    "Understands resource allocation and limits"
                ],
                ExpertiseLevel.EXPERT: [
                    "Can design and implement high-availability clusters",
                    "Can optimize storage and network performance",
                    "Can implement advanced security measures",
                    "Can automate infrastructure operations",
                    "Can troubleshoot complex cluster issues",
                    "Can plan capacity and architect enterprise solutions"
                ]
            },
            
            TechnicalDomain.INFRASTRUCTURE_AS_CODE: {
                ExpertiseLevel.BEGINNER: [
                    "Understands IaC concepts and benefits",
                    "Can write basic Terraform configurations",
                    "Can create simple Ansible playbooks",
                    "Understands state management basics",
                    "Can deploy simple infrastructure"
                ],
                ExpertiseLevel.INTERMEDIATE: [
                    "Can create reusable Terraform modules",
                    "Can implement complex Ansible roles",
                    "Can manage state across environments",
                    "Can implement testing and validation",
                    "Can integrate with CI/CD pipelines",
                    "Understands security best practices"
                ],
                ExpertiseLevel.EXPERT: [
                    "Can architect complex multi-environment setups",
                    "Can implement advanced state management strategies",
                    "Can design custom providers and plugins",
                    "Can implement policy as code",
                    "Can optimize for performance and cost",
                    "Can mentor teams on IaC practices"
                ]
            },
            
            TechnicalDomain.CONTAINERIZATION: {
                ExpertiseLevel.BEGINNER: [
                    "Understands container concepts and benefits",
                    "Can create and run Docker containers",
                    "Can write basic Dockerfiles",
                    "Can use Docker Compose for multi-container apps",
                    "Understands basic networking and storage"
                ],
                ExpertiseLevel.INTERMEDIATE: [
                    "Can optimize Docker images and builds",
                    "Can deploy applications to Kubernetes",
                    "Can configure services and ingress",
                    "Can implement monitoring and logging",
                    "Can troubleshoot container issues",
                    "Understands security best practices"
                ],
                ExpertiseLevel.EXPERT: [
                    "Can architect microservices solutions",
                    "Can implement service mesh technologies",
                    "Can optimize cluster performance and costs",
                    "Can implement advanced security measures",
                    "Can design CI/CD pipelines for containers",
                    "Can mentor teams on containerization"
                ]
            }
        }
    
    def assess_user_skill_level(
        self,
        user_id: str,
        domain: TechnicalDomain,
        user_responses: List[Dict[str, Any]] = None,
        conversation_history: List[Dict[str, Any]] = None
    ) -> SkillAssessment:
        """
        Assess user skill level in a specific domain.
        
        Args:
            user_id: User identifier
            domain: Technical domain to assess
            user_responses: Responses to assessment questions
            conversation_history: Previous conversation context
            
        Returns:
            Comprehensive skill assessment
        """
        try:
            # Analyze conversation history for skill indicators
            conversation_level = self._analyze_conversation_for_skill_level(
                conversation_history or [], domain
            )
            
            # Analyze user responses if provided
            response_level = ExpertiseLevel.INTERMEDIATE  # Default
            if user_responses:
                response_level = self._analyze_assessment_responses(user_responses, domain)
            
            # Combine assessments with weighted average
            levels = [ExpertiseLevel.BEGINNER, ExpertiseLevel.INTERMEDIATE, ExpertiseLevel.EXPERT]
            conversation_weight = 0.6
            response_weight = 0.4
            
            conversation_score = levels.index(conversation_level)
            response_score = levels.index(response_level)
            
            combined_score = (conversation_score * conversation_weight + 
                            response_score * response_weight)
            
            final_level = levels[min(int(round(combined_score)), len(levels) - 1)]
            confidence = self._calculate_assessment_confidence(
                conversation_history, user_responses, domain
            )
            
            # Identify strengths and gaps based on conversation patterns
            strengths, gaps = self._identify_strengths_and_gaps(
                conversation_history or [], domain, final_level
            )
            
            # Generate recommendations
            recommended_topics = self._generate_topic_recommendations(
                domain, final_level, gaps
            )
            
            # Determine next learning objectives
            next_objectives = self._determine_learning_objectives(final_level)
            
            assessment = SkillAssessment(
                domain=domain,
                current_level=final_level,
                confidence_level=confidence,
                strengths=strengths,
                knowledge_gaps=gaps,
                recommended_topics=recommended_topics,
                next_objectives=next_objectives,
                assessment_date=time.time()
            )
            
            # Store assessment in user profile
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {}
            
            self.user_profiles[user_id][domain.value] = asdict(assessment)
            
            logger.info(
                "User skill assessment completed",
                user_id=user_id,
                domain=domain.value,
                assessed_level=final_level.value,
                confidence=confidence
            )
            
            return assessment
            
        except Exception as e:
            logger.error("Skill assessment failed", error=str(e), user_id=user_id, domain=domain.value)
            
            # Return default assessment
            return SkillAssessment(
                domain=domain,
                current_level=ExpertiseLevel.INTERMEDIATE,
                confidence_level=0.5,
                strengths=[],
                knowledge_gaps=[],
                recommended_topics=[],
                next_objectives=[LearningObjective.APPLY_CONCEPTS],
                assessment_date=time.time()
            )
    
    def _analyze_conversation_for_skill_level(
        self,
        conversation_history: List[Dict[str, Any]],
        domain: TechnicalDomain
    ) -> ExpertiseLevel:
        """Analyze conversation history to infer skill level."""
        if not conversation_history:
            return ExpertiseLevel.INTERMEDIATE
        
        # Analyze question complexity and terminology usage
        beginner_indicators = 0
        intermediate_indicators = 0
        expert_indicators = 0
        
        for entry in conversation_history[-10:]:  # Last 10 interactions
            user_input = entry.get("user_input", "").lower()
            
            # Beginner indicators
            beginner_patterns = [
                "what is", "how do i", "explain", "tutorial", "guide", "help me",
                "beginner", "new to", "first time", "don't know", "basic", "simple"
            ]
            
            # Intermediate indicators
            intermediate_patterns = [
                "best practice", "how to configure", "implement", "setup", "deploy",
                "troubleshoot", "optimize", "integrate", "automate", "performance"
            ]
            
            # Expert indicators
            expert_patterns = [
                "architecture", "design pattern", "enterprise", "scalability",
                "high availability", "distributed", "microservices", "governance",
                "compliance", "advanced", "custom", "extend", "api integration"
            ]
            
            for pattern in beginner_patterns:
                if pattern in user_input:
                    beginner_indicators += 1
            
            for pattern in intermediate_patterns:
                if pattern in user_input:
                    intermediate_indicators += 1
            
            for pattern in expert_patterns:
                if pattern in user_input:
                    expert_indicators += 1
        
        # Determine level based on indicators
        if expert_indicators > intermediate_indicators and expert_indicators > beginner_indicators:
            return ExpertiseLevel.EXPERT
        elif intermediate_indicators > beginner_indicators:
            return ExpertiseLevel.INTERMEDIATE
        else:
            return ExpertiseLevel.BEGINNER
    
    def _analyze_assessment_responses(
        self,
        responses: List[Dict[str, Any]],
        domain: TechnicalDomain
    ) -> ExpertiseLevel:
        """Analyze user responses to assessment questions."""
        if not responses:
            return ExpertiseLevel.INTERMEDIATE
        
        # This would contain logic to analyze specific assessment responses
        # For now, return a simple assessment based on response quality
        
        correct_responses = sum(1 for response in responses if response.get("correct", False))
        total_responses = len(responses)
        
        if total_responses == 0:
            return ExpertiseLevel.INTERMEDIATE
        
        accuracy = correct_responses / total_responses
        
        if accuracy >= 0.8:
            return ExpertiseLevel.EXPERT
        elif accuracy >= 0.6:
            return ExpertiseLevel.INTERMEDIATE
        else:
            return ExpertiseLevel.BEGINNER
    
    def _calculate_assessment_confidence(
        self,
        conversation_history: Optional[List[Dict[str, Any]]],
        user_responses: Optional[List[Dict[str, Any]]],
        domain: TechnicalDomain
    ) -> float:
        """Calculate confidence level for the assessment."""
        confidence_factors = []
        
        # Conversation history factor
        if conversation_history:
            conversation_length = len(conversation_history)
            if conversation_length >= 10:
                confidence_factors.append(0.9)
            elif conversation_length >= 5:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.3)
        
        # User responses factor
        if user_responses:
            response_quality = len(user_responses) / 10  # Assume 10 is ideal
            confidence_factors.append(min(response_quality, 1.0))
        else:
            confidence_factors.append(0.5)
        
        # Domain-specific factor (how well we can assess this domain)
        domain_confidence = {
            TechnicalDomain.VIRTUALIZATION: 0.9,
            TechnicalDomain.INFRASTRUCTURE_AS_CODE: 0.9,
            TechnicalDomain.CONTAINERIZATION: 0.8,
            TechnicalDomain.CLOUD_COMPUTING: 0.8,
            TechnicalDomain.SYSTEM_ENGINEERING: 0.7
        }
        
        confidence_factors.append(domain_confidence.get(domain, 0.6))
        
        # Calculate weighted average
        return sum(confidence_factors) / len(confidence_factors)
    
    def _identify_strengths_and_gaps(
        self,
        conversation_history: List[Dict[str, Any]],
        domain: TechnicalDomain,
        assessed_level: ExpertiseLevel
    ) -> Tuple[List[str], List[str]]:
        """Identify user strengths and knowledge gaps."""
        strengths = []
        gaps = []
        
        # Get assessment criteria for the domain and level
        criteria = self.assessment_criteria.get(domain, {})
        current_criteria = criteria.get(assessed_level, [])
        
        # Analyze conversation for demonstrated knowledge
        conversation_text = " ".join([
            entry.get("user_input", "") for entry in conversation_history[-20:]
        ]).lower()
        
        # Check for demonstrated strengths
        if "automation" in conversation_text or "script" in conversation_text:
            strengths.append("Automation and scripting")
        
        if "security" in conversation_text or "hardening" in conversation_text:
            strengths.append("Security awareness")
        
        if "performance" in conversation_text or "optimization" in conversation_text:
            strengths.append("Performance optimization")
        
        if "troubleshoot" in conversation_text or "debug" in conversation_text:
            strengths.append("Problem-solving and troubleshooting")
        
        # Identify potential gaps based on what hasn't been discussed
        common_gaps = {
            ExpertiseLevel.BEGINNER: [
                "Basic terminology and concepts",
                "Hands-on practical experience",
                "Understanding of best practices"
            ],
            ExpertiseLevel.INTERMEDIATE: [
                "Advanced configuration options",
                "Integration with other systems",
                "Performance tuning techniques"
            ],
            ExpertiseLevel.EXPERT: [
                "Enterprise architecture patterns",
                "Advanced security implementations",
                "Mentoring and knowledge transfer"
            ]
        }
        
        gaps = common_gaps.get(assessed_level, [])
        
        return strengths, gaps
    
    def _generate_topic_recommendations(
        self,
        domain: TechnicalDomain,
        level: ExpertiseLevel,
        gaps: List[str]
    ) -> List[str]:
        """Generate personalized topic recommendations."""
        recommendations = []
        
        # Get domain knowledge
        try:
            from .knowledge_base import KnowledgeContext
            
            knowledge_context = KnowledgeContext(
                domain=domain,
                expertise_level=level,
                specific_technologies=[],
                use_case="learning",
                security_requirements="medium",
                compliance_needs=[]
            )
            
            domain_knowledge = self.knowledge_base.get_domain_knowledge(knowledge_context)
            
            # Extract relevant topics based on gaps
            for topic, knowledge in domain_knowledge.items():
                if isinstance(knowledge, dict) and "topic" in knowledge:
                    recommendations.append(knowledge["topic"])
            
        except Exception as e:
            logger.debug("Could not load domain knowledge for recommendations", error=str(e))
        
        # Add general recommendations based on level
        level_recommendations = {
            ExpertiseLevel.BEGINNER: [
                "Fundamental concepts and terminology",
                "Basic hands-on exercises",
                "Common use cases and examples"
            ],
            ExpertiseLevel.INTERMEDIATE: [
                "Best practices and patterns",
                "Integration techniques",
                "Troubleshooting methodologies"
            ],
            ExpertiseLevel.EXPERT: [
                "Advanced architecture patterns",
                "Performance optimization strategies",
                "Leadership and mentoring skills"
            ]
        }
        
        recommendations.extend(level_recommendations.get(level, []))
        
        return recommendations[:8]  # Return top 8 recommendations
    
    def _determine_learning_objectives(self, level: ExpertiseLevel) -> List[LearningObjective]:
        """Determine appropriate learning objectives for skill level."""
        objectives_by_level = {
            ExpertiseLevel.BEGINNER: [
                LearningObjective.UNDERSTAND_BASICS,
                LearningObjective.APPLY_CONCEPTS
            ],
            ExpertiseLevel.INTERMEDIATE: [
                LearningObjective.APPLY_CONCEPTS,
                LearningObjective.ANALYZE_SYSTEMS,
                LearningObjective.DESIGN_SOLUTIONS
            ],
            ExpertiseLevel.EXPERT: [
                LearningObjective.DESIGN_SOLUTIONS,
                LearningObjective.OPTIMIZE_PERFORMANCE,
                LearningObjective.TEACH_OTHERS
            ]
        }
        
        return objectives_by_level.get(level, [LearningObjective.APPLY_CONCEPTS])
    
    def generate_personalized_content(
        self,
        user_id: str,
        domain: TechnicalDomain,
        topic: str,
        content_type: str = "tutorial"
    ) -> PersonalizedContent:
        """
        Generate personalized content based on user's skill level and preferences.
        
        Args:
            user_id: User identifier
            domain: Technical domain
            topic: Specific topic to create content for
            content_type: Type of content (tutorial, example, exercise)
            
        Returns:
            Personalized content tailored to user's expertise level
        """
        try:
            # Get user's skill assessment
            user_profile = self.user_profiles.get(user_id, {})
            domain_profile = user_profile.get(domain.value)
            
            if domain_profile:
                skill_level = ExpertiseLevel(domain_profile["current_level"])
                strengths = domain_profile.get("strengths", [])
                gaps = domain_profile.get("knowledge_gaps", [])
            else:
                # Default assessment
                skill_level = ExpertiseLevel.INTERMEDIATE
                strengths = []
                gaps = []
            
            # Get content template for skill level
            template = self.content_templates[skill_level]
            
            # Get domain knowledge
            from .knowledge_base import KnowledgeContext
            
            knowledge_context = KnowledgeContext(
                domain=domain,
                expertise_level=skill_level,
                specific_technologies=[topic],
                use_case="learning",
                security_requirements="medium",
                compliance_needs=[]
            )
            
            domain_knowledge = self.knowledge_base.get_domain_knowledge(knowledge_context)
            
            # Generate content based on template and knowledge
            content = self._generate_content_by_level(
                topic, skill_level, template, domain_knowledge, content_type
            )
            
            # Generate examples appropriate for skill level
            examples = self._generate_examples_by_level(topic, skill_level, domain_knowledge)
            
            # Generate exercises
            exercises = self._generate_exercises_by_level(topic, skill_level, gaps)
            
            # Estimate time based on complexity and skill level
            time_estimates = {
                ExpertiseLevel.BEGINNER: "30-45 minutes",
                ExpertiseLevel.INTERMEDIATE: "20-30 minutes",
                ExpertiseLevel.EXPERT: "15-20 minutes"
            }
            
            personalized_content = PersonalizedContent(
                content_type=content_type,
                title=f"{topic} - {skill_level.value.title()} Level",
                description=f"Personalized {content_type} for {topic} at {skill_level.value} level",
                difficulty_level=skill_level,
                prerequisites=self._get_prerequisites_for_level(topic, skill_level),
                learning_objectives=self._get_learning_objectives_for_topic(topic, skill_level),
                content=content,
                examples=examples,
                exercises=exercises,
                references=self._get_references_for_topic(topic, skill_level),
                estimated_time=time_estimates[skill_level]
            )
            
            logger.info(
                "Generated personalized content",
                user_id=user_id,
                domain=domain.value,
                topic=topic,
                skill_level=skill_level.value,
                content_type=content_type
            )
            
            return personalized_content
            
        except Exception as e:
            logger.error("Failed to generate personalized content", error=str(e))
            
            # Return basic content as fallback
            return PersonalizedContent(
                content_type=content_type,
                title=f"{topic} Tutorial",
                description=f"Introduction to {topic}",
                difficulty_level=ExpertiseLevel.INTERMEDIATE,
                prerequisites=[],
                learning_objectives=[],
                content=f"This is a tutorial about {topic}. Content generation failed temporarily.",
                examples=[],
                exercises=[],
                references=[],
                estimated_time="20-30 minutes"
            )
    
    def _generate_content_by_level(
        self,
        topic: str,
        skill_level: ExpertiseLevel,
        template: Dict[str, Any],
        domain_knowledge: Dict[str, Any],
        content_type: str
    ) -> str:
        """Generate content appropriate for skill level."""
        
        # Get the content structure for this skill level
        structure = template.get("content_structure", [])
        explanation_depth = template.get("explanation_depth", "")
        terminology = template.get("terminology", "")
        
        content_parts = []
        
        # Add introduction based on skill level
        if skill_level == ExpertiseLevel.BEGINNER:
            content_parts.append(f"""
# {topic} - Comprehensive Beginner's Guide

## What You'll Learn
In this tutorial, we'll cover {topic} from the ground up. We'll start with the fundamental concepts, provide plenty of examples, and guide you through hands-on exercises.

## Prerequisites
Before we begin, make sure you have:
- Basic understanding of command line operations
- Access to a practice environment
- Patience and willingness to learn!

## Why {topic} Matters
{topic} is an essential skill in modern infrastructure management. Understanding this concept will help you...
""")
        
        elif skill_level == ExpertiseLevel.INTERMEDIATE:
            content_parts.append(f"""
# {topic} - Practical Implementation Guide

## Overview
This guide focuses on practical implementation of {topic} with real-world examples and best practices.

## Learning Objectives
By the end of this guide, you'll be able to:
- Implement {topic} effectively in production environments
- Apply best practices and common patterns
- Troubleshoot common issues
""")
            
        else:  # Expert
            content_parts.append(f"""
# {topic} - Advanced Architecture and Optimization

## Executive Summary
This technical deep-dive covers advanced {topic} implementations, architectural considerations, and optimization strategies for enterprise environments.

## Key Focus Areas
- Enterprise-grade patterns and practices
- Performance optimization techniques
- Integration with complex systems
- Operational excellence considerations
""")
        
        # Add domain-specific knowledge content
        for knowledge_topic, knowledge_data in domain_knowledge.items():
            if isinstance(knowledge_data, dict):
                if "concepts" in knowledge_data and knowledge_data["concepts"]:
                    content_parts.append(f"\n## Key Concepts")
                    for concept, definition in knowledge_data["concepts"].items():
                        if skill_level == ExpertiseLevel.BEGINNER:
                            content_parts.append(f"**{concept}**: {definition} (This is important because...)")
                        else:
                            content_parts.append(f"**{concept}**: {definition}")
                
                if "best_practices" in knowledge_data and knowledge_data["best_practices"]:
                    content_parts.append(f"\n## Best Practices")
                    practices = knowledge_data["best_practices"]
                    if skill_level == ExpertiseLevel.BEGINNER:
                        practices = practices[:3]  # Limit for beginners
                    
                    for i, practice in enumerate(practices, 1):
                        content_parts.append(f"{i}. {practice}")
        
        return "\n".join(content_parts)
    
    def _generate_examples_by_level(
        self,
        topic: str,
        skill_level: ExpertiseLevel,
        domain_knowledge: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate examples appropriate for skill level."""
        examples = []
        
        if skill_level == ExpertiseLevel.BEGINNER:
            examples.append({
                "title": f"Basic {topic} Example",
                "description": "Simple, step-by-step example with detailed explanations",
                "code": f"# Basic {topic} example\n# Step 1: ...\n# Step 2: ...",
                "explanation": "This example shows the fundamental concepts of " + topic
            })
            
        elif skill_level == ExpertiseLevel.INTERMEDIATE:
            examples.extend([
                {
                    "title": f"Practical {topic} Implementation",
                    "description": "Real-world scenario with best practices",
                    "code": f"# Production-ready {topic} example\n# Includes error handling and optimization",
                    "explanation": "This example demonstrates practical implementation with best practices"
                },
                {
                    "title": f"Common {topic} Patterns",
                    "description": "Frequently used patterns and their applications",
                    "code": f"# Common patterns for {topic}",
                    "explanation": "These patterns are commonly used in enterprise environments"
                }
            ])
            
        else:  # Expert
            examples.extend([
                {
                    "title": f"Advanced {topic} Architecture",
                    "description": "Complex enterprise-grade implementation",
                    "code": f"# Enterprise {topic} architecture\n# Includes advanced features and optimizations",
                    "explanation": "This example shows advanced architectural patterns"
                },
                {
                    "title": f"Performance-Optimized {topic}",
                    "description": "High-performance implementation with optimization techniques",
                    "code": f"# Performance-optimized {topic}\n# Includes caching, parallelization, etc.",
                    "explanation": "This example focuses on performance optimization techniques"
                }
            ])
        
        return examples
    
    def _generate_exercises_by_level(
        self,
        topic: str,
        skill_level: ExpertiseLevel,
        gaps: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate exercises appropriate for skill level."""
        exercises = []
        
        if skill_level == ExpertiseLevel.BEGINNER:
            exercises.extend([
                {
                    "title": f"Getting Started with {topic}",
                    "description": f"Basic hands-on exercise to practice {topic} fundamentals",
                    "difficulty": "Easy",
                    "estimated_time": "15 minutes",
                    "instructions": [
                        f"Set up your environment for {topic}",
                        f"Follow the basic {topic} tutorial",
                        "Complete the verification steps",
                        "Document what you learned"
                    ]
                }
            ])
            
        elif skill_level == ExpertiseLevel.INTERMEDIATE:
            exercises.extend([
                {
                    "title": f"Implementing {topic} Best Practices",
                    "description": f"Apply best practices in a realistic {topic} scenario",
                    "difficulty": "Medium",
                    "estimated_time": "30 minutes",
                    "instructions": [
                        f"Design a {topic} solution for the given scenario",
                        "Implement with best practices",
                        "Test and validate your implementation",
                        "Document your design decisions"
                    ]
                },
                {
                    "title": f"Troubleshooting {topic} Issues",
                    "description": f"Practice debugging common {topic} problems",
                    "difficulty": "Medium",
                    "estimated_time": "20 minutes",
                    "instructions": [
                        "Identify the problem in the given scenario",
                        "Use appropriate troubleshooting techniques",
                        "Implement and test the solution",
                        "Prevent similar issues in the future"
                    ]
                }
            ])
            
        else:  # Expert
            exercises.extend([
                {
                    "title": f"Architecting Enterprise {topic} Solution",
                    "description": f"Design a comprehensive {topic} architecture",
                    "difficulty": "Hard",
                    "estimated_time": "60 minutes", 
                    "instructions": [
                        f"Analyze requirements for enterprise {topic} deployment",
                        "Design scalable and secure architecture",
                        "Consider integration points and dependencies",
                        "Create implementation roadmap"
                    ]
                },
                {
                    "title": f"Optimizing {topic} Performance",
                    "description": f"Performance tune an existing {topic} implementation",
                    "difficulty": "Hard",
                    "estimated_time": "45 minutes",
                    "instructions": [
                        "Analyze current performance bottlenecks",
                        "Implement optimization strategies",
                        "Measure and validate improvements",
                        "Document optimization techniques used"
                    ]
                }
            ])
        
        return exercises
    
    def _get_prerequisites_for_level(self, topic: str, skill_level: ExpertiseLevel) -> List[str]:
        """Get prerequisites appropriate for skill level."""
        prerequisites = {
            ExpertiseLevel.BEGINNER: [
                "Basic command line knowledge",
                "Understanding of fundamental IT concepts",
                "Access to practice environment"
            ],
            ExpertiseLevel.INTERMEDIATE: [
                f"Basic {topic} knowledge",
                "Experience with related technologies",
                "Understanding of system administration"
            ],
            ExpertiseLevel.EXPERT: [
                f"Advanced {topic} experience",
                "Enterprise infrastructure knowledge",
                "Architecture and design experience"
            ]
        }
        
        return prerequisites.get(skill_level, [])
    
    def _get_learning_objectives_for_topic(self, topic: str, skill_level: ExpertiseLevel) -> List[str]:
        """Get learning objectives for topic and skill level."""
        objectives = {
            ExpertiseLevel.BEGINNER: [
                f"Understand fundamental {topic} concepts",
                f"Perform basic {topic} operations",
                f"Identify common {topic} use cases"
            ],
            ExpertiseLevel.INTERMEDIATE: [
                f"Implement {topic} best practices",
                f"Troubleshoot {topic} issues",
                f"Integrate {topic} with other systems"
            ],
            ExpertiseLevel.EXPERT: [
                f"Architect enterprise {topic} solutions",
                f"Optimize {topic} performance",
                f"Mentor others in {topic} practices"
            ]
        }
        
        return objectives.get(skill_level, [])
    
    def _get_references_for_topic(self, topic: str, skill_level: ExpertiseLevel) -> List[str]:
        """Get references appropriate for skill level."""
        references = {
            ExpertiseLevel.BEGINNER: [
                f"{topic} Official Documentation - Getting Started",
                f"{topic} Community Tutorials",
                f"{topic} Best Practices Guide"
            ],
            ExpertiseLevel.INTERMEDIATE: [
                f"{topic} Advanced Configuration Guide",  
                f"{topic} Integration Patterns",
                f"{topic} Troubleshooting Reference"
            ],
            ExpertiseLevel.EXPERT: [
                f"{topic} Architecture Patterns",
                f"{topic} Performance Optimization Guide",
                f"{topic} Enterprise Implementation Guide"
            ]
        }
        
        return references.get(skill_level, [])
    
    def get_learning_path(
        self,
        user_id: str,
        domain: TechnicalDomain,
        target_level: ExpertiseLevel
    ) -> Optional[LearningPath]:
        """Get personalized learning path for user."""
        try:
            # Get user's current skill assessment
            user_profile = self.user_profiles.get(user_id, {})
            domain_profile = user_profile.get(domain.value)
            
            if domain_profile:
                current_level = ExpertiseLevel(domain_profile["current_level"])
            else:
                # Perform quick assessment
                assessment = self.assess_user_skill_level(user_id, domain)
                current_level = assessment.current_level
            
            # Find appropriate learning path
            path_key = f"{current_level.value}_to_{target_level.value}"
            domain_paths = self.learning_paths.get(domain, {})
            
            if path_key in domain_paths:
                return domain_paths[path_key]
            
            # If exact path not found, generate custom path
            return self._generate_custom_learning_path(current_level, target_level, domain)
            
        except Exception as e:
            logger.error("Failed to get learning path", error=str(e))
            return None
    
    def _generate_custom_learning_path(
        self,
        start_level: ExpertiseLevel,
        target_level: ExpertiseLevel,
        domain: TechnicalDomain
    ) -> LearningPath:
        """Generate custom learning path."""
        # This would contain logic to dynamically generate learning paths
        # For now, return a basic path structure
        
        return LearningPath(
            domain=domain,
            start_level=start_level,
            target_level=target_level,
            prerequisites=[f"Current {start_level.value} level knowledge in {domain.value}"],
            learning_modules=[
                {
                    "title": f"Advancing from {start_level.value} to {target_level.value}",
                    "topics": ["Advanced concepts", "Practical applications", "Best practices"],
                    "duration": "Variable",
                    "hands_on": ["Practical exercises", "Real-world projects"]
                }
            ],
            estimated_duration="4-6 weeks",
            success_criteria=[f"Demonstrate {target_level.value} level competency"],
            resources=[f"{domain.value} advanced learning resources"]
        )


# Global expertise engine instance
expertise_engine = ExpertiseLevelsEngine()