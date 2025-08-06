"""
Advanced AI Model Fine-Tuning Framework for Infrastructure Automation.

This module provides enterprise-grade model fine-tuning capabilities optimized for
Intel N150 hardware with 4 cores and 7.8GB RAM, supporting infrastructure-specific
model customization and optimization.
"""

import os
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import torch
import structlog
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments,
    DataCollatorForLanguageModeling, BitsAndBytesConfig, 
    TrainerCallback, TrainerState, TrainerControl
)
from datasets import Dataset, load_dataset
from peft import LoraConfig, get_peft_model, TaskType, PeftConfig, PeftModel
from optimum.intel import OVModelForCausalLM
import evaluate
import psutil

from ..core.hardware_detector import hardware_detector
from ..core.performance_monitor import PerformanceMonitor

logger = structlog.get_logger(__name__)


@dataclass
class FineTuningConfig:
    """Fine-tuning configuration optimized for Intel N150 hardware."""
    
    # Model configuration
    base_model: str = "microsoft/DialoGPT-small"  # Lightweight model for N150
    model_name: str = "proxmox-ai-infrastructure"
    max_seq_length: int = 512  # Conservative for memory constraints
    
    # LoRA configuration for memory efficiency
    lora_r: int = 8  # Rank - lower for memory efficiency
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    lora_target_modules: List[str] = None
    
    # Training parameters optimized for N150
    batch_size: int = 1  # Very small for memory constraints
    gradient_accumulation_steps: int = 8  # Simulate larger batch
    learning_rate: float = 2e-4
    num_epochs: int = 3  # Conservative for quick training
    warmup_steps: int = 100
    weight_decay: float = 0.01
    
    # Hardware optimization
    use_4bit_quantization: bool = True
    use_8bit_adam: bool = True
    gradient_checkpointing: bool = True
    dataloader_num_workers: int = 1  # Single worker for N150
    
    # Memory management
    max_memory_usage_gb: float = 5.0  # Leave headroom for system
    enable_memory_monitoring: bool = True
    
    def __post_init__(self):
        """Post-initialization hardware optimization."""
        if self.lora_target_modules is None:
            self.lora_target_modules = ["q_proj", "v_proj"]
        
        # Adjust for hardware constraints
        available_memory = hardware_detector.specs.available_memory_gb
        cpu_cores = hardware_detector.specs.cpu_cores
        
        if available_memory < 6.0:
            self.batch_size = 1
            self.max_seq_length = min(self.max_seq_length, 256)
            self.gradient_accumulation_steps = max(self.gradient_accumulation_steps, 16)
        
        if cpu_cores <= 4:
            self.dataloader_num_workers = 1


@dataclass
class FineTuningMetrics:
    """Training metrics and performance data."""
    
    epoch: int
    loss: float
    learning_rate: float
    memory_usage_mb: float
    training_time_seconds: float
    perplexity: Optional[float] = None
    bleu_score: Optional[float] = None
    rouge_score: Optional[float] = None


@dataclass
class InfrastructureDataset:
    """Infrastructure-specific training dataset."""
    
    prompts: List[str]
    completions: List[str]
    categories: List[str]  # e.g., 'terraform', 'ansible', 'proxmox'
    difficulty_levels: List[str]  # 'beginner', 'intermediate', 'expert'
    metadata: List[Dict[str, Any]]


class HardwareOptimizedMemoryCallback(TrainerCallback):
    """Custom callback for memory monitoring during training."""
    
    def __init__(self, config: FineTuningConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor()
        self.memory_alerts = []
    
    def on_step_begin(self, args, state, control, **kwargs):
        """Monitor memory usage at step begin."""
        if self.config.enable_memory_monitoring:
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > 85:  # 85% threshold
                self.memory_alerts.append({
                    'step': state.global_step,
                    'memory_percent': memory_usage,
                    'timestamp': time.time()
                })
                logger.warning(
                    "High memory usage detected",
                    step=state.global_step,
                    memory_percent=memory_usage
                )
                # Trigger garbage collection
                import gc
                gc.collect()
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
    
    def on_epoch_end(self, args, state, control, **kwargs):
        """Log memory stats at epoch end."""
        memory_stats = self.performance_monitor.get_memory_stats()
        logger.info(
            "Epoch memory summary",
            epoch=state.epoch,
            memory_stats=memory_stats
        )


class InfrastructureDatasetGenerator:
    """Generate infrastructure-specific training datasets."""
    
    def __init__(self):
        self.terraform_templates = self._load_terraform_templates()
        self.ansible_templates = self._load_ansible_templates()
        self.proxmox_scenarios = self._load_proxmox_scenarios()
    
    def generate_infrastructure_dataset(self, size: int = 1000) -> InfrastructureDataset:
        """Generate comprehensive infrastructure training dataset."""
        logger.info("Generating infrastructure training dataset", size=size)
        
        prompts = []
        completions = []
        categories = []
        difficulty_levels = []
        metadata = []
        
        # Generate Terraform examples
        terraform_data = self._generate_terraform_examples(size // 3)
        prompts.extend(terraform_data['prompts'])
        completions.extend(terraform_data['completions'])
        categories.extend(['terraform'] * len(terraform_data['prompts']))
        difficulty_levels.extend(terraform_data['difficulty_levels'])
        metadata.extend(terraform_data['metadata'])
        
        # Generate Ansible examples
        ansible_data = self._generate_ansible_examples(size // 3)
        prompts.extend(ansible_data['prompts'])
        completions.extend(ansible_data['completions'])
        categories.extend(['ansible'] * len(ansible_data['prompts']))
        difficulty_levels.extend(ansible_data['difficulty_levels'])
        metadata.extend(ansible_data['metadata'])
        
        # Generate Proxmox examples
        proxmox_data = self._generate_proxmox_examples(size // 3)
        prompts.extend(proxmox_data['prompts'])
        completions.extend(proxmox_data['completions'])
        categories.extend(['proxmox'] * len(proxmox_data['prompts']))
        difficulty_levels.extend(proxmox_data['difficulty_levels'])
        metadata.extend(proxmox_data['metadata'])
        
        return InfrastructureDataset(
            prompts=prompts,
            completions=completions,
            categories=categories,
            difficulty_levels=difficulty_levels,
            metadata=metadata
        )
    
    def _generate_terraform_examples(self, count: int) -> Dict[str, List]:
        """Generate Terraform training examples."""
        prompts = []
        completions = []
        difficulty_levels = []
        metadata = []
        
        # Beginner examples
        for i in range(count // 3):
            prompt = f"Create a simple Proxmox VM with {2 + i % 4} GB RAM"
            completion = f"""resource "proxmox_vm_qemu" "vm_{i}" {{
  name        = "vm-{i}"
  target_node = "proxmox-node"
  cores       = 2
  memory      = {2048 + (i % 4) * 1024}
  disk {{
    size    = "20G"
    type    = "scsi"
    storage = "local-lvm"
  }}
  network {{
    model  = "virtio"
    bridge = "vmbr0"
  }}
  os_type = "cloud-init"
}}"""
            prompts.append(prompt)
            completions.append(completion)
            difficulty_levels.append('beginner')
            metadata.append({'vm_count': 1, 'complexity': 'low'})
        
        # Intermediate examples
        for i in range(count // 3):
            prompt = f"Deploy a load-balanced web application with {2 + i % 3} VMs"
            completion = f"""# Load Balancer
resource "proxmox_vm_qemu" "lb" {{
  name        = "loadbalancer"
  target_node = "proxmox-node"
  cores       = 2
  memory      = 2048
  disk {{
    size    = "20G"
    type    = "scsi"
    storage = "local-lvm"
  }}
  network {{
    model  = "virtio"
    bridge = "vmbr0"
  }}
}}

# Web Servers
resource "proxmox_vm_qemu" "web" {{
  count       = {2 + i % 3}
  name        = "web-server-${{count.index + 1}}"
  target_node = "proxmox-node"
  cores       = 2
  memory      = 4096
  disk {{
    size    = "30G"
    type    = "scsi"
    storage = "local-lvm"
  }}
  network {{
    model  = "virtio"
    bridge = "vmbr0"
  }}
}}"""
            prompts.append(prompt)
            completions.append(completion)
            difficulty_levels.append('intermediate')
            metadata.append({'vm_count': 3 + i % 3, 'complexity': 'medium'})
        
        # Expert examples
        for i in range(count // 3):
            prompt = f"Create a high-availability Kubernetes cluster with monitoring"
            completion = f"""# Kubernetes Master Nodes
resource "proxmox_vm_qemu" "k8s_master" {{
  count       = 3
  name        = "k8s-master-${{count.index + 1}}"
  target_node = "proxmox-node"
  cores       = 4
  memory      = 8192
  disk {{
    size    = "50G"
    type    = "scsi"
    storage = "local-lvm"
  }}
  network {{
    model  = "virtio"
    bridge = "vmbr0"
  }}
  tags = "kubernetes,master"
}}

# Kubernetes Worker Nodes
resource "proxmox_vm_qemu" "k8s_worker" {{
  count       = {3 + i % 5}
  name        = "k8s-worker-${{count.index + 1}}"
  target_node = "proxmox-node"
  cores       = 4
  memory      = 16384
  disk {{
    size    = "100G"
    type    = "scsi"
    storage = "local-lvm"
  }}
  network {{
    model  = "virtio"
    bridge = "vmbr0"
  }}
  tags = "kubernetes,worker"
}}

# Monitoring Stack
resource "proxmox_vm_qemu" "monitoring" {{
  name        = "monitoring-stack"
  target_node = "proxmox-node"
  cores       = 4
  memory      = 8192
  disk {{
    size    = "100G"
    type    = "scsi"
    storage = "local-lvm"
  }}
  network {{
    model  = "virtio"
    bridge = "vmbr0"
  }}
  tags = "monitoring,prometheus,grafana"
}}"""
            prompts.append(prompt)
            completions.append(completion)
            difficulty_levels.append('expert')
            metadata.append({'vm_count': 7 + i % 5, 'complexity': 'high'})
        
        return {
            'prompts': prompts,
            'completions': completions,
            'difficulty_levels': difficulty_levels,
            'metadata': metadata
        }
    
    def _generate_ansible_examples(self, count: int) -> Dict[str, List]:
        """Generate Ansible training examples."""
        prompts = []
        completions = []
        difficulty_levels = []
        metadata = []
        
        # Beginner examples
        for i in range(count // 3):
            prompt = f"Configure a web server with {['nginx', 'apache'][i % 2]}"
            service = ['nginx', 'apache'][i % 2]
            completion = f"""---
- name: Configure {service} web server
  hosts: web_servers
  become: yes
  tasks:
    - name: Install {service}
      package:
        name: {service}
        state: present
    
    - name: Start and enable {service}
      service:
        name: {service}
        state: started
        enabled: yes
    
    - name: Configure firewall
      firewalld:
        service: http
        permanent: yes
        state: enabled
        immediate: yes"""
            prompts.append(prompt)
            completions.append(completion)
            difficulty_levels.append('beginner')
            metadata.append({'service': service, 'complexity': 'low'})
        
        # Intermediate examples
        for i in range(count // 3):
            prompt = f"Deploy a database cluster with replication"
            completion = f"""---
- name: Deploy PostgreSQL cluster
  hosts: db_servers
  become: yes
  vars:
    postgres_version: "14"
    replication_user: "replicator"
  
  tasks:
    - name: Install PostgreSQL
      package:
        name: 
          - postgresql{{{{ postgres_version }}}}
          - postgresql{{{{ postgres_version }}}}-server
        state: present
    
    - name: Initialize database
      command: postgresql-setup --initdb
      when: ansible_hostname == groups['db_servers'][0]
    
    - name: Configure PostgreSQL
      template:
        src: postgresql.conf.j2
        dest: /var/lib/pgsql/data/postgresql.conf
      notify: restart postgresql
    
    - name: Configure replication
      template:
        src: pg_hba.conf.j2
        dest: /var/lib/pgsql/data/pg_hba.conf
      notify: restart postgresql
    
    - name: Start PostgreSQL
      service:
        name: postgresql
        state: started
        enabled: yes
  
  handlers:
    - name: restart postgresql
      service:
        name: postgresql
        state: restarted"""
            prompts.append(prompt)
            completions.append(completion)
            difficulty_levels.append('intermediate')
            metadata.append({'service': 'postgresql', 'complexity': 'medium'})
        
        # Expert examples
        for i in range(count // 3):
            prompt = f"Set up a complete monitoring and alerting stack"
            completion = f"""---
- name: Deploy monitoring stack
  hosts: monitoring
  become: yes
  vars:
    prometheus_version: "2.40.0"
    grafana_version: "9.3.0"
    alertmanager_version: "0.25.0"
  
  tasks:
    - name: Create monitoring users
      user:
        name: "{{{{ item }}}}"
        system: yes
        shell: /bin/false
        home: "/var/lib/{{{{ item }}}}"
      loop:
        - prometheus
        - grafana
        - alertmanager
    
    - name: Install Prometheus
      unarchive:
        src: "https://github.com/prometheus/prometheus/releases/download/v{{{{ prometheus_version }}}}/prometheus-{{{{ prometheus_version }}}}.linux-amd64.tar.gz"
        dest: /opt
        remote_src: yes
        owner: prometheus
        group: prometheus
        creates: "/opt/prometheus-{{{{ prometheus_version }}}}.linux-amd64"
    
    - name: Configure Prometheus
      template:
        src: prometheus.yml.j2
        dest: /etc/prometheus/prometheus.yml
        owner: prometheus
        group: prometheus
      notify: restart prometheus
    
    - name: Install Grafana
      yum:
        name: "https://dl.grafana.com/oss/release/grafana-{{{{ grafana_version }}}}-1.x86_64.rpm"
        state: present
    
    - name: Configure Grafana
      template:
        src: grafana.ini.j2
        dest: /etc/grafana/grafana.ini
      notify: restart grafana
    
    - name: Install Alertmanager
      unarchive:
        src: "https://github.com/prometheus/alertmanager/releases/download/v{{{{ alertmanager_version }}}}/alertmanager-{{{{ alertmanager_version }}}}.linux-amd64.tar.gz"
        dest: /opt
        remote_src: yes
        owner: prometheus
        group: prometheus
    
    - name: Start monitoring services
      service:
        name: "{{{{ item }}}}"
        state: started
        enabled: yes
      loop:
        - prometheus
        - grafana-server
        - alertmanager
  
  handlers:
    - name: restart prometheus
      service:
        name: prometheus
        state: restarted
    
    - name: restart grafana
      service:
        name: grafana-server
        state: restarted"""
            prompts.append(prompt)
            completions.append(completion)
            difficulty_levels.append('expert')
            metadata.append({'services': ['prometheus', 'grafana', 'alertmanager'], 'complexity': 'high'})
        
        return {
            'prompts': prompts,
            'completions': completions,
            'difficulty_levels': difficulty_levels,
            'metadata': metadata
        }
    
    def _generate_proxmox_examples(self, count: int) -> Dict[str, List]:
        """Generate Proxmox-specific examples."""
        prompts = []
        completions = []
        difficulty_levels = []
        metadata = []
        
        # Add Proxmox-specific scenarios
        for i in range(count):
            if i % 3 == 0:  # Beginner
                prompt = f"Create a Proxmox backup schedule for VM {100 + i}"
                completion = f"""# Proxmox Backup Configuration
vzdump --mode snapshot --vmid {100 + i} --storage backup-storage --compress gzip --mailnotification always --quiet 1

# Schedule in crontab
# 0 2 * * * vzdump --mode snapshot --vmid {100 + i} --storage backup-storage --compress gzip"""
                difficulty = 'beginner'
            elif i % 3 == 1:  # Intermediate
                prompt = f"Configure Proxmox HA cluster with {2 + i % 3} nodes"
                completion = f"""# HA Cluster Configuration
pvecm create cluster-prod

# Add nodes to cluster
{chr(10).join([f'pvecm add node-{j+2}' for j in range(1 + i % 3)])}

# Configure HA group
ha-manager add group backup-group --nodes "node-1,node-2" --restricted 1

# Add VM to HA
ha-manager add vm:{200 + i} --group backup-group --state started"""
                difficulty = 'intermediate'
            else:  # Expert
                prompt = f"Set up Proxmox Ceph storage cluster"
                completion = f"""# Install Ceph packages
pveceph install --repository quincy

# Initialize Ceph cluster
pveceph init --network 10.0.0.0/24

# Create monitors
pveceph mon create

# Create OSD (Object Storage Daemon)
pveceph osd create /dev/sdb
pveceph osd create /dev/sdc

# Create Ceph pool
pveceph pool create ceph-pool --size 2 --min_size 1

# Add Ceph storage to Proxmox
pvesm add cephfs ceph-storage --server 10.0.0.1 --username admin --content backup,vztmpl,iso,images"""
                difficulty = 'expert'
            
            prompts.append(prompt)
            completions.append(completion)
            difficulty_levels.append(difficulty)
            metadata.append({'platform': 'proxmox', 'complexity': difficulty})
        
        return {
            'prompts': prompts,
            'completions': completions,
            'difficulty_levels': difficulty_levels,
            'metadata': metadata
        }
    
    def _load_terraform_templates(self) -> Dict[str, str]:
        """Load Terraform template library."""
        return {
            'vm_basic': 'Basic VM configuration',
            'vm_cluster': 'Multi-VM cluster setup',
            'networking': 'Network configuration',
            'storage': 'Storage setup'
        }
    
    def _load_ansible_templates(self) -> Dict[str, str]:
        """Load Ansible template library."""
        return {
            'web_server': 'Web server configuration',
            'database': 'Database setup',
            'monitoring': 'Monitoring stack',
            'security': 'Security hardening'
        }
    
    def _load_proxmox_scenarios(self) -> Dict[str, str]:
        """Load Proxmox scenario library."""
        return {
            'backup': 'Backup configuration',
            'ha_cluster': 'High availability setup',
            'storage_cluster': 'Storage clustering',
            'networking': 'Network configuration'
        }


class AdvancedModelFineTuner:
    """Advanced model fine-tuning with hardware optimization and enterprise features."""
    
    def __init__(self, config: FineTuningConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor()
        self.dataset_generator = InfrastructureDatasetGenerator()
        self.training_metrics: List[FineTuningMetrics] = []
        
        # Hardware optimization
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_memory = self._calculate_max_memory()
        
        logger.info(
            "Advanced model fine-tuner initialized",
            config=asdict(config),
            device=self.device,
            max_memory_gb=self.max_memory
        )
    
    def _calculate_max_memory(self) -> float:
        """Calculate maximum safe memory usage."""
        available_memory = hardware_detector.specs.available_memory_gb
        # Reserve 2GB for system operations
        return min(self.config.max_memory_usage_gb, available_memory - 2.0)
    
    async def prepare_model_and_tokenizer(self) -> Tuple[Any, Any]:
        """Prepare optimized model and tokenizer for Intel N150."""
        logger.info("Preparing model and tokenizer", base_model=self.config.base_model)
        
        # Quantization config for memory efficiency
        if self.config.use_4bit_quantization:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        else:
            quantization_config = None
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model,
            padding_side="right",
            use_fast=True
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model with optimization
        model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            quantization_config=quantization_config,
            device_map="auto" if torch.cuda.is_available() else None,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        
        # Enable gradient checkpointing for memory efficiency
        if self.config.gradient_checkpointing:
            model.gradient_checkpointing_enable()
        
        # Apply LoRA for parameter-efficient fine-tuning
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.lora_target_modules,
        )
        
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()
        
        return model, tokenizer
    
    def prepare_dataset(self, dataset: InfrastructureDataset) -> Dataset:
        """Prepare training dataset with proper tokenization."""
        logger.info("Preparing training dataset", size=len(dataset.prompts))
        
        # Combine prompts and completions
        formatted_examples = []
        for prompt, completion, category, difficulty in zip(
            dataset.prompts, dataset.completions, 
            dataset.categories, dataset.difficulty_levels
        ):
            # Format as conversation
            formatted_text = f"### Human: {prompt}\n### Assistant: {completion}"
            formatted_examples.append({
                'text': formatted_text,
                'category': category,
                'difficulty': difficulty
            })
        
        # Create HuggingFace dataset
        hf_dataset = Dataset.from_list(formatted_examples)
        
        return hf_dataset
    
    def tokenize_dataset(self, dataset: Dataset, tokenizer) -> Dataset:
        """Tokenize dataset for training."""
        def tokenize_function(examples):
            # Tokenize with proper truncation and padding
            tokenized = tokenizer(
                examples['text'],
                truncation=True,
                padding=False,
                max_length=self.config.max_seq_length,
                return_overflowing_tokens=False,
            )
            
            # For causal LM, labels are the same as input_ids
            tokenized['labels'] = tokenized['input_ids'].copy()
            
            return tokenized
        
        # Apply tokenization
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            num_proc=1,  # Single process for N150
            remove_columns=dataset.column_names,
            desc="Tokenizing dataset"
        )
        
        return tokenized_dataset
    
    async def fine_tune_model(self, dataset: InfrastructureDataset) -> Dict[str, Any]:
        """Fine-tune model with advanced optimization."""
        logger.info("Starting model fine-tuning", dataset_size=len(dataset.prompts))
        
        start_time = time.time()
        
        try:
            # Prepare model and tokenizer
            model, tokenizer = await self.prepare_model_and_tokenizer()
            
            # Prepare dataset
            hf_dataset = self.prepare_dataset(dataset)
            tokenized_dataset = self.tokenize_dataset(hf_dataset, tokenizer)
            
            # Split dataset
            train_size = int(0.9 * len(tokenized_dataset))
            train_dataset = tokenized_dataset.select(range(train_size))
            eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False,  # Causal LM, not masked LM
                pad_to_multiple_of=8 if self.device == "cuda" else None
            )
            
            # Training arguments optimized for Intel N150
            training_args = TrainingArguments(
                output_dir=f"./models/{self.config.model_name}",
                overwrite_output_dir=True,
                num_train_epochs=self.config.num_epochs,
                per_device_train_batch_size=self.config.batch_size,
                per_device_eval_batch_size=self.config.batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
                warmup_steps=self.config.warmup_steps,
                logging_dir=f"./logs/{self.config.model_name}",
                logging_steps=10,
                eval_steps=50,
                save_steps=100,
                evaluation_strategy="steps",
                save_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                report_to=[],  # Disable wandb, tensorboard for simplicity
                dataloader_num_workers=self.config.dataloader_num_workers,
                dataloader_pin_memory=False,  # Disable for CPU training
                group_by_length=True,  # Group similar lengths for efficiency
                remove_unused_columns=False,
                optim="adamw_torch" if not self.config.use_8bit_adam else "adamw_8bit",
                fp16=self.device == "cuda",  # Use fp16 only for GPU
                gradient_checkpointing=self.config.gradient_checkpointing,
                dataloader_drop_last=True,
                push_to_hub=False,
                resume_from_checkpoint=None,
                ignore_data_skip=True
            )
            
            # Memory monitoring callback
            memory_callback = HardwareOptimizedMemoryCallback(self.config)
            
            # Custom training callback for metrics
            class MetricsCallback(TrainerCallback):
                def __init__(self, fine_tuner):
                    self.fine_tuner = fine_tuner
                
                def on_epoch_end(self, args, state, control, **kwargs):
                    # Record metrics
                    memory_usage = psutil.virtual_memory().used / (1024**2)  # MB
                    
                    metric = FineTuningMetrics(
                        epoch=int(state.epoch),
                        loss=state.log_history[-1].get('eval_loss', 0.0),
                        learning_rate=state.log_history[-1].get('learning_rate', 0.0),
                        memory_usage_mb=memory_usage,
                        training_time_seconds=time.time() - start_time
                    )
                    
                    self.fine_tuner.training_metrics.append(metric)
                    
                    logger.info(
                        "Epoch completed",
                        epoch=metric.epoch,
                        loss=metric.loss,
                        memory_mb=metric.memory_usage_mb
                    )
            
            metrics_callback = MetricsCallback(self)
            
            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                callbacks=[memory_callback, metrics_callback]
            )
            
            # Start training
            logger.info("Beginning model training")
            trainer.train()
            
            # Save final model
            final_model_path = f"./models/{self.config.model_name}_final"
            trainer.save_model(final_model_path)
            tokenizer.save_pretrained(final_model_path)
            
            # Calculate final metrics
            total_time = time.time() - start_time
            final_memory = psutil.virtual_memory().used / (1024**2)
            
            results = {
                'model_path': final_model_path,
                'training_time_seconds': total_time,
                'final_memory_usage_mb': final_memory,
                'epochs_completed': self.config.num_epochs,
                'training_metrics': [asdict(m) for m in self.training_metrics],
                'model_size_mb': self._get_model_size_mb(final_model_path),
                'success': True
            }
            
            # Evaluate model
            eval_results = trainer.evaluate()
            results['evaluation_metrics'] = eval_results
            
            logger.info(
                "Model fine-tuning completed successfully",
                total_time=total_time,
                final_loss=eval_results.get('eval_loss', 'N/A'),
                model_path=final_model_path
            )
            
            return results
            
        except Exception as e:
            logger.error("Model fine-tuning failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'training_time_seconds': time.time() - start_time
            }
    
    def _get_model_size_mb(self, model_path: str) -> float:
        """Calculate model size in MB."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(model_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
    
    async def optimize_for_inference(self, model_path: str) -> Dict[str, Any]:
        """Optimize fine-tuned model for inference."""
        logger.info("Optimizing model for inference", model_path=model_path)
        
        try:
            # Load the fine-tuned model
            model = PeftModel.from_pretrained(
                AutoModelForCausalLM.from_pretrained(self.config.base_model),
                model_path
            )
            
            # Merge LoRA weights for faster inference
            merged_model = model.merge_and_unload()
            
            # Save merged model
            optimized_path = f"{model_path}_optimized"
            merged_model.save_pretrained(optimized_path)
            
            # Optionally convert to ONNX for Intel optimization
            if hardware_detector.specs.cpu_model and "intel" in hardware_detector.specs.cpu_model.lower():
                try:
                    # Intel OpenVINO optimization
                    ov_model = OVModelForCausalLM.from_pretrained(
                        optimized_path,
                        export=True,
                        device="CPU"
                    )
                    ov_optimized_path = f"{model_path}_openvino"
                    ov_model.save_pretrained(ov_optimized_path)
                    
                    logger.info("Intel OpenVINO optimization completed", path=ov_optimized_path)
                    
                    return {
                        'success': True,
                        'optimized_path': optimized_path,
                        'openvino_path': ov_optimized_path,
                        'optimization_type': 'intel_openvino'
                    }
                except Exception as e:
                    logger.warning("OpenVINO optimization failed", error=str(e))
            
            return {
                'success': True,
                'optimized_path': optimized_path,
                'optimization_type': 'lora_merged'
            }
            
        except Exception as e:
            logger.error("Model optimization failed", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary."""
        if not self.training_metrics:
            return {'status': 'no_training_data'}
        
        total_time = sum(m.training_time_seconds for m in self.training_metrics)
        avg_loss = sum(m.loss for m in self.training_metrics) / len(self.training_metrics)
        max_memory = max(m.memory_usage_mb for m in self.training_metrics)
        
        return {
            'total_epochs': len(self.training_metrics),
            'total_training_time_seconds': total_time,
            'average_loss': avg_loss,
            'final_loss': self.training_metrics[-1].loss if self.training_metrics else 0,
            'max_memory_usage_mb': max_memory,
            'hardware_optimized': True,
            'config_used': asdict(self.config),
            'metrics_by_epoch': [asdict(m) for m in self.training_metrics]
        }


# Global fine-tuning manager
fine_tuning_manager = None

def get_fine_tuning_manager(config: Optional[FineTuningConfig] = None) -> AdvancedModelFineTuner:
    """Get global fine-tuning manager instance."""
    global fine_tuning_manager
    
    if fine_tuning_manager is None:
        if config is None:
            config = FineTuningConfig()
        fine_tuning_manager = AdvancedModelFineTuner(config)
    
    return fine_tuning_manager


# CLI integration functions
async def quick_fine_tune_infrastructure_model(
    dataset_size: int = 500,
    model_name: str = "proxmox-ai-infrastructure",
    epochs: int = 2
) -> Dict[str, Any]:
    """Quick fine-tuning for infrastructure automation."""
    
    # Create optimized config for Intel N150
    config = FineTuningConfig(
        model_name=model_name,
        num_epochs=epochs,
        batch_size=1,
        gradient_accumulation_steps=16,
        max_seq_length=384  # Conservative for memory
    )
    
    # Initialize fine-tuner
    fine_tuner = AdvancedModelFineTuner(config)
    
    # Generate dataset
    dataset = fine_tuner.dataset_generator.generate_infrastructure_dataset(dataset_size)
    
    # Fine-tune model
    results = await fine_tuner.fine_tune_model(dataset)
    
    if results.get('success'):
        # Optimize for inference
        optimization_results = await fine_tuner.optimize_for_inference(results['model_path'])
        results['optimization'] = optimization_results
    
    return results


# Export main classes and functions
__all__ = [
    'FineTuningConfig',
    'FineTuningMetrics', 
    'InfrastructureDataset',
    'AdvancedModelFineTuner',
    'InfrastructureDatasetGenerator',
    'get_fine_tuning_manager',
    'quick_fine_tune_infrastructure_model'
]