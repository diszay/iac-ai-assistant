"""
Configuration management commands for Proxmox AI Assistant.

Provides comprehensive configuration management including setup, validation,
credential management, and environment configuration.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
import structlog

from ...core.config import get_settings, reload_settings, Settings
from ...core.security import CredentialManager, get_or_prompt_credentials
from ...api.proxmox_client import SecureProxmoxClient

logger = structlog.get_logger(__name__)
console = Console()

# Create config command group
app = typer.Typer(
    name="config",
    help="Configuration management operations",
    rich_markup_mode="rich"
)


@app.command()
def show(
    format_output: str = typer.Option(
        "table", "--format", "-f",
        help="Output format: table, json, yaml"
    ),
    include_sensitive: bool = typer.Option(
        False, "--include-sensitive", "-s",
        help="Include sensitive configuration values"
    )
):
    """
    Display current configuration settings.
    
    Shows all configuration values in a readable format, with the option
    to include or exclude sensitive information.
    """
    try:
        settings = get_settings()
        
        if format_output == "json":
            config_dict = settings.to_dict()
            if include_sensitive:
                # Re-add sensitive data for JSON output if requested
                config_dict['anthropic']['api_key'] = settings.anthropic.api_key
            console.print(json.dumps(config_dict, indent=2, default=str))
            
        elif format_output == "yaml":
            import yaml
            config_dict = settings.to_dict()
            if include_sensitive:
                config_dict['anthropic']['api_key'] = settings.anthropic.api_key
            console.print(yaml.dump(config_dict, default_flow_style=False))
            
        else:
            _display_config_table(settings, include_sensitive)
            
    except Exception as e:
        logger.error("Failed to display configuration", error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _display_config_table(settings: Settings, include_sensitive: bool):
    """Display configuration in table format."""
    
    # Application Configuration
    app_table = Table(title="Application Configuration", show_header=True)
    app_table.add_column("Setting", style="bold")
    app_table.add_column("Value", style="cyan")
    
    app_table.add_row("App Name", settings.app_name)
    app_table.add_row("Version", settings.version)
    app_table.add_row("Environment", settings.environment)
    app_table.add_row("Debug Mode", "Enabled" if settings.debug else "Disabled")
    app_table.add_row("Config Dir", str(settings.config_dir))
    app_table.add_row("Data Dir", str(settings.data_dir))
    app_table.add_row("Cache Dir", str(settings.cache_dir))
    
    console.print(app_table)
    console.print()
    
    # Proxmox Configuration
    proxmox_table = Table(title="Proxmox Configuration", show_header=True)
    proxmox_table.add_column("Setting", style="bold")
    proxmox_table.add_column("Value", style="cyan")
    
    proxmox_table.add_row("Host", settings.proxmox.host)
    proxmox_table.add_row("Port", str(settings.proxmox.port))
    proxmox_table.add_row("User", settings.proxmox.user)
    proxmox_table.add_row("SSL Verification", "Enabled" if settings.proxmox.verify_ssl else "Disabled")
    proxmox_table.add_row("Timeout", f"{settings.proxmox.timeout}s")
    
    console.print(proxmox_table)
    console.print()
    
    # AI Configuration
    ai_table = Table(title="AI Configuration", show_header=True)
    ai_table.add_column("Setting", style="bold")
    ai_table.add_column("Value", style="cyan")
    
    ai_table.add_row("AI Generation", "Enabled" if settings.enable_ai_generation else "Disabled")
    ai_table.add_row("Model", settings.anthropic.model)
    ai_table.add_row("Max Tokens", str(settings.anthropic.max_tokens))
    ai_table.add_row("Temperature", str(settings.anthropic.temperature))
    ai_table.add_row("Timeout", f"{settings.anthropic.timeout}s")
    
    api_key_display = settings.anthropic.api_key if include_sensitive else (
        "Configured" if settings.anthropic.api_key else "Not set"
    )
    ai_table.add_row("API Key", api_key_display)
    
    console.print(ai_table)
    console.print()
    
    # Security Configuration
    security_table = Table(title="Security Configuration", show_header=True)
    security_table.add_column("Setting", style="bold")
    security_table.add_column("Value", style="cyan")
    
    security_table.add_row("Audit Logging", "Enabled" if settings.security.enable_audit_logging else "Disabled")
    security_table.add_row("Log Sensitive Data", "Enabled" if settings.security.log_sensitive_data else "Disabled")
    security_table.add_row("Session Timeout", f"{settings.security.session_timeout}s")
    security_table.add_row("Max Retry Attempts", str(settings.security.max_retry_attempts))
    security_table.add_row("Credential Cache TTL", f"{settings.security.credential_cache_ttl}s")
    
    console.print(security_table)
    console.print()
    
    # Logging Configuration
    logging_table = Table(title="Logging Configuration", show_header=True)
    logging_table.add_column("Setting", style="bold")
    logging_table.add_column("Value", style="cyan")
    
    logging_table.add_row("Level", settings.logging.level)
    logging_table.add_row("Format", settings.logging.format)
    logging_table.add_row("File Path", str(settings.logging.file_path) if settings.logging.file_path else "Not set")
    logging_table.add_row("Max File Size", f"{settings.logging.max_file_size} bytes")
    logging_table.add_row("Backup Count", str(settings.logging.backup_count))
    
    console.print(logging_table)


@app.command()
def setup(
    interactive: bool = typer.Option(
        True, "--interactive/--non-interactive", "-i/-n",
        help="Run in interactive mode"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Load configuration from file"
    )
):
    """
    Interactive setup wizard for initial configuration.
    
    Guides you through setting up Proxmox connection, AI integration,
    and other essential configuration options.
    """
    try:
        console.print(Panel.fit(
            "[bold blue]Proxmox AI Assistant Setup Wizard[/bold blue]",
            style="blue"
        ))
        
        if config_file and config_file.exists():
            console.print(f"[green]Loading configuration from {config_file}[/green]")
            _load_config_from_file(config_file)
        
        if interactive:
            _interactive_setup()
        else:
            console.print("[yellow]Non-interactive setup not yet implemented[/yellow]")
            
        console.print("[green]✅ Setup completed successfully![/green]")
        console.print("\n[dim]Run 'proxmox-ai doctor' to verify your configuration.[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Setup failed", error=str(e))
        console.print(f"[red]Setup failed: {e}[/red]")
        raise typer.Exit(1)


def _load_config_from_file(config_file: Path):
    """Load configuration from a file."""
    try:
        with open(config_file, 'r') as f:
            if config_file.suffix == '.json':
                config_data = json.load(f)
            elif config_file.suffix in ['.yaml', '.yml']:
                import yaml
                config_data = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported config file format. Use JSON or YAML.")
        
        # Set environment variables from config
        for key, value in _flatten_dict(config_data).items():
            env_key = key.upper().replace('.', '__')
            os.environ[env_key] = str(value)
        
        # Reload settings to pick up new values
        reload_settings()
        
    except Exception as e:
        logger.error("Failed to load config file", file=str(config_file), error=str(e))
        raise


def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary for environment variable conversion."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def _interactive_setup():
    """Run interactive setup wizard."""
    console.print("\n[bold cyan]Step 1: Proxmox Configuration[/bold cyan]")
    
    # Proxmox configuration
    settings = get_settings()
    
    proxmox_host = Prompt.ask(
        "Proxmox host address",
        default=settings.proxmox.host
    )
    
    proxmox_port = IntPrompt.ask(
        "Proxmox port",
        default=settings.proxmox.port
    )
    
    proxmox_user = Prompt.ask(
        "Proxmox username",
        default=settings.proxmox.user
    )
    
    verify_ssl = Confirm.ask(
        "Enable SSL verification?",
        default=settings.proxmox.verify_ssl
    )
    
    # Set environment variables
    os.environ['PROXMOX__HOST'] = proxmox_host
    os.environ['PROXMOX__PORT'] = str(proxmox_port)
    os.environ['PROXMOX__USER'] = proxmox_user
    os.environ['PROXMOX__VERIFY_SSL'] = str(verify_ssl).lower()
    
    console.print("\n[bold cyan]Step 2: AI Configuration[/bold cyan]")
    
    enable_ai = Confirm.ask(
        "Enable AI-powered code generation?",
        default=settings.enable_ai_generation
    )
    
    if enable_ai:
        anthropic_api_key = Prompt.ask(
            "Anthropic API key (leave empty to skip)",
            password=True,
            default=""
        )
        
        if anthropic_api_key:
            os.environ['ANTHROPIC__API_KEY'] = anthropic_api_key
        
        model = Prompt.ask(
            "Claude model to use",
            default=settings.anthropic.model
        )
        os.environ['ANTHROPIC__MODEL'] = model
    
    os.environ['ENABLE_AI_GENERATION'] = str(enable_ai).lower()
    
    console.print("\n[bold cyan]Step 3: Credential Setup[/bold cyan]")
    
    if Confirm.ask("Set up Proxmox credentials now?", default=True):
        _setup_credentials(proxmox_host, proxmox_user)
    
    console.print("\n[bold cyan]Step 4: Environment Settings[/bold cyan]")
    
    environment = Prompt.ask(
        "Environment (development/production)",
        choices=["development", "production"],
        default=settings.environment
    )
    os.environ['ENVIRONMENT'] = environment
    
    debug_mode = Confirm.ask(
        "Enable debug mode?",
        default=settings.debug
    )
    os.environ['DEBUG'] = str(debug_mode).lower()
    
    # Reload settings to apply changes
    reload_settings()
    
    console.print("\n[green]Configuration updated successfully![/green]")


def _setup_credentials(host: str, username: str):
    """Set up Proxmox credentials."""
    try:
        service_name = f"proxmox_{host}"
        credential_manager = CredentialManager()
        
        console.print(f"\n[cyan]Setting up credentials for Proxmox at {host}[/cyan]")
        
        credentials = credential_manager.prompt_for_credentials(
            service_name=service_name,
            username_prompt=f"Proxmox username [{username}]",
            password_prompt="Proxmox password",
            host_prompt=f"Proxmox host [{host}]",
            port_prompt="Proxmox port [8006]"
        )
        
        console.print("[green]✅ Credentials stored successfully[/green]")
        
    except Exception as e:
        logger.error("Failed to setup credentials", error=str(e))
        console.print(f"[yellow]⚠️  Credential setup failed: {e}[/yellow]")


@app.command()
def test(
    component: Optional[str] = typer.Option(
        None, "--component", "-c",
        help="Test specific component (proxmox, ai, credentials)"
    )
):
    """
    Test configuration settings and connectivity.
    
    Verifies that all configured services are accessible and working properly.
    """
    try:
        settings = get_settings()
        
        console.print(Panel.fit(
            "[bold blue]Configuration Test Results[/bold blue]",
            style="blue"
        ))
        
        if not component or component == "proxmox":
            _test_proxmox_connection(settings)
        
        if not component or component == "ai":
            _test_ai_integration(settings)
        
        if not component or component == "credentials":
            _test_credential_system(settings)
            
    except Exception as e:
        logger.error("Configuration test failed", error=str(e))
        console.print(f"[red]Test failed: {e}[/red]")
        raise typer.Exit(1)


def _test_proxmox_connection(settings: Settings):
    """Test Proxmox connectivity."""
    console.print("\n[cyan]Testing Proxmox connection...[/cyan]")
    
    try:
        import asyncio
        
        async def test_connection():
            client = SecureProxmoxClient(settings)
            try:
                await client.connect()
                nodes = await client.get_nodes()
                return len(nodes)
            finally:
                await client.disconnect()
        
        node_count = asyncio.run(test_connection())
        console.print(f"[green]✅ Proxmox connection successful - Found {node_count} nodes[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Proxmox connection failed: {e}[/red]")


def _test_ai_integration(settings: Settings):
    """Test AI integration."""
    console.print("\n[cyan]Testing AI integration...[/cyan]")
    
    if not settings.enable_ai_generation:
        console.print("[yellow]⚠️  AI generation is disabled[/yellow]")
        return
    
    if not settings.anthropic.api_key:
        console.print("[yellow]⚠️  No Anthropic API key configured[/yellow]")
        return
    
    try:
        # Test with a simple API call
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic.api_key)
        
        response = client.messages.create(
            model=settings.anthropic.model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        console.print("[green]✅ AI integration working correctly[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ AI integration failed: {e}[/red]")


def _test_credential_system(settings: Settings):
    """Test credential management system."""
    console.print("\n[cyan]Testing credential system...[/cyan]")
    
    try:
        credential_manager = CredentialManager()
        
        # Test basic functionality
        test_service = "test_service_temp"
        test_creds = credential_manager.store_credentials(
            service_name=test_service,
            username="test_user",
            password="example_password_here"
        )
        
        retrieved_creds = credential_manager.get_credentials(test_service)
        
        if retrieved_creds and retrieved_creds.username == "test_user":
            console.print("[green]✅ Credential system working correctly[/green]")
            # Cleanup
            credential_manager.delete_credentials(test_service)
        else:
            console.print("[red]❌ Credential system failed - could not retrieve stored credentials[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Credential system failed: {e}[/red]")


@app.command()
def reset(
    component: Optional[str] = typer.Option(
        None, "--component", "-c",
        help="Reset specific component (config, credentials, all)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip confirmation prompts"
    )
):
    """
    Reset configuration to defaults.
    
    [red]WARNING: This will delete existing configuration![/red]
    """
    try:
        if not force:
            console.print("[red]⚠️  WARNING: This will reset your configuration![/red]")
            
            if not Confirm.ask("Are you sure you want to continue?"):
                console.print("[yellow]Reset cancelled[/yellow]")
                return
        
        if not component or component == "config":
            _reset_config()
        
        if not component or component == "credentials":
            _reset_credentials()
        
        if component == "all":
            _reset_config()
            _reset_credentials()
            _reset_cache()
        
        console.print("[green]✅ Reset completed successfully[/green]")
        
    except Exception as e:
        logger.error("Reset failed", error=str(e))
        console.print(f"[red]Reset failed: {e}[/red]")
        raise typer.Exit(1)


def _reset_config():
    """Reset configuration files."""
    settings = get_settings()
    
    # Remove config file if it exists
    if settings.config_file.exists():
        settings.config_file.unlink()
        console.print(f"[yellow]Removed config file: {settings.config_file}[/yellow]")
    
    # Clear environment variables
    env_vars_to_clear = [
        'PROXMOX__HOST', 'PROXMOX__PORT', 'PROXMOX__USER', 'PROXMOX__VERIFY_SSL',
        'ANTHROPIC__API_KEY', 'ANTHROPIC__MODEL',
        'ENABLE_AI_GENERATION', 'DEBUG', 'ENVIRONMENT'
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
    
    console.print("[green]Configuration reset to defaults[/green]")


def _reset_credentials():
    """Reset stored credentials."""
    try:
        credential_manager = CredentialManager()
        services = credential_manager.list_services()
        
        for service in services:
            credential_manager.delete_credentials(service)
        
        console.print(f"[green]Removed credentials for {len(services)} services[/green]")
        
    except Exception as e:
        console.print(f"[yellow]Warning: Could not reset all credentials: {e}[/yellow]")


def _reset_cache():
    """Reset cache directory."""
    settings = get_settings()
    
    if settings.cache_dir.exists():
        import shutil
        shutil.rmtree(settings.cache_dir)
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]Cache directory reset: {settings.cache_dir}[/green]")


@app.command()
def validate(
    fix_issues: bool = typer.Option(
        False, "--fix", "-f",
        help="Automatically fix common issues"
    )
):
    """
    Validate configuration and check for common issues.
    
    Performs comprehensive validation of all configuration settings
    and reports any issues found.
    """
    try:
        settings = get_settings()
        issues = []
        
        console.print(Panel.fit(
            "[bold blue]Configuration Validation[/bold blue]",
            style="blue"
        ))
        
        # Validate Proxmox configuration
        if not settings.proxmox.host:
            issues.append("❌ Proxmox host not configured")
        elif settings.proxmox.host == "192.168.1.50":
            issues.append("⚠️  Using default Proxmox host address")
        
        if settings.proxmox.port < 1 or settings.proxmox.port > 65535:
            issues.append("❌ Invalid Proxmox port number")
        
        if not settings.proxmox.verify_ssl and settings.is_production():
            issues.append("⚠️  SSL verification disabled in production environment")
        
        # Validate AI configuration
        if settings.enable_ai_generation and not settings.anthropic.api_key:
            issues.append("❌ AI generation enabled but no API key configured")
        
        # Validate directories
        for dir_name, directory in [
            ("config", settings.config_dir),
            ("data", settings.data_dir),
            ("cache", settings.cache_dir)
        ]:
            if not directory.exists():
                if fix_issues:
                    directory.mkdir(parents=True, exist_ok=True)
                    console.print(f"[green]✅ Created {dir_name} directory: {directory}[/green]")
                else:
                    issues.append(f"❌ {dir_name.title()} directory missing: {directory}")
            elif not os.access(directory, os.W_OK):
                issues.append(f"❌ {dir_name.title()} directory not writable: {directory}")
        
        # Validate logging configuration
        if settings.logging.file_path and not settings.logging.file_path.parent.exists():
            if fix_issues:
                settings.logging.file_path.parent.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]✅ Created log directory: {settings.logging.file_path.parent}[/green]")
            else:
                issues.append(f"❌ Log directory missing: {settings.logging.file_path.parent}")
        
        # Display results
        if not issues:
            console.print("\n[bold green]✅ All validation checks passed![/bold green]")
        else:
            console.print(f"\n[bold yellow]Found {len(issues)} issue(s):[/bold yellow]")
            for issue in issues:
                console.print(f"  {issue}")
            
            if not fix_issues:
                console.print("\n[dim]Run with --fix to automatically fix common issues.[/dim]")
        
    except Exception as e:
        logger.error("Validation failed", error=str(e))
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()