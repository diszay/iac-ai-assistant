"""
VM lifecycle management commands for Proxmox AI Assistant.

Provides comprehensive VM operations including creation, management, monitoring,
and automated lifecycle operations with AI-powered assistance.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
import structlog

from ...api.proxmox_client import get_proxmox_client, ProxmoxAPIError
from ...core.config import get_settings
from ...core.security import get_or_prompt_credentials

logger = structlog.get_logger(__name__)
console = Console()

# Create VM command group
app = typer.Typer(
    name="vm",
    help="Virtual Machine lifecycle operations",
    rich_markup_mode="rich"
)


@app.command()
def list(
    node: Optional[str] = typer.Option(
        None, "--node", "-n",
        help="Filter VMs by node name"
    ),
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter VMs by status (running, stopped, paused)"
    ),
    format_output: str = typer.Option(
        "table", "--format", "-f",
        help="Output format: table, json, csv"
    ),
    show_config: bool = typer.Option(
        False, "--config", "-c",
        help="Show VM configuration details"
    )
):
    """
    List virtual machines in the Proxmox cluster.
    
    Displays a comprehensive view of all VMs with their current status,
    resource usage, and configuration details.
    """
    asyncio.run(_list_vms(node, status, format_output, show_config))


async def _list_vms(
    node: Optional[str],
    status: Optional[str], 
    format_output: str,
    show_config: bool
):
    """Async implementation of VM listing."""
    try:
        async with get_proxmox_client() as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Fetching VM information...", total=None)
                
                # Get VMs from specified node or all nodes
                if node:
                    vms = await client.get_vms(node=node)
                else:
                    vms = await client.get_vms()
                
                progress.update(task, completed=True)
            
            # Filter by status if specified
            if status:
                vms = [vm for vm in vms if vm.get('status', '').lower() == status.lower()]
            
            # Get detailed info if requested
            if show_config:
                detailed_vms = []
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeElapsedColumn(),
                    console=console
                ) as progress:
                    task = progress.add_task("Getting VM details...", total=len(vms))
                    
                    for vm in vms:
                        try:
                            vm_details = await client.get_vm_info(vm['node'], vm['vmid'])
                            vm.update(vm_details)
                            detailed_vms.append(vm)
                        except Exception as e:
                            logger.warning(f"Failed to get details for VM {vm['vmid']}", error=str(e))
                            detailed_vms.append(vm)
                        
                        progress.update(task, advance=1)
                
                vms = detailed_vms
            
            # Output results
            if format_output == "json":
                console.print(json.dumps(vms, indent=2, default=str))
            elif format_output == "csv":
                _output_csv(vms)
            else:
                _output_table(vms, show_config)
                
    except ProxmoxAPIError as e:
        console.print(f"[red]Proxmox API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Failed to list VMs", error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _output_table(vms: List[Dict[str, Any]], show_config: bool):
    """Output VMs in table format."""
    if not vms:
        console.print("[yellow]No VMs found[/yellow]")
        return
    
    table = Table(title="Proxmox Virtual Machines", show_header=True)
    table.add_column("VMID", style="bold blue")
    table.add_column("Name", style="bold")
    table.add_column("Node", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("CPU", justify="right")
    table.add_column("Memory", justify="right")
    
    if show_config:
        table.add_column("Disk", justify="right")
        table.add_column("Network")
        table.add_column("OS Type")
    
    for vm in vms:
        status_color = {
            'running': 'green',
            'stopped': 'red', 
            'paused': 'yellow'
        }.get(vm.get('status', '').lower(), 'white')
        
        row = [
            str(vm.get('vmid', 'N/A')),
            vm.get('name', 'N/A'),
            vm.get('node', 'N/A'),
            f"[{status_color}]{vm.get('status', 'N/A')}[/{status_color}]",
            f"{vm.get('cpus', 'N/A')}",
            _format_memory(vm.get('maxmem')),
        ]
        
        if show_config:
            row.extend([
                _format_disk_size(vm.get('maxdisk')),
                vm.get('net0', 'N/A'),
                vm.get('ostype', 'N/A')
            ])
        
        table.add_row(*row)
    
    console.print(table)


def _output_csv(vms: List[Dict[str, Any]]):
    """Output VMs in CSV format."""
    if not vms:
        return
    
    # Print CSV header
    headers = ["vmid", "name", "node", "status", "cpus", "maxmem", "maxdisk"]
    console.print(",".join(headers))
    
    # Print VM data
    for vm in vms:
        row = [
            str(vm.get('vmid', '')),
            vm.get('name', ''),
            vm.get('node', ''),
            vm.get('status', ''),
            str(vm.get('cpus', '')),
            str(vm.get('maxmem', '')),
            str(vm.get('maxdisk', ''))
        ]
        console.print(",".join(row))


def _format_memory(memory_bytes: Optional[int]) -> str:
    """Format memory size in human-readable format."""
    if not memory_bytes:
        return "N/A"
    
    # Convert bytes to MB
    memory_mb = memory_bytes / (1024 * 1024)
    
    if memory_mb >= 1024:
        return f"{memory_mb / 1024:.1f}GB"
    else:
        return f"{memory_mb:.0f}MB"


def _format_disk_size(disk_bytes: Optional[int]) -> str:
    """Format disk size in human-readable format."""
    if not disk_bytes:
        return "N/A"
    
    # Convert bytes to GB
    disk_gb = disk_bytes / (1024 * 1024 * 1024)
    
    if disk_gb >= 1024:
        return f"{disk_gb / 1024:.1f}TB"
    else:
        return f"{disk_gb:.1f}GB"


@app.command()
def create(
    vmid: int = typer.Argument(..., help="VM ID number"),
    name: str = typer.Argument(..., help="VM name"),
    node: str = typer.Option(..., "--node", "-n", help="Target Proxmox node"),
    memory: int = typer.Option(2048, "--memory", "-m", help="Memory in MB"),
    cores: int = typer.Option(2, "--cores", "-c", help="Number of CPU cores"),
    disk_size: str = typer.Option("32G", "--disk", "-d", help="Disk size (e.g., 32G)"),
    os_type: str = typer.Option("l26", "--os-type", "-o", help="OS type"),
    iso: Optional[str] = typer.Option(None, "--iso", "-i", help="ISO image path"),
    start: bool = typer.Option(False, "--start", "-s", help="Start VM after creation"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="JSON config file")
):
    """
    Create a new virtual machine.
    
    Creates a VM with the specified configuration. Can use a config file
    for advanced settings or command line options for basic setup.
    """
    asyncio.run(_create_vm(vmid, name, node, memory, cores, disk_size, os_type, iso, start, config_file))


async def _create_vm(
    vmid: int, name: str, node: str, memory: int, cores: int,
    disk_size: str, os_type: str, iso: Optional[str], start: bool,
    config_file: Optional[Path]
):
    """Async implementation of VM creation."""
    try:
        # Load configuration from file if provided
        if config_file:
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            # Build configuration from command line options
            config = {
                'name': name,
                'memory': memory,
                'cores': cores,
                'ostype': os_type,
                'ide2': f'{iso},media=cdrom' if iso else None,
                'virtio0': f'local-lvm:{disk_size}',
                'net0': 'virtio,bridge=vmbr0',
                'boot': 'order=virtio0;ide2',
                'agent': 'enabled=1'
            }
            
            # Remove None values
            config = {k: v for k, v in config.items() if v is not None}
        
        console.print(Panel.fit(
            f"[bold blue]Creating VM {vmid} ({name}) on {node}[/bold blue]",
            style="blue"
        ))
        
        # Display configuration for confirmation
        config_table = Table(title="VM Configuration", show_header=True)
        config_table.add_column("Setting", style="bold")
        config_table.add_column("Value", style="cyan")
        
        for key, value in config.items():
            config_table.add_row(key, str(value))
        
        console.print(config_table)
        
        if not Confirm.ask("\nProceed with VM creation?"):
            console.print("[yellow]VM creation cancelled[/yellow]")
            return
        
        async with get_proxmox_client() as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating VM...", total=None)
                
                # Create the VM
                result = await client.create_vm(node, vmid, config)
                
                progress.update(task, description="VM created successfully")
                progress.update(task, completed=True)
            
            console.print(f"[green]✅ VM {vmid} created successfully[/green]")
            
            # Start VM if requested
            if start:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Starting VM...", total=None)
                    
                    await client.start_vm(node, vmid)
                    
                    progress.update(task, completed=True)
                
                console.print(f"[green]✅ VM {vmid} started successfully[/green]")
                
    except ProxmoxAPIError as e:
        console.print(f"[red]Proxmox API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Failed to create VM", vmid=vmid, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def start(
    vmid: int = typer.Argument(..., help="VM ID to start"),
    node: Optional[str] = typer.Option(None, "--node", "-n", help="Node name (auto-detected if not provided)")
):
    """Start a virtual machine."""
    asyncio.run(_start_vm(vmid, node))


async def _start_vm(vmid: int, node: Optional[str]):
    """Async implementation of VM start."""
    try:
        async with get_proxmox_client() as client:
            # Auto-detect node if not provided
            if not node:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Finding VM...", total=None)
                    vms = await client.get_vms()
                    vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                    
                    if not vm:
                        console.print(f"[red]VM {vmid} not found[/red]")
                        raise typer.Exit(1)
                    
                    node = vm['node']
                    progress.update(task, completed=True)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Starting VM {vmid}...", total=None)
                
                await client.start_vm(node, vmid)
                
                progress.update(task, completed=True)
            
            console.print(f"[green]✅ VM {vmid} started successfully[/green]")
            
    except ProxmoxAPIError as e:
        console.print(f"[red]Proxmox API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Failed to start VM", vmid=vmid, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def stop(
    vmid: int = typer.Argument(..., help="VM ID to stop"),
    node: Optional[str] = typer.Option(None, "--node", "-n", help="Node name (auto-detected if not provided)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force stop (power off)")
):
    """Stop a virtual machine."""
    asyncio.run(_stop_vm(vmid, node, force))


async def _stop_vm(vmid: int, node: Optional[str], force: bool):
    """Async implementation of VM stop."""
    try:
        async with get_proxmox_client() as client:
            # Auto-detect node if not provided
            if not node:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Finding VM...", total=None)
                    vms = await client.get_vms()
                    vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                    
                    if not vm:
                        console.print(f"[red]VM {vmid} not found[/red]")
                        raise typer.Exit(1)
                    
                    node = vm['node']
                    progress.update(task, completed=True)
            
            action = "Force stopping" if force else "Stopping"
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"{action} VM {vmid}...", total=None)
                
                await client.stop_vm(node, vmid, force=force)
                
                progress.update(task, completed=True)
            
            action_past = "force stopped" if force else "stopped"
            console.print(f"[green]✅ VM {vmid} {action_past} successfully[/green]")
            
    except ProxmoxAPIError as e:
        console.print(f"[red]Proxmox API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Failed to stop VM", vmid=vmid, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(
    vmid: int = typer.Argument(..., help="VM ID to delete"),
    node: Optional[str] = typer.Option(None, "--node", "-n", help="Node name (auto-detected if not provided)"),
    purge: bool = typer.Option(False, "--purge", "-p", help="Purge VM from all storages"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt")
):
    """
    Delete a virtual machine.
    
    [red]WARNING: This action is irreversible![/red]
    """
    asyncio.run(_delete_vm(vmid, node, purge, force))


async def _delete_vm(vmid: int, node: Optional[str], purge: bool, force: bool):
    """Async implementation of VM deletion."""
    try:
        async with get_proxmox_client() as client:
            # Auto-detect node if not provided
            if not node:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Finding VM...", total=None)
                    vms = await client.get_vms()
                    vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                    
                    if not vm:
                        console.print(f"[red]VM {vmid} not found[/red]")
                        raise typer.Exit(1)
                    
                    node = vm['node']
                    progress.update(task, completed=True)
            
            # Confirmation prompt (unless forced)
            if not force:
                console.print(f"[red]⚠️  WARNING: You are about to delete VM {vmid}[/red]")
                if purge:
                    console.print("[red]This will also purge all associated storage![/red]")
                
                if not Confirm.ask(f"Are you sure you want to delete VM {vmid}?"):
                    console.print("[yellow]VM deletion cancelled[/yellow]")
                    return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Deleting VM {vmid}...", total=None)
                
                await client.delete_vm(node, vmid, purge=purge)
                
                progress.update(task, completed=True)
            
            console.print(f"[green]✅ VM {vmid} deleted successfully[/green]")
            
    except ProxmoxAPIError as e:
        console.print(f"[red]Proxmox API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Failed to delete VM", vmid=vmid, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    vmid: int = typer.Argument(..., help="VM ID to check"),
    node: Optional[str] = typer.Option(None, "--node", "-n", help="Node name (auto-detected if not provided)"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch status changes")
):
    """Show detailed status information for a virtual machine."""
    asyncio.run(_show_vm_status(vmid, node, watch))


async def _show_vm_status(vmid: int, node: Optional[str], watch: bool):
    """Async implementation of VM status display."""
    try:
        async with get_proxmox_client() as client:
            # Auto-detect node if not provided
            if not node:
                vms = await client.get_vms()
                vm = next((vm for vm in vms if vm['vmid'] == vmid), None)
                
                if not vm:
                    console.print(f"[red]VM {vmid} not found[/red]")
                    raise typer.Exit(1)
                
                node = vm['node']
            
            if watch:
                console.print(f"[blue]Watching VM {vmid} status (Press Ctrl+C to stop)[/blue]")
                try:
                    while True:
                        console.clear()
                        await _display_vm_status(client, node, vmid)
                        await asyncio.sleep(2)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Status monitoring stopped[/yellow]")
            else:
                await _display_vm_status(client, node, vmid)
                
    except ProxmoxAPIError as e:
        console.print(f"[red]Proxmox API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Failed to get VM status", vmid=vmid, error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


async def _display_vm_status(client, node: str, vmid: int):
    """Display VM status information."""
    vm_info = await client.get_vm_info(node, vmid)
    
    # Create status panel
    status_color = {
        'running': 'green',
        'stopped': 'red',
        'paused': 'yellow'
    }.get(vm_info.get('status', '').lower(), 'white')
    
    status_text = f"[{status_color}]{vm_info.get('status', 'Unknown').upper()}[/{status_color}]"
    
    console.print(Panel.fit(
        f"[bold blue]VM {vmid} Status: {status_text}[/bold blue]",
        style="blue"
    ))
    
    # Create details table
    table = Table(title=f"VM {vmid} Details", show_header=True)
    table.add_column("Property", style="bold")
    table.add_column("Value", style="cyan")
    
    # Add basic info
    table.add_row("VMID", str(vmid))
    table.add_row("Name", vm_info.get('name', 'N/A'))
    table.add_row("Node", node)
    table.add_row("Status", vm_info.get('status', 'N/A'))
    table.add_row("Uptime", str(vm_info.get('uptime', 'N/A')))
    
    # Add resource info
    table.add_row("CPU Usage", f"{vm_info.get('cpu', 0) * 100:.1f}%")
    table.add_row("Memory", _format_memory(vm_info.get('mem')))
    table.add_row("Max Memory", _format_memory(vm_info.get('maxmem')))
    table.add_row("Disk Usage", _format_disk_size(vm_info.get('disk')))
    table.add_row("Max Disk", _format_disk_size(vm_info.get('maxdisk')))
    
    console.print(table)


if __name__ == "__main__":
    app()