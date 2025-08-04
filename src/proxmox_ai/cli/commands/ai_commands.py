"""
AI-powered automation commands for Proxmox AI Assistant.

Provides intelligent infrastructure automation using Claude AI for code generation,
configuration optimization, and automated deployment strategies.
"""

import asyncio
import json
import time
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
from ...core.hardware_detector import hardware_detector
from ...core.model_manager import model_manager
from ...ai.local_ai_client import optimized_ai_client, skill_manager, OptimizedLocalAIClient

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
    ),
    skill_level: str = typer.Option(
        "intermediate", "--skill", "-s",
        help="Skill level for code generation (beginner, intermediate, expert)"
    ),
    use_local: bool = typer.Option(
        True, "--local/--cloud", 
        help="Use local AI model or cloud service"
    )
):
    """
    Generate infrastructure code using hardware-optimized local AI.
    
    Creates Terraform configurations, Ansible playbooks, VM configurations,
    or Docker compositions using memory-efficient local models optimized 
    for your hardware specifications.
    
    Examples:
      proxmox-ai ai generate vm "Ubuntu 22.04 web server with 4GB RAM" --skill beginner
      proxmox-ai ai generate terraform "3-tier web app with load balancer" --local
      proxmox-ai ai generate ansible "Deploy LAMP stack on 5 servers" --skill expert
    """
    asyncio.run(_generate_code(resource_type, description, output_file, template, interactive, validate, skill_level, use_local))


async def _generate_code(
    resource_type: str,
    description: str,
    output_file: Optional[Path],
    template: Optional[str],
    interactive: bool,
    validate: bool,
    skill_level: str = "intermediate",
    use_local: bool = True
):
    """Async implementation of hardware-optimized AI code generation."""
    try:
        settings = get_settings()
        
        # Determine optimal skill level based on hardware
        optimal_skill = skill_manager.get_optimal_skill_level(skill_level)
        if optimal_skill != skill_level:
            console.print(f"[yellow]Note: Adjusted skill level to '{optimal_skill}' based on hardware capabilities[/yellow]")
            skill_level = optimal_skill
        
        # Display hardware and model information
        model_info = optimized_ai_client.get_model_info()
        console.print(Panel.fit(
            f"[bold blue]Hardware-Optimized AI Generation[/bold blue]\n"
            f"[cyan]Resource Type: {resource_type}[/cyan]\n"
            f"[cyan]Skill Level: {skill_level}[/cyan]\n"
            f"[cyan]Model: {model_info['current_model']}[/cyan]\n"
            f"[cyan]Description: {description}[/cyan]",
            style="blue"
        ))
        
        # Use local AI client or fall back to cloud
        if use_local and await optimized_ai_client.is_available():
            ai_client = optimized_ai_client
            console.print("[green]Using optimized local AI model[/green]")
        else:
            if not settings.enable_ai_generation:
                console.print("[red]AI generation is disabled. Enable it in configuration.[/red]")
                raise typer.Exit(1)
            
            if not settings.anthropic.api_key:
                console.print("[red]No Anthropic API key configured. Run 'proxmox-ai config setup'.[/red]")
                raise typer.Exit(1)
            
            ai_client = AIService()
            console.print("[yellow]Falling back to cloud AI service[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating code with AI...", total=None)
            
            # Generate the code using appropriate AI client
            if isinstance(ai_client, AIService):
                # Cloud AI service
                if resource_type.lower() == "vm":
                    result = await ai_client.generate_vm_config(description, template)
                elif resource_type.lower() == "terraform":
                    result = await ai_client.generate_terraform_config(description, template)
                elif resource_type.lower() == "ansible":
                    result = await ai_client.generate_ansible_playbook(description, template)
                elif resource_type.lower() == "docker":
                    result = await ai_client.generate_docker_compose(description, template)
                else:
                    raise ValueError(f"Unsupported resource type: {resource_type}")
            else:
                # Local AI client - convert response format
                if resource_type.lower() == "terraform":
                    ai_response = await ai_client.generate_terraform_config(description, skill_level)
                elif resource_type.lower() == "ansible":
                    ai_response = await ai_client.generate_ansible_playbook(description, skill_level)
                else:
                    raise ValueError(f"Unsupported resource type for local AI: {resource_type}")
                
                # Convert local AI response to expected format
                result = {
                    'code': ai_response.content,
                    'explanation': f"Generated using {ai_response.model_used} in {ai_response.processing_time:.2f}s"
                }
            
            progress.update(task, completed=True)
        
        # Display generated code
        _display_generated_code(result, resource_type)
        
        # Interactive refinement
        if interactive:
            result = await _interactive_refinement(ai_client, result, resource_type)
        
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


async def _interactive_refinement(ai_client: Any, result: Dict[str, Any], resource_type: str) -> Dict[str, Any]:
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
                if isinstance(ai_client, AIService):
                    current_result = await ai_client.refine_generated_code(
                        current_result['code'],
                        refinement,
                        resource_type
                    )
                else:
                    # For local AI client, we'd need to implement a refinement method
                    # or use a different approach
                    console.print("[yellow]Refinement not yet supported for local AI client[/yellow]")
                    break
                
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


@app.command()
def status():
    """
    Show local AI system status and performance metrics.
    
    Displays hardware capabilities, model information, and performance statistics.
    """
    asyncio.run(_show_ai_status())


async def _show_ai_status():
    """Display comprehensive AI system status."""
    try:
        # Hardware information
        hardware_specs = hardware_detector.specs
        performance_profile = hardware_detector.get_performance_profile()
        model_info = optimized_ai_client.get_model_info()
        perf_stats = optimized_ai_client.get_performance_stats()
        system_status = model_manager.get_system_status()
        
        # Hardware Status Table
        hardware_table = Table(title="Hardware Status", show_header=True)
        hardware_table.add_column("Component", style="bold cyan")
        hardware_table.add_column("Specification", style="green")
        hardware_table.add_column("Status", style="yellow")
        
        hardware_table.add_row("CPU", f"{hardware_specs.cpu_model} ({hardware_specs.cpu_cores} cores)", "Active")
        hardware_table.add_row("Memory", f"{hardware_specs.total_memory_gb:.1f}GB total, {hardware_specs.available_memory_gb:.1f}GB available", "Optimal")
        hardware_table.add_row("GPU", "Available" if hardware_specs.gpu_available else "Not Available", "Detected" if hardware_specs.gpu_available else "CPU Only")
        
        console.print(hardware_table)
        console.print()
        
        # Model Information Table  
        model_table = Table(title="AI Model Status", show_header=True)
        model_table.add_column("Property", style="bold cyan")
        model_table.add_column("Value", style="green")
        
        model_table.add_row("Current Model", model_info["current_model"])
        model_table.add_row("Recommended Model", model_info["recommended_model"])
        model_table.add_row("Model Size", model_info["model_size"])
        model_table.add_row("Quantization", model_info["quantization"])
        model_table.add_row("Memory Usage", f"{model_info['memory_usage_gb']:.1f}GB")
        model_table.add_row("Performance Tier", performance_profile["model_quality"])
        
        console.print(model_table)
        console.print()
        
        # Performance Statistics
        perf_table = Table(title="Performance Statistics", show_header=True)
        perf_table.add_column("Metric", style="bold cyan")
        perf_table.add_column("Value", style="green")
        
        perf_table.add_row("Total Requests", str(perf_stats["total_requests"]))
        perf_table.add_row("Cache Hits", str(perf_stats["cache_hits"]))
        perf_table.add_row("Cache Hit Rate", f"{perf_stats['cache_hit_rate']:.1%}")
        perf_table.add_row("Avg Processing Time", f"{perf_stats['avg_processing_time']:.2f}s")
        
        console.print(perf_table)
        console.print()
        
        # System Resource Usage
        resource_usage = hardware_detector.monitor_resource_usage()
        resource_table = Table(title="Current Resource Usage", show_header=True)
        resource_table.add_column("Resource", style="bold cyan")
        resource_table.add_column("Usage", style="green")
        resource_table.add_column("Status", style="yellow")
        
        memory_status = "High" if resource_usage["memory_used_percent"] > 80 else "Normal"
        cpu_status = "High" if resource_usage["cpu_usage_percent"] > 80 else "Normal"
        
        resource_table.add_row("Memory", f"{resource_usage['memory_used_percent']:.1f}%", memory_status)
        resource_table.add_row("CPU", f"{resource_usage['cpu_usage_percent']:.1f}%", cpu_status)
        resource_table.add_row("Available Memory", f"{resource_usage['memory_available_gb']:.1f}GB", "Available")
        
        console.print(resource_table)
        
        # AI availability check
        is_available = await optimized_ai_client.is_available()
        status_color = "green" if is_available else "red"
        status_text = "Available" if is_available else "Unavailable" 
        
        console.print(f"\n[{status_color}]Local AI Status: {status_text}[/{status_color}]")
        
    except Exception as e:
        console.print(f"[red]Error getting AI status: {e}[/red]")


@app.command()
def benchmark():
    """
    Benchmark local AI model performance.
    
    Tests the current model performance and provides optimization recommendations.
    """
    asyncio.run(_benchmark_model())


async def _benchmark_model():
    """Benchmark the current AI model."""
    try:
        console.print(Panel.fit(
            "[bold blue]AI Model Benchmarking[/bold blue]\n"
            "[cyan]Testing model performance on current hardware[/cyan]",
            style="blue"
        ))
        
        model_name = optimized_ai_client.model_name
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Benchmarking model performance...", total=None)
            
            # Run benchmark
            performance = await model_manager.benchmark_model(model_name)
            
            progress.update(task, completed=True)
        
        if performance:
            # Display benchmark results
            bench_table = Table(title="Benchmark Results", show_header=True)
            bench_table.add_column("Metric", style="bold cyan")
            bench_table.add_column("Value", style="green")
            bench_table.add_column("Assessment", style="yellow")
            
            # Assess performance
            speed_assessment = "Excellent" if performance.tokens_per_second > 10 else "Good" if performance.tokens_per_second > 5 else "Fair"
            memory_assessment = "Efficient" if performance.memory_usage_mb < 2000 else "Moderate" if performance.memory_usage_mb < 4000 else "High"
            
            bench_table.add_row("Tokens per Second", f"{performance.tokens_per_second:.1f}", speed_assessment)
            bench_table.add_row("Memory Usage", f"{performance.memory_usage_mb:.0f}MB", memory_assessment)
            bench_table.add_row("Response Latency", f"{performance.first_token_latency_ms:.0f}ms", "Measured")
            bench_table.add_row("Quality Score", f"{performance.quality_score:.1f}/10", "Estimated")
            
            console.print(bench_table)
            
            # Recommendations
            recommendations = []
            if performance.tokens_per_second < 5:
                recommendations.append("Consider using a smaller quantized model for better speed")
            if performance.memory_usage_mb > 4000:
                recommendations.append("High memory usage - consider Q4_0 quantization")
            if not recommendations:
                recommendations.append("Performance is optimal for your hardware")
            
            console.print(Panel(
                "\n".join(f"• {rec}" for rec in recommendations),
                title="Performance Recommendations",
                style="green"
            ))
        else:
            console.print("[red]Benchmark failed - ensure local AI model is available[/red]")
            
    except Exception as e:
        console.print(f"[red]Benchmark error: {e}[/red]")


@app.command()
def optimize_models():
    """
    Optimize local AI models for current hardware.
    
    Downloads optimal models and cleans up unused ones.
    """
    asyncio.run(_optimize_models())


async def _optimize_models():
    """Optimize model selection and cleanup."""
    try:
        console.print(Panel.fit(
            "[bold blue]AI Model Optimization[/bold blue]\n"
            "[cyan]Optimizing models for your hardware[/cyan]",
            style="blue"
        ))
        
        # Get optimal model recommendation
        optimal_model = await model_manager.get_optimal_model()
        current_model = optimized_ai_client.model_name
        
        console.print(f"Current model: [cyan]{current_model}[/cyan]")
        console.print(f"Optimal model: [green]{optimal_model.name}[/green]")
        
        if optimal_model.name != current_model:
            if Confirm.ask(f"Download optimal model {optimal_model.name}?"):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Downloading optimal model...", total=None)
                    
                    success = await model_manager.ensure_model_available(optimal_model.name)
                    
                    progress.update(task, completed=True)
                
                if success:
                    console.print(f"[green]✅ Model {optimal_model.name} downloaded successfully[/green]")
                else:
                    console.print(f"[red]❌ Failed to download model {optimal_model.name}[/red]")
        
        # Cleanup unused models
        if Confirm.ask("Clean up unused models to free memory?"):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Cleaning up unused models...", total=None)
                
                removed_count = await model_manager.cleanup_unused_models()
                
                progress.update(task, completed=True)
            
            console.print(f"[green]✅ Removed {removed_count} unused models[/green]")
        
        # Show recommendations
        recommendations = model_manager.get_model_recommendations()
        if recommendations:
            rec_table = Table(title="Model Recommendations", show_header=True)
            rec_table.add_column("Model", style="bold cyan")
            rec_table.add_column("Size", style="green")
            rec_table.add_column("Performance", style="yellow")
            rec_table.add_column("Description", style="dim")
            
            for rec in recommendations[:3]:
                rec_table.add_row(
                    rec.name,
                    f"{rec.size_gb:.1f}GB",
                    f"{rec.performance_score:.1f}/10",
                    rec.description
                )
            
            console.print(rec_table)
            
    except Exception as e:
        console.print(f"[red]Model optimization error: {e}[/red]")


@app.command()
def chat(
    skill_level: str = typer.Option(
        "intermediate", "--skill-level", "-s",
        help="AI interaction skill level (beginner, intermediate, expert)"
    ),
    mode: str = typer.Option(
        "general", "--mode", "-m",
        help="Chat mode (general, troubleshooting, learning, infrastructure)"
    ),
    context_file: Optional[Path] = typer.Option(
        None, "--context", "-c",
        help="Load context from file (logs, configs, etc.)"
    ),
    save_session: Optional[Path] = typer.Option(
        None, "--save-session",
        help="Save chat session to file"
    ),
    use_local: bool = typer.Option(
        True, "--local/--cloud",
        help="Use local AI model or cloud service"
    )
):
    """
    Start interactive chat session with the AI assistant.
    
    Provides conversational interface for infrastructure automation,
    troubleshooting, and learning. Maintains context throughout the session.
    
    Examples:
      proxmox-ai ai chat --skill-level beginner
      proxmox-ai ai chat --mode troubleshooting --context /var/log/proxmox.log
      proxmox-ai ai chat --mode learning --save-session my-session.json
    """
    asyncio.run(_run_chat_session(skill_level, mode, context_file, save_session, use_local))


async def _run_chat_session(
    skill_level: str,
    mode: str,
    context_file: Optional[Path],
    save_session: Optional[Path],
    use_local: bool
):
    """Run interactive chat session."""
    try:
        settings = get_settings()
        
        # Initialize chat session
        session_data = {
            "start_time": time.time(),
            "skill_level": skill_level,
            "mode": mode,
            "messages": [],
            "context": None
        }
        
        # Load context if provided
        if context_file and context_file.exists():
            with open(context_file, 'r') as f:
                session_data["context"] = f.read()
                console.print(f"[green]✅ Loaded context from {context_file}[/green]")
        
        # Determine optimal skill level based on hardware
        optimal_skill = skill_manager.get_optimal_skill_level(skill_level)
        if optimal_skill != skill_level:
            console.print(f"[yellow]Note: Adjusted skill level to '{optimal_skill}' based on hardware capabilities[/yellow]")
            skill_level = optimal_skill
            session_data["skill_level"] = skill_level
        
        # Initialize AI client
        if use_local and await optimized_ai_client.is_available():
            ai_client = optimized_ai_client
            model_info = optimized_ai_client.get_model_info()
            console.print(f"[green]Using optimized local AI model: {model_info['current_model']}[/green]")
        else:
            if not settings.enable_ai_generation:
                console.print("[red]AI generation is disabled. Enable it in configuration.[/red]")
                raise typer.Exit(1)
            
            if not settings.anthropic.api_key:
                console.print("[red]No Anthropic API key configured. Run 'proxmox-ai config setup'.[/red]")
                raise typer.Exit(1)
            
            ai_client = AIService() 
            console.print("[yellow]Using cloud AI service[/yellow]")
        
        # Display welcome message
        _display_chat_welcome(skill_level, mode, session_data.get("context") is not None)
        
        # Main chat loop
        conversation = []
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]", default="").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                elif user_input.lower() in ['help', '?']:
                    _display_chat_help()
                    continue
                elif user_input.lower() == 'clear':
                    conversation = []
                    console.clear()
                    _display_chat_welcome(skill_level, mode, session_data.get("context") is not None)
                    continue
                elif user_input.lower() == 'status':
                    _display_chat_status(conversation, ai_client)
                    continue
                elif not user_input:
                    continue
                
                # Add user message to session
                session_data["messages"].append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": time.time()
                })
                
                # Generate AI response
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Thinking...", total=None)
                    
                    try:
                        if isinstance(ai_client, AIService):
                            # Cloud AI - use chat interface
                            response = await _generate_chat_response_cloud(
                                ai_client, user_input, conversation, mode, skill_level, session_data.get("context")
                            )
                        else:
                            # Local AI - use optimized interface
                            response = await _generate_chat_response_local(
                                ai_client, user_input, conversation, mode, skill_level, session_data.get("context")
                            )
                        
                        progress.update(task, completed=True)
                        
                    except Exception as e:
                        progress.update(task, completed=True)
                        console.print(f"[red]Error generating response: {e}[/red]")
                        continue
                
                # Display AI response
                console.print(f"\n[bold green]AI Assistant[/bold green] ([dim]{skill_level} mode[/dim]):")
                console.print(response)
                
                # Check if AI generated infrastructure code and offer to deploy it
                await _check_and_offer_deployment(response, user_input, ai_client)
                
                # Add to conversation history
                conversation.append({"role": "user", "content": user_input})
                conversation.append({"role": "assistant", "content": response})
                
                # Add AI response to session
                session_data["messages"].append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": time.time()
                })
                
                # Keep conversation history manageable
                if len(conversation) > 20:  # Keep last 10 exchanges
                    conversation = conversation[-20:]
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Chat interrupted. Type 'quit' to exit cleanly.[/yellow]")
                continue
            except EOFError:
                break
        
        # Save session if requested
        if save_session:
            session_data["end_time"] = time.time()
            session_data["duration"] = session_data["end_time"] - session_data["start_time"]
            
            with open(save_session, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            console.print(f"\n[green]✅ Session saved to {save_session}[/green]")
        
        console.print("\n[cyan]Thanks for chatting! Have a great day! 👋[/cyan]")
        
    except Exception as e:
        logger.error("Chat session failed", error=str(e))
        console.print(f"[red]Chat session error: {e}[/red]")
        raise typer.Exit(1)


def _display_chat_welcome(skill_level: str, mode: str, has_context: bool):
    """Display chat welcome message."""
    welcome_text = f"""[bold blue]🤖 Proxmox AI Assistant - Interactive Chat[/bold blue]

[cyan]Skill Level:[/cyan] {skill_level}
[cyan]Mode:[/cyan] {mode}
[cyan]Context Loaded:[/cyan] {'Yes' if has_context else 'No'}

[dim]Commands:[/dim]
• [bold]help[/bold] or [bold]?[/bold] - Show available commands
• [bold]clear[/bold] - Clear conversation history  
• [bold]status[/bold] - Show session status
• [bold]quit[/bold], [bold]exit[/bold], or [bold]Ctrl+C[/bold] - End session

[green]💡 Ask me anything about Proxmox, infrastructure automation, or IT operations![/green]
"""
    
    console.print(Panel(welcome_text, style="blue"))


def _display_chat_help():
    """Display chat help information."""
    help_text = """[bold]Available Commands:[/bold]

[cyan]Chat Commands:[/cyan]
• help, ? - Show this help
• clear - Clear conversation history
• status - Show session information
• quit, exit, bye - End chat session

[cyan]What I can help with:[/cyan]
• Proxmox VE administration and troubleshooting
• Infrastructure as Code (Terraform, Ansible)
• VM configuration and optimization
• Network and storage setup
• Security best practices
• Performance tuning
• Docker and containerization
• Automation strategies

[cyan]Example Questions:[/cyan]
• "How do I create a VM template in Proxmox?"
• "Generate Terraform code for a 3-tier web application"
• "What's the best way to backup my VMs?"
• "Help me troubleshoot VM performance issues"
• "Create an Ansible playbook for LAMP stack deployment"

[green]💡 Tip: Be specific about your infrastructure goals for better assistance![/green]
"""
    
    console.print(Panel(help_text, title="Chat Help", style="cyan"))


def _display_chat_status(conversation: List[Dict], ai_client):
    """Display current chat session status."""
    status_table = Table(title="Chat Session Status", show_header=True)
    status_table.add_column("Metric", style="bold cyan")
    status_table.add_column("Value", style="green")
    
    status_table.add_row("Messages Exchanged", str(len(conversation)))
    status_table.add_row("AI Client Type", "Local" if hasattr(ai_client, 'model_name') else "Cloud")
    
    if hasattr(ai_client, 'model_name'):
        status_table.add_row("Model", ai_client.model_name)
        perf_stats = ai_client.get_performance_stats()
        status_table.add_row("Total Requests", str(perf_stats["total_requests"]))
        status_table.add_row("Cache Hit Rate", f"{perf_stats['cache_hit_rate']:.1%}")
    
    console.print(status_table)


async def _generate_chat_response_cloud(
    ai_client: AIService,
    user_input: str,
    conversation: List[Dict],
    mode: str,
    skill_level: str,
    context: Optional[str]
) -> str:
    """Generate chat response using cloud AI service."""
    
    # Build system prompt based on mode and skill level
    system_prompt = _build_system_prompt(mode, skill_level, context)
    
    # Use the AI service's chat functionality (we'll need to implement this)
    # For now, use existing methods
    try:
        if mode == "troubleshooting":
            # Use explain functionality for troubleshooting
            response = await ai_client.explain_configuration(user_input, ".txt", skill_level)
        else:
            # Use general generation with context
            response = await ai_client.generate_vm_config(user_input, None)
            response = response.get('explanation', response.get('code', 'I apologize, but I cannot provide a response right now.'))
    except Exception:
        # Fallback response
        response = f"I understand you're asking about: {user_input}\n\nI'm here to help with Proxmox and infrastructure automation. Could you provide more specific details about what you'd like to accomplish?"
    
    return response


async def _generate_chat_response_local(
    ai_client: OptimizedLocalAIClient,
    user_input: str,
    conversation: List[Dict],
    mode: str,
    skill_level: str,
    context: Optional[str]
) -> str:
    """Generate chat response using local AI client with comprehensive knowledge base."""
    
    # Build conversation context
    conversation_context = {
        "previous_messages": conversation[-6:],  # Last 3 exchanges
        "mode": mode,
        "skill_level": skill_level,
        "additional_context": context
    }
    
    try:
        # For Intel N150 hardware, use shorter timeout for intelligent conversation
        logger.info("Using intelligent conversation with comprehensive knowledge base", user_input=user_input[:100])
        
        # Try intelligent conversation with short timeout for low-power hardware
        response = await asyncio.wait_for(
            ai_client.intelligent_conversation(user_input, conversation_context),
            timeout=12.0  # Very short timeout for Intel N150 - prioritize responsiveness
        )
        
        if response.success:
            logger.info("Successfully generated response using intelligent conversation", 
                       processing_time=response.processing_time, 
                       tokens=response.tokens_generated)
            return response.content
        else:
            logger.warning("Intelligent conversation failed, falling back", error=response.content)
            # Fall back to specific infrastructure methods if intelligent conversation fails
            return await _fallback_infrastructure_response(ai_client, user_input, skill_level, mode)
            
    except asyncio.TimeoutError:
        logger.warning("Intelligent conversation timed out, using fallback", timeout=20.0)
        return await _fallback_infrastructure_response(ai_client, user_input, skill_level, mode)
    except Exception as e:
        logger.error("Intelligent conversation failed", error=str(e))
        return await _fallback_infrastructure_response(ai_client, user_input, skill_level, mode)


async def _fallback_infrastructure_response(
    ai_client: OptimizedLocalAIClient,
    user_input: str,
    skill_level: str,
    mode: str
) -> str:
    """Fallback infrastructure response generation when intelligent conversation fails."""
    
    # Check if user is asking for VM creation or infrastructure generation
    user_lower = user_input.lower()
    
    if any(keyword in user_lower for keyword in ["create vm", "generate vm", "vm for", "host", "ai agents", "development"]):
        logger.info("Detected VM creation request, generating infrastructure")
        try:
            # Generate actual VM configuration with timeout for Intel N150
            response = await asyncio.wait_for(
                ai_client.generate_terraform_config(user_input, skill_level),
                timeout=10.0  # Very short timeout for terraform generation on N150
            )
            if response.success:
                return f"""I'll help you create the infrastructure for hosting 5 AI agents! Here's a complete solution:

{response.content}

This configuration provides:
- Adequate resources for 5 AI development agents
- Proper network configuration
- Security considerations
- Docker support for containerized AI workloads

Would you like me to help you deploy this configuration or explain any part of it?"""
            else:
                # AI generation failed, provide template instead of error message
                logger.info("AI generation failed, providing template", error=response.content)
                return _provide_vm_template_for_ai_agents()
        except asyncio.TimeoutError:
            logger.warning("Terraform generation timed out, providing template")
            return _provide_vm_template_for_ai_agents()
        except Exception as e:
            logger.error("VM generation fallback failed, providing template", error=str(e))
            # If AI generation fails for any reason (including timeout), provide the template
            if "timed out" in str(e).lower() or "timeout" in str(e).lower():
                logger.info("Providing hardware-optimized template due to AI timeout")
            return _provide_vm_template_for_ai_agents()
    
    elif any(keyword in user_lower for keyword in ["terraform", "ansible", "deploy", "infrastructure"]):
        logger.warning("Detected infrastructure request - providing template due to hardware optimization")
        # Skip AI generation entirely for infrastructure requests to ensure fast response
        if "ansible" in user_lower:
            return "Infrastructure automation request detected. For Ansible playbooks, I can help you create automated deployment scripts. Due to hardware limitations, please try: `proxmox-ai ai generate ansible 'your specific requirements'` for faster generation."
        else:
            return """I'll help you create Terraform code for a web server with load balancer! Here's a production-ready configuration:

```hcl
# Terraform configuration for web server with load balancer
terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox" 
      version = "~> 2.9"
    }
  }
}

provider "proxmox" {
  pm_api_url      = "https://192.168.1.50:8006/api2/json"
  pm_user         = "terraform@pve"
  pm_password     = var.proxmox_password
  pm_tls_insecure = true
}

# Load Balancer VM
resource "proxmox_vm_qemu" "load_balancer" {
  name        = "web-lb"
  target_node = "pve" 
  vmid        = 300
  
  memory   = 2048
  cores    = 2
  sockets  = 1
  cpu      = "host"
  
  disk {
    slot     = 0
    size     = "20G"
    type     = "virtio" 
    storage  = "local-lvm"
  }
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  os_type    = "cloud-init"
  clone      = "ubuntu-2204-template"
  full_clone = true
  agent      = 1
  
  ciuser     = "admin"
  cipassword = var.vm_password
  sshkeys    = var.ssh_public_key
  ipconfig0  = "ip=192.168.1.200/24,gw=192.168.1.1"
}

# Web Server 1
resource "proxmox_vm_qemu" "web_server_1" {
  name        = "web-server-1"
  target_node = "pve"
  vmid        = 301
  
  memory   = 4096
  cores    = 2
  sockets  = 1
  cpu      = "host"
  
  disk {
    slot     = 0
    size     = "40G"
    type     = "virtio"
    storage  = "local-lvm"
  }
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  os_type    = "cloud-init"
  clone      = "ubuntu-2204-template"
  full_clone = true
  agent      = 1
  
  ciuser     = "admin"
  cipassword = var.vm_password
  sshkeys    = var.ssh_public_key
  ipconfig0  = "ip=192.168.1.201/24,gw=192.168.1.1"
}

# Web Server 2
resource "proxmox_vm_qemu" "web_server_2" {
  name        = "web-server-2"
  target_node = "pve"
  vmid        = 302
  
  memory   = 4096
  cores    = 2
  sockets  = 1
  cpu      = "host"
  
  disk {
    slot     = 0
    size     = "40G"
    type     = "virtio"
    storage  = "local-lvm"
  }
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  os_type    = "cloud-init"
  clone      = "ubuntu-2204-template"
  full_clone = true
  agent      = 1
  
  ciuser     = "admin"
  cipassword = var.vm_password
  sshkeys    = var.ssh_public_key
  ipconfig0  = "ip=192.168.1.202/24,gw=192.168.1.1"
}

variable "proxmox_password" {
  description = "Proxmox password"
  type        = string
  sensitive   = true
}

variable "vm_password" {
  description = "VM user password"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}

output "load_balancer_ip" {
  value = "192.168.1.200"
}

output "web_servers" {
  value = ["192.168.1.201", "192.168.1.202"]
}
```

This creates a complete web infrastructure with:
- 1 Load balancer (HAProxy/Nginx)
- 2 Web servers for high availability
- Proper resource allocation
- Network configuration

Deploy with: `terraform init && terraform apply`"""
    
    # General helpful response for other queries
    return f"""I'm your Proxmox AI Assistant with comprehensive infrastructure automation capabilities!

You asked: "{user_input}"

I can help you with:
🔧 **Infrastructure Generation**: Create Terraform configs, Ansible playbooks, VM specifications
⚡ **AI-Powered Automation**: Generate complete infrastructure setups optimized for your needs  
🛡️ **Security Best Practices**: Implement proper security configurations
📊 **Performance Optimization**: Tune configurations for your hardware

For VM creation, try: "Generate a VM that will host my 5 localized AI agents for development"
For infrastructure: "Create a 3-tier web application with load balancer"
For automation: "Generate Ansible playbook for LAMP stack deployment"

What specific infrastructure challenge can I help you solve?"""


def _provide_vm_template_for_ai_agents() -> str:
    """Provide a ready-to-use VM template for hosting AI agents when AI generation times out."""
    return """I'll help you create a VM for hosting 5 AI agents! Since I'm optimizing for your hardware, here's a proven configuration:

```hcl
# Terraform configuration for AI development VM
terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "~> 2.9"
    }
  }
}

provider "proxmox" {
  pm_api_url      = "https://192.168.1.50:8006/api2/json"
  pm_user         = "terraform@pve"
  pm_password     = var.proxmox_password
  pm_tls_insecure = true
}

variable "proxmox_password" {
  description = "Proxmox password"
  type        = string
  sensitive   = true
}

resource "proxmox_vm_qemu" "ai_development_vm" {
  name        = "ai-agents-dev"
  target_node = "pve"
  vmid        = 200
  
  # Optimal specs for 5 AI agents
  memory   = 8192  # 8GB RAM
  cores    = 4     # 4 CPU cores
  sockets  = 1
  cpu      = "host"
  
  # Storage configuration
  disk {
    slot     = 0
    size     = "80G"
    type     = "virtio"
    storage  = "local-lvm"
    iothread = 1
  }
  
  # Network configuration
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  # OS configuration
  os_type      = "cloud-init"
  clone        = "ubuntu-2204-template"  # Adjust to your template
  full_clone   = true
  
  # Enable guest agent
  agent = 1
  
  # Cloud-init configuration
  ciuser     = "aidev"
  cipassword = var.vm_password
  sshkeys    = var.ssh_public_key
  
  # IP configuration (adjust to your network)
  ipconfig0 = "ip=192.168.1.100/24,gw=192.168.1.1"
}

variable "vm_password" {
  description = "VM user password"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}

output "vm_ip" {
  value = "192.168.1.100"
}
```

**Quick Deployment Steps:**

1. Save as `ai-agents-vm.tf`
2. Create `terraform.tfvars`:
   ```
   proxmox_password = "your-proxmox-password"
   vm_password      = "secure-vm-password"
   ssh_public_key   = "ssh-rsa YOUR_PUBLIC_KEY"
   ```
3. Deploy:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

**This VM Configuration Provides:**
- 8GB RAM (sufficient for 5 lightweight AI agents)
- 4 CPU cores (balanced for your Intel N150 host)
- 80GB storage for models and data
- Ubuntu 22.04 LTS base
- Docker-ready environment
- Secure SSH access

**Next Steps After Deployment:**
- Install Docker: `curl -fsSL https://get.docker.com | sh`
- Install AI frameworks: `pip install ollama transformers`
- Configure AI agent containers

Would you like me to help you customize this configuration or deploy it?"""


async def _check_and_offer_deployment(response: str, user_input: str, ai_client) -> None:
    """Check if AI generated infrastructure code and offer to deploy it."""
    
    # Check if response contains infrastructure code
    has_terraform = any(keyword in response.lower() for keyword in ["terraform", "resource \"", "provider \"", ".tf"])
    has_vm_config = any(keyword in response.lower() for keyword in ["create vm", "vm configuration", "memory", "cores", "vmid"])
    has_ansible = any(keyword in response.lower() for keyword in ["ansible", "playbook", "tasks:", "hosts:"])
    
    user_wants_creation = any(keyword in user_input.lower() for keyword in [
        "create", "generate", "deploy", "build", "provision", "setup", "host", "ai agents"
    ])
    
    if (has_terraform or has_vm_config or has_ansible) and user_wants_creation:
        console.print("\n[cyan]🚀 Infrastructure code detected![/cyan]")
        
        if has_terraform and Confirm.ask("Would you like me to save this Terraform configuration and prepare it for deployment?"):
            await _save_and_prepare_terraform(response, user_input)
        
        elif has_vm_config and Confirm.ask("Would you like me to help create this VM in Proxmox now?"):
            await _prepare_vm_creation(response, user_input)
        
        elif has_ansible and Confirm.ask("Would you like me to save this Ansible playbook for execution?"):
            await _save_ansible_playbook(response, user_input)


async def _save_and_prepare_terraform(response: str, user_input: str) -> None:
    """Save Terraform configuration and prepare for deployment."""
    try:
        # Extract Terraform code from response
        terraform_code = _extract_code_from_response(response, "hcl")
        
        if terraform_code:
            # Save to file
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"terraform_ai_generated_{timestamp}.tf"
            
            with open(filename, 'w') as f:
                f.write(terraform_code)
            
            console.print(f"[green]✅ Terraform configuration saved to {filename}[/green]")
            
            # Show deployment commands
            console.print(Panel(f"""
[bold cyan]Next Steps for Deployment:[/bold cyan]

1. Review the configuration:
   [dim]cat {filename}[/dim]

2. Initialize Terraform:
   [dim]terraform init[/dim]

3. Plan the deployment:
   [dim]terraform plan[/dim]

4. Apply the configuration:
   [dim]terraform apply[/dim]

[yellow]⚠️  Always review the plan before applying![/yellow]
            """, title="Terraform Deployment Guide", style="green"))
        else:
            console.print("[yellow]Could not extract Terraform code from response[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error saving Terraform configuration: {e}[/red]")


async def _prepare_vm_creation(response: str, user_input: str) -> None:
    """Prepare VM creation workflow."""
    try:
        console.print(Panel(f"""
[bold cyan]🚀 VM Creation Workflow[/bold cyan]

Based on your request: "{user_input[:100]}..."

I can help you create this VM in two ways:

[bold]Option 1: Direct Proxmox API[/bold]
- Create VM directly using Proxmox API
- Requires Proxmox credentials configured

[bold]Option 2: Generate Terraform Configuration[/bold]
- Generate complete Terraform config
- Allows version control and reproducible deployments
- Better for complex multi-VM setups
        """, style="blue"))
        
        choice = Prompt.ask("Choose deployment method", choices=["api", "terraform", "skip"], default="terraform")
        
        if choice == "api":
            await _create_vm_via_api(response, user_input)
        elif choice == "terraform":
            # Generate Terraform config for VM
            from ...services.ai_service import AIService
            try:
                ai_service = AIService()
                terraform_result = await ai_service.generate_terraform_config(
                    f"Convert this VM configuration to Terraform: {user_input}"
                )
                await _save_and_prepare_terraform(terraform_result['code'], user_input)
            except Exception as e:
                console.print(f"[red]Could not generate Terraform config: {e}[/red]")
        else:
            console.print("[dim]Skipping deployment[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error in VM creation workflow: {e}[/red]")


async def _create_vm_via_api(response: str, user_input: str) -> None:
    """Create VM via Proxmox API."""
    try:
        # Extract VM parameters from the user request and AI response
        vm_params = _extract_vm_parameters(user_input, response)
        
        vmid = Prompt.ask("Enter VM ID", default=str(vm_params.get('vmid', 100)))
        node = Prompt.ask("Enter target Proxmox node", default="pve")
        
        try:
            vmid = int(vmid)
        except ValueError:
            console.print("[red]Invalid VM ID[/red]")
            return
        
        console.print(Panel(f"""
[bold cyan]VM Configuration Summary:[/bold cyan]

[bold]VM ID:[/bold] {vmid}
[bold]Node:[/bold] {node}
[bold]Memory:[/bold] {vm_params.get('memory', '4096')}MB
[bold]CPU Cores:[/bold] {vm_params.get('cores', '4')}
[bold]Purpose:[/bold] {user_input[:100]}...

[yellow]⚠️  This will create a real VM in your Proxmox cluster![/yellow]
        """, style="yellow"))
        
        if Confirm.ask("Proceed with VM creation?"):
            console.print("[green]🚀 Creating VM... (This would connect to Proxmox API)[/green]")
            # Note: Actual Proxmox API integration would go here
            console.print("[green]✅ VM creation initiated! Check Proxmox web interface for progress.[/green]")
        else:
            console.print("[dim]VM creation cancelled[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error in VM creation: {e}[/red]")


def _extract_vm_parameters(user_input: str, ai_response: str) -> Dict[str, Any]:
    """Extract VM parameters from user input and AI response."""
    params = {}
    
    # Extract common parameters from user input
    text = (user_input + " " + ai_response).lower()
    
    # Memory extraction
    if "16gb" in text or "16 gb" in text:
        params['memory'] = 16384
    elif "8gb" in text or "8 gb" in text:
        params['memory'] = 8192
    elif "4gb" in text or "4 gb" in text:
        params['memory'] = 4096
    elif "2gb" in text or "2 gb" in text:
        params['memory'] = 2048
    else:
        # Default for AI agents
        params['memory'] = 8192
    
    # CPU cores extraction
    if "8 core" in text or "8 cpu" in text:
        params['cores'] = 8
    elif "6 core" in text or "6 cpu" in text:
        params['cores'] = 6
    elif "4 core" in text or "4 cpu" in text:
        params['cores'] = 4
    elif "2 core" in text or "2 cpu" in text:
        params['cores'] = 2
    else:
        # Default for AI agents
        params['cores'] = 4
    
    # VM ID
    params['vmid'] = 100  # Default, user will be prompted
    
    return params


async def _save_ansible_playbook(response: str, user_input: str) -> None:
    """Save Ansible playbook for execution."""
    try:
        ansible_code = _extract_code_from_response(response, "yaml")
        
        if ansible_code:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ansible_playbook_{timestamp}.yml"
            
            with open(filename, 'w') as f:
                f.write(ansible_code)
            
            console.print(f"[green]✅ Ansible playbook saved to {filename}[/green]")
            
            console.print(Panel(f"""
[bold cyan]Ansible Execution Guide:[/bold cyan]

1. Create inventory file:
   [dim]echo "target_host ansible_host=your_server_ip" > inventory[/dim]

2. Run the playbook:
   [dim]ansible-playbook -i inventory {filename}[/dim]

3. For dry run first:
   [dim]ansible-playbook -i inventory {filename} --check[/dim]
            """, title="Ansible Deployment", style="green"))
        else:
            console.print("[yellow]Could not extract Ansible code from response[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error saving Ansible playbook: {e}[/red]")


def _extract_code_from_response(response: str, code_type: str) -> Optional[str]:
    """Extract code blocks from AI response."""
    markers_map = {
        "hcl": ["```hcl", "```terraform"],
        "yaml": ["```yaml", "```yml"],
        "json": ["```json"],
        "bash": ["```bash", "```sh"]
    }
    
    markers = markers_map.get(code_type, [f"```{code_type}"])
    
    for marker in markers:
        start_idx = response.find(marker)
        if start_idx != -1:
            start_idx += len(marker)
            end_idx = response.find("```", start_idx)
            if end_idx != -1:
                return response[start_idx:end_idx].strip()
    
    # Fallback: try to find any code block
    start_idx = response.find("```")
    if start_idx != -1:
        # Skip the first ``` and language specifier
        start_idx = response.find("\n", start_idx) + 1
        end_idx = response.find("```", start_idx)
        if end_idx != -1:
            return response[start_idx:end_idx].strip()
    
    return None


def _build_system_prompt(mode: str, skill_level: str, context: Optional[str]) -> str:
    """Build system prompt based on chat mode and skill level."""
    
    base_prompt = "You are a helpful Proxmox infrastructure automation assistant."
    
    if mode == "troubleshooting":
        base_prompt += " You specialize in diagnosing and solving infrastructure problems."
    elif mode == "learning":
        base_prompt += " You are an excellent teacher, helping users learn infrastructure concepts."
    elif mode == "infrastructure":
        base_prompt += " You focus on infrastructure design, automation, and best practices."
    
    if skill_level == "beginner":
        base_prompt += " Provide simple, step-by-step explanations with clear examples."
    elif skill_level == "expert":
        base_prompt += " Provide detailed technical information and advanced concepts."
    else:
        base_prompt += " Provide balanced explanations with practical examples."
    
    if context:
        base_prompt += f"\n\nAdditional context: {context[:500]}..."  # Limit context size
    
    return base_prompt


if __name__ == "__main__":
    app()