#!/usr/bin/env python3
"""
VM Template Versioning and Management System for Proxmox
Handles template creation, versioning, and lifecycle management
"""

import os
import json
import yaml
import hashlib
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
import logging
from proxmoxer import ProxmoxAPI
from config_manager import SecureConfigManager

@dataclass
class TemplateVersion:
    """VM template version information"""
    version_id: str
    template_id: int
    name: str
    description: str
    created_at: str
    created_by: str
    base_image: str
    os_type: str
    memory: int
    cores: int
    disk_size: int
    packages: List[str]
    config_hash: str
    parent_version: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class TemplateConfig:
    """Template configuration specification"""
    name: str
    description: str
    base_image: str
    os_type: str
    memory: int
    cores: int
    disk_size: int
    network_config: Dict[str, Any]
    cloud_init_config: Dict[str, Any]
    packages: List[str]
    custom_scripts: List[str]
    security_hardening: bool = True
    monitoring_enabled: bool = True

class TemplateVersionManager:
    """Manages VM template versions and lifecycle"""
    
    def __init__(self, config_manager: SecureConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.templates_dir = Path("/home/diszay-claudedev/projects/iac-ai-assistant/config/templates")
        self.versions_file = self.templates_dir / "versions.json"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize Proxmox connection
        self._init_proxmox_connection()
        
        # Load existing versions
        self.versions = self._load_versions()
    
    def _init_proxmox_connection(self):
        """Initialize Proxmox API connection"""
        try:
            credentials = self.config_manager.load_credentials("production")
            self.proxmox = ProxmoxAPI(
                credentials.host,
                user=credentials.user,
                password=credentials.password,
                verify_ssl=credentials.verify_ssl
            )
            self.logger.info("Proxmox API connection established")
        except Exception as e:
            self.logger.error(f"Failed to connect to Proxmox API: {str(e)}")
            self.proxmox = None
    
    def _load_versions(self) -> Dict[str, List[TemplateVersion]]:
        """Load template versions from storage"""
        if not self.versions_file.exists():
            return {}
        
        try:
            with open(self.versions_file, 'r') as f:
                versions_data = json.load(f)
            
            versions = {}
            for template_name, version_list in versions_data.items():
                versions[template_name] = [
                    TemplateVersion(**version_data) 
                    for version_data in version_list
                ]
            
            return versions
            
        except Exception as e:
            self.logger.error(f"Failed to load template versions: {str(e)}")
            return {}
    
    def _save_versions(self):
        """Save template versions to storage"""
        try:
            versions_data = {}
            for template_name, version_list in self.versions.items():
                versions_data[template_name] = [
                    asdict(version) for version in version_list
                ]
            
            with open(self.versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)
            
            self.logger.info("Template versions saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save template versions: {str(e)}")
    
    def _generate_version_id(self, template_name: str) -> str:
        """Generate unique version ID"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{template_name}-{timestamp}"
    
    def _calculate_config_hash(self, config: TemplateConfig) -> str:
        """Calculate hash of template configuration"""
        config_str = json.dumps(asdict(config), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def create_template_from_config(self, config_file: str, created_by: str = "system") -> TemplateVersion:
        """Create new template version from configuration file"""
        config_path = self.templates_dir / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"Template configuration not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        template_config = TemplateConfig(**config_data)
        return self.create_template(template_config, created_by)
    
    def create_template(self, config: TemplateConfig, created_by: str = "system") -> TemplateVersion:
        """Create new template version"""
        self.logger.info(f"Creating new template version: {config.name}")
        
        # Generate version information
        version_id = self._generate_version_id(config.name)
        config_hash = self._calculate_config_hash(config)
        
        # Get next available template ID
        template_id = self._get_next_template_id()
        
        # Create template version record
        version = TemplateVersion(
            version_id=version_id,
            template_id=template_id,
            name=config.name,
            description=config.description,
            created_at=datetime.datetime.now().isoformat(),
            created_by=created_by,
            base_image=config.base_image,
            os_type=config.os_type,
            memory=config.memory,
            cores=config.cores,
            disk_size=config.disk_size,
            packages=config.packages,
            config_hash=config_hash
        )
        
        # Build template using Proxmox API
        if self.proxmox:
            try:
                self._build_template_in_proxmox(version, config)
                self.logger.info(f"Template {version_id} built successfully in Proxmox")
            except Exception as e:
                self.logger.error(f"Failed to build template in Proxmox: {str(e)}")
                raise
        
        # Store version information
        if config.name not in self.versions:
            self.versions[config.name] = []
        
        self.versions[config.name].append(version)
        self._save_versions()
        
        # Apply retention policy
        self._apply_retention_policy(config.name)
        
        self.logger.info(f"Template version {version_id} created successfully")
        return version
    
    def _get_next_template_id(self) -> int:
        """Get next available template ID"""
        used_ids = set()
        
        # Get IDs from configuration
        for template_data in self.config.get("vm_templates", {}).get("base_images", {}).values():
            if "template_id" in template_data:
                used_ids.add(template_data["template_id"])
        
        # Get IDs from existing versions
        for version_list in self.versions.values():
            for version in version_list:
                used_ids.add(version.template_id)
        
        # Start from 9000 and find next available
        template_id = 9000
        while template_id in used_ids:
            template_id += 1
        
        return template_id
    
    def _build_template_in_proxmox(self, version: TemplateVersion, config: TemplateConfig):
        """Build template in Proxmox VE"""
        node = list(self.proxmox.nodes.get())[0]['node']  # Use first available node
        
        # Create VM
        vm_config = {
            'vmid': version.template_id,
            'name': version.name,
            'memory': config.memory,
            'cores': config.cores,
            'ostype': config.os_type,
            'net0': f"virtio,bridge={config.network_config.get('bridge', 'vmbr0')}",
            'agent': 1,
            'boot': 'c',
            'bootdisk': 'scsi0'
        }
        
        # Create the VM
        self.proxmox.nodes(node).qemu.create(**vm_config)
        
        # Configure cloud-init
        if config.cloud_init_config:
            cloud_init_config = {
                'ide2': f"{config.cloud_init_config.get('storage', 'local-lvm')}:cloudinit",
                'ciuser': config.cloud_init_config.get('user', 'ubuntu'),
                'cipassword': config.cloud_init_config.get('password', ''),
                'sshkeys': self._get_ssh_keys(),
                'ipconfig0': config.cloud_init_config.get('ip_config', 'dhcp')
            }
            
            self.proxmox.nodes(node).qemu(version.template_id).config.put(**cloud_init_config)
        
        # Install packages and run custom scripts
        self._customize_template(node, version.template_id, config)
        
        # Convert to template
        self.proxmox.nodes(node).qemu(version.template_id).template.post()
    
    def _get_ssh_keys(self) -> str:
        """Get SSH public keys for cloud-init"""
        ssh_keys_file = Path("/home/diszay-claudedev/projects/iac-ai-assistant/config/secrets/ssh_public_keys")
        if ssh_keys_file.exists():
            return ssh_keys_file.read_text().strip()
        return ""
    
    def _customize_template(self, node: str, vm_id: int, config: TemplateConfig):
        """Customize template with packages and scripts"""
        # Start VM for customization
        self.proxmox.nodes(node).qemu(vm_id).status.start.post()
        
        # Wait for VM to be ready (implement proper waiting logic)
        import time
        time.sleep(30)
        
        # Run package installation and custom scripts
        for package in config.packages:
            self._run_command_in_vm(node, vm_id, f"apt-get install -y {package}")
        
        for script_path in config.custom_scripts:
            script_content = self._load_script(script_path)
            self._run_script_in_vm(node, vm_id, script_content)
        
        # Apply security hardening if enabled
        if config.security_hardening:
            self._apply_security_hardening(node, vm_id)
        
        # Stop VM
        self.proxmox.nodes(node).qemu(vm_id).status.stop.post()
    
    def _run_command_in_vm(self, node: str, vm_id: int, command: str):
        """Run command in VM via QEMU agent"""
        try:
            result = self.proxmox.nodes(node).qemu(vm_id).agent.exec.post(
                command=['bash', '-c', command]
            )
            self.logger.info(f"Command executed in VM {vm_id}: {command}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to execute command in VM {vm_id}: {str(e)}")
    
    def _load_script(self, script_path: str) -> str:
        """Load custom script content"""
        full_path = self.templates_dir / "scripts" / script_path
        if full_path.exists():
            return full_path.read_text()
        return ""
    
    def _run_script_in_vm(self, node: str, vm_id: int, script_content: str):
        """Run script in VM"""
        if not script_content:
            return
        
        # Create temporary script file in VM and execute
        script_commands = [
            f"echo '{script_content}' > /tmp/custom_script.sh",
            "chmod +x /tmp/custom_script.sh",
            "/tmp/custom_script.sh",
            "rm /tmp/custom_script.sh"
        ]
        
        for command in script_commands:
            self._run_command_in_vm(node, vm_id, command)
    
    def _apply_security_hardening(self, node: str, vm_id: int):
        """Apply security hardening to template"""
        hardening_commands = [
            "apt-get update && apt-get upgrade -y",
            "apt-get install -y fail2ban ufw aide",
            "ufw --force enable",
            "systemctl enable fail2ban",
            "passwd -l root",  # Lock root account
            "sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config",
            "systemctl restart ssh"
        ]
        
        for command in hardening_commands:
            self._run_command_in_vm(node, vm_id, command)
    
    def get_template_versions(self, template_name: str) -> List[TemplateVersion]:
        """Get all versions of a template"""
        return self.versions.get(template_name, [])
    
    def get_latest_version(self, template_name: str) -> Optional[TemplateVersion]:
        """Get latest version of a template"""
        versions = self.get_template_versions(template_name)
        if not versions:
            return None
        
        return max(versions, key=lambda v: v.created_at)
    
    def clone_template(self, template_name: str, version_id: str, 
                      new_vm_id: int, new_name: str) -> bool:
        """Clone template to create new VM"""
        if not self.proxmox:
            self.logger.error("Proxmox API not available")
            return False
        
        # Find template version
        versions = self.get_template_versions(template_name)
        template_version = next(
            (v for v in versions if v.version_id == version_id), None
        )
        
        if not template_version:
            self.logger.error(f"Template version not found: {version_id}")
            return False
        
        try:
            node = list(self.proxmox.nodes.get())[0]['node']
            
            # Clone template
            clone_task = self.proxmox.nodes(node).qemu(template_version.template_id).clone.post(
                newid=new_vm_id,
                name=new_name,
                full=1  # Full clone
            )
            
            self.logger.info(f"Template {version_id} cloned to VM {new_vm_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clone template: {str(e)}")
            return False
    
    def _apply_retention_policy(self, template_name: str):
        """Apply retention policy to template versions"""
        if template_name not in self.versions:
            return
        
        versions = self.versions[template_name]
        retention_config = self.config.get("vm_templates", {}).get("versioning", {}).get("retention_policy", {})
        
        # Default retention policy
        max_versions = retention_config.get("production", 20)
        
        if len(versions) > max_versions:
            # Sort by creation date and keep only the latest versions
            versions.sort(key=lambda v: v.created_at, reverse=True)
            versions_to_remove = versions[max_versions:]
            
            for version in versions_to_remove:
                self._remove_template_version(version)
            
            # Update versions list
            self.versions[template_name] = versions[:max_versions]
            self._save_versions()
            
            self.logger.info(f"Applied retention policy for {template_name}: removed {len(versions_to_remove)} old versions")
    
    def _remove_template_version(self, version: TemplateVersion):
        """Remove template version from Proxmox"""
        if not self.proxmox:
            return
        
        try:
            node = list(self.proxmox.nodes.get())[0]['node']
            self.proxmox.nodes(node).qemu(version.template_id).delete()
            self.logger.info(f"Removed template version: {version.version_id}")
        except Exception as e:
            self.logger.error(f"Failed to remove template version {version.version_id}: {str(e)}")
    
    def export_template_config(self, template_name: str, version_id: str) -> Dict[str, Any]:
        """Export template configuration for backup/migration"""
        versions = self.get_template_versions(template_name)
        version = next((v for v in versions if v.version_id == version_id), None)
        
        if not version:
            raise ValueError(f"Template version not found: {version_id}")
        
        return {
            "version_info": asdict(version),
            "proxmox_config": self._get_proxmox_template_config(version.template_id) if self.proxmox else {},
            "export_timestamp": datetime.datetime.now().isoformat()
        }
    
    def _get_proxmox_template_config(self, template_id: int) -> Dict[str, Any]:
        """Get template configuration from Proxmox"""
        try:
            node = list(self.proxmox.nodes.get())[0]['node']
            return self.proxmox.nodes(node).qemu(template_id).config.get()
        except Exception as e:
            self.logger.error(f"Failed to get Proxmox config for template {template_id}: {str(e)}")
            return {}

def main():
    """Example usage of TemplateVersionManager"""
    config_manager = SecureConfigManager("/home/diszay-claudedev/projects/iac-ai-assistant/config")
    template_manager = TemplateVersionManager(config_manager)
    
    # Example template configuration
    template_config = TemplateConfig(
        name="ubuntu-22.04-base",
        description="Ubuntu 22.04 LTS base template with security hardening",
        base_image="ubuntu-22.04-server-cloudimg-amd64.img",
        os_type="l26",
        memory=2048,
        cores=2,
        disk_size=20,
        network_config={"bridge": "vmbr0"},
        cloud_init_config={
            "user": "ubuntu",
            "storage": "local-lvm",
            "ip_config": "dhcp"
        },
        packages=["curl", "wget", "vim", "git", "htop", "fail2ban", "ufw"],
        custom_scripts=["security_hardening.sh"],
        security_hardening=True,
        monitoring_enabled=True
    )
    
    # Create template version
    version = template_manager.create_template(template_config, "admin")
    print(f"Created template version: {version.version_id}")

if __name__ == "__main__":
    main()