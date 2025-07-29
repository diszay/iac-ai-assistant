# API Authentication Guide

## Overview

The Proxmox AI Infrastructure Assistant API implements multiple authentication methods with enterprise-grade security controls. This guide covers all supported authentication methods, security best practices, and implementation examples.

## Authentication Methods

### 1. API Token Authentication (Recommended)

API tokens provide secure, programmatic access with fine-grained permissions and built-in expiration.

#### Token Generation

**Via CLI:**
```bash
# Generate API token
proxmox-ai auth token create \
  --name "deployment-automation" \
  --description "Token for CI/CD deployment" \
  --expires-in 2592000 \
  --permissions "vm:read,vm:write,network:read"
```

**Via API:**
```http
POST /v1/auth/tokens
Authorization: Basic <base64(username:password)>
Content-Type: application/json

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
    ],
    "created_at": "2025-07-29T12:00:00Z"
  }
}
```

#### Using API Tokens

**HTTP Header:**
```http
Authorization: Bearer pxa_1234567890abcdef1234567890abcdef
```

**cURL Example:**
```bash
curl -H "Authorization: Bearer pxa_1234567890abcdef1234567890abcdef" \
     https://api.proxmox-ai.internal/v1/vms
```

**Python Example:**
```python
import requests

headers = {
    'Authorization': 'Bearer pxa_1234567890abcdef1234567890abcdef',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.proxmox-ai.internal/v1/vms',
    headers=headers
)
```

### 2. OAuth 2.0 Authentication (Enterprise)

OAuth 2.0 provides secure authentication with support for external identity providers.

#### Supported Flows

1. **Authorization Code Flow** (Web applications)
2. **Client Credentials Flow** (Service-to-service)
3. **Device Code Flow** (CLI applications)

#### Authorization Code Flow

**Step 1: Authorization Request**
```http
GET /v1/oauth/authorize?
  response_type=code&
  client_id=your_client_id&
  redirect_uri=https://your-app.com/callback&
  scope=vm:read vm:write&
  state=random_state_string
```

**Step 2: Token Exchange**
```http
POST /v1/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
client_id=your_client_id&
client_secret=your_client_secret&
code=authorization_code&
redirect_uri=https://your-app.com/callback
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "vm:read vm:write"
}
```

#### Client Credentials Flow

```http
POST /v1/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=your_client_id&
client_secret=your_client_secret&
scope=vm:read vm:write
```

#### Using OAuth Tokens

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Token Refresh

```http
POST /v1/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
client_id=your_client_id&
client_secret=your_client_secret&
refresh_token=your_refresh_token
```

### 3. Multi-Factor Authentication (MFA)

MFA is required for all administrative operations and can be configured for API access.

#### TOTP-based MFA

**Setup Process:**
1. Enable MFA for user account
2. Scan QR code with authenticator app
3. Verify TOTP token
4. Receive backup codes

**API Authentication with MFA:**
```http
POST /v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "secure_password",
  "mfa_token": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "pxa_1234567890abcdef1234567890abcdef",
    "expires_in": 3600,
    "mfa_required": false,
    "session_id": "sess_1234567890"
  }
}
```

### 4. SSH Key Authentication (CLI)

For CLI access, SSH key authentication provides secure, password-less access.

#### SSH Key Setup

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/proxmox_ai_key -C "proxmox-ai-$(whoami)"

# Add public key to Proxmox AI
proxmox-ai auth ssh-key add ~/.ssh/proxmox_ai_key.pub
```

#### SSH Configuration

```bash
# ~/.ssh/config
Host proxmox-ai
    HostName api.proxmox-ai.internal
    Port 2849
    User your_username
    IdentityFile ~/.ssh/proxmox_ai_key
    IdentitiesOnly yes
```

## Permission System

### Permission Scopes

The API uses a hierarchical permission system with the following scopes:

#### Resource Types
- `system` - System-level operations
- `vm` - Virtual machine operations
- `network` - Network configuration
- `storage` - Storage management
- `backup` - Backup operations
- `security` - Security management
- `monitoring` - Monitoring and metrics

#### Access Levels
- `read` - Read-only access
- `write` - Create, update operations
- `admin` - Administrative operations
- `owner` - Full control including deletion

#### Permission Format
```
{resource_type}:{access_level}[:{resource_id}]
```

**Examples:**
- `vm:read` - Read access to all VMs
- `vm:write:vm-001` - Write access to specific VM
- `network:admin` - Administrative access to all networks
- `system:owner` - Full system access

### Role-Based Permissions

#### Predefined Roles

```json
{
  "system_admin": [
    "system:owner",
    "vm:admin",
    "network:admin",
    "storage:admin",
    "backup:admin",
    "security:admin",
    "monitoring:admin"
  ],
  "infrastructure_operator": [
    "vm:write",
    "network:write",
    "storage:read",
    "backup:read",
    "monitoring:read"
  ],
  "security_auditor": [
    "security:read",
    "system:read",
    "vm:read",
    "network:read",
    "monitoring:read"
  ],
  "developer": [
    "vm:write",
    "network:read",
    "storage:read",
    "monitoring:read"
  ],
  "readonly_user": [
    "vm:read",
    "network:read",
    "storage:read",
    "monitoring:read"
  ]
}
```

### Custom Permissions

#### Creating Custom Tokens

```bash
# Create token with specific permissions
proxmox-ai auth token create \
  --name "backup-automation" \
  --permissions "vm:read,backup:write,storage:read" \
  --expires-in 86400
```

#### Permission Validation

The API validates permissions for every request:

```python
# Example permission check
def check_permission(user_token, resource_type, access_level, resource_id=None):
    """
    Check if user token has required permission
    """
    user_permissions = get_token_permissions(user_token)
    
    required_permission = f"{resource_type}:{access_level}"
    if resource_id:
        required_permission += f":{resource_id}"
    
    # Check exact match
    if required_permission in user_permissions:
        return True
    
    # Check wildcard permissions
    wildcard_permission = f"{resource_type}:{access_level}"
    if wildcard_permission in user_permissions:
        return True
    
    # Check higher access levels
    access_hierarchy = {"read": 1, "write": 2, "admin": 3, "owner": 4}
    current_level = access_hierarchy.get(access_level, 0)
    
    for permission in user_permissions:
        parts = permission.split(":")
        if len(parts) >= 2 and parts[0] == resource_type:
            perm_level = access_hierarchy.get(parts[1], 0)
            if perm_level >= current_level:
                return True
    
    return False
```

## Security Best Practices

### 1. Token Management

#### Secure Token Storage

```python
# ❌ BAD: Hardcoded token
API_TOKEN = "pxa_1234567890abcdef1234567890abcdef"

# ✅ GOOD: Environment variable
import os
API_TOKEN = os.getenv('PROXMOX_AI_API_TOKEN')

# ✅ GOOD: Secure vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://vault.vault.azure.net/", credential=credential)
API_TOKEN = client.get_secret("ProxmoxAIToken").value
```

#### Token Rotation

```bash
#!/bin/bash
# Automated token rotation script

OLD_TOKEN_ID="tok_old_token"
NEW_TOKEN_NAME="automated-rotation-$(date +%s)"

# Create new token
NEW_TOKEN=$(proxmox-ai auth token create \
  --name "$NEW_TOKEN_NAME" \
  --permissions "$(proxmox-ai auth token show $OLD_TOKEN_ID --permissions-only)" \
  --expires-in 2592000 \
  --output json | jq -r '.data.access_token')

# Update application configuration
kubectl create secret generic proxmox-ai-token \
  --from-literal=token="$NEW_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify new token works
if curl -f -H "Authorization: Bearer $NEW_TOKEN" \
   https://api.proxmox-ai.internal/v1/health > /dev/null; then
  
  # Revoke old token
  proxmox-ai auth token revoke "$OLD_TOKEN_ID"
  echo "Token rotation completed successfully"
else
  echo "New token verification failed"
  exit 1
fi
```

### 2. Request Security

#### Request Signing

For sensitive operations, implement request signing:

```python
import hmac
import hashlib
import time
import json

def sign_request(method, path, body, secret):
    """
    Generate request signature for sensitive operations
    """
    timestamp = str(int(time.time()))
    
    # Create signature payload
    payload = f"{method}\n{path}\n{timestamp}\n{body}"
    
    # Generate signature
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'X-Signature': signature,
        'X-Timestamp': timestamp
    }

# Usage
headers = {
    'Authorization': 'Bearer your_token',
    'Content-Type': 'application/json'
}

# Add signature for sensitive operations
if operation_requires_signing:
    signature_headers = sign_request('POST', '/v1/vms', json.dumps(payload), secret_key)
    headers.update(signature_headers)
```

#### Rate Limiting Compliance

```python
import time
import requests
from datetime import datetime, timedelta

class RateLimitedClient:
    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url
        self.request_times = []
        self.max_requests_per_hour = 1000
    
    def _check_rate_limit(self):
        """Check and enforce client-side rate limiting"""
        now = datetime.now()
        # Remove requests older than 1 hour
        self.request_times = [
            req_time for req_time in self.request_times
            if now - req_time < timedelta(hours=1)
        ]
        
        if len(self.request_times) >= self.max_requests_per_hour:
            sleep_time = (self.request_times[0] + timedelta(hours=1) - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def make_request(self, method, endpoint, **kwargs):
        """Make rate-limited API request"""
        self._check_rate_limit()
        
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'
        kwargs['headers'] = headers
        
        response = requests.request(method, f"{self.base_url}{endpoint}", **kwargs)
        
        # Record request time
        self.request_times.append(datetime.now())
        
        # Handle rate limiting response
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            return self.make_request(method, endpoint, **kwargs)
        
        return response
```

### 3. Error Handling

#### Authentication Error Handling

```python
class AuthenticationError(Exception):
    pass

class AuthorizationError(Exception):
    pass

def handle_auth_errors(response):
    """Handle authentication and authorization errors"""
    if response.status_code == 401:
        error_data = response.json()
        error_code = error_data.get('error', {}).get('code')
        
        if error_code == 'INVALID_TOKEN':
            raise AuthenticationError("API token is invalid or expired")
        elif error_code == 'MFA_REQUIRED':
            raise AuthenticationError("Multi-factor authentication required")
        else:
            raise AuthenticationError("Authentication failed")
    
    elif response.status_code == 403:
        error_data = response.json()
        raise AuthorizationError(f"Insufficient permissions: {error_data.get('error', {}).get('message')}")

# Usage
try:
    response = requests.get(url, headers=headers)
    handle_auth_errors(response)
    return response.json()
except AuthenticationError as e:
    # Refresh token or re-authenticate
    refresh_authentication()
    retry_request()
except AuthorizationError as e:
    # Log permission issue and notify admin
    log_permission_error(e)
    raise
```

## Integration Examples

### 1. Python SDK Integration

```python
from proxmox_ai import ProxmoxAIClient, AuthenticationError
import os

# Initialize client with token
client = ProxmoxAIClient(
    api_token=os.getenv('PROXMOX_AI_TOKEN'),
    base_url='https://api.proxmox-ai.internal/v1'
)

# Set up authentication error handling
@client.on_auth_error
def handle_auth_error(error):
    if error.code == 'TOKEN_EXPIRED':
        # Attempt token refresh
        new_token = refresh_api_token()
        client.set_token(new_token)
        return True  # Retry request
    return False  # Don't retry

# Use client with automatic error handling
try:
    vms = client.vms.list()
    for vm in vms:
        print(f"VM: {vm.name} - Status: {vm.status}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### 2. JavaScript/Node.js Integration

```javascript
const ProxmoxAI = require('proxmox-ai-sdk');

class AuthenticatedProxmoxClient {
  constructor(options) {
    this.client = new ProxmoxAI(options);
    this.setupAuthHandling();
  }
  
  setupAuthHandling() {
    // Intercept requests to add authentication
    this.client.interceptors.request.use((config) => {
      const token = process.env.PROXMOX_AI_TOKEN;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    // Handle authentication errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          const newToken = await this.refreshToken();
          if (newToken) {
            // Retry original request with new token
            error.config.headers.Authorization = `Bearer ${newToken}`;
            return this.client.request(error.config);
          }
        }
        throw error;
      }
    );
  }
  
  async refreshToken() {
    try {
      // Implement token refresh logic
      const response = await fetch('/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken })
      });
      
      const data = await response.json();
      const newToken = data.access_token;
      
      // Update environment variable or secure storage
      process.env.PROXMOX_AI_TOKEN = newToken;
      
      return newToken;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return null;
    }
  }
}

// Usage
const client = new AuthenticatedProxmoxClient({
  baseURL: 'https://api.proxmox-ai.internal/v1'
});

async function listVMs() {
  try {
    const vms = await client.vms.list();
    console.log('VMs:', vms.data);
  } catch (error) {
    if (error.response?.status === 403) {
      console.error('Insufficient permissions:', error.response.data.error.message);
    } else {
      console.error('API Error:', error.message);
    }
  }
}
```

### 3. CI/CD Integration

#### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Infrastructure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Proxmox AI CLI
        run: |
          curl -sSL https://get.proxmox-ai.com/install.sh | bash
          echo "${{ secrets.PROXMOX_AI_TOKEN }}" > ~/.proxmox-ai/token
      
      - name: Deploy VMs
        run: |
          proxmox-ai vm create --config deployment/vm-config.yaml
        env:
          PROXMOX_AI_TOKEN: ${{ secrets.PROXMOX_AI_TOKEN }}
      
      - name: Verify Deployment
        run: |
          proxmox-ai vm list --status running --format json | \
            jq '.data.vms[] | select(.name | startswith("prod-"))'
```

#### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        PROXMOX_AI_TOKEN = credentials('proxmox-ai-token')
    }
    
    stages {
        stage('Deploy Infrastructure') {
            steps {
                script {
                    // Use API token for authentication
                    sh '''
                        curl -X POST \
                          -H "Authorization: Bearer $PROXMOX_AI_TOKEN" \
                          -H "Content-Type: application/json" \
                          -d @deployment/vm-config.json \
                          https://api.proxmox-ai.internal/v1/vms
                    '''
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                script {
                    sh '''
                        # Check deployment status
                        response=$(curl -s -H "Authorization: Bearer $PROXMOX_AI_TOKEN" \
                          https://api.proxmox-ai.internal/v1/vms?status=running)
                        
                        echo "$response" | jq '.data.vms[].name'
                    '''
                }
            }
        }
    }
    
    post {
        always {
            // Clean up temporary tokens
            sh 'unset PROXMOX_AI_TOKEN'
        }
    }
}
```

## Troubleshooting

### Common Authentication Issues

#### 1. Invalid Token Error

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "API token is invalid or expired"
  }
}
```

**Solutions:**
- Verify token is correctly formatted
- Check token expiration date
- Regenerate token if expired
- Ensure token has required permissions

#### 2. Permission Denied

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "User lacks required permissions for this operation"
  }
}
```

**Solutions:**
- Check token permissions: `proxmox-ai auth token show <token_id>`
- Request additional permissions from administrator
- Use a token with appropriate scope

#### 3. Rate Limit Exceeded

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded"
  }
}
```

**Solutions:**
- Implement exponential backoff
- Check `X-RateLimit-Reset` header
- Reduce request frequency
- Consider upgrading to higher rate limits

### Debugging Authentication

#### Enable Debug Logging

```bash
# CLI debug mode
export PROXMOX_AI_DEBUG=true
proxmox-ai vm list

# API request debugging
curl -v -H "Authorization: Bearer $TOKEN" \
  https://api.proxmox-ai.internal/v1/vms
```

#### Token Validation

```bash
# Validate token
proxmox-ai auth token validate

# Check token permissions
proxmox-ai auth token show --permissions

# Test token with minimal request
curl -H "Authorization: Bearer $TOKEN" \
  https://api.proxmox-ai.internal/v1/health
```

## Migration and Upgrades

### Token Migration

When upgrading authentication systems:

```bash
#!/bin/bash
# Token migration script

echo "Starting token migration..."

# Export existing tokens
proxmox-ai auth token export --output tokens.json

# Backup current configuration
cp ~/.proxmox-ai/config ~/.proxmox-ai/config.backup

# Upgrade system
proxmox-ai upgrade --version latest

# Import tokens with new format
proxmox-ai auth token import --input tokens.json --verify

echo "Token migration completed"
```

### OAuth Migration

```python
# Migrate from API tokens to OAuth
def migrate_to_oauth():
    """
    Migrate application from API tokens to OAuth authentication
    """
    # Step 1: Register OAuth application
    oauth_client = register_oauth_client(
        name="My Application",
        redirect_uris=["https://myapp.com/oauth/callback"],
        scopes=["vm:read", "vm:write"]
    )
    
    # Step 2: Update application configuration
    update_config({
        'auth_method': 'oauth',
        'client_id': oauth_client.client_id,
        'client_secret': oauth_client.client_secret,
        'redirect_uri': 'https://myapp.com/oauth/callback'
    })
    
    # Step 3: Implement OAuth flow
    implement_oauth_flow()
    
    # Step 4: Revoke old API tokens
    revoke_api_tokens()
```

---

**Classification**: Internal Use - Authentication Guide
**Last Updated**: 2025-07-29
**Review Schedule**: Monthly
**Approved By**: Security Team, API Development Team
**Document Version**: 1.0