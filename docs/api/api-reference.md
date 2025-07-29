# Proxmox AI Infrastructure Assistant - API Reference

## Overview

The Proxmox AI Infrastructure Assistant provides a comprehensive REST API for programmatic access to infrastructure management capabilities. The API follows REST principles, uses JSON for data exchange, and implements enterprise-grade security controls.

## API Architecture

### Base URL
```
https://api.proxmox-ai.internal/v1
```

### Authentication Methods

#### 1. API Token Authentication (Recommended)
```http
Authorization: Bearer <api_token>
```

#### 2. OAuth 2.0 (Enterprise)
```http
Authorization: Bearer <oauth_access_token>
```

#### 3. Basic Authentication (Development Only)
```http
Authorization: Basic <base64(username:password)>
```

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`
- **File Upload**: `multipart/form-data`

### API Versioning
The API uses URL-based versioning:
- Current version: `v1`
- Supported versions: `v1`
- Version header: `API-Version: v1`

## Core API Endpoints

### 1. Authentication API

#### Generate API Token
Generate a new API token for programmatic access.

```http
POST /v1/auth/tokens
```

**Request Headers:**
```
Content-Type: application/json
Authorization: Basic <credentials>
```

**Request Body:**
```json
{
  "name": "deployment-automation",
  "description": "Token for CI/CD deployment automation",
  "expires_in": 2592000,
  "permissions": [
    "vm:read",
    "vm:write",
    "network:read"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token_id": "tok_1234567890abcdef",
    "access_token": "pxa_1234567890abcdef1234567890abcdef",
    "token_type": "bearer",
    "expires_at": "2025-08-29T12:00:00Z",
    "permissions": [
      "vm:read",
      "vm:write", 
      "network:read"
    ]
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password",
    "details": {
      "field": "password",
      "reason": "authentication_failed"
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

#### Revoke API Token
```http
DELETE /v1/auth/tokens/{token_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Token revoked successfully",
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

### 2. Virtual Machine API

#### List Virtual Machines
Retrieve a list of all virtual machines with filtering and pagination.

```http
GET /v1/vms
```

**Query Parameters:**
- `status` (string): Filter by VM status (`running`, `stopped`, `paused`)
- `environment` (string): Filter by environment (`production`, `development`, `staging`)
- `limit` (integer): Number of results to return (default: 50, max: 200)
- `offset` (integer): Number of results to skip (default: 0)
- `sort` (string): Sort field (`name`, `created_at`, `status`) (default: `name`)
- `order` (string): Sort order (`asc`, `desc`) (default: `asc`)

**Example Request:**
```http
GET /v1/vms?status=running&environment=production&limit=25&sort=name&order=asc
Authorization: Bearer pxa_1234567890abcdef1234567890abcdef
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vms": [
      {
        "id": "vm-001",
        "name": "web-server-01",
        "status": "running",
        "environment": "production",
        "cpu_cores": 4,
        "memory_mb": 8192,
        "storage_gb": 100,
        "ip_address": "192.168.1.101",
        "os_type": "ubuntu-22.04",
        "created_at": "2025-07-01T10:00:00Z",
        "updated_at": "2025-07-29T09:30:00Z",
        "tags": ["web", "nginx", "production"],
        "security": {
          "encrypted": true,
          "firewall_enabled": true,
          "last_security_scan": "2025-07-28T06:00:00Z",
          "compliance_score": 95
        }
      }
    ],
    "pagination": {
      "total": 150,
      "limit": 25,
      "offset": 0,
      "pages": 6,
      "current_page": 1
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z",
    "execution_time_ms": 45
  }
}
```

#### Get Virtual Machine Details
```http
GET /v1/vms/{vm_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vm": {
      "id": "vm-001",
      "name": "web-server-01",
      "description": "Production web server running Nginx",
      "status": "running",
      "environment": "production",
      "configuration": {
        "cpu_cores": 4,
        "cpu_sockets": 1,
        "memory_mb": 8192,
        "storage": [
          {
            "disk_id": "disk-001",
            "size_gb": 100,
            "type": "ssd",
            "encrypted": true,
            "mount_point": "/"
          }
        ],
        "network": [
          {
            "interface": "eth0",
            "ip_address": "192.168.1.101",
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "vlan_id": 100
          }
        ]
      },
      "performance": {
        "cpu_usage_percent": 25.5,
        "memory_usage_percent": 68.2,
        "disk_usage_percent": 45.8,
        "network_rx_mbps": 12.5,
        "network_tx_mbps": 8.3,
        "uptime_seconds": 2592000
      },
      "security": {
        "encrypted": true,
        "firewall_enabled": true,
        "ssh_key_auth": true,
        "last_security_scan": "2025-07-28T06:00:00Z",
        "compliance_score": 95,
        "vulnerabilities": {
          "critical": 0,
          "high": 1,
          "medium": 3,
          "low": 5
        }
      },
      "backup": {
        "enabled": true,
        "schedule": "daily",
        "retention_days": 30,
        "last_backup": "2025-07-29T02:00:00Z",
        "backup_size_gb": 45.2
      },
      "created_at": "2025-07-01T10:00:00Z",
      "updated_at": "2025-07-29T09:30:00Z"
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

#### Create Virtual Machine
```http
POST /v1/vms
```

**Request Body:**
```json
{
  "name": "app-server-01",
  "description": "Application server for microservices",
  "template": "ubuntu-22.04-secure",
  "environment": "production",
  "configuration": {
    "cpu_cores": 4,
    "memory_mb": 8192,
    "storage_gb": 100,
    "network": {
      "vlan_id": 100,
      "static_ip": "192.168.1.102"
    }
  },
  "security": {
    "encrypt_disk": true,
    "enable_firewall": true,
    "ssh_keys": [
      "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ..."
    ]
  },
  "tags": ["application", "microservices", "production"],
  "backup": {
    "enabled": true,
    "schedule": "daily",
    "retention_days": 30
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vm": {
      "id": "vm-102",
      "name": "app-server-01",
      "status": "creating",
      "creation_job_id": "job_create_vm_102"
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

#### Update Virtual Machine
```http
PUT /v1/vms/{vm_id}
```

**Request Body:**
```json
{
  "description": "Updated application server description",
  "configuration": {
    "memory_mb": 16384
  },
  "tags": ["application", "microservices", "production", "high-memory"]
}
```

#### Delete Virtual Machine
```http
DELETE /v1/vms/{vm_id}
```

**Query Parameters:**
- `force` (boolean): Force delete without graceful shutdown (default: false)
- `keep_backups` (boolean): Keep existing backups (default: true)

#### Start Virtual Machine
```http
POST /v1/vms/{vm_id}/start
```

#### Stop Virtual Machine
```http
POST /v1/vms/{vm_id}/stop
```

**Request Body:**
```json
{
  "graceful": true,
  "timeout_seconds": 300
}
```

#### Restart Virtual Machine
```http
POST /v1/vms/{vm_id}/restart
```

#### Create VM Snapshot
```http
POST /v1/vms/{vm_id}/snapshots
```

**Request Body:**
```json
{
  "name": "pre-deployment-snapshot",
  "description": "Snapshot before application deployment",
  "include_memory": false
}
```

#### List VM Snapshots
```http
GET /v1/vms/{vm_id}/snapshots
```

#### Restore VM Snapshot
```http
POST /v1/vms/{vm_id}/snapshots/{snapshot_id}/restore
```

### 3. Network API

#### List Networks
```http
GET /v1/networks
```

**Response:**
```json
{
  "success": true,
  "data": {
    "networks": [
      {
        "id": "net-001",
        "name": "production-vlan",
        "type": "vlan",
        "vlan_id": 100,
        "subnet": "192.168.1.0/24",
        "gateway": "192.168.1.1",
        "dns_servers": ["8.8.8.8", "8.8.4.4"],
        "dhcp_enabled": false,
        "firewall_rules": [
          {
            "id": "rule-001",
            "action": "allow",
            "protocol": "tcp",
            "port": 22,
            "source": "192.168.0.0/16"
          }
        ],
        "created_at": "2025-07-01T10:00:00Z"
      }
    ]
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

#### Create Network
```http
POST /v1/networks
```

**Request Body:**
```json
{
  "name": "development-vlan",
  "type": "vlan",
  "vlan_id": 200,
  "subnet": "192.168.2.0/24",
  "gateway": "192.168.2.1",
  "dns_servers": ["8.8.8.8", "8.8.4.4"],
  "dhcp_enabled": true,
  "dhcp_range": {
    "start": "192.168.2.100",
    "end": "192.168.2.200"
  }
}
```

### 4. Storage API

#### List Storage Pools
```http
GET /v1/storage
```

#### Create Storage Pool
```http
POST /v1/storage
```

### 5. Security API

#### Run Security Scan
```http
POST /v1/security/scans
```

**Request Body:**
```json
{
  "scan_type": "vulnerability",
  "targets": ["vm-001", "vm-002"],
  "scan_options": {
    "deep_scan": true,
    "include_dependencies": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scan": {
      "id": "scan-001",
      "type": "vulnerability",
      "status": "running",
      "started_at": "2025-07-29T12:00:00Z",
      "estimated_completion": "2025-07-29T12:15:00Z"
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

#### Get Security Scan Results
```http
GET /v1/security/scans/{scan_id}
```

### 6. Backup API

#### List Backups
```http
GET /v1/backups
```

#### Create Backup
```http
POST /v1/backups
```

**Request Body:**
```json
{
  "vm_id": "vm-001",
  "backup_type": "full",
  "compression": "gzip",
  "encryption": true,
  "description": "Monthly full backup"
}
```

#### Restore Backup
```http
POST /v1/backups/{backup_id}/restore
```

### 7. Jobs API

#### List Jobs
```http
GET /v1/jobs
```

#### Get Job Status
```http
GET /v1/jobs/{job_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job": {
      "id": "job_create_vm_102",
      "type": "vm_creation",
      "status": "running",
      "progress": 65,
      "started_at": "2025-07-29T12:00:00Z",
      "estimated_completion": "2025-07-29T12:10:00Z",
      "logs": [
        {
          "timestamp": "2025-07-29T12:00:00Z",
          "level": "info",
          "message": "VM creation started"
        },
        {
          "timestamp": "2025-07-29T12:02:00Z",
          "level": "info",
          "message": "Disk allocation completed"
        }
      ]
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

#### Cancel Job
```http
DELETE /v1/jobs/{job_id}
```

### 8. Monitoring API

#### Get System Metrics
```http
GET /v1/monitoring/metrics
```

#### Get VM Metrics
```http
GET /v1/monitoring/vms/{vm_id}/metrics
```

**Query Parameters:**
- `period` (string): Time period (`1h`, `24h`, `7d`, `30d`)
- `metrics` (string): Comma-separated metrics (`cpu,memory,disk,network`)

### 9. AI Integration API

#### Generate Infrastructure Code
```http
POST /v1/ai/generate
```

**Request Body:**
```json
{
  "prompt": "Create a secure web server VM with Nginx, SSL certificate, and firewall rules",
  "context": {
    "environment": "production",
    "compliance_requirements": ["CIS", "SOC2"]
  },
  "output_format": "terraform"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "generated_code": {
      "format": "terraform",
      "code": "resource \"proxmox_vm_qemu\" \"web_server\" { ... }",
      "validation_score": 95,
      "security_analysis": {
        "passed": true,
        "issues": [],
        "recommendations": [
          "Consider enabling automatic security updates"
        ]
      }
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z",
    "ai_model": "claude-3-sonnet",
    "tokens_used": 1250
  }
}
```

## Error Handling

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Requested resource not found |
| 409 | Conflict | Resource conflict (e.g., name already exists) |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more validation errors occurred",
    "details": {
      "field": "memory_mb",
      "reason": "must_be_positive_integer",
      "provided_value": -1024
    }
  },
  "meta": {
    "request_id": "req_1234567890",
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| INVALID_TOKEN | API token is invalid or expired |
| INSUFFICIENT_PERMISSIONS | User lacks required permissions |
| RESOURCE_NOT_FOUND | Requested resource does not exist |
| VALIDATION_ERROR | Request validation failed |
| RESOURCE_CONFLICT | Resource name or identifier conflicts |
| RATE_LIMIT_EXCEEDED | API rate limit exceeded |
| MAINTENANCE_MODE | API is in maintenance mode |
| RESOURCE_LIMIT_EXCEEDED | Account or resource limits exceeded |

## Rate Limiting

### Rate Limit Headers

All API responses include rate limiting information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1627834800
X-RateLimit-Window: 3600
```

### Rate Limits by Endpoint

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| VM Operations | 100 requests | 1 hour |
| Read Operations | 1000 requests | 1 hour |
| Bulk Operations | 50 requests | 1 hour |
| AI Generation | 10 requests | 1 hour |

## Pagination

### Request Parameters

- `limit`: Maximum number of results (1-200, default: 50)
- `offset`: Number of results to skip (default: 0)
- `cursor`: Cursor-based pagination token (alternative to offset)

### Response Format

```json
{
  "data": {
    "items": [...],
    "pagination": {
      "total": 1500,
      "limit": 50,
      "offset": 100,
      "pages": 30,
      "current_page": 3,
      "has_next": true,
      "has_previous": true,
      "next_cursor": "eyJ0aW1lc3RhbXAiOiIyMDI1LTA3LTI5VDEyOjAwOjAwWiIsImlkIjoidm0tMTAwIn0=",
      "previous_cursor": "eyJ0aW1lc3RhbXAiOiIyMDI1LTA3LTI5VDExOjAwOjAwWiIsImlkIjoidm0tNTAifQ=="
    }
  }
}
```

## Webhook Integration

### Webhook Events

The API supports webhooks for real-time event notifications:

| Event Type | Description |
|------------|-------------|
| `vm.created` | VM creation completed |
| `vm.deleted` | VM deletion completed |
| `vm.status_changed` | VM status changed |
| `backup.completed` | Backup operation completed |
| `security.scan_completed` | Security scan completed |
| `job.completed` | Background job completed |
| `system.alert` | System alert triggered |

### Webhook Configuration

```http
POST /v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/proxmox-ai",
  "events": ["vm.created", "vm.status_changed"],
  "secret": "your-webhook-secret",
  "active": true
}
```

### Webhook Payload

```json
{
  "event": "vm.created",
  "timestamp": "2025-07-29T12:00:00Z",
  "data": {
    "vm": {
      "id": "vm-102",
      "name": "app-server-01",
      "status": "running"
    }
  },
  "webhook": {
    "id": "webhook-001",
    "attempt": 1
  }
}
```

## SDK and Client Libraries

### Official SDKs

#### Python SDK
```bash
pip install proxmox-ai-sdk
```

```python
from proxmox_ai import ProxmoxAIClient

client = ProxmoxAIClient(
    api_token="pxa_1234567890abcdef1234567890abcdef",
    base_url="https://api.proxmox-ai.internal/v1"
)

# List VMs
vms = client.vms.list(status="running")

# Create VM
vm = client.vms.create({
    "name": "test-vm",
    "template": "ubuntu-22.04",
    "cpu_cores": 2,
    "memory_mb": 4096
})

# Monitor job status
job = client.jobs.get(vm.creation_job_id)
while job.status == "running":
    time.sleep(5)
    job = client.jobs.get(job.id)
```

#### JavaScript/Node.js SDK
```bash
npm install proxmox-ai-sdk
```

```javascript
const ProxmoxAI = require('proxmox-ai-sdk');

const client = new ProxmoxAI({
  apiToken: 'pxa_1234567890abcdef1234567890abcdef',
  baseURL: 'https://api.proxmox-ai.internal/v1'
});

// Create VM
const vm = await client.vms.create({
  name: 'test-vm',
  template: 'ubuntu-22.04',
  cpu_cores: 2,
  memory_mb: 4096
});

console.log('VM created:', vm.id);
```

#### Go SDK
```bash
go get github.com/proxmox-ai/go-sdk
```

```go
package main

import (
    "context"
    "fmt"
    proxmoxai "github.com/proxmox-ai/go-sdk"
)

func main() {
    client := proxmoxai.NewClient("pxa_1234567890abcdef1234567890abcdef")
    
    vm, err := client.VMs.Create(context.Background(), &proxmoxai.VMCreateRequest{
        Name:     "test-vm",
        Template: "ubuntu-22.04",
        CPUCores: 2,
        MemoryMB: 4096,
    })
    
    if err != nil {
        panic(err)
    }
    
    fmt.Printf("VM created: %s\n", vm.ID)
}
```

## Testing and Development

### API Testing

#### Health Check Endpoint
```http
GET /v1/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 86400,
    "components": {
      "database": "healthy",
      "proxmox": "healthy",
      "ai_service": "healthy"
    }
  },
  "meta": {
    "timestamp": "2025-07-29T12:00:00Z"
  }
}
```

#### API Information
```http
GET /v1/info
```

### Sandbox Environment

A sandbox environment is available for testing:

**Base URL:** `https://sandbox-api.proxmox-ai.internal/v1`

- No real infrastructure changes
- Reset daily at 00:00 UTC
- Rate limits: 10x normal limits
- Test data provided

### Postman Collection

Download the official Postman collection:
```
https://api.proxmox-ai.internal/v1/postman/collection.json
```

### OpenAPI Specification

The complete OpenAPI 3.0 specification is available:
```
https://api.proxmox-ai.internal/v1/openapi.json
```

## Best Practices

### 1. Authentication Security
- Use API tokens instead of basic authentication
- Rotate tokens regularly (every 90 days)
- Use environment variables for tokens
- Implement token scoping with minimal permissions

### 2. Error Handling
- Always check the `success` field in responses
- Implement exponential backoff for retries
- Log request IDs for troubleshooting
- Handle rate limiting gracefully

### 3. Performance Optimization
- Use pagination for large datasets
- Implement caching for frequently accessed data
- Use webhook notifications instead of polling
- Batch operations when possible

### 4. Security Considerations
- Validate all inputs on client side
- Use HTTPS for all API communications
- Implement request signing for sensitive operations
- Monitor API usage for anomalies

## Support and Resources

### Documentation
- **API Reference**: https://docs.proxmox-ai.internal/api/
- **SDK Documentation**: https://docs.proxmox-ai.internal/sdks/
- **Tutorials**: https://docs.proxmox-ai.internal/tutorials/

### Community
- **GitHub Issues**: https://github.com/proxmox-ai/issues
- **Community Forum**: https://community.proxmox-ai.internal/
- **Stack Overflow**: Use tag `proxmox-ai`

### Support Channels
- **Email**: api-support@proxmox-ai.internal
- **Enterprise Support**: Available 24/7 for enterprise customers
- **Status Page**: https://status.proxmox-ai.internal/

---

**Classification**: Internal Use - API Documentation
**Last Updated**: 2025-07-29
**Review Schedule**: Monthly
**Approved By**: API Development Team
**Document Version**: 1.0