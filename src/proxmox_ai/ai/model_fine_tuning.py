"""
Model Fine-tuning Framework for Proxmox AI Assistant.

This module provides capabilities to fine-tune local models using HuggingFace
transformers for better infrastructure automation understanding.
"""

import os
import json
import torch
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

try:
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer,
        DataCollatorForLanguageModeling, BitsAndBytesConfig
    )
    from datasets import Dataset, load_dataset
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel
    import wandb
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class FineTuningConfig:
    """Configuration for model fine-tuning."""
    model_name: str
    output_dir: str
    dataset_path: str
    max_seq_length: int = 512
    batch_size: int = 4
    learning_rate: float = 2e-4
    num_epochs: int = 3
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    save_steps: int = 500
    logging_steps: int = 50
    use_lora: bool = True
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    quantization: bool = True
    wandb_project: Optional[str] = None


@dataclass
class InfrastructureDataPoint:
    """Single training data point for infrastructure automation."""
    user_input: str
    intent: str
    parameters: Dict[str, Any]
    generated_code: str
    explanation: str
    skill_level: str


class InfrastructureDatasetGenerator:
    """
    Generates synthetic training data for infrastructure automation tasks.
    """
    
    def __init__(self):
        """Initialize the dataset generator."""
        self.terraform_templates = self._load_terraform_templates()
        self.ansible_templates = self._load_ansible_templates()
        self.user_intents = self._load_user_intents()
    
    def _load_terraform_templates(self) -> List[Dict]:
        """Load Terraform template patterns."""
        return [
            {
                "intent": "create_vm",
                "template": """
resource "proxmox_vm_qemu" "vm" {
  name         = "{vm_name}"
  target_node  = "{node}"
  clone        = "{template}"
  cores        = {cores}
  memory       = {memory}
  disk {{
    size     = "{disk_size}"
    storage  = "{storage}"
  }}
  network {{
    model    = "virtio"
    bridge   = "{bridge}"
  }}
}""",
                "parameters": ["vm_name", "node", "template", "cores", "memory", "disk_size", "storage", "bridge"]
            },
            {
                "intent": "create_web_server",
                "template": """
resource "proxmox_vm_qemu" "web_server" {
  name         = "{vm_name}"
  target_node  = "{node}"
  clone        = "ubuntu-22.04-template"
  cores        = {cores}
  memory       = {memory}
  
  disk {{
    size     = "{disk_size}"
    storage  = "local-lvm"
  }}
  
  network {{
    model    = "virtio"
    bridge   = "vmbr0"
    firewall = true
  }}
  
  ciuser     = "ubuntu"
  sshkeys    = file("~/.ssh/id_rsa.pub")
  ipconfig0  = "ip=dhcp"
  
  provisioner "remote-exec" {{
    inline = [
      "sudo apt update",
      "sudo apt install -y nginx",
      "sudo systemctl enable nginx",
      "sudo systemctl start nginx"
    ]
  }}
}""",
                "parameters": ["vm_name", "node", "cores", "memory", "disk_size"]
            }
        ]
    
    def _load_ansible_templates(self) -> List[Dict]:
        """Load Ansible playbook patterns."""
        return [
            {
                "intent": "configure_web_server",
                "template": """
---
- name: Configure Web Server
  hosts: {target_hosts}
  become: yes
  vars:
    domain_name: {domain_name}
    ssl_enabled: {ssl_enabled}
  
  tasks:
    - name: Install Nginx
      package:
        name: nginx
        state: present
    
    - name: Start and enable Nginx
      service:
        name: nginx
        state: started
        enabled: yes
    
    - name: Configure firewall for HTTP/HTTPS
      ufw:
        rule: allow
        port: "{{ item }}"
      loop:
        - '80'
        - '443'
""",
                "parameters": ["target_hosts", "domain_name", "ssl_enabled"]
            }
        ]
    
    def _load_user_intents(self) -> List[Dict]:
        """Load user intent patterns for training data generation."""
        return [
            {
                "intent": "create_vm",
                "patterns": [
                    "Create a VM with {cores} cores and {memory}GB RAM",
                    "I need a virtual machine with {cores} CPU cores and {memory}GB memory",
                    "Deploy a server with {cores} cores, {memory}GB RAM and {disk_size} storage",
                    "Set up a VM: {cores} cores, {memory}GB RAM, {disk_size} disk",
                    "Provision a virtual machine - {cores} CPU, {memory}GB memory, {disk_size} storage"
                ],
                "skill_levels": ["beginner", "intermediate", "expert"]
            },
            {
                "intent": "create_web_server",
                "patterns": [
                    "Create a web server with nginx",
                    "I need a web server for my application",
                    "Set up an nginx web server with {cores} cores",
                    "Deploy a web server with {memory}GB RAM and nginx",
                    "Build a web hosting server with security hardening"
                ],
                "skill_levels": ["beginner", "intermediate", "expert"]
            }
        ]
    
    def generate_training_data(self, num_samples: int = 1000) -> List[InfrastructureDataPoint]:
        """Generate synthetic training data for infrastructure tasks."""
        training_data = []
        
        for _ in range(num_samples):
            # Randomly select intent and template
            intent_data = self._select_random_intent()
            
            # Generate parameters
            parameters = self._generate_parameters(intent_data)
            
            # Generate user input
            user_input = self._generate_user_input(intent_data, parameters)
            
            # Generate code
            if intent_data["type"] == "terraform":
                generated_code = self._generate_terraform_code(intent_data, parameters)
            else:
                generated_code = self._generate_ansible_code(intent_data, parameters)
            
            # Generate explanation
            explanation = self._generate_explanation(intent_data, parameters, generated_code)
            
            # Select skill level
            skill_level = self._select_skill_level()
            
            training_data.append(InfrastructureDataPoint(
                user_input=user_input,
                intent=intent_data["intent"],
                parameters=parameters,
                generated_code=generated_code,
                explanation=explanation,
                skill_level=skill_level
            ))
        
        return training_data
    
    def _select_random_intent(self) -> Dict:
        """Randomly select an intent and corresponding template."""
        import random
        
        # Combine terraform and ansible intents
        all_intents = []
        
        for template in self.terraform_templates:
            all_intents.append({
                "intent": template["intent"],
                "template": template["template"],
                "parameters": template["parameters"],
                "type": "terraform"
            })
        
        for template in self.ansible_templates:
            all_intents.append({
                "intent": template["intent"],
                "template": template["template"], 
                "parameters": template["parameters"],
                "type": "ansible"
            })
        
        return random.choice(all_intents)
    
    def _generate_parameters(self, intent_data: Dict) -> Dict[str, Any]:
        """Generate realistic parameters for templates."""
        import random
        
        parameters = {}
        
        # Common parameter generation
        if "cores" in intent_data["parameters"]:
            parameters["cores"] = random.choice([1, 2, 4, 8])
        
        if "memory" in intent_data["parameters"]:
            parameters["memory"] = random.choice([1024, 2048, 4096, 8192])
        
        if "disk_size" in intent_data["parameters"]:
            parameters["disk_size"] = random.choice(["20G", "40G", "80G", "100G"])
        
        if "vm_name" in intent_data["parameters"]:
            names = ["web-server", "app-server", "db-server", "dev-vm", "test-vm"]
            parameters["vm_name"] = random.choice(names)
        
        if "node" in intent_data["parameters"]:
            parameters["node"] = "proxmox-01"
        
        if "template" in intent_data["parameters"]:
            templates = ["ubuntu-22.04-template", "debian-11-template", "centos-8-template"]
            parameters["template"] = random.choice(templates)
        
        if "storage" in intent_data["parameters"]:
            parameters["storage"] = "local-lvm"
        
        if "bridge" in intent_data["parameters"]:
            parameters["bridge"] = "vmbr0"
        
        # Ansible-specific parameters
        if "target_hosts" in intent_data["parameters"]:
            parameters["target_hosts"] = "webservers"
        
        if "domain_name" in intent_data["parameters"]:
            domains = ["example.com", "myapp.local", "webapp.dev"]
            parameters["domain_name"] = random.choice(domains)
        
        if "ssl_enabled" in intent_data["parameters"]:
            parameters["ssl_enabled"] = random.choice([True, False])
        
        return parameters
    
    def _generate_user_input(self, intent_data: Dict, parameters: Dict) -> str:
        """Generate natural language user input."""
        import random
        
        # Find matching user intent patterns
        for intent_pattern in self.user_intents:
            if intent_pattern["intent"] == intent_data["intent"]:
                pattern = random.choice(intent_pattern["patterns"])
                
                # Fill in parameters
                try:
                    return pattern.format(**parameters)
                except KeyError:
                    # If some parameters are missing, use the pattern as-is
                    return pattern
        
        # Fallback generic pattern
        return f"Create infrastructure for {intent_data['intent']}"
    
    def _generate_terraform_code(self, intent_data: Dict, parameters: Dict) -> str:
        """Generate Terraform code from template and parameters."""
        try:
            return intent_data["template"].format(**parameters)
        except KeyError as e:
            logger.warning(f"Missing parameter for Terraform template: {e}")
            return intent_data["template"]
    
    def _generate_ansible_code(self, intent_data: Dict, parameters: Dict) -> str:
        """Generate Ansible code from template and parameters."""
        try:
            return intent_data["template"].format(**parameters)
        except KeyError as e:
            logger.warning(f"Missing parameter for Ansible template: {e}")
            return intent_data["template"]
    
    def _generate_explanation(self, intent_data: Dict, parameters: Dict, generated_code: str) -> str:
        """Generate explanation for the generated code."""
        explanations = {
            "create_vm": f"This Terraform configuration creates a virtual machine with {parameters.get('cores', 'N')} CPU cores and {parameters.get('memory', 'N')}MB of RAM. The VM is cloned from a template and configured with appropriate networking and storage settings.",
            "create_web_server": f"This configuration deploys a web server VM with nginx pre-installed. The server has {parameters.get('cores', 'N')} cores and {parameters.get('memory', 'N')}MB RAM, with automatic provisioning of the web server software.",
            "configure_web_server": f"This Ansible playbook configures nginx on target servers, installs necessary packages, and sets up firewall rules for HTTP/HTTPS traffic."
        }
        
        return explanations.get(intent_data["intent"], "This configuration sets up the requested infrastructure components with best practices for security and performance.")
    
    def _select_skill_level(self) -> str:
        """Randomly select a skill level for the training sample."""
        import random
        return random.choice(["beginner", "intermediate", "expert"])


class HuggingFaceFineTuner:
    """
    Fine-tuning implementation using HuggingFace transformers and PEFT.
    """
    
    def __init__(self, config: FineTuningConfig):
        """Initialize the fine-tuner."""
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace transformers not available. Install with: pip install transformers datasets peft bitsandbytes")
        
        self.config = config
        self.tokenizer = None
        self.model = None
        self.training_dataset = None
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging and experiment tracking."""
        if self.config.wandb_project:
            try:
                wandb.init(project=self.config.wandb_project)
            except Exception as e:
                logger.warning(f"Failed to initialize wandb: {e}")
    
    def load_model_and_tokenizer(self):
        """Load the base model and tokenizer."""
        logger.info(f"Loading model: {self.config.model_name}")
        
        # Setup quantization if requested
        quantization_config = None
        if self.config.quantization:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        
        # Setup LoRA if requested
        if self.config.use_lora:
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=self.config.lora_rank,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
            )
            
            self.model = get_peft_model(self.model, peft_config)
            self.model.print_trainable_parameters()
        
        logger.info("Model and tokenizer loaded successfully")
    
    def prepare_dataset(self, training_data: List[InfrastructureDataPoint]):
        """Prepare the training dataset."""
        logger.info(f"Preparing dataset with {len(training_data)} samples")
        
        # Convert training data to instruction format
        formatted_data = []
        for data_point in training_data:
            instruction = self._format_instruction(data_point)
            formatted_data.append({"text": instruction})
        
        # Create HuggingFace dataset
        dataset = Dataset.from_list(formatted_data)
        
        # Tokenize the dataset
        def tokenize_function(examples):
            outputs = self.tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=self.config.max_seq_length,
                return_overflowing_tokens=False,
            )
            return outputs
        
        self.training_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
        )
        
        logger.info("Dataset prepared successfully")
    
    def _format_instruction(self, data_point: InfrastructureDataPoint) -> str:
        """Format a data point as an instruction for training."""
        instruction = f"""### Instruction:
You are an expert infrastructure automation assistant. A user with {data_point.skill_level} skill level is asking for help with infrastructure as code.

User Request: {data_point.user_input}

### Response:
I'll help you {data_point.intent.replace('_', ' ')}. Here's the configuration:

```
{data_point.generated_code}
```

**Explanation**: {data_point.explanation}

**Parameters detected**:
{json.dumps(data_point.parameters, indent=2)}

This configuration follows best practices for security, performance, and maintainability suitable for {data_point.skill_level} level users.
"""
        return instruction
    
    def train(self):
        """Execute the fine-tuning process."""
        if not self.model or not self.training_dataset:
            raise ValueError("Model and dataset must be prepared before training")
        
        logger.info("Starting fine-tuning process")
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            num_train_epochs=self.config.num_epochs,
            learning_rate=self.config.learning_rate,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            optim="paged_adamw_8bit",
            logging_dir=f"{self.config.output_dir}/logs",
            save_strategy="steps",
            report_to="wandb" if self.config.wandb_project else None,
            run_name=f"proxmox-ai-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        )
        
        # Setup data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.training_dataset,
            data_collator=data_collator,
        )
        
        # Start training
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        logger.info(f"Fine-tuning completed. Model saved to {self.config.output_dir}")
    
    def save_model(self, path: str):
        """Save the fine-tuned model."""
        if self.model:
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            logger.info(f"Model saved to {path}")


def create_infrastructure_dataset(num_samples: int = 5000, output_path: str = "infrastructure_dataset.json"):
    """Create and save a synthetic infrastructure automation dataset."""
    logger.info(f"Generating {num_samples} training samples")
    
    generator = InfrastructureDatasetGenerator()
    training_data = generator.generate_training_data(num_samples)
    
    # Convert to JSON serializable format
    dataset_json = [asdict(data_point) for data_point in training_data]
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(dataset_json, f, indent=2)
    
    logger.info(f"Dataset saved to {output_path}")
    return training_data


def fine_tune_infrastructure_model(
    base_model: str = "microsoft/DialoGPT-medium",
    dataset_path: str = "infrastructure_dataset.json",
    output_dir: str = "./fine-tuned-infrastructure-model",
    num_samples: int = 1000
):
    """Fine-tune a model for infrastructure automation tasks."""
    
    # Create dataset if it doesn't exist
    if not os.path.exists(dataset_path):
        logger.info("Creating training dataset...")
        create_infrastructure_dataset(num_samples, dataset_path)
    
    # Load training data
    with open(dataset_path, 'r') as f:
        dataset_json = json.load(f)
    
    training_data = [InfrastructureDataPoint(**data) for data in dataset_json]
    
    # Setup fine-tuning configuration
    config = FineTuningConfig(
        model_name=base_model,
        output_dir=output_dir,
        dataset_path=dataset_path,
        num_epochs=3,
        batch_size=4,
        learning_rate=2e-4,
        use_lora=True,
        quantization=True
    )
    
    # Initialize fine-tuner
    fine_tuner = HuggingFaceFineTuner(config)
    
    # Load model and prepare dataset
    fine_tuner.load_model_and_tokenizer()
    fine_tuner.prepare_dataset(training_data)
    
    # Start training
    fine_tuner.train()
    
    logger.info("Fine-tuning process completed successfully")


if __name__ == "__main__":
    # Example usage
    create_infrastructure_dataset(1000, "infrastructure_dataset.json")
    print("Dataset created successfully!")
    
    # Uncomment to run fine-tuning (requires significant computational resources)
    # fine_tune_infrastructure_model()