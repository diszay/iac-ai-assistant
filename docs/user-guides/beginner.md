# Beginner's Guide to Proxmox AI Infrastructure Assistant

Welcome to your first steps in Infrastructure as Code (IaC) with local AI assistance! This guide will help you understand and use the Proxmox AI Assistant even if you're new to infrastructure automation.

## 🎯 What You'll Learn

- **Basic Infrastructure Concepts**: Understanding VMs, networks, and automation
- **Local AI Assistance**: How AI helps you learn and create infrastructure
- **Practical Examples**: Simple, real-world configurations you can use immediately
- **Safety First**: How to experiment safely without breaking anything

## 🚀 Getting Started

### Your First AI-Generated Configuration

Let's start with something simple - creating a basic web server VM:

```bash
# Generate your first VM configuration
proxmox-ai generate terraform --skill-level beginner \
  --description "Simple Ubuntu web server for learning"

# The AI will create a complete configuration with explanations
```

**What happens here?**
- The AI creates a complete Terraform configuration
- It includes detailed comments explaining each section
- It uses safe, standard settings perfect for learning
- It suggests next steps and modifications you can try

### Understanding the Output

When you run the command above, you'll get something like this:

```hcl
# Terraform configuration for a simple Ubuntu web server
# Generated for: beginner skill level
# This creates one virtual machine with basic settings

terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "2.9.0"
    }
  }
}

# This defines our Proxmox connection
provider "proxmox" {
  pm_api_url      = var.proxmox_api_url
  pm_user         = var.proxmox_user
  pm_password     = var.proxmox_password
  pm_tls_insecure = true
}

# This creates our virtual machine
resource "proxmox_vm_qemu" "web_server" {
  name        = "ubuntu-web-01"          # Name of the VM
  target_node = "pve"                    # Which Proxmox node to use
  vmid        = 100                      # Unique VM ID
  
  # Basic VM specifications
  memory    = 2048                       # 2GB RAM - good for learning
  cores     = 2                          # 2 CPU cores
  sockets   = 1                          # Single CPU socket
  
  # Operating system settings
  clone      = "ubuntu-22.04-template"   # Template to clone from
  full_clone = true                      # Complete copy, not linked
  
  # Network configuration
  network {
    model  = "virtio"                    # Fast virtual network adapter
    bridge = "vmbr0"                     # Default bridge
  }
  
  # Storage configuration
  disk {
    storage = "local-lvm"                # Storage location
    type    = "virtio"                   # Fast disk type
    size    = "20G"                      # 20GB storage
  }
}

# Variables make our configuration flexible
variable "proxmox_api_url" {
  description = "URL for Proxmox API"
  type        = string
  default     = "https://your-proxmox-server:8006/api2/json"
}

variable "proxmox_user" {
  description = "Proxmox username"
  type        = string
  default     = "root@pam"
}

variable "proxmox_password" {
  description = "Proxmox password"
  type        = string
  sensitive   = true
}

# Outputs show us important information after creation
output "vm_ip_address" {
  description = "IP address of the created VM"
  value       = proxmox_vm_qemu.web_server.default_ipv4_address
}
```

### Breaking Down the Configuration

**Don't worry if this looks complex!** Let's understand it piece by piece:

1. **Provider Block**: Tells Terraform how to connect to Proxmox
2. **Resource Block**: Defines what we want to create (our VM)
3. **Variables**: Allow us to customize settings without changing the main code
4. **Outputs**: Show us useful information after the VM is created

## 🎓 Interactive Learning

### Ask Questions About Your Configuration

```bash
# Get explanations about any part of your configuration
proxmox-ai explain --file my-vm-config.tf --skill-level beginner

# Ask specific questions
proxmox-ai ask "What does the 'clone' setting do in my VM configuration?"

# Start an interactive learning session
proxmox-ai learn --topic "terraform-basics" --skill-level beginner
```

### Common Beginner Questions

**Q: What's the difference between memory and storage?**
```bash
proxmox-ai ask "Explain the difference between memory and storage in VMs"
```

**Q: How do I change the VM specifications?**
```bash
proxmox-ai ask "How do I increase the memory in my VM configuration?"
```

**Q: What happens if I make a mistake?**
```bash
proxmox-ai ask "How can I safely test my configuration without breaking anything?"
```

## 🛠️ Practical Exercises

### Exercise 1: Create Your First VM

1. **Generate the configuration:**
```bash
proxmox-ai generate terraform --skill-level beginner \
  --description "Ubuntu development server with 4GB RAM"
```

2. **Save it to a file:**
```bash
# The AI will suggest saving it, or you can specify:
proxmox-ai generate terraform --skill-level beginner \
  --description "Ubuntu development server with 4GB RAM" \
  --output-file dev-server.tf
```

3. **Review and understand:**
```bash
proxmox-ai explain --file dev-server.tf --skill-level beginner
```

### Exercise 2: Modify Your Configuration

1. **Ask for help with modifications:**
```bash
proxmox-ai ask "How do I add more storage to my Ubuntu server?"
```

2. **Generate an improved version:**
```bash
proxmox-ai optimize --file dev-server.tf --skill-level beginner
```

### Exercise 3: Learn About Networking

1. **Generate a configuration with custom networking:**
```bash
proxmox-ai generate terraform --skill-level beginner \
  --description "Web server with custom network settings"
```

2. **Understand the networking:**
```bash
proxmox-ai ask "Explain VM networking in simple terms"
```

## 🔒 Safety and Best Practices

### Always Test First

Before applying any configuration to your production Proxmox system:

1. **Review the configuration carefully**
2. **Ask the AI to explain anything you don't understand**
3. **Start with small, simple configurations**
4. **Use a test Proxmox environment if possible**

### Understand Before Applying

```bash
# Always explain configurations before using them
proxmox-ai explain --file any-config.tf --skill-level beginner

# Check for security issues
proxmox-ai security-review --file any-config.tf --skill-level beginner

# Ask about potential problems
proxmox-ai ask "What could go wrong with this configuration?"
```

## 📚 Learning Resources

### Built-in Learning Tools

```bash
# Start an interactive workshop
proxmox-ai workshop beginner

# Browse examples
proxmox-ai examples terraform --skill-level beginner

# Get step-by-step tutorials
proxmox-ai tutorial "creating-your-first-vm"
```

### Key Concepts to Master

1. **Virtual Machines**: Understanding what VMs are and how they work
2. **Networks**: How VMs connect to each other and the internet
3. **Storage**: Different types of storage and when to use them
4. **Templates**: Pre-configured VM images that save time
5. **Infrastructure as Code**: Why we use code to manage infrastructure

### Gradually Increase Complexity

Start with these simple scenarios and gradually work up to more complex ones:

1. **Single VM**: One simple virtual machine
2. **VM with Software**: VM with automatic software installation
3. **Multiple VMs**: Several VMs working together
4. **VM with Backup**: Adding backup and recovery
5. **Load Balanced VMs**: Multiple VMs sharing workload

## 🚨 Common Beginner Mistakes

### 1. Skipping the Learning Phase
**Don't:** Jump straight to complex configurations
**Do:** Start simple and build understanding gradually

```bash
# Good: Start with basics
proxmox-ai generate vm --skill-level beginner --description "Simple test VM"

# Not ideal: Complex configurations too early
# proxmox-ai generate kubernetes-cluster --skill-level expert
```

### 2. Not Understanding Output
**Don't:** Apply configurations you don't understand
**Do:** Always ask for explanations

```bash
# Always do this before applying configurations
proxmox-ai explain --file my-config.tf --skill-level beginner
```

### 3. Ignoring Security
**Don't:** Skip security considerations
**Do:** Always review security implications

```bash
# Check security implications
proxmox-ai security-review --file my-config.tf --skill-level beginner
```

## 🎉 Next Steps

Once you're comfortable with basic VM creation, you can:

1. **Learn about Ansible**: Automating software installation and configuration
2. **Explore Templates**: Creating reusable VM templates
3. **Understand Networking**: Setting up custom networks and VLANs
4. **Practice Backup**: Implementing backup and recovery strategies
5. **Move to Intermediate**: Try more complex multi-VM scenarios

### Graduating to Intermediate Level

You're ready for intermediate-level tasks when you can:

- ✅ Create and understand basic VM configurations
- ✅ Explain what each major configuration section does
- ✅ Safely test configurations before applying them
- ✅ Troubleshoot simple configuration issues
- ✅ Use the AI assistant effectively to learn new concepts

```bash
# Test your readiness for intermediate level
proxmox-ai ask "Am I ready for intermediate-level infrastructure automation?"

# Try an intermediate-level task
proxmox-ai generate terraform --skill-level intermediate \
  --description "Web server with database backend"
```

## 🆘 Getting Help

### When You're Stuck

```bash
# Get help with error messages
proxmox-ai ask "I got this error: [paste your error here]"

# Ask for step-by-step guidance
proxmox-ai ask "Walk me through creating my first VM step by step"

# Get troubleshooting help
proxmox-ai troubleshoot --issue "VM won't start" --skill-level beginner
```

### Resources for Continued Learning

- **Interactive Chat**: `proxmox-ai chat --skill-level beginner`
- **Built-in Tutorials**: `proxmox-ai tutorial --list`
- **Example Gallery**: `proxmox-ai examples --skill-level beginner`
- **Troubleshooting Guide**: `docs/troubleshooting/common-issues.md`

Remember: **Everyone starts as a beginner!** Take your time, ask lots of questions, and don't be afraid to experiment with simple configurations. The AI assistant is here to help you learn at your own pace.

---

**Next:** Ready for more complex scenarios? Check out the [Intermediate Guide](intermediate.md)!