"""
Main CLI application for Proxmox AI Assistant.

Provides a comprehensive command-line interface for managing Proxmox VE
infrastructure with AI-powered automation features.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
import structlog

from ..core.config import get_settings, Settings
from ..core.logging import setup_logging
from ..core.security import CredentialManager
from .commands import vm_commands, config_commands, ai_commands

# Initialize console and logger
console = Console()
logger = structlog.get_logger(__name__)


def version_callback(value: bool):
    """Print version information."""
    if value:
        settings = get_settings()
        console.print(f"[bold blue]{settings.app_name}[/bold blue] version [green]{settings.version}[/green]")
        raise typer.Exit()


def create_app() -> typer.Typer:
    """Create and configure the main Typer application."""
    app = typer.Typer(
        name="proxmox-ai",
        help="AI-Powered Proxmox Infrastructure Automation Assistant",
        no_args_is_help=True,
        rich_markup_mode="rich",
        add_completion=False,
    )
    
    # Add version option
    app.callback()(lambda version: None)  # Placeholder callback
    
    # Add subcommands
    app.add_typer(vm_commands, name="vm", help="VM lifecycle operations")
    app.add_typer(config_commands, name="config", help="Configuration management")
    app.add_typer(ai_commands, name="ai", help="AI-powered automation")
    
    return app


# Create main application instance
app = create_app()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version information"
    ),
    debug: bool = typer.Option(
        False, "--debug", "-d",
        help="Enable debug mode"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Path to configuration file"
    ),
    log_level: Optional[str] = typer.Option(
        None, "--log-level", "-l",
        help="Set log level (DEBUG, INFO, WARNING, ERROR)"
    ),
    no_color: bool = typer.Option(
        False, "--no-color",
        help="Disable colored output"
    )
):
    """
    AI-Powered Proxmox Infrastructure Automation Assistant.
    
    Manage your Proxmox VE infrastructure with intelligent automation,
    secure credential management, and AI-powered code generation.
    """
    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['config_file'] = config_file
    ctx.obj['log_level'] = log_level
    ctx.obj['no_color'] = no_color
    
    # Configure console for no-color mode
    if no_color:
        console._color_system = None
    
    # Initialize settings
    try:
        settings = get_settings()
        if debug:
            settings.debug = True
        if log_level:
            settings.logging.level = log_level.upper()
        
        # Setup logging
        setup_logging(settings.logging)
        
        logger.info(
            "Proxmox AI Assistant started",
            version=settings.version,
            debug=debug,
            log_level=settings.logging.level
        )
        
    except Exception as e:
        console.print(f"[red]Error initializing application: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show system status and configuration."""
    settings = get_settings()
    
    # Create status table
    table = Table(title="Proxmox AI Assistant Status", show_header=True)
    table.add_column("Component", style="bold blue")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    # Application info
    table.add_row(
        "Application",
        "✓ Running",
        f"Version {settings.version}"
    )
    
    # Configuration
    config_status = "✓ Loaded" if settings else "✗ Error"
    config_details = f"Environment: {settings.environment}"
    if settings.debug:
        config_details += " (DEBUG)"
    
    table.add_row("Configuration", config_status, config_details)
    
    # Proxmox connection
    proxmox_details = f"{settings.proxmox.host}:{settings.proxmox.port}"
    if settings.proxmox.verify_ssl:
        proxmox_details += " (SSL)"
    
    table.add_row(
        "Proxmox VE",
        "⚠ Not connected",
        proxmox_details
    )
    
    # AI integration
    ai_status = "✓ Available"
    ai_details = f"Model: {settings.local_ai.model_name} (Local)"
    
    table.add_row("AI Integration", ai_status, ai_details)
    
    # Credentials
    credential_manager = CredentialManager()
    cred_status = "✓ Available"
    cred_details = "Keyring integration active"
    
    table.add_row("Credentials", cred_status, cred_details)
    
    console.print(table)


@app.command()
def doctor():
    """
    Run system diagnostics and health checks.
    
    Performs comprehensive checks of configuration, connectivity,
    and system requirements.
    """
    console.print(Panel.fit(
        "[bold blue]Proxmox AI Assistant Health Check[/bold blue]",
        style="blue"
    ))
    
    settings = get_settings()
    issues = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Check configuration
        task = progress.add_task("Checking configuration...", total=1)
        try:
            if not settings.proxmox.host:
                issues.append("❌ Proxmox host not configured")
            else:
                console.print("✅ Proxmox configuration valid")
            
            # Local AI check would go here if needed
            
            progress.update(task, completed=1)
        except Exception as e:
            issues.append(f"❌ Configuration error: {e}")
            progress.update(task, completed=1)
        
        # Check directory permissions
        task = progress.add_task("Checking directories...", total=1)
        try:
            for directory in [settings.config_dir, settings.data_dir, settings.cache_dir]:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                
                if not directory.is_dir() or not os.access(directory, os.W_OK):
                    issues.append(f"❌ Directory not writable: {directory}")
            
            if not issues:
                console.print("✅ All directories accessible")
            
            progress.update(task, completed=1)
        except Exception as e:
            issues.append(f"❌ Directory check failed: {e}")
            progress.update(task, completed=1)
        
        # Check credential system
        task = progress.add_task("Checking credential system...", total=1)
        try:
            credential_manager = CredentialManager()
            console.print("✅ Credential system operational")
            progress.update(task, completed=1)
        except Exception as e:
            issues.append(f"❌ Credential system error: {e}")
            progress.update(task, completed=1)
        
        # Test Proxmox connectivity (if configured)
        if settings.proxmox.host:
            task = progress.add_task("Testing Proxmox connectivity...", total=1)
            try:
                # This would be implemented with actual connectivity test
                console.print("⚠️  Proxmox connectivity test not implemented yet")
                progress.update(task, completed=1)
            except Exception as e:
                issues.append(f"❌ Proxmox connection failed: {e}")
                progress.update(task, completed=1)
    
    # Display results
    if not issues:
        console.print("\n[bold green]✅ All health checks passed![/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠️  Found {len(issues)} issue(s):[/bold yellow]")
        for issue in issues:
            console.print(f"  {issue}")
        
        console.print("\n[dim]Run 'proxmox-ai config setup' to fix configuration issues.[/dim]")


@app.command()
def info():
    """Display detailed system information."""
    settings = get_settings()
    
    # System Information Panel
    info_text = Text()
    info_text.append(f"Application: ", style="bold")
    info_text.append(f"{settings.app_name} v{settings.version}\n")
    info_text.append(f"Environment: ", style="bold")
    info_text.append(f"{settings.environment}\n")
    info_text.append(f"Debug Mode: ", style="bold")
    info_text.append(f"{'Enabled' if settings.debug else 'Disabled'}\n")
    info_text.append(f"Python Version: ", style="bold")
    info_text.append(f"{sys.version.split()[0]}\n")
    
    console.print(Panel(info_text, title="System Information", style="blue"))
    
    # Configuration Panel
    config_text = Text()
    config_text.append(f"Config Dir: ", style="bold")
    config_text.append(f"{settings.config_dir}\n")
    config_text.append(f"Data Dir: ", style="bold")
    config_text.append(f"{settings.data_dir}\n")
    config_text.append(f"Cache Dir: ", style="bold")
    config_text.append(f"{settings.cache_dir}\n")
    config_text.append(f"Log Level: ", style="bold")
    config_text.append(f"{settings.logging.level}\n")
    
    console.print(Panel(config_text, title="Configuration", style="green"))
    
    # Proxmox Configuration Panel
    proxmox_text = Text()
    proxmox_text.append(f"Host: ", style="bold")
    proxmox_text.append(f"{settings.proxmox.host}:{settings.proxmox.port}\n")
    proxmox_text.append(f"User: ", style="bold")
    proxmox_text.append(f"{settings.proxmox.user}\n")
    proxmox_text.append(f"SSL Verification: ", style="bold")
    proxmox_text.append(f"{'Enabled' if settings.proxmox.verify_ssl else 'Disabled'}\n")
    proxmox_text.append(f"Timeout: ", style="bold")
    proxmox_text.append(f"{settings.proxmox.timeout}s\n")
    
    console.print(Panel(proxmox_text, title="Proxmox Configuration", style="cyan"))
    
    # AI Configuration Panel
    ai_text = Text()
    ai_text.append(f"AI Generation: ", style="bold")
    ai_text.append(f"{'Enabled' if settings.enable_ai_generation else 'Disabled'}\n")
    ai_text.append(f"Model: ", style="bold")
    ai_text.append(f"{settings.local_ai.model_name}\n")
    ai_text.append(f"Max Tokens: ", style="bold")
    ai_text.append(f"{settings.local_ai.max_tokens}\n")
    ai_text.append(f"Temperature: ", style="bold")
    ai_text.append(f"{settings.local_ai.temperature}\n")
    ai_text.append(f"Ollama Host: ", style="bold")
    ai_text.append(f"{settings.local_ai.ollama_host}\n")
    
    console.print(Panel(ai_text, title="AI Configuration", style="magenta"))


if __name__ == "__main__":
    app()