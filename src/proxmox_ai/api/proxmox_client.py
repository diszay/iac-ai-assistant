"""
Secure Proxmox VE API client with TLS encryption and connection pooling.

Provides a high-level, secure interface to the Proxmox VE API with proper
error handling, retry logic, and connection management.
"""

import asyncio
import ssl
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from urllib.parse import urljoin
import time

import aiohttp
import structlog
from proxmoxer import ProxmoxAPI
from proxmoxer.backends import https

from ..core.config import Settings, get_settings
from ..core.security import CredentialManager, SecureCredentials
from ..core.logging import log_api_call, log_security_event

logger = structlog.get_logger(__name__)


class ProxmoxAPIError(Exception):
    """Base exception for Proxmox API errors."""
    pass


class ProxmoxAuthenticationError(ProxmoxAPIError):
    """Raised when authentication fails."""
    pass


class ProxmoxConnectionError(ProxmoxAPIError):
    """Raised when connection to Proxmox fails."""
    pass


class ProxmoxResourceError(ProxmoxAPIError):
    """Raised when a resource operation fails."""
    pass


class SecureProxmoxClient:
    """
    Secure Proxmox VE API client with advanced features.
    
    Features:
    - Secure credential management
    - TLS certificate validation
    - Connection pooling and reuse
    - Automatic retry with exponential backoff
    - Request/response logging
    - Session management
    - Resource caching
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.credential_manager = CredentialManager()
        self._proxmox_api: Optional[ProxmoxAPI] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._credentials: Optional[SecureCredentials] = None
        self._auth_ticket: Optional[str] = None
        self._csrf_token: Optional[str] = None
        self._ticket_expires: Optional[float] = None
        
        logger.info(
            "Proxmox client initialized",
            host=self.settings.proxmox.host,
            port=self.settings.proxmox.port,
            verify_ssl=self.settings.proxmox.verify_ssl
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self, credentials: Optional[SecureCredentials] = None) -> None:
        """
        Establish connection to Proxmox VE API.
        
        Args:
            credentials: Optional credentials. If not provided, will try to load
                        from storage or prompt user.
        """
        try:
            # Get credentials if not provided
            if not credentials:
                credentials = await self._get_credentials()
            
            self._credentials = credentials
            
            # Create SSL context
            ssl_context = self._create_ssl_context()
            
            # Create aiohttp session
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,  # Connection pool size
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.settings.proxmox.timeout)
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': f'{self.settings.app_name}/{self.settings.version}',
                    'Content-Type': 'application/json'
                }
            )
            
            # Initialize proxmoxer client
            self._proxmox_api = ProxmoxAPI(
                self.settings.proxmox.host,
                user=credentials.username,
                password=credentials.password.get_secret_value(),
                port=self.settings.proxmox.port,
                verify_ssl=self.settings.proxmox.verify_ssl,
                timeout=self.settings.proxmox.timeout
            )
            
            # Test connection and get authentication ticket
            await self._authenticate()
            
            log_security_event(
                "Proxmox connection established",
                success=True,
                user=credentials.username,
                resource=f"{self.settings.proxmox.host}:{self.settings.proxmox.port}"
            )
            
            logger.info(
                "Connected to Proxmox VE",
                host=self.settings.proxmox.host,
                user=credentials.username
            )
            
        except Exception as e:
            logger.error("Failed to connect to Proxmox", error=str(e))
            
            log_security_event(
                "Proxmox connection failed",
                success=False,
                user=credentials.username if credentials else None,
                resource=f"{self.settings.proxmox.host}:{self.settings.proxmox.port}",
                details={'error': str(e)}
            )
            
            await self.disconnect()
            
            if "authentication" in str(e).lower():
                raise ProxmoxAuthenticationError(f"Authentication failed: {e}")
            elif "connection" in str(e).lower():
                raise ProxmoxConnectionError(f"Connection failed: {e}")
            else:
                raise ProxmoxAPIError(f"Proxmox API error: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from Proxmox VE API and cleanup resources."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self._proxmox_api = None
            self._auth_ticket = None
            self._csrf_token = None
            self._ticket_expires = None
            
            logger.debug("Disconnected from Proxmox VE")
            
        except Exception as e:
            logger.error("Error during disconnect", error=str(e))
    
    def _create_ssl_context(self) -> Union[ssl.SSLContext, bool]:
        """Create SSL context for secure connections."""
        if not self.settings.proxmox.verify_ssl:
            logger.warning(
                "SSL verification disabled - this is not recommended for production"
            )
            return False
        
        # Create secure SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Configure secure protocols
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS")
        
        return context
    
    async def _get_credentials(self) -> SecureCredentials:
        """Get Proxmox credentials from storage or prompt user."""
        service_name = f"proxmox_{self.settings.proxmox.host}"
        
        try:
            # Try to get stored credentials
            credentials = self.credential_manager.get_credentials(service_name)
            if credentials:
                logger.debug("Using stored Proxmox credentials")
                return credentials
        except Exception as e:
            logger.debug("Failed to load stored credentials", error=str(e))
        
        # Prompt for credentials
        logger.info("Prompting for Proxmox credentials")
        return self.credential_manager.prompt_for_credentials(
            service_name=service_name,
            username_prompt=f"Proxmox username [{self.settings.proxmox.user}]",
            password_prompt="Proxmox password",
            host_prompt="Proxmox host",
            port_prompt="Proxmox port"
        )
    
    async def _authenticate(self) -> None:
        """Authenticate with Proxmox and get API ticket."""
        if not self._proxmox_api or not self._credentials:
            raise ProxmoxAPIError("Client not initialized")
        
        try:
            # Get authentication ticket
            start_time = time.time()
            
            auth_result = self._proxmox_api.access.ticket.post(
                username=self._credentials.username,
                password=self._credentials.password.get_secret_value()
            )
            
            duration = time.time() - start_time
            
            # Store authentication info
            self._auth_ticket = auth_result['ticket']
            self._csrf_token = auth_result['CSRFPreventionToken']
            self._ticket_expires = time.time() + 7200  # 2 hours default
            
            log_api_call(
                method="POST",
                endpoint="/access/ticket",
                status_code=200,
                duration=duration,
                user=self._credentials.username
            )
            
            logger.debug("Authentication successful")
            
        except Exception as e:
            logger.error("Authentication failed", error=str(e))
            raise ProxmoxAuthenticationError(f"Authentication failed: {e}")
    
    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid authentication ticket."""
        if not self._auth_ticket or not self._csrf_token:
            await self._authenticate()
            return
        
        # Check if ticket is about to expire (refresh 5 minutes early)
        if self._ticket_expires and time.time() > (self._ticket_expires - 300):
            logger.debug("Refreshing authentication ticket")
            await self._authenticate()
    
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Proxmox API.
        
        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            data: Request body data
            retry_count: Current retry attempt
            
        Returns:
            Dict containing API response
        """
        if not self._session:
            raise ProxmoxAPIError("Client not connected")
        
        await self._ensure_authenticated()
        
        # Build URL
        base_url = self.settings.get_proxmox_url()
        url = urljoin(base_url, path.lstrip('/'))
        
        # Prepare headers
        headers = {}
        if self._csrf_token and method.upper() in ('POST', 'PUT', 'DELETE'):
            headers['CSRFPreventionToken'] = self._csrf_token
        
        # Prepare cookies
        cookies = {}
        if self._auth_ticket:
            cookies['PVEAuthCookie'] = self._auth_ticket
        
        start_time = time.time()
        
        try:
            async with self._session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=data,
                headers=headers,
                cookies=cookies
            ) as response:
                duration = time.time() - start_time
                response_data = await response.json()
                
                # Log API call
                log_api_call(
                    method=method.upper(),
                    endpoint=path,
                    status_code=response.status,
                    duration=duration,
                    user=self._credentials.username if self._credentials else None
                )
                
                if response.status >= 400:
                    error_msg = response_data.get('errors', response_data)
                    raise ProxmoxAPIError(f"API request failed: {error_msg}")
                
                return response_data.get('data', response_data)
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            duration = time.time() - start_time
            
            log_api_call(
                method=method.upper(),
                endpoint=path,
                status_code=None,
                duration=duration,
                user=self._credentials.username if self._credentials else None,
                error=str(e)
            )
            
            # Retry logic with exponential backoff
            max_retries = self.settings.security.max_retry_attempts
            if retry_count < max_retries:
                wait_time = (2 ** retry_count) + (retry_count * 0.1)
                logger.warning(
                    "Request failed, retrying",
                    error=str(e),
                    retry_count=retry_count + 1,
                    wait_time=wait_time
                )
                
                await asyncio.sleep(wait_time)
                return await self._make_request(method, path, params, data, retry_count + 1)
            
            raise ProxmoxConnectionError(f"Request failed after {max_retries} retries: {e}")
    
    # High-level API methods
    
    async def get_nodes(self) -> List[Dict[str, Any]]:
        """Get list of cluster nodes."""
        return await self._make_request('GET', '/nodes')
    
    async def get_node_info(self, node: str) -> Dict[str, Any]:
        """Get information about a specific node."""
        return await self._make_request('GET', f'/nodes/{node}/status')
    
    async def get_vms(self, node: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of virtual machines.
        
        Args:
            node: Optional node name. If not provided, returns VMs from all nodes.
        """
        if node:
            return await self._make_request('GET', f'/nodes/{node}/qemu')
        else:
            # Get VMs from all nodes
            nodes = await self.get_nodes()
            all_vms = []
            
            for node_info in nodes:
                node_name = node_info['node']
                try:
                    vms = await self._make_request('GET', f'/nodes/{node_name}/qemu')
                    # Add node information to each VM
                    for vm in vms:
                        vm['node'] = node_name
                    all_vms.extend(vms)
                except Exception as e:
                    logger.warning(f"Failed to get VMs from node {node_name}", error=str(e))
            
            return all_vms
    
    async def get_vm_info(self, node: str, vmid: int) -> Dict[str, Any]:
        """Get detailed information about a VM."""
        return await self._make_request('GET', f'/nodes/{node}/qemu/{vmid}/status/current')
    
    async def create_vm(
        self,
        node: str,
        vmid: int,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new virtual machine.
        
        Args:
            node: Target node name
            vmid: VM ID
            config: VM configuration
        """
        logger.info("Creating VM", node=node, vmid=vmid)
        
        result = await self._make_request(
            'POST',
            f'/nodes/{node}/qemu',
            data={'vmid': vmid, **config}
        )
        
        log_security_event(
            "VM created",
            success=True,
            user=self._credentials.username if self._credentials else None,
            resource=f"VM {vmid} on {node}",
            details={'vmid': vmid, 'node': node}
        )
        
        return result
    
    async def start_vm(self, node: str, vmid: int) -> Dict[str, Any]:
        """Start a virtual machine."""
        logger.info("Starting VM", node=node, vmid=vmid)
        
        result = await self._make_request('POST', f'/nodes/{node}/qemu/{vmid}/status/start')
        
        log_security_event(
            "VM started",
            success=True,
            user=self._credentials.username if self._credentials else None,
            resource=f"VM {vmid} on {node}"
        )
        
        return result
    
    async def stop_vm(self, node: str, vmid: int, force: bool = False) -> Dict[str, Any]:
        """Stop a virtual machine."""
        logger.info("Stopping VM", node=node, vmid=vmid, force=force)
        
        endpoint = f'/nodes/{node}/qemu/{vmid}/status/shutdown'
        if force:
            endpoint = f'/nodes/{node}/qemu/{vmid}/status/stop'
        
        result = await self._make_request('POST', endpoint)
        
        log_security_event(
            "VM stopped",
            success=True,
            user=self._credentials.username if self._credentials else None,
            resource=f"VM {vmid} on {node}",
            details={'force': force}
        )
        
        return result
    
    async def delete_vm(self, node: str, vmid: int, purge: bool = False) -> Dict[str, Any]:
        """Delete a virtual machine."""
        logger.warning("Deleting VM", node=node, vmid=vmid, purge=purge)
        
        params = {}
        if purge:
            params['purge'] = 1
        
        result = await self._make_request(
            'DELETE',
            f'/nodes/{node}/qemu/{vmid}',
            params=params
        )
        
        log_security_event(
            "VM deleted",
            success=True,
            user=self._credentials.username if self._credentials else None,
            resource=f"VM {vmid} on {node}",
            details={'vmid': vmid, 'node': node, 'purge': purge}
        )
        
        return result
    
    async def get_storages(self, node: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available storage systems."""
        if node:
            return await self._make_request('GET', f'/nodes/{node}/storage')
        else:
            return await self._make_request('GET', '/storage')
    
    async def get_templates(self, node: str, storage: str) -> List[Dict[str, Any]]:
        """Get available VM templates."""
        return await self._make_request('GET', f'/nodes/{node}/storage/{storage}/content')


@asynccontextmanager
async def get_proxmox_client(
    settings: Optional[Settings] = None
) -> AsyncGenerator[SecureProxmoxClient, None]:
    """
    Context manager for Proxmox client.
    
    Args:
        settings: Optional settings instance
        
    Yields:
        SecureProxmoxClient: Connected Proxmox client
    """
    client = SecureProxmoxClient(settings)
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()