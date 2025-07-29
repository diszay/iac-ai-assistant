"""
AI integration service for Proxmox AI Assistant.

Provides intelligent code generation, optimization recommendations, and 
configuration analysis using Anthropic Claude API.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional

import anthropic
import structlog
from anthropic.types import Message

from ..core.config import get_settings
from ..core.logging import log_security_event

logger = structlog.get_logger(__name__)


class AIServiceError(Exception):
    """Raised when AI service operations fail."""
    pass


class AIService:
    """
    AI-powered service for infrastructure automation.
    
    Provides intelligent code generation, optimization analysis, and
    configuration explanation using Claude AI.
    """
    
    def __init__(self):
        self.settings = get_settings()
        
        if not self.settings.anthropic.api_key:
            raise AIServiceError("No Anthropic API key configured")
        
        self.client = anthropic.Anthropic(
            api_key=self.settings.anthropic.api_key
        )
        
        logger.info("AI service initialized", model=self.settings.anthropic.model)
    
    async def generate_vm_config(
        self, 
        description: str, 
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate VM configuration from natural language description.
        
        Args:
            description: Natural language description of the VM requirements
            template: Optional template style to use
            
        Returns:
            Dict containing generated VM configuration and explanation
        """
        prompt = self._build_vm_config_prompt(description, template)
        
        try:
            start_time = time.time()
            
            response = await self._make_ai_request(prompt)
            
            duration = time.time() - start_time
            
            # Parse the response
            result = self._parse_vm_config_response(response.content[0].text)
            
            log_security_event(
                "AI VM configuration generated",
                success=True,
                details={
                    'description_length': len(description),
                    'duration': duration,
                    'model': self.settings.anthropic.model
                }
            )
            
            logger.info(
                "VM configuration generated",
                description_length=len(description),
                duration=duration
            )
            
            return result
            
        except Exception as e:
            logger.error("Failed to generate VM config", error=str(e))
            raise AIServiceError(f"VM config generation failed: {e}")
    
    def _build_vm_config_prompt(self, description: str, template: Optional[str]) -> str:
        """Build prompt for VM configuration generation."""
        base_prompt = f"""
You are an expert Proxmox VE administrator. Generate a JSON configuration for a virtual machine based on this description:

"{description}"

Requirements:
1. Generate valid Proxmox VM configuration in JSON format
2. Include reasonable defaults for unspecified parameters
3. Use best practices for VM configuration
4. Include brief explanation of configuration choices

{f"Style/Template: {template}" if template else ""}

Proxmox Configuration Guidelines:
- Memory should be in MB (e.g., 2048 for 2GB)
- Cores should be integer value (1-16 typical)
- Use virtio drivers for better performance
- Set ostype appropriately (l26 for Linux, w10 for Windows 10, etc.)
- Include network interface (typically virtio with bridge vmbr0)
- Set reasonable disk size with virtio storage
- Enable QEMU guest agent when possible

Return your response in this exact format:
```json
{
  "name": "vm-name",
  "memory": 2048,
  "cores": 2,
  "ostype": "l26",
  "net0": "virtio,bridge=vmbr0",
  "virtio0": "local-lvm:32",
  "agent": "1",
  "boot": "order=virtio0"
}
```

EXPLANATION:
[Provide 2-3 sentences explaining the configuration choices]
"""
        return base_prompt
    
    def _parse_vm_config_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response for VM configuration."""
        try:
            # Extract JSON configuration
            start_marker = "```json"
            end_marker = "```"
            
            start_idx = response_text.find(start_marker)
            if start_idx == -1:
                raise ValueError("No JSON configuration found in response")
            
            start_idx += len(start_marker)
            end_idx = response_text.find(end_marker, start_idx)
            
            if end_idx == -1:
                raise ValueError("Incomplete JSON configuration in response")
            
            json_str = response_text[start_idx:end_idx].strip()
            config = json.loads(json_str)
            
            # Extract explanation
            explanation_start = response_text.find("EXPLANATION:")
            explanation = ""
            if explanation_start != -1:
                explanation = response_text[explanation_start + len("EXPLANATION:"):].strip()
            
            return {
                'code': json.dumps(config, indent=2),
                'config': config,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error("Failed to parse VM config response", error=str(e))
            raise AIServiceError(f"Failed to parse AI response: {e}")
    
    async def generate_terraform_config(
        self, 
        description: str, 
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate Terraform configuration from description."""
        prompt = self._build_terraform_prompt(description, template)
        
        try:
            response = await self._make_ai_request(prompt)
            result = self._parse_code_response(response.content[0].text, "terraform")
            
            logger.info("Terraform configuration generated", description_length=len(description))
            return result
            
        except Exception as e:
            logger.error("Failed to generate Terraform config", error=str(e))
            raise AIServiceError(f"Terraform config generation failed: {e}")
    
    def _build_terraform_prompt(self, description: str, template: Optional[str]) -> str:
        """Build prompt for Terraform configuration generation."""
        return f"""
You are an expert Terraform developer. Generate Terraform configuration for Proxmox infrastructure based on this description:

"{description}"

Requirements:
1. Use the Proxmox Terraform provider
2. Follow Terraform best practices
3. Include appropriate variables and outputs
4. Use descriptive resource names
5. Include comments explaining the configuration

{f"Style/Template: {template}" if template else ""}

Provider Configuration:
- Use telmate/proxmox provider
- Configure connection to Proxmox API
- Use variables for sensitive data

Return your response with:
1. Complete Terraform configuration
2. Brief explanation of the infrastructure design

Format your response as:
```hcl
[Terraform configuration here]
```

EXPLANATION:
[Explanation of the infrastructure design and configuration choices]
"""
    
    async def generate_ansible_playbook(
        self, 
        description: str, 
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate Ansible playbook from description."""
        prompt = self._build_ansible_prompt(description, template)
        
        try:
            response = await self._make_ai_request(prompt)
            result = self._parse_code_response(response.content[0].text, "ansible")
            
            logger.info("Ansible playbook generated", description_length=len(description))
            return result
            
        except Exception as e:
            logger.error("Failed to generate Ansible playbook", error=str(e))
            raise AIServiceError(f"Ansible playbook generation failed: {e}")
    
    def _build_ansible_prompt(self, description: str, template: Optional[str]) -> str:
        """Build prompt for Ansible playbook generation."""
        return f"""
You are an expert Ansible developer. Generate an Ansible playbook based on this description:

"{description}"

Requirements:
1. Create a complete, runnable Ansible playbook
2. Use appropriate modules and best practices
3. Include error handling and idempotency
4. Add meaningful task names and comments
5. Use variables where appropriate

{f"Style/Template: {template}" if template else ""}

Ansible Best Practices:
- Use appropriate modules (package, service, file, etc.)
- Include become directives when needed
- Add tags for selective execution
- Use handlers for service restarts
- Include meaningful task descriptions

Return your response as:
```yaml
[Ansible playbook here]
```

EXPLANATION:
[Explanation of the playbook structure and automation approach]
"""
    
    async def generate_docker_compose(
        self, 
        description: str, 
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate Docker Compose configuration from description."""
        prompt = self._build_docker_prompt(description, template)
        
        try:
            response = await self._make_ai_request(prompt)
            result = self._parse_code_response(response.content[0].text, "docker")
            
            logger.info("Docker Compose generated", description_length=len(description))
            return result
            
        except Exception as e:
            logger.error("Failed to generate Docker Compose", error=str(e))
            raise AIServiceError(f"Docker Compose generation failed: {e}")
    
    def _build_docker_prompt(self, description: str, template: Optional[str]) -> str:
        """Build prompt for Docker Compose generation."""
        return f"""
You are an expert Docker developer. Generate a Docker Compose configuration based on this description:

"{description}"

Requirements:
1. Create a complete docker-compose.yml file
2. Use appropriate Docker images and configurations
3. Include proper networking and volume configurations
4. Follow Docker Compose best practices
5. Include environment variables where needed

{f"Style/Template: {template}" if template else ""}

Docker Compose Best Practices:
- Use specific image tags, not 'latest'
- Configure proper restart policies
- Use named volumes for persistent data
- Set up appropriate networks
- Include health checks where applicable
- Use environment files for sensitive data

Return your response as:
```yaml
[Docker Compose configuration here]
```

EXPLANATION:
[Explanation of the service architecture and Docker configuration]
"""
    
    def _parse_code_response(self, response_text: str, code_type: str) -> Dict[str, Any]:
        """Parse AI response for code generation."""
        try:
            # Determine code block markers based on type
            markers = {
                'terraform': 'hcl',
                'ansible': 'yaml',
                'docker': 'yaml'
            }
            
            marker = markers.get(code_type, 'text')
            start_marker = f"```{marker}"
            end_marker = "```"
            
            # Extract code
            start_idx = response_text.find(start_marker)
            if start_idx == -1:
                # Try without language specifier
                start_marker = "```"
                start_idx = response_text.find(start_marker)
                
            if start_idx == -1:
                raise ValueError(f"No code block found in response")
            
            start_idx += len(start_marker)
            end_idx = response_text.find(end_marker, start_idx)
            
            if end_idx == -1:
                raise ValueError("Incomplete code block in response")
            
            code = response_text[start_idx:end_idx].strip()
            
            # Extract explanation
            explanation_start = response_text.find("EXPLANATION:")
            explanation = ""
            if explanation_start != -1:
                explanation = response_text[explanation_start + len("EXPLANATION:"):].strip()
            
            return {
                'code': code,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error("Failed to parse code response", error=str(e))
            raise AIServiceError(f"Failed to parse AI response: {e}")
    
    async def refine_generated_code(
        self, 
        current_code: str, 
        refinement_request: str,
        code_type: str
    ) -> Dict[str, Any]:
        """Refine previously generated code based on user feedback."""
        prompt = f"""
You previously generated this {code_type} configuration:

```
{current_code}
```

The user has requested this refinement:
"{refinement_request}"

Please modify the configuration to address the user's request while maintaining the existing functionality where possible.

Requirements:
1. Make the requested changes accurately
2. Preserve existing functionality unless explicitly asked to change it
3. Maintain proper syntax and best practices
4. Explain what changes were made and why

Return the refined configuration in the same format as before, followed by an explanation of the changes.
"""
        
        try:
            response = await self._make_ai_request(prompt)
            result = self._parse_code_response(response.content[0].text, code_type)
            
            logger.info("Code refined", refinement_length=len(refinement_request))
            return result
            
        except Exception as e:
            logger.error("Failed to refine code", error=str(e))
            raise AIServiceError(f"Code refinement failed: {e}")
    
    async def generate_optimization_recommendations(
        self,
        current_state: Dict[str, Any],
        target: str,
        analysis_type: str
    ) -> Dict[str, Any]:
        """Generate optimization recommendations based on current infrastructure state."""
        prompt = self._build_optimization_prompt(current_state, target, analysis_type)
        
        try:
            response = await self._make_ai_request(prompt)
            result = self._parse_optimization_response(response.content[0].text)
            
            logger.info(
                "Optimization recommendations generated",
                target=target,
                analysis_type=analysis_type
            )
            return result
            
        except Exception as e:
            logger.error("Failed to generate optimization recommendations", error=str(e))
            raise AIServiceError(f"Optimization analysis failed: {e}")
    
    def _build_optimization_prompt(
        self, 
        current_state: Dict[str, Any], 
        target: str, 
        analysis_type: str
    ) -> str:
        """Build prompt for optimization analysis."""
        return f"""
You are an expert Proxmox infrastructure consultant. Analyze the current infrastructure state and provide optimization recommendations.

Target: {target}
Analysis Type: {analysis_type}

Current Infrastructure State:
{json.dumps(current_state, indent=2)}

Please provide:
1. Key findings about the current state
2. Specific optimization recommendations
3. Priority levels (High, Medium, Low)
4. Expected impact of each recommendation
5. Implementation steps where applicable

Focus on {analysis_type} optimization for {target}.

Format your response as structured recommendations with clear categories and actionable items.
"""
    
    def _parse_optimization_response(self, response_text: str) -> Dict[str, Any]:
        """Parse optimization recommendations from AI response."""
        # This is a simplified parser - in production you might want more sophisticated parsing
        return {
            'recommendations': response_text,
            'performance': [],
            'cost': [],
            'security': [],
            'resource': []
        }
    
    async def explain_configuration(
        self, 
        config_content: str, 
        file_type: str,
        detail_level: str = "detailed"
    ) -> str:
        """Explain configuration files in plain English."""
        prompt = f"""
You are an expert system administrator. Please explain this {file_type} configuration file in plain English.

Detail Level: {detail_level}

Configuration:
```
{config_content}
```

Please provide:
1. Overview of what this configuration does
2. Explanation of key components and settings
3. Any potential issues or recommendations
4. Security considerations if applicable

Adjust the detail level based on: {detail_level}
- brief: High-level overview only
- detailed: Comprehensive explanation of all components
- comprehensive: In-depth analysis with best practices and alternatives
"""
        
        try:
            response = await self._make_ai_request(prompt)
            explanation = response.content[0].text
            
            logger.info("Configuration explained", file_type=file_type, detail_level=detail_level)
            return explanation
            
        except Exception as e:
            logger.error("Failed to explain configuration", error=str(e))
            raise AIServiceError(f"Configuration explanation failed: {e}")
    
    async def _make_ai_request(self, prompt: str) -> Message:
        """Make request to Anthropic Claude API with proper error handling."""
        try:
            # Run the synchronous API call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.settings.anthropic.model,
                    max_tokens=self.settings.anthropic.max_tokens,
                    temperature=self.settings.anthropic.temperature,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
            )
            
            return response
            
        except anthropic.APIConnectionError as e:
            logger.error("AI API connection error", error=str(e))
            raise AIServiceError(f"Failed to connect to AI service: {e}")
        except anthropic.APIError as e:
            logger.error("AI API error", error=str(e))
            raise AIServiceError(f"AI service error: {e}")
        except Exception as e:
            logger.error("Unexpected AI service error", error=str(e))
            raise AIServiceError(f"Unexpected error: {e}")


# Convenience functions for common operations

async def generate_vm_from_description(description: str) -> Dict[str, Any]:
    """Generate VM configuration from natural language description."""
    service = AIService()
    return await service.generate_vm_config(description)


async def optimize_infrastructure(target: str, analysis_type: str = "performance") -> Dict[str, Any]:
    """Get optimization recommendations for infrastructure."""
    service = AIService()
    # This would need to gather current state first
    current_state = {}  # Placeholder
    return await service.generate_optimization_recommendations(current_state, target, analysis_type)


async def explain_config_file(file_path: str, detail_level: str = "detailed") -> str:
    """Explain a configuration file."""
    from pathlib import Path
    
    path = Path(file_path)
    with open(path, 'r') as f:
        content = f.read()
    
    service = AIService()
    return await service.explain_configuration(content, path.suffix, detail_level)