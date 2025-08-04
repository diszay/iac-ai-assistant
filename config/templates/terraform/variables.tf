# Terraform Variables for Proxmox Infrastructure
# Comprehensive variable definitions for secure and flexible VM deployment

# =============================================================================
# PROXMOX CONNECTION VARIABLES
# =============================================================================

variable "proxmox_api_url" {
  description = "Proxmox API URL (e.g., https://YOUR_PROXMOX_HOST:8006/api2/json)"
  type        = string
  validation {
    condition     = can(regex("^https://", var.proxmox_api_url))
    error_message = "Proxmox API URL must use HTTPS for security."
  }
}

variable "proxmox_api_token_id" {
  description = "Proxmox API token ID (format: user@realm!tokenname)"
  type        = string
  sensitive   = true
}

variable "proxmox_api_token_secret" {
  description = "Proxmox API token secret"
  type        = string
  sensitive   = true
}

variable "proxmox_tls_insecure" {
  description = "Skip TLS certificate verification (not recommended for production)"
  type        = bool
  default     = false
}

variable "proxmox_parallel" {
  description = "Number of parallel API calls to Proxmox"
  type        = number
  default     = 4
  validation {
    condition     = var.proxmox_parallel >= 1 && var.proxmox_parallel <= 10
    error_message = "Proxmox parallel calls must be between 1 and 10."
  }
}

variable "proxmox_timeout" {
  description = "API timeout in seconds"
  type        = number
  default     = 300
}

variable "proxmox_debug" {
  description = "Enable debug logging for Proxmox provider"
  type        = bool
  default     = false
}

variable "proxmox_node" {
  description = "Target Proxmox node name"
  type        = string
}

variable "proxmox_storage" {
  description = "Default storage backend for VM disks"
  type        = string
  default     = "local-lvm"
}

# =============================================================================
# PROJECT AND ENVIRONMENT VARIABLES
# =============================================================================

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod", "test"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod, test."
  }
}

variable "application_name" {
  description = "Application or service name"
  type        = string
  default     = "app"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.application_name))
    error_message = "Application name must be lowercase alphanumeric with hyphens."
  }
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "proxmox-infrastructure"
}

variable "instance_name" {
  description = "Instance identifier for VM naming"
  type        = string
  default     = "vm"
}

variable "description" {
  description = "Description of the infrastructure deployment"
  type        = string
  default     = "Proxmox VMs managed by Terraform"
}

variable "security_level" {
  description = "Security level classification (low, medium, high, critical)"
  type        = string
  default     = "medium"
  validation {
    condition     = contains(["low", "medium", "high", "critical"], var.security_level)
    error_message = "Security level must be one of: low, medium, high, critical."
  }
}

# =============================================================================
# VM CONFIGURATION VARIABLES
# =============================================================================

variable "vm_count" {
  description = "Number of VMs to create"
  type        = number
  default     = 1
  validation {
    condition     = var.vm_count >= 1 && var.vm_count <= 50
    error_message = "VM count must be between 1 and 50."
  }
}

variable "template_name" {
  description = "VM template to clone from"
  type        = string
  default     = "ubuntu-22.04-template"
}

variable "full_clone" {
  description = "Create a full clone instead of linked clone"
  type        = bool
  default     = true
}

# CPU Configuration
variable "default_cpu_cores" {
  description = "Number of CPU cores per VM"
  type        = number
  default     = 2
  validation {
    condition     = var.default_cpu_cores >= 1 && var.default_cpu_cores <= 64
    error_message = "CPU cores must be between 1 and 64."
  }
}

variable "cpu_sockets" {
  description = "Number of CPU sockets"
  type        = number
  default     = 1
}

variable "cpu_vcpus" {
  description = "Number of vCPUs (0 = same as cores)"
  type        = number
  default     = 0
}

variable "cpu_type" {
  description = "CPU type for VMs"
  type        = string
  default     = "host"
}

# Memory Configuration
variable "default_memory" {
  description = "RAM in MB per VM"
  type        = number
  default     = 2048
  validation {
    condition     = var.default_memory >= 512 && var.default_memory <= 131072
    error_message = "Memory must be between 512MB and 128GB."
  }
}

variable "memory_balloon" {
  description = "Enable memory ballooning"
  type        = number
  default     = 0
}

# Disk Configuration
variable "default_disk_size" {
  description = "Primary disk size (e.g., '20G')"
  type        = string
  default     = "20G"
  validation {
    condition     = can(regex("^[0-9]+[GM]$", var.default_disk_size))
    error_message = "Disk size must be in format like '20G' or '1024M'."
  }
}

variable "disk_format" {
  description = "Disk format (raw, qcow2, vmdk)"
  type        = string
  default     = "qcow2"
  validation {
    condition     = contains(["raw", "qcow2", "vmdk"], var.disk_format)
    error_message = "Disk format must be one of: raw, qcow2, vmdk."
  }
}

variable "disk_cache" {
  description = "Disk cache mode"
  type        = string
  default     = "none"
  validation {
    condition     = contains(["none", "writethrough", "writeback"], var.disk_cache)
    error_message = "Disk cache must be one of: none, writethrough, writeback."
  }
}

variable "disk_backup" {
  description = "Include disk in backups"
  type        = bool
  default     = true
}

variable "disk_iothread" {
  description = "Enable IO threads for disk"
  type        = bool
  default     = false
}

variable "disk_discard" {
  description = "Enable disk discard/TRIM"
  type        = string
  default     = "ignore"
}

variable "disk_ssd" {
  description = "Mark disk as SSD"
  type        = bool
  default     = false
}

variable "additional_disks" {
  description = "Additional disks configuration"
  type = list(object({
    slot     = number
    type     = string
    storage  = string
    size     = string
    format   = string
    cache    = string
    backup   = bool
    iothread = bool
    discard  = string
    ssd      = bool
  }))
  default = []
}

# =============================================================================
# NETWORK CONFIGURATION VARIABLES
# =============================================================================

variable "network_bridge" {
  description = "Network bridge name"
  type        = string
  default     = "vmbr0"
}

variable "vlan_tag" {
  description = "VLAN tag for network interface"
  type        = number
  default     = null
  validation {
    condition     = var.vlan_tag == null || (var.vlan_tag >= 1 && var.vlan_tag <= 4094)
    error_message = "VLAN tag must be between 1 and 4094."
  }
}

variable "network_mtu" {
  description = "Network MTU size"
  type        = number
  default     = null
}

variable "network_queues" {
  description = "Number of network queues"
  type        = number
  default     = null
}

variable "network_rate_limit" {
  description = "Network rate limit in MB/s"
  type        = number
  default     = null
}

variable "additional_networks" {
  description = "Additional network interfaces"
  type = list(object({
    model     = string
    bridge    = string
    vlan_tag  = number
    firewall  = bool
    macaddr   = string
    mtu       = number
    queues    = number
    rate      = number
  }))
  default = []
}

variable "mac_addresses" {
  description = "Static MAC addresses for VMs (optional)"
  type        = list(string)
  default     = null
}

# =============================================================================
# CLOUD-INIT AND SSH CONFIGURATION
# =============================================================================

variable "default_username" {
  description = "Default username for VM access"
  type        = string
  default     = "ubuntu"
  validation {
    condition     = can(regex("^[a-z][a-z0-9_-]*$", var.default_username))
    error_message = "Username must start with lowercase letter and contain only lowercase letters, numbers, underscores, and hyphens."
  }
}

variable "generate_ssh_key" {
  description = "Generate SSH key pair for VM access"
  type        = bool
  default     = true
}

variable "ssh_public_keys" {
  description = "SSH public keys for VM access"
  type        = string
  default     = ""
}

variable "ssh_private_key" {
  description = "SSH private key for VM connection"
  type        = string
  default     = ""
  sensitive   = true
}

variable "ssh_private_key_path" {
  description = "Path to SSH private key file"
  type        = string
  default     = ""
}

variable "ssh_port" {
  description = "SSH port for connections"
  type        = number
  default     = 22
  validation {
    condition     = var.ssh_port >= 1 && var.ssh_port <= 65535
    error_message = "SSH port must be between 1 and 65535."
  }
}

variable "generate_vm_password" {
  description = "Generate random password for VM user"
  type        = bool
  default     = true
}

variable "ci_password" {
  description = "Cloud-init user password"
  type        = string
  default     = ""
  sensitive   = true
}

variable "password_hash" {
  description = "Pre-hashed password for cloud-init"
  type        = string
  default     = ""
  sensitive   = true
}

variable "enable_cloud_init" {
  description = "Enable custom cloud-init configuration"
  type        = bool
  default     = true
}

# =============================================================================
# IP AND DNS CONFIGURATION
# =============================================================================

variable "ip_config" {
  description = "IP configuration per VM (e.g., 'ip=YOUR_VM_IP_START/24,gw=YOUR_VM_IP')"
  type        = list(string)
  default     = null
}

variable "additional_ip_configs" {
  description = "Additional IP configurations for secondary interfaces"
  type        = list(string)
  default     = null
}

variable "search_domain" {
  description = "Search domain for DNS resolution"
  type        = string
  default     = "local"
}

variable "nameservers" {
  description = "DNS nameservers (space-separated)"
  type        = string
  default     = "8.8.8.8 8.8.4.4"
}

variable "connection_host" {
  description = "Specific hosts for SSH connections (overrides auto-detection)"
  type        = list(string)
  default     = null
}

variable "connection_timeout" {
  description = "SSH connection timeout"
  type        = string
  default     = "5m"
}

# =============================================================================
# VM BEHAVIOR AND LIFECYCLE
# =============================================================================

variable "vm_startup_order" {
  description = "VM startup order and delay"
  type        = string
  default     = ""
}

variable "vm_autostart" {
  description = "Start VM automatically on node boot"
  type        = bool
  default     = true
}

variable "initial_vm_state" {
  description = "Initial VM state (running, stopped)"
  type        = string
  default     = "running"
  validation {
    condition     = contains(["running", "stopped"], var.initial_vm_state)
    error_message = "Initial VM state must be 'running' or 'stopped'."
  }
}

variable "enable_qemu_agent" {
  description = "Enable QEMU guest agent"
  type        = bool
  default     = true
}

variable "create_before_destroy" {
  description = "Create replacement VMs before destroying old ones"
  type        = bool
  default     = false
}

# =============================================================================
# HARDWARE AND DEVICES
# =============================================================================

variable "usb_devices" {
  description = "USB device passthrough configuration"
  type = list(object({
    host = string
    usb3 = bool
  }))
  default = []
}

variable "serial_devices" {
  description = "Serial device configuration"
  type = list(object({
    id   = number
    type = string
  }))
  default = []
}

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

variable "timezone" {
  description = "System timezone"
  type        = string
  default     = "UTC"
}

variable "locale" {
  description = "System locale"
  type        = string
  default     = "en_US.UTF-8"
}

variable "default_packages" {
  description = "Default packages to install via cloud-init"
  type        = list(string)
  default = [
    "curl",
    "wget",
    "vim",
    "htop",
    "unzip",
    "software-properties-common",
    "apt-transport-https",
    "ca-certificates",
    "gnupg",
    "lsb-release"
  ]
}

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

variable "enable_automatic_security_updates" {
  description = "Enable automatic security updates"
  type        = bool
  default     = true
}

variable "enable_fail2ban" {
  description = "Install and configure fail2ban"
  type        = bool
  default     = true
}

variable "enable_ufw_firewall" {
  description = "Enable UFW firewall"
  type        = bool
  default     = true
}

variable "enable_initial_hardening" {
  description = "Apply initial security hardening during provisioning"
  type        = bool
  default     = true
}

variable "enable_docker" {
  description = "Install Docker during cloud-init"
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Install monitoring agents"
  type        = bool
  default     = false
}

# =============================================================================
# PROVISIONING AND AUTOMATION
# =============================================================================

variable "provisioning_scripts" {
  description = "Custom provisioning scripts to run"
  type = list(object({
    commands = list(string)
  }))
  default = []
}

variable "file_uploads" {
  description = "Files to upload to VMs"
  type = list(object({
    source      = string
    destination = string
  }))
  default = []
}

variable "generate_ansible_inventory" {
  description = "Generate Ansible inventory file"
  type        = bool
  default     = true
}

# =============================================================================
# VALIDATION RULES AND CONSTRAINTS
# =============================================================================

# Ensure consistent VM naming
locals {
  validate_vm_count_and_ips = var.ip_config != null ? (
    length(var.ip_config) == var.vm_count ? true : 
    tobool("IP config count must match VM count")
  ) : true
  
  validate_mac_addresses = var.mac_addresses != null ? (
    length(var.mac_addresses) == var.vm_count ? true :
    tobool("MAC addresses count must match VM count")
  ) : true
}