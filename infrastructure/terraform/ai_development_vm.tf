# Terraform configuration for AI development VM
terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "~> 2.9"
    }
  }
}

provider "proxmox" {
  pm_api_url      = "https://192.168.1.50:8006/api2/json"
  pm_user         = "terraform@pve"
  pm_password     = var.proxmox_password
  pm_tls_insecure = true
}

variable "proxmox_password" {
  description = "Proxmox password"
  type        = string
  sensitive   = true
}

resource "proxmox_vm_qemu" "ai_development_vm" {
  name        = "ai-agents-dev"
  target_node = "pve"
  vmid        = 200
  
  # Optimal specs for 5 AI agents
  memory   = 8192  # 8GB RAM
  cores    = 4     # 4 CPU cores
  sockets  = 1
  cpu      = "host"
  
  # Storage configuration
  disk {
    slot     = 0
    size     = "80G"
    type     = "virtio"
    storage  = "local-lvm"
    iothread = 1
  }
  
  # Network configuration
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  # OS configuration
  os_type      = "cloud-init"
  clone        = "ubuntu-2204-template"  # Adjust to your template
  full_clone   = true
  
  # Enable guest agent
  agent = 1
  
  # Cloud-init configuration
  ciuser     = "aidev"
  cipassword = var.vm_password
  sshkeys    = var.ssh_public_key
  
  # IP configuration (adjust to your network)
  ipconfig0 = "ip=192.168.1.100/24,gw=192.168.1.1"
}

variable "vm_password" {
  description = "VM user password"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}

output "vm_ip" {
  value = "192.168.1.100"
}