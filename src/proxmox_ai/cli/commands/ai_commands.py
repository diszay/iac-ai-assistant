"""
AI-powered automation commands for Proxmox AI Assistant.

Provides intelligent infrastructure automation using Claude AI for code generation,
configuration optimization, and automated deployment strategies.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
import structlog

from ...core.config import get_settings
from ...services.ai_service import AIService, AIServiceError
from ...api.proxmox_client import get_proxmox_client

logger = structlog.get_logger(__name__)
console = Console()

# Create AI command group
app = typer.Typer(
    name="ai",
    help="AI-powered automation and code generation",
    rich_markup_mode="rich"
)


@app.command()
def generate(
    resource_type: str = typer.Argument(
        ..., 
        help="Type of resource to generate (vm, terraform, ansible, docker)"
    ),
    description: str = typer.Argument(
        ...,
        help="Natural language description of what to create"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Save generated code to file"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t",
        help="Use specific template or style"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--batch", "-i/-b",
        help="Run in interactive mode for refinements"
    ),
    validate: bool = typer.Option(
        True, "--validate/--no-validate", "-v",
        help="Validate generated configurations"
    )
):
    """
    Generate infrastructure code using AI.
    
    Creates Terraform configurations, Ansible playbooks, VM configurations,
    or Docker compositions based on natural language descriptions.
    
    Examples:
      proxmox-ai ai generate vm "Ubuntu 22.04 web server with 4GB RAM"
      proxmox-ai ai generate terraform "3-tier web app with load balancer"
      proxmox-ai ai generate ansible "Deploy LAMP stack on 5 servers"
    """
    asyncio.run(_generate_code(resource_type, description, output_file, template, interactive, validate))


async def _generate_code(
    resource_type: str,
    description: str,
    output_file: Optional[Path],
    template: Optional[str],
    interactive: bool,
    validate: bool
):
    """Async implementation of AI code generation."""
    try:
        settings = get_settings()
        
        if not settings.enable_ai_generation:
            console.print("[red]AI generation is disabled. Enable it in configuration.[/red]")
            raise typer.Exit(1)
        
        if not settings.anthropic.api_key:
            console.print("[red]No Anthropic API key configured. Run 'proxmox-ai config setup'.[/red]")
            raise typer.Exit(1)
        
        console.print(Panel.fit(
            f"[bold blue]Generating {resource_type} configuration[/bold blue]\n"
            f"[cyan]Description: {description}[/cyan]",
            style="blue"
        ))
        
        ai_service = AIService()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating code with AI...", total=None)
            
            # Generate the code
            if resource_type.lower() == "vm":
                result = await ai_service.generate_vm_config(description, template)
            elif resource_type.lower() == "terraform":
                result = await ai_service.generate_terraform_config(description, template)
            elif resource_type.lower() == "ansible":
                result = await ai_service.generate_ansible_playbook(description, template)
            elif resource_type.lower() == "docker":
                result = await ai_service.generate_docker_compose(description, template)
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
            
            progress.update(task, completed=True)
        
        # Display generated code
        _display_generated_code(result, resource_type)
        
        # Interactive refinement
        if interactive:
            result = await _interactive_refinement(ai_service, result, resource_type)
        
        # Validation
        if validate:
            await _validate_generated_code(result, resource_type)
        
        # Save to file
        if output_file:
            _save_generated_code(result, output_file)
            console.print(f"[green]✅ Code saved to {output_file}[/green]")
        
        # Offer to apply/deploy
        if resource_type.lower() == "vm" and Confirm.ask("Create this VM now?"):
            await _apply_vm_config(result)
        
    except AIServiceError as e:
        console.print(f"[red]AI Service Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Code generation failed", error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _display_generated_code(result: Dict[str, Any], resource_type: str):
    """Display the generated code with syntax highlighting."""
    code = result.get('code', '')
    explanation = result.get('explanation', '')
    
    # Determine syntax highlighting language
    syntax_map = {
        'vm': 'json',
        'terraform': 'hcl',
        'ansible': 'yaml',
        'docker': 'yaml'
    }
    
    language = syntax_map.get(resource_type.lower(), 'text')
    
    # Display explanation
    if explanation:
        console.print(Panel(
            explanation,
            title="AI Explanation",
            style="cyan"
        ))
        console.print()
    
    # Display code with syntax highlighting
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(Panel(
        syntax,
        title=f"Generated {resource_type.title()} Configuration",
        style="green"
    ))


async def _interactive_refinement(ai_service: AIService, result: Dict[str, Any], resource_type: str) -> Dict[str, Any]:
    """Allow user to refine the generated code interactively."""
    console.print("\n[cyan]Interactive Refinement Mode[/cyan]")
    console.print("[dim]Enter refinement requests or 'done' to finish[/dim]")
    
    current_result = result
    
    while True:
        refinement = Prompt.ask("\n[bold]Refinement request (or 'done')")
        
        if refinement.lower() in ['done', 'exit', 'quit']:
            break
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Refining code...", total=None)
            
            try:
                # Apply refinement
                current_result = await ai_service.refine_generated_code(
                    current_result['code'],
                    refinement,
                    resource_type
                )
                
                progress.update(task, completed=True)
                
                # Display refined code
                console.print()
                _display_generated_code(current_result, resource_type)
                
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]Refinement failed: {e}[/red]")
    
    return current_result


async def _validate_generated_code(result: Dict[str, Any], resource_type: str):
    """Validate the generated code for syntax and best practices."""
    console.print("\n[cyan]Validating generated code...[/cyan]")
    
    code = result.get('code', '')
    issues = []
    
    try:
        if resource_type.lower() == "vm":
            issues = _validate_vm_config(code)
        elif resource_type.lower() == "terraform":
            issues = _validate_terraform_config(code)
        elif resource_type.lower() == "ansible":
            issues = _validate_ansible_playbook(code)
        elif resource_type.lower() == "docker":
            issues = _validate_docker_compose(code)
        
        if not issues:
            console.print("[green]✅ Validation passed - no issues found[/green]")
        else:
            console.print(f"[yellow]⚠️  Found {len(issues)} validation issue(s):[/yellow]")
            for issue in issues:
                console.print(f"  • {issue}")
    
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")


def _validate_vm_config(code: str) -> List[str]:
    """Validate VM configuration."""
    issues = []
    
    try:
        config = json.loads(code)
        
        # Check required fields
        required_fields = ['name', 'memory', 'cores']
        for field in required_fields:
            if field not in config:
                issues.append(f"Missing required field: {field}")
        
        # Check memory is reasonable
        if 'memory' in config:
            memory = config['memory']
            if memory < 512:
                issues.append("Memory too low (minimum 512MB recommended)")
            elif memory > 32768:
                issues.append("Memory very high (consider if necessary)")
        
        # Check core count
        if 'cores' in config:
            cores = config['cores']
            if cores < 1:
                issues.append("Invalid core count (minimum 1)")
            elif cores > 16:
                issues.append("High core count (consider resource availability)")
    
    except json.JSONDecodeError:
        issues.append("Invalid JSON format")
    
    return issues


def _validate_terraform_config(code: str) -> List[str]:
    """Validate Terraform configuration."""
    issues = []
    
    # Basic syntax checks
    if 'provider' not in code:
        issues.append("No provider configuration found")
    
    if 'resource' not in code:
        issues.append("No resources defined")
    
    # Check for hardcoded values
    if any(ip in code for ip in ['192.168.', '10.0.', '172.']):
        issues.append("Hardcoded IP addresses found - consider using variables")
    
    return issues


def _validate_ansible_playbook(code: str) -> List[str]:
    """Validate Ansible playbook."""
    issues = []
    
    try:
        import yaml
        playbook = yaml.safe_load(code)
        
        if not isinstance(playbook, list):
            issues.append("Playbook should be a list of plays")
        elif len(playbook) == 0:
            issues.append("Empty playbook")
        else:
            for i, play in enumerate(playbook):
                if 'hosts' not in play:
                    issues.append(f"Play {i+1}: Missing 'hosts' field")
                if 'tasks' not in play and 'roles' not in play:
                    issues.append(f"Play {i+1}: No tasks or roles defined")
    
    except yaml.YAMLError:
        issues.append("Invalid YAML format")
    
    return issues


def _validate_docker_compose(code: str) -> List[str]:
    """Validate Docker Compose configuration."""
    issues = []
    
    try:
        import yaml
        compose = yaml.safe_load(code)
        
        if 'version' not in compose:
            issues.append("No version specified")
        
        if 'services' not in compose:
            issues.append("No services defined")
        elif len(compose['services']) == 0:
            issues.append("No services in composition")
        
        # Check for exposed ports
        for service_name, service in compose.get('services', {}).items():
            if 'ports' in service:
                for port in service['ports']:
                    if isinstance(port, str) and ':' in port:
                        host_port = port.split(':')[0]
                        if host_port in ['22', '80', '443']:
                            issues.append(f"Service {service_name}: Consider security implications of exposing port {host_port}")
    
    except yaml.YAMLError:
        issues.append("Invalid YAML format")
    
    return issues


def _save_generated_code(result: Dict[str, Any], output_file: Path):
    """Save generated code to file."""
    code = result.get('code', '')
    
    # Create directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write code to file
    with open(output_file, 'w') as f:
        f.write(code)
    
    # Also save metadata if available
    if result.get('explanation'):
        from datetime import datetime
        metadata_file = output_file.with_suffix('.metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump({
                'explanation': result['explanation'],
                'generated_at': datetime.now().isoformat(),
                'ai_model': get_settings().anthropic.model
            }, f, indent=2)


async def _apply_vm_config(result: Dict[str, Any]):
    """Apply VM configuration to create actual VM."""
    try:
        config = json.loads(result['code'])
        
        # Get required parameters
        vmid = Prompt.ask("Enter VM ID", default="100")
        node = Prompt.ask("Enter target node", default="pve")
        
        try:
            vmid = int(vmid)
        except ValueError:
            console.print("[red]Invalid VM ID[/red]")
            return
        
        async with get_proxmox_client() as client:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating VM...", total=None)
                
                await client.create_vm(node, vmid, config)
                
                progress.update(task, completed=True)
            
            console.print(f"[green]✅ VM {vmid} created successfully![/green]")
            
            if Confirm.ask("Start VM now?"):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Starting VM...", total=None)
                    
                    await client.start_vm(node, vmid)
                    
                    progress.update(task, completed=True)
                
                console.print(f"[green]✅ VM {vmid} started successfully![/green]")
    
    except Exception as e:
        console.print(f"[red]Failed to apply VM configuration: {e}[/red]")


@app.command()
def optimize(
    target: str = typer.Argument(
        ...,
        help="What to optimize (vm, cluster, storage, network)"
    ),
    analysis_type: str = typer.Option(
        "performance", "--type", "-t",
        help="Type of optimization (performance, cost, security, resource)"
    ),
    output_format: str = typer.Option(
        "recommendations", "--format", "-f",
        help="Output format (recommendations, script, report)"
    )
):
    """
    Get AI-powered optimization recommendations.
    
    Analyzes your Proxmox infrastructure and provides intelligent
    recommendations for improvements.
    """
    asyncio.run(_run_optimization(target, analysis_type, output_format))


async def _run_optimization(target: str, analysis_type: str, output_format: str):
    """Run optimization analysis."""
    try:
        console.print(Panel.fit(
            f"[bold blue]AI Optimization Analysis[/bold blue]\n"
            f"[cyan]Target: {target}[/cyan]\n"
            f"[cyan]Type: {analysis_type}[/cyan]",
            style="blue"
        ))
        
        ai_service = AIService()
        
        # Gather current state
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing current infrastructure...", total=None)
            
            current_state = await _gather_infrastructure_state(target)
            
            progress.update(task, completed=True)
        
        # Get AI recommendations
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating optimization recommendations...", total=None)
            
            recommendations = await ai_service.generate_optimization_recommendations(
                current_state, target, analysis_type
            )
            
            progress.update(task, completed=True)
        
        # Display results
        _display_optimization_results(recommendations, output_format)
        
    except Exception as e:
        logger.error("Optimization analysis failed", error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


async def _gather_infrastructure_state(target: str) -> Dict[str, Any]:
    """Gather current infrastructure state for analysis."""
    state = {}
    
    try:
        async with get_proxmox_client() as client:
            # Get nodes
            nodes = await client.get_nodes()
            state['nodes'] = nodes
            
            # Get all VMs
            if target in ['vm', 'cluster']:
                vms = await client.get_vms()
                state['vms'] = vms
            
            # Get storage information
            if target in ['storage', 'cluster']:
                storages = await client.get_storages()
                state['storages'] = storages
            
            # Get detailed node information
            for node in nodes:
                node_info = await client.get_node_info(node['node'])
                node.update(node_info)
    
    except Exception as e:
        logger.warning("Failed to gather some infrastructure data", error=str(e))
    
    return state


def _display_optimization_results(recommendations: Dict[str, Any], output_format: str):
    """Display optimization recommendations."""
    if output_format == "report":
        _display_optimization_report(recommendations)
    elif output_format == "script":
        _display_optimization_script(recommendations)
    else:
        _display_optimization_recommendations(recommendations)


def _display_optimization_recommendations(recommendations: Dict[str, Any]):
    """Display recommendations in structured format."""
    console.print(Panel.fit(
        "[bold green]AI Optimization Recommendations[/bold green]",
        style="green"
    ))
    
    for category, items in recommendations.items():
        if isinstance(items, list) and items:
            table = Table(title=f"{category.title()} Recommendations", show_header=True)
            table.add_column("Priority", style="bold")
            table.add_column("Recommendation", style="cyan")
            table.add_column("Impact", style="green")
            
            for item in items:
                table.add_row(
                    item.get('priority', 'Medium'),
                    item.get('recommendation', ''),
                    item.get('impact', '')
                )
            
            console.print(table)
            console.print()


def _display_optimization_report(recommendations: Dict[str, Any]):
    """Display detailed optimization report."""
    console.print(Syntax(
        recommendations.get('report', 'No report generated'),
        'markdown',
        theme='monokai'
    ))


def _display_optimization_script(recommendations: Dict[str, Any]):
    """Display optimization as executable script."""
    console.print(Syntax(
        recommendations.get('script', 'No script generated'),
        'bash',
        theme='monokai',
        line_numbers=True
    ))


@app.command()
def explain(
    config_file: Path = typer.Argument(
        ...,
        help="Configuration file to explain",
        exists=True
    ),
    detail_level: str = typer.Option(
        "detailed", "--detail", "-d",
        help="Explanation detail level (brief, detailed, comprehensive)"
    )
):
    """
    Get AI explanation of configuration files.
    
    Analyzes and explains Terraform, Ansible, Docker, or VM configuration
    files in plain English.
    """
    asyncio.run(_explain_config(config_file, detail_level))


async def _explain_config(config_file: Path, detail_level: str):
    """Get AI explanation of configuration file."""
    try:
        console.print(Panel.fit(
            f"[bold blue]AI Configuration Analysis[/bold blue]\n"
            f"[cyan]File: {config_file}[/cyan]",
            style="blue"
        ))
        
        # Read the file
        with open(config_file, 'r') as f:
            content = f.read()
        
        ai_service = AIService()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing configuration...", total=None)
            
            explanation = await ai_service.explain_configuration(content, config_file.suffix, detail_level)
            
            progress.update(task, completed=True)
        
        # Display explanation
        console.print(Panel(
            explanation,
            title="AI Explanation",
            style="green"
        ))
        
    except Exception as e:
        logger.error("Configuration explanation failed", error=str(e))
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()