"""
Local AI Model Integration for Proxmox Infrastructure Automation.

Provides offline AI capabilities for IaC code generation and optimization
without any cloud dependencies.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import requests
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class AIResponse:
    """Response from local AI model."""
    content: str
    success: bool
    model_used: str
    processing_time: float
    skill_level: str


class LocalAIClient:
    """
    Local AI client for Infrastructure as Code automation.
    
    Supports multiple skill levels and local model integration.
    """
    
    def __init__(self, model_name: str = "llama3.2", ollama_host: str = "http://localhost:11434"):
        """Initialize local AI client."""
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.skill_levels = {
            "beginner": "Simple, guided explanations with step-by-step instructions",
            "intermediate": "Balanced detail with best practices and common patterns", 
            "expert": "Advanced configurations, optimizations, and edge cases"
        }
        
        logger.info("Local AI client initialized", model=model_name, host=ollama_host)
    
    def is_available(self) -> bool:
        """Check if local AI model is available."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning("Local AI model not available", error=str(e))
            return False
    
    def generate_terraform_config(self, 
                                 description: str, 
                                 skill_level: str = "intermediate",
                                 provider: str = "proxmox") -> AIResponse:
        """Generate Terraform configuration based on description."""
        
        skill_context = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
        
        prompt = f"""
        You are an expert in Infrastructure as Code using Terraform for Proxmox.
        Skill level: {skill_level} - {skill_context}
        
        Generate a Terraform configuration for: {description}
        
        Requirements:
        - Use Proxmox provider
        - Include proper resource definitions
        - Add appropriate variables and outputs
        - Include security best practices
        - {self._get_skill_specific_requirements(skill_level)}
        
        Respond with clean Terraform HCL code only.
        """
        
        return self._make_request(prompt, skill_level)
    
    def generate_ansible_playbook(self, 
                                 description: str, 
                                 skill_level: str = "intermediate") -> AIResponse:
        """Generate Ansible playbook for VM configuration."""
        
        skill_context = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
        
        prompt = f"""
        You are an expert in Ansible automation for infrastructure configuration.
        Skill level: {skill_level} - {skill_context}
        
        Generate an Ansible playbook for: {description}
        
        Requirements:
        - YAML format
        - Include proper tasks and handlers
        - Add security hardening steps
        - Include error handling
        - {self._get_skill_specific_requirements(skill_level)}
        
        Respond with clean Ansible YAML only.
        """
        
        return self._make_request(prompt, skill_level)
    
    def optimize_infrastructure(self, 
                               config: str, 
                               skill_level: str = "intermediate") -> AIResponse:
        """Optimize existing infrastructure configuration."""
        
        skill_context = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
        
        prompt = f"""
        You are an expert in infrastructure optimization and best practices.
        Skill level: {skill_level} - {skill_context}
        
        Review and optimize this infrastructure configuration:
        
        {config}
        
        Focus on:
        - Performance improvements
        - Security enhancements
        - Cost optimization
        - Best practices
        - {self._get_skill_specific_requirements(skill_level)}
        
        Provide optimized configuration with explanations.
        """
        
        return self._make_request(prompt, skill_level)
    
    def explain_configuration(self, 
                             config: str, 
                             skill_level: str = "beginner") -> AIResponse:
        """Explain infrastructure configuration for learning."""
        
        skill_context = self.skill_levels.get(skill_level, self.skill_levels["beginner"])
        
        prompt = f"""
        You are an expert teacher in Infrastructure as Code.
        Skill level: {skill_level} - {skill_context}
        
        Explain this infrastructure configuration:
        
        {config}
        
        Explanation should include:
        - What each component does
        - Why it's structured this way
        - Security considerations
        - Best practices demonstrated
        - {self._get_skill_specific_requirements(skill_level)}
        """
        
        return self._make_request(prompt, skill_level)
    
    def _get_skill_specific_requirements(self, skill_level: str) -> str:
        """Get skill-level specific requirements."""
        requirements = {
            "beginner": "Use simple, clear examples with detailed comments explaining each step",
            "intermediate": "Include best practices, common patterns, and moderate complexity",
            "expert": "Show advanced patterns, edge cases, and enterprise-grade configurations"
        }
        return requirements.get(skill_level, requirements["intermediate"])
    
    def _make_request(self, prompt: str, skill_level: str) -> AIResponse:
        """Make request to local AI model."""
        import time
        start_time = time.time()
        
        try:
            if not self.is_available():
                return AIResponse(
                    content="Local AI model not available. Please ensure Ollama is running.",
                    success=False,
                    model_used=self.model_name,
                    processing_time=0.0,
                    skill_level=skill_level
                )
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                logger.info(
                    "Local AI request successful",
                    model=self.model_name,
                    skill_level=skill_level,
                    processing_time=processing_time
                )
                
                return AIResponse(
                    content=result.get("response", ""),
                    success=True,
                    model_used=self.model_name,
                    processing_time=processing_time,
                    skill_level=skill_level
                )
            else:
                logger.error("Local AI request failed", status_code=response.status_code)
                return AIResponse(
                    content=f"AI request failed with status {response.status_code}",
                    success=False,
                    model_used=self.model_name,
                    processing_time=time.time() - start_time,
                    skill_level=skill_level
                )
                
        except Exception as e:
            logger.error("Local AI request error", error=str(e))
            return AIResponse(
                content=f"Error: {str(e)}",
                success=False,
                model_used=self.model_name,
                processing_time=time.time() - start_time,
                skill_level=skill_level
            )


class IaCSkillManager:
    """Manages Infrastructure as Code skill level adaptation."""
    
    def __init__(self):
        """Initialize skill manager."""
        self.templates = {
            "beginner": self._load_beginner_templates(),
            "intermediate": self._load_intermediate_templates(),
            "expert": self._load_expert_templates()
        }
    
    def get_template(self, skill_level: str, template_type: str) -> Dict[str, Any]:
        """Get template for specific skill level."""
        return self.templates.get(skill_level, {}).get(template_type, {})
    
    def _load_beginner_templates(self) -> Dict[str, Any]:
        """Load beginner-friendly templates."""
        return {
            "vm_basic": {
                "description": "Simple VM with basic configuration",
                "complexity": "low",
                "features": ["basic_networking", "simple_storage", "guided_setup"]
            },
            "network_simple": {
                "description": "Basic network setup with minimal configuration", 
                "complexity": "low",
                "features": ["single_vlan", "basic_firewall", "dhcp"]
            }
        }
    
    def _load_intermediate_templates(self) -> Dict[str, Any]:
        """Load intermediate templates."""
        return {
            "vm_clustered": {
                "description": "Multi-VM setup with load balancing",
                "complexity": "medium",
                "features": ["clustering", "load_balancing", "monitoring"]
            },
            "network_segmented": {
                "description": "Segmented network with multiple VLANs",
                "complexity": "medium", 
                "features": ["multiple_vlans", "advanced_firewall", "routing"]
            }
        }
    
    def _load_expert_templates(self) -> Dict[str, Any]:
        """Load expert-level templates."""
        return {
            "vm_enterprise": {
                "description": "Enterprise-grade VM deployment with HA",
                "complexity": "high",
                "features": ["high_availability", "auto_scaling", "disaster_recovery"]
            },
            "network_enterprise": {
                "description": "Enterprise network with advanced security",
                "complexity": "high",
                "features": ["micro_segmentation", "zero_trust", "advanced_monitoring"]
            }
        }


# Global instances
local_ai_client = LocalAIClient()
skill_manager = IaCSkillManager()