"""
VM lifecycle management service for Proxmox AI Assistant.

Provides high-level VM operations, lifecycle management, and automated
provisioning with intelligent resource allocation and monitoring.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

import structlog

from ..api.proxmox_client import get_proxmox_client, ProxmoxAPIError
from ..core.config import get_settings
from ..core.logging import log_security_event

logger = structlog.get_logger(__name__)


class VMState(Enum):
    """VM state enumeration."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


class VMServiceError(Exception):
    """Raised when VM service operations fail."""
    pass


@dataclass
class VMResourceLimits:
    """VM resource limits and constraints."""
    min_memory: int = 512  # MB
    max_memory: int = 32768  # MB
    min_cores: int = 1
    max_cores: int = 16
    min_disk: int = 8  # GB
    max_disk: int = 1024  # GB


@dataclass
class VMTemplate:
    """VM template definition."""
    name: str
    description: str
    config: Dict[str, Any]
    os_type: str
    recommended_resources: Dict[str, Any]
    tags: List[str]


@dataclass
class VMInfo:
    """VM information container."""
    vmid: int
    name: str
    node: str
    state: VMState
    memory: int
    cores: int
    disk_size: int
    uptime: Optional[int]
    cpu_usage: float
    memory_usage: int
    network_interfaces: List[Dict[str, Any]]
    disks: List[Dict[str, Any]]
    config: Dict[str, Any]


class VMLifecycleService:
    """
    High-level VM lifecycle management service.
    
    Provides intelligent VM operations with resource validation,
    automated provisioning, and lifecycle management.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.resource_limits = VMResourceLimits()
        self._templates = {}
        self._load_builtin_templates()
        
        logger.info("VM lifecycle service initialized")
    
    def _load_builtin_templates(self):
        """Load built-in VM templates."""
        self._templates = {
            'ubuntu-server': VMTemplate(
                name="Ubuntu Server",
                description="Ubuntu 22.04 LTS Server",
                config={
                    'ostype': 'l26',
                    'memory': 2048,
                    'cores': 2,
                    'net0': 'virtio,bridge=vmbr0',
                    'virtio0': 'local-lvm:32',
                    'agent': '1',
                    'boot': 'order=virtio0',
                    'description': 'Ubuntu 22.04 LTS Server - Auto-generated'
                },
                os_type='linux',
                recommended_resources={'memory': 2048, 'cores': 2, 'disk': 32},
                tags=['linux', 'ubuntu', 'server']
            ),
            'centos-server': VMTemplate(
                name="CentOS Server",
                description="CentOS 9 Stream Server",
                config={
                    'ostype': 'l26',
                    'memory': 2048,
                    'cores': 2,
                    'net0': 'virtio,bridge=vmbr0',
                    'virtio0': 'local-lvm:32',
                    'agent': '1',
                    'boot': 'order=virtio0',
                    'description': 'CentOS 9 Stream Server - Auto-generated'
                },
                os_type='linux',
                recommended_resources={'memory': 2048, 'cores': 2, 'disk': 32},
                tags=['linux', 'centos', 'server']
            ),
            'windows-server': VMTemplate(
                name="Windows Server",
                description="Windows Server 2022",
                config={
                    'ostype': 'win11',
                    'memory': 4096,
                    'cores': 4,
                    'net0': 'virtio,bridge=vmbr0',
                    'virtio0': 'local-lvm:60',
                    'ide2': 'local:iso/virtio-win.iso,media=cdrom',
                    'boot': 'order=virtio0',
                    'description': 'Windows Server 2022 - Auto-generated'
                },
                os_type='windows',
                recommended_resources={'memory': 4096, 'cores': 4, 'disk': 60},
                tags=['windows', 'server']
            ),
            'docker-host': VMTemplate(
                name="Docker Host",
                description="Docker Container Host (Ubuntu)",
                config={
                    'ostype': 'l26',
                    'memory': 4096,
                    'cores': 4,
                    'net0': 'virtio,bridge=vmbr0',
                    'virtio0': 'local-lvm:64',
                    'agent': '1',
                    'boot': 'order=virtio0',
                    'description': 'Docker Container Host - Auto-generated'
                },
                os_type='linux',
                recommended_resources={'memory': 4096, 'cores': 4, 'disk': 64},
                tags=['linux', 'docker', 'container']
            ),
            'web-server': VMTemplate(
                name="Web Server",
                description="LAMP/NGINX Web Server",
                config={
                    'ostype': 'l26',
                    'memory': 2048,
                    'cores': 2,
                    'net0': 'virtio,bridge=vmbr0',
                    'virtio0': 'local-lvm:32',
                    'agent': '1',
                    'boot': 'order=virtio0',
                    'description': 'Web Server (LAMP/NGINX) - Auto-generated'
                },
                os_type='linux',
                recommended_resources={'memory': 2048, 'cores': 2, 'disk': 32},
                tags=['linux', 'web', 'apache', 'nginx']
            ),
            'database-server': VMTemplate(
                name="Database Server",
                description="MySQL/PostgreSQL Database Server",
                config={
                    'ostype': 'l26',
                    'memory': 4096,
                    'cores': 4,
                    'net0': 'virtio,bridge=vmbr0',
                    'virtio0': 'local-lvm:64',
                    'agent': '1',
                    'boot': 'order=virtio0',
                    'description': 'Database Server - Auto-generated'
                },
                os_type='linux',
                recommended_resources={'memory': 4096, 'cores': 4, 'disk': 64},
                tags=['linux', 'database', 'mysql', 'postgresql']
            )
        }
    
    async def create_vm(
        self,
        vmid: int,
        name: str,
        node: str,
        config: Dict[str, Any],
        template: Optional[str] = None,
        validate_resources: bool = True,
        start_after_creation: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new virtual machine with advanced options.
        
        Args:
            vmid: VM ID number
            name: VM name
            node: Target Proxmox node
            config: VM configuration
            template: Optional template to use as base
            validate_resources: Whether to validate resource allocation
            start_after_creation: Whether to start VM after creation
            
        Returns:
            Dict containing creation result and VM information
        """
        try:
            logger.info("Creating VM", vmid=vmid, name=name, node=node)
            
            # Apply template if specified
            if template:
                config = self._apply_template(config, template)
            
            # Validate configuration
            if validate_resources:
                self._validate_vm_config(config)
            
            # Add metadata
            config['name'] = name
            config['description'] = config.get('description', f'VM {name} - Created by Proxmox AI Assistant')
            
            async with get_proxmox_client() as client:
                # Check if VMID is available
                await self._validate_vmid_available(client, vmid)
                
                # Check node capacity
                if validate_resources:
                    await self._validate_node_capacity(client, node, config)
                
                # Create the VM
                start_time = time.time()
                create_result = await client.create_vm(node, vmid, config)
                creation_time = time.time() - start_time
                
                # Start VM if requested
                if start_after_creation:
                    await client.start_vm(node, vmid)
                
                # Get VM information
                vm_info = await self._get_vm_info_detailed(client, node, vmid)
                
                result = {
                    'vmid': vmid,
                    'name': name,
                    'node': node,
                    'status': 'created',
                    'creation_time': creation_time,
                    'started': start_after_creation,
                    'vm_info': vm_info,
                    'proxmox_result': create_result
                }
                
                log_security_event(
                    "VM created via service",
                    success=True,
                    details={
                        'vmid': vmid,
                        'name': name,
                        'node': node,
                        'template': template,
                        'started': start_after_creation
                    }
                )
                
                logger.info(
                    "VM created successfully",
                    vmid=vmid,
                    name=name,
                    creation_time=creation_time
                )
                
                return result
                
        except Exception as e:
            logger.error("Failed to create VM", vmid=vmid, error=str(e))
            raise VMServiceError(f"VM creation failed: {e}")
    
    def _apply_template(self, config: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Apply template configuration to VM config."""
        if template_name not in self._templates:
            available = ', '.join(self._templates.keys())
            raise VMServiceError(f"Template '{template_name}' not found. Available: {available}")
        
        template = self._templates[template_name]
        
        # Start with template config
        merged_config = template.config.copy()
        
        # Override with user-provided config
        merged_config.update(config)
        
        logger.debug("Applied template", template=template_name, config=merged_config)
        return merged_config
    
    def _validate_vm_config(self, config: Dict[str, Any]):
        """Validate VM configuration against resource limits."""
        errors = []
        
        # Validate memory
        memory = config.get('memory', 0)
        if memory < self.resource_limits.min_memory:
            errors.append(f"Memory too low: {memory}MB (minimum: {self.resource_limits.min_memory}MB)")
        elif memory > self.resource_limits.max_memory:
            errors.append(f"Memory too high: {memory}MB (maximum: {self.resource_limits.max_memory}MB)")
        
        # Validate cores
        cores = config.get('cores', 0)
        if cores < self.resource_limits.min_cores:
            errors.append(f"CPU cores too low: {cores} (minimum: {self.resource_limits.min_cores})")
        elif cores > self.resource_limits.max_cores:
            errors.append(f"CPU cores too high: {cores} (maximum: {self.resource_limits.max_cores})")
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f"Required field missing: {field}")
        
        if errors:
            raise VMServiceError("Configuration validation failed: " + "; ".join(errors))
    
    async def _validate_vmid_available(self, client, vmid: int):
        """Check if VMID is available."""
        try:
            vms = await client.get_vms()
            existing_vmids = [vm['vmid'] for vm in vms]
            
            if vmid in existing_vmids:
                raise VMServiceError(f"VMID {vmid} is already in use")
                
        except ProxmoxAPIError:
            # If we can't check, proceed anyway
            logger.warning("Could not validate VMID availability", vmid=vmid)
    
    async def _validate_node_capacity(self, client, node: str, config: Dict[str, Any]):
        """Validate node has sufficient capacity."""
        try:
            node_info = await client.get_node_info(node)
            
            # Check memory capacity
            requested_memory = config.get('memory', 0) * 1024 * 1024  # Convert MB to bytes
            available_memory = node_info.get('memory', {}).get('free', 0)
            
            if requested_memory > available_memory:
                logger.warning(
                    "Node may not have sufficient memory",
                    node=node,
                    requested=requested_memory,
                    available=available_memory
                )
                # Don't fail, just warn
                
        except Exception as e:
            logger.warning("Could not validate node capacity", node=node, error=str(e))
    
    async def get_vm_info(self, vmid: int, node: Optional[str] = None) -> VMInfo:
        """Get detailed VM information."""
        try:
            async with get_proxmox_client() as client:
                # Find node if not provided
                if not node:
                    vms = await client.get_vms()
                    vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                    if not vm:
                        raise VMServiceError(f"VM {vmid} not found")
                    node = vm['node']
                
                return await self._get_vm_info_detailed(client, node, vmid)
                
        except Exception as e:
            logger.error("Failed to get VM info", vmid=vmid, error=str(e))
            raise VMServiceError(f"Failed to get VM info: {e}")
    
    async def _get_vm_info_detailed(self, client, node: str, vmid: int) -> VMInfo:
        """Get detailed VM information from Proxmox."""
        try:
            # Get current status
            vm_status = await client.get_vm_info(node, vmid)
            
            # Parse VM information
            state_map = {
                'running': VMState.RUNNING,
                'stopped': VMState.STOPPED,
                'paused': VMState.PAUSED,
                'suspended': VMState.SUSPENDED
            }
            
            state = state_map.get(vm_status.get('status', '').lower(), VMState.UNKNOWN)
            
            vm_info = VMInfo(
                vmid=vmid,
                name=vm_status.get('name', f'VM-{vmid}'),
                node=node,
                state=state,
                memory=vm_status.get('maxmem', 0) // (1024 * 1024),  # Convert to MB
                cores=vm_status.get('cpus', 0),
                disk_size=vm_status.get('maxdisk', 0) // (1024 * 1024 * 1024),  # Convert to GB
                uptime=vm_status.get('uptime'),
                cpu_usage=vm_status.get('cpu', 0.0) * 100,  # Convert to percentage
                memory_usage=vm_status.get('mem', 0) // (1024 * 1024),  # Convert to MB
                network_interfaces=[],  # Would need additional API calls to populate
                disks=[],  # Would need additional API calls to populate
                config=vm_status
            )
            
            return vm_info
            
        except Exception as e:
            logger.error("Failed to get detailed VM info", vmid=vmid, error=str(e))
            raise VMServiceError(f"Failed to get detailed VM info: {e}")
    
    async def start_vm(self, vmid: int, node: Optional[str] = None, wait_for_startup: bool = False) -> Dict[str, Any]:
        """Start a virtual machine with advanced options."""
        try:
            async with get_proxmox_client() as client:
                # Find node if not provided
                if not node:
                    vms = await client.get_vms()
                    vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                    if not vm:
                        raise VMServiceError(f"VM {vmid} not found")
                    node = vm['node']
                
                start_time = time.time()
                result = await client.start_vm(node, vmid)
                
                # Wait for startup if requested
                if wait_for_startup:
                    await self._wait_for_vm_state(client, node, vmid, VMState.RUNNING, timeout=120)
                
                startup_time = time.time() - start_time
                
                vm_info = await self._get_vm_info_detailed(client, node, vmid)
                
                logger.info("VM started", vmid=vmid, startup_time=startup_time)
                
                return {
                    'vmid': vmid,
                    'node': node,
                    'status': 'started',
                    'startup_time': startup_time,
                    'vm_info': vm_info,
                    'proxmox_result': result
                }
                
        except Exception as e:
            logger.error("Failed to start VM", vmid=vmid, error=str(e))
            raise VMServiceError(f"VM start failed: {e}")
    
    async def stop_vm(
        self, 
        vmid: int, 
        node: Optional[str] = None, 
        force: bool = False,
        wait_for_shutdown: bool = False
    ) -> Dict[str, Any]:
        """Stop a virtual machine with advanced options."""
        try:
            async with get_proxmox_client() as client:
                # Find node if not provided
                if not node:
                    vms = await client.get_vms()
                    vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                    if not vm:
                        raise VMServiceError(f"VM {vmid} not found")
                    node = vm['node']
                
                start_time = time.time()
                result = await client.stop_vm(node, vmid, force=force)
                
                # Wait for shutdown if requested
                if wait_for_shutdown:
                    await self._wait_for_vm_state(client, node, vmid, VMState.STOPPED, timeout=60)
                
                shutdown_time = time.time() - start_time
                
                vm_info = await self._get_vm_info_detailed(client, node, vmid)
                
                logger.info("VM stopped", vmid=vmid, force=force, shutdown_time=shutdown_time)
                
                return {
                    'vmid': vmid,
                    'node': node,
                    'status': 'stopped',
                    'force': force,
                    'shutdown_time': shutdown_time,
                    'vm_info': vm_info,
                    'proxmox_result': result
                }
                
        except Exception as e:
            logger.error("Failed to stop VM", vmid=vmid, error=str(e))
            raise VMServiceError(f"VM stop failed: {e}")
    
    async def restart_vm(
        self, 
        vmid: int, 
        node: Optional[str] = None,
        wait_for_restart: bool = False
    ) -> Dict[str, Any]:
        """Restart a virtual machine."""
        try:
            logger.info("Restarting VM", vmid=vmid)
            
            start_time = time.time()
            
            # Stop the VM (graceful shutdown)
            stop_result = await self.stop_vm(vmid, node, wait_for_shutdown=True)
            node = stop_result['node']  # Get the node from stop result
            
            # Start the VM
            start_result = await self.start_vm(vmid, node, wait_for_startup=wait_for_restart)
            
            restart_time = time.time() - start_time
            
            logger.info("VM restarted", vmid=vmid, restart_time=restart_time)
            
            return {
                'vmid': vmid,
                'node': node,
                'status': 'restarted',
                'restart_time': restart_time,
                'vm_info': start_result['vm_info'],
                'stop_result': stop_result,
                'start_result': start_result
            }
            
        except Exception as e:
            logger.error("Failed to restart VM", vmid=vmid, error=str(e))
            raise VMServiceError(f"VM restart failed: {e}")
    
    async def delete_vm(
        self, 
        vmid: int, 
        node: Optional[str] = None,
        purge_storage: bool = False,
        force_stop: bool = False
    ) -> Dict[str, Any]:
        """Delete a virtual machine with advanced options."""
        try:
            logger.warning("Deleting VM", vmid=vmid, purge_storage=purge_storage)
            
            async with get_proxmox_client() as client:
                # Find node if not provided
                if not node:
                    vms = await client.get_vms()
                    vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                    if not vm:
                        raise VMServiceError(f"VM {vmid} not found")
                    node = vm['node']
                
                # Get VM info before deletion
                vm_info = await self._get_vm_info_detailed(client, node, vmid)
                
                # Stop VM if running
                if vm_info.state == VMState.RUNNING:
                    if force_stop:
                        await client.stop_vm(node, vmid, force=True)
                    else:
                        await client.stop_vm(node, vmid, force=False)
                    
                    # Wait for VM to stop
                    await self._wait_for_vm_state(client, node, vmid, VMState.STOPPED, timeout=60)
                
                # Delete the VM
                start_time = time.time()
                result = await client.delete_vm(node, vmid, purge=purge_storage)
                deletion_time = time.time() - start_time
                
                log_security_event(
                    "VM deleted via service",
                    success=True,
                    details={
                        'vmid': vmid,
                        'node': node,
                        'purge_storage': purge_storage,
                        'force_stop': force_stop
                    }
                )
                
                logger.warning("VM deleted", vmid=vmid, deletion_time=deletion_time)
                
                return {
                    'vmid': vmid,
                    'node': node,
                    'status': 'deleted',
                    'purge_storage': purge_storage,
                    'deletion_time': deletion_time,
                    'vm_info_before_deletion': vm_info,
                    'proxmox_result': result
                }
                
        except Exception as e:
            logger.error("Failed to delete VM", vmid=vmid, error=str(e))
            raise VMServiceError(f"VM deletion failed: {e}")
    
    async def _wait_for_vm_state(
        self, 
        client, 
        node: str, 
        vmid: int, 
        target_state: VMState, 
        timeout: int = 60
    ):
        """Wait for VM to reach target state."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                vm_info = await self._get_vm_info_detailed(client, node, vmid)
                if vm_info.state == target_state:
                    return
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.warning("Error checking VM state", vmid=vmid, error=str(e))
                await asyncio.sleep(2)
        
        raise VMServiceError(f"VM {vmid} did not reach state {target_state.value} within {timeout} seconds")
    
    async def list_vms(
        self, 
        node: Optional[str] = None,
        state_filter: Optional[VMState] = None,
        include_details: bool = False
    ) -> List[VMInfo]:
        """List VMs with optional filtering and details."""
        try:
            async with get_proxmox_client() as client:
                if node:
                    vms = await client.get_vms(node=node)
                else:
                    vms = await client.get_vms()
                
                vm_list = []
                
                for vm in vms:
                    if include_details:
                        vm_info = await self._get_vm_info_detailed(client, vm['node'], vm['vmid'])
                    else:
                        # Create basic VM info from list data
                        state_map = {
                            'running': VMState.RUNNING,
                            'stopped': VMState.STOPPED,
                            'paused': VMState.PAUSED,
                            'suspended': VMState.SUSPENDED
                        }
                        
                        state = state_map.get(vm.get('status', '').lower(), VMState.UNKNOWN)
                        
                        vm_info = VMInfo(
                            vmid=vm['vmid'],
                            name=vm.get('name', f'VM-{vm["vmid"]}'),
                            node=vm['node'],
                            state=state,
                            memory=vm.get('maxmem', 0) // (1024 * 1024),
                            cores=vm.get('cpus', 0),
                            disk_size=vm.get('maxdisk', 0) // (1024 * 1024 * 1024),
                            uptime=vm.get('uptime'),
                            cpu_usage=vm.get('cpu', 0.0) * 100,
                            memory_usage=vm.get('mem', 0) // (1024 * 1024),
                            network_interfaces=[],
                            disks=[],
                            config=vm
                        )
                    
                    # Apply state filter if specified
                    if state_filter is None or vm_info.state == state_filter:
                        vm_list.append(vm_info)
                
                logger.info("Listed VMs", count=len(vm_list), node=node, state_filter=state_filter)
                return vm_list
                
        except Exception as e:
            logger.error("Failed to list VMs", error=str(e))
            raise VMServiceError(f"VM listing failed: {e}")
    
    def get_templates(self) -> Dict[str, VMTemplate]:
        """Get available VM templates."""
        return self._templates.copy()
    
    def add_template(self, name: str, template: VMTemplate):
        """Add a custom VM template."""
        self._templates[name] = template
        logger.info("Template added", name=name)
    
    def remove_template(self, name: str):
        """Remove a VM template."""
        if name in self._templates:
            del self._templates[name]
            logger.info("Template removed", name=name)
        else:
            raise VMServiceError(f"Template '{name}' not found")


# Convenience functions for common operations

async def create_vm_from_template(
    vmid: int,
    name: str,
    node: str,
    template: str,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create VM from template with optional overrides."""
    service = VMLifecycleService()
    config = overrides or {}
    return await service.create_vm(vmid, name, node, config, template=template)


async def bulk_vm_operation(
    vmids: List[int],
    operation: str,
    **kwargs
) -> List[Dict[str, Any]]:
    """Perform bulk operations on multiple VMs."""
    service = VMLifecycleService()
    results = []
    
    for vmid in vmids:
        try:
            if operation == 'start':
                result = await service.start_vm(vmid, **kwargs)
            elif operation == 'stop':
                result = await service.stop_vm(vmid, **kwargs)
            elif operation == 'restart':
                result = await service.restart_vm(vmid, **kwargs)
            elif operation == 'delete':
                result = await service.delete_vm(vmid, **kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            results.append(result)
            
        except Exception as e:
            results.append({
                'vmid': vmid,
                'status': 'failed',
                'error': str(e)
            })
    
    return results