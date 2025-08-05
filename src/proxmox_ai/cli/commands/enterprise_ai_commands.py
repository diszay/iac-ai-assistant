"""
Enterprise AI Commands for Advanced Features.

This module provides CLI commands for the advanced AI features including
fine-tuning, multimodal processing, security scanning, and enterprise-grade
capabilities optimized for Intel N150 hardware.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.tree import Tree
from rich.text import Text
import structlog

# Import advanced AI modules
from ...ai.advanced_model_fine_tuning import (
    get_fine_tuning_manager, FineTuningConfig, quick_fine_tune_infrastructure_model
)
from ...ai.multimodal_ai_engine import (
    get_multimodal_engine, VisualizationRequest, quick_visualize_infrastructure
)
from ...ai.advanced_nlp_processor import (
    get_enhanced_nlp_processor, AdvancedNLPConfig
)
from ...ai.intelligent_code_completion import (
    get_intelligent_completion, CodeContext, get_quick_suggestions
)
from ...ai.context_aware_recommendations import (
    get_recommendation_engine, InfrastructureContext, get_quick_recommendations
)
from ...ai.security_vulnerability_scanner import (
    get_security_scanner, quick_security_scan
)
from ...core.enterprise_caching import get_cache_manager
from ...core.comprehensive_metrics import get_metrics_manager

logger = structlog.get_logger(__name__)
console = Console()

# Create the enterprise AI command group
enterprise_ai = typer.Typer(
    name="enterprise",
    help="Enterprise-grade AI features and advanced capabilities",
    rich_markup_mode="rich"
)


@enterprise_ai.command()
def fine_tune(
    dataset_size: int = typer.Option(500, "--dataset-size", "-d", help="Size of training dataset"),
    model_name: str = typer.Option("proxmox-ai-infrastructure", "--model-name", "-m", help="Name for fine-tuned model"),
    epochs: int = typer.Option(2, "--epochs", "-e", help="Number of training epochs"),
    batch_size: int = typer.Option(1, "--batch-size", "-b", help="Training batch size"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory for model"),
):
    """
    Fine-tune AI models for infrastructure automation.
    
    This command creates a custom AI model trained specifically on infrastructure
    automation tasks using advanced techniques like LoRA and quantization.
    """
    console.print(Panel.fit(
        "[bold blue]AI Model Fine-Tuning[/bold blue]\n"
        "Training a custom model for infrastructure automation",
        style="blue"
    ))
    
    async def run_fine_tuning():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # Initialize fine-tuning
            task = progress.add_task("Initializing fine-tuning system...", total=100)
            
            config = FineTuningConfig(
                model_name=model_name,
                num_epochs=epochs,
                batch_size=batch_size,
                max_seq_length=384  # Optimized for Intel N150
            )
            
            progress.update(task, advance=20, description="Configuration set up")
            
            # Start fine-tuning
            progress.update(task, description="Starting model fine-tuning...")
            results = await quick_fine_tune_infrastructure_model(
                dataset_size=dataset_size,
                model_name=model_name,
                epochs=epochs
            )
            
            progress.update(task, advance=80, description="Fine-tuning completed")
            
            if results.get('success'):
                console.print(f"\n[green]✅ Fine-tuning completed successfully![/green]")
                console.print(f"Model saved to: {results['model_path']}")
                console.print(f"Training time: {results['training_time_seconds']:.1f} seconds")
                
                if 'optimization' in results:
                    opt_results = results['optimization']
                    if opt_results.get('success'):
                        console.print(f"Optimized model: {opt_results['optimized_path']}")
                
                # Display training metrics
                if 'training_metrics' in results:
                    metrics_table = Table(title="Training Metrics")
                    metrics_table.add_column("Epoch")
                    metrics_table.add_column("Loss")
                    metrics_table.add_column("Memory (MB)")
                    
                    for metric in results['training_metrics']:
                        metrics_table.add_row(
                            str(metric['epoch']),
                            f"{metric['loss']:.4f}",
                            f"{metric['memory_usage_mb']:.1f}"
                        )
                    
                    console.print(metrics_table)
            else:
                console.print(f"[red]❌ Fine-tuning failed: {results.get('error', 'Unknown error')}[/red]")
    
    asyncio.run(run_fine_tuning())


@enterprise_ai.command()
def visualize(
    description: str = typer.Argument(..., help="Description of infrastructure to visualize"),
    visualization_type: str = typer.Option("auto", "--type", "-t", help="Type of visualization (network, architecture, deployment)"),
    style: str = typer.Option("professional", "--style", "-s", help="Visualization style (professional, minimal, dark)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path for visualization")
):
    """
    Generate infrastructure visualizations using multimodal AI.
    
    Creates professional diagrams and visualizations of infrastructure
    based on text descriptions using advanced AI and rendering engines.
    """
    console.print(Panel.fit(
        "[bold green]Infrastructure Visualization[/bold green]\n"
        f"Generating {visualization_type} diagram for: {description[:50]}...",
        style="green"
    ))
    
    async def run_visualization():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Generating visualization...", total=None)
            
            try:
                result = await quick_visualize_infrastructure(
                    description=description,
                    visualization_type=visualization_type,
                    style=style
                )
                
                if result.success:
                    console.print(f"\n[green]✅ Visualization generated successfully![/green]")
                    console.print(f"Description: {result.description}")
                    console.print(f"Processing time: {result.processing_time:.2f} seconds")
                    
                    if output_file and result.image_data:
                        output_path = Path(output_file)
                        output_path.write_bytes(result.image_data)
                        console.print(f"Saved to: {output_path}")
                    
                    # Display metadata
                    if result.metadata:
                        metadata_table = Table(title="Visualization Metadata")
                        metadata_table.add_column("Property")
                        metadata_table.add_column("Value")
                        
                        for key, value in result.metadata.items():
                            metadata_table.add_row(key.replace('_', ' ').title(), str(value))
                        
                        console.print(metadata_table)
                else:
                    console.print(f"[red]❌ Visualization failed: {result.error_message}[/red]")
                    
            except Exception as e:
                console.print(f"[red]❌ Error: {str(e)}[/red]")
    
    asyncio.run(run_visualization())


@enterprise_ai.command()
def scan_security(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="File to scan"),
    directory: Optional[str] = typer.Option(None, "--directory", "-d", help="Directory to scan"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Code string to scan"),
    file_type: str = typer.Option("auto", "--type", "-t", help="File type (terraform, ansible, yaml, bash)"),
    report_format: str = typer.Option("table", "--format", help="Report format (table, json, detailed)")
):
    """
    Perform advanced security vulnerability scanning.
    
    Scans infrastructure code for security vulnerabilities, misconfigurations,
    and compliance issues using enterprise-grade security rules and patterns.
    """
    console.print(Panel.fit(
        "[bold red]Security Vulnerability Scanner[/bold red]\n"
        "Analyzing code for security issues and vulnerabilities",
        style="red"
    ))
    
    async def run_security_scan():
        scanner = get_security_scanner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Performing security scan...", total=None)
            
            try:
                if code:
                    # Scan provided code string
                    results = await quick_security_scan(code, file_type)
                elif file_path:
                    # Scan single file
                    file_content = Path(file_path).read_text()
                    detected_type = file_type if file_type != "auto" else scanner._detect_file_type(Path(file_path).suffix)
                    results = await quick_security_scan(file_content, detected_type)
                elif directory:
                    # Scan directory
                    scan_results = await scanner.scan_directory(directory)
                    if scan_results:
                        report = await scanner.generate_security_report(scan_results)
                        _display_security_report(report, report_format)
                    else:
                        console.print("[yellow]No files found to scan[/yellow]")
                    return
                else:
                    console.print("[red]Please specify --file, --directory, or --code[/red]")
                    return
                
                # Display results
                _display_security_results(results, report_format)
                
            except Exception as e:
                console.print(f"[red]❌ Security scan failed: {str(e)}[/red]")
    
    asyncio.run(run_security_scan())


@enterprise_ai.command()
def recommendations(
    vm_count: int = typer.Option(0, "--vms", help="Number of VMs"),
    cpu_cores: int = typer.Option(0, "--cpu-cores", help="Total CPU cores"),
    memory_gb: float = typer.Option(0.0, "--memory-gb", help="Total memory in GB"),
    cpu_utilization: float = typer.Option(0.0, "--cpu-util", help="CPU utilization percentage"),
    memory_utilization: float = typer.Option(0.0, "--memory-util", help="Memory utilization percentage"),
    environment: str = typer.Option("production", "--env", help="Environment type"),
    focus_areas: Optional[str] = typer.Option(None, "--focus", help="Focus areas (comma-separated)")
):
    """
    Get intelligent infrastructure recommendations.
    
    Provides context-aware recommendations for infrastructure optimization,
    security improvements, and best practices based on current configuration.
    """
    console.print(Panel.fit(
        "[bold cyan]Infrastructure Recommendations[/bold cyan]\n"
        "Analyzing infrastructure for optimization opportunities",
        style="cyan"
    ))
    
    async def run_recommendations():
        engine = get_recommendation_engine()
        
        # Create infrastructure context
        context = InfrastructureContext(
            vm_count=vm_count,
            total_cpu_cores=cpu_cores,
            total_memory_gb=memory_gb,
            cpu_utilization=cpu_utilization,
            memory_utilization=memory_utilization,
            environment_type=environment
        )
        
        focus_list = focus_areas.split(',') if focus_areas else None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Generating recommendations...", total=None)
            
            try:
                recommendations = await engine.generate_recommendations(context, focus_list)
                
                if recommendations:
                    _display_recommendations(recommendations)
                else:
                    console.print("[yellow]No specific recommendations found for current configuration[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]❌ Recommendation generation failed: {str(e)}[/red]")
    
    asyncio.run(run_recommendations())


@enterprise_ai.command()
def code_complete(
    file_path: str = typer.Argument(..., help="File to analyze for code completion"),
    cursor_line: int = typer.Option(0, "--line", "-l", help="Cursor line number"),
    max_suggestions: int = typer.Option(5, "--max", "-m", help="Maximum number of suggestions")
):
    """
    Get intelligent code completion suggestions.
    
    Provides context-aware code completion and suggestions for infrastructure
    code including Terraform, Ansible, Kubernetes, and shell scripts.
    """
    console.print(Panel.fit(
        "[bold magenta]Intelligent Code Completion[/bold magenta]\n"
        f"Analyzing {file_path} for completion suggestions",
        style="magenta"  
    ))
    
    async def run_code_completion():
        try:
            file_content = Path(file_path).read_text()
            file_type = Path(file_path).suffix.lstrip('.')
            
            # Map extensions to types
            type_mapping = {
                'tf': 'terraform',
                'yml': 'yaml',
                'yaml': 'yaml', 
                'sh': 'bash',
                'py': 'python'
            }
            
            detected_type = type_mapping.get(file_type, file_type)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("Analyzing code context...", total=None)
                
                suggestions = await get_quick_suggestions(
                    file_content, 
                    detected_type, 
                    cursor_line
                )
                
                if suggestions:
                    _display_code_suggestions(suggestions[:max_suggestions])
                else:
                    console.print("[yellow]No code suggestions available for current context[/yellow]")
                    
        except Exception as e:
            console.print(f"[red]❌ Code completion failed: {str(e)}[/red]")
    
    asyncio.run(run_code_completion())


@enterprise_ai.command()
def system_status():
    """
    Show comprehensive system status and metrics.
    
    Displays detailed information about AI models, caches, metrics,
    and overall system health for enterprise monitoring.
    """
    console.print(Panel.fit(
        "[bold yellow]Enterprise System Status[/bold yellow]\n"
        "Comprehensive system health and performance metrics",
        style="yellow"
    ))
    
    async def show_system_status():
        try:
            # Get metrics manager
            metrics_mgr = get_metrics_manager()
            cache_mgr = get_cache_manager()
            
            # System health
            health = await metrics_mgr.get_health_status()
            _display_health_status(health)
            
            # Cache statistics
            cache_stats = await cache_mgr.get_comprehensive_stats()
            _display_cache_stats(cache_stats)
            
            # Metrics summary
            metrics_summary = metrics_mgr.get_registry().get_metrics_summary()
            _display_metrics_summary(metrics_summary)
            
        except Exception as e:
            console.print(f"[red]❌ Failed to get system status: {str(e)}[/red]")
    
    asyncio.run(show_system_status())


@enterprise_ai.command()
def benchmark(
    duration: int = typer.Option(30, "--duration", "-d", help="Benchmark duration in seconds"),
    workload: str = typer.Option("mixed", "--workload", "-w", help="Workload type (ai, cache, security, mixed)"),
    iterations: int = typer.Option(10, "--iterations", "-i", help="Number of iterations")
):
    """
    Run performance benchmarks on AI and system components.
    
    Tests the performance of various system components including AI models,
    caching systems, and security scanners to validate optimization.
    """
    console.print(Panel.fit(
        "[bold blue]Performance Benchmark[/bold blue]\n"
        f"Running {workload} workload for {duration} seconds",
        style="blue"
    ))
    
    async def run_benchmark():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Running benchmark...", total=iterations)
            
            results = {
                'workload': workload,
                'duration': duration,
                'iterations': iterations,
                'results': []
            }
            
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    if workload in ['ai', 'mixed']:
                        # AI workload test
                        nlp_processor = get_enhanced_nlp_processor()
                        await nlp_processor.parse_user_input("Create a simple web server with nginx")
                    
                    if workload in ['cache', 'mixed']:
                        # Cache workload test
                        cache_mgr = get_cache_manager()
                        await cache_mgr.set(f"test_key_{i}", f"test_value_{i}")
                        await cache_mgr.get(f"test_key_{i}")
                    
                    if workload in ['security', 'mixed']:
                        # Security workload test
                        test_code = '''
                        resource "aws_instance" "example" {
                          ami           = "ami-0123456789abcdef0"
                          instance_type = "t2.micro"
                          password      = "hardcoded_password"
                        }
                        '''
                        await quick_security_scan(test_code, "terraform")
                    
                    iteration_time = time.time() - start_time
                    results['results'].append({
                        'iteration': i + 1,
                        'duration': iteration_time,
                        'success': True
                    })
                    
                except Exception as e:
                    results['results'].append({
                        'iteration': i + 1,
                        'duration': time.time() - start_time,
                        'success': False,
                        'error': str(e)
                    })
                
                progress.update(task, advance=1)
                
                if time.time() - start_time < duration / iterations:
                    await asyncio.sleep((duration / iterations) - (time.time() - start_time))
            
            _display_benchmark_results(results)
    
    asyncio.run(run_benchmark())


def _display_security_results(results: Dict[str, Any], format_type: str):
    """Display security scan results."""
    if format_type == "json":
        console.print(json.dumps(results, indent=2))
        return
    
    # Create summary table
    summary_table = Table(title="Security Scan Summary")
    summary_table.add_column("Metric")
    summary_table.add_column("Value")
    
    summary_table.add_row("Vulnerabilities Found", str(results['vulnerabilities_found']))
    summary_table.add_row("Critical", str(results['critical_count']))
    summary_table.add_row("High", str(results['high_count']))
    summary_table.add_row("Medium", str(results['medium_count']))
    summary_table.add_row("Scan Duration", f"{results['scan_duration']:.2f}s")
    
    console.print(summary_table)
    
    # Display top vulnerabilities
    if results['top_vulnerabilities']:
        vuln_table = Table(title="Top Vulnerabilities")
        vuln_table.add_column("Severity")
        vuln_table.add_column("Title")
        vuln_table.add_column("Description")
        
        for vuln in results['top_vulnerabilities']:
            severity_color = {
                'critical': 'red',
                'high': 'orange',
                'medium': 'yellow',
                'low': 'blue'
            }.get(vuln['severity'], 'white')
            
            vuln_table.add_row(
                f"[{severity_color}]{vuln['severity'].upper()}[/{severity_color}]",
                vuln['title'],
                vuln['description'][:50] + "..." if len(vuln['description']) > 50 else vuln['description']
            )
        
        console.print(vuln_table)


def _display_security_report(report: Dict[str, Any], format_type: str):
    """Display comprehensive security report."""
    if format_type == "json":
        console.print(json.dumps(report, indent=2, default=str))
        return
    
    # Summary
    summary = report['summary']
    console.print(f"\n[bold]Security Report Summary[/bold]")
    console.print(f"Files Scanned: {summary['total_files_scanned']}")
    console.print(f"Total Vulnerabilities: {summary['total_vulnerabilities']}")
    console.print(f"Risk Score: {summary['risk_score']}")
    
    # Severity breakdown
    severity_table = Table(title="Severity Breakdown")
    severity_table.add_column("Severity")
    severity_table.add_column("Count")
    
    for severity, count in report['severity_breakdown'].items():
        severity_table.add_row(severity.title(), str(count))
    
    console.print(severity_table)
    
    # Recommendations
    if report['recommendations']:
        console.print(f"\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(report['recommendations'], 1):
            console.print(f"{i}. {rec}")


def _display_recommendations(recommendations):
    """Display infrastructure recommendations."""
    if not recommendations:
        return
    
    # Group by priority
    by_priority = {}
    for rec in recommendations:
        priority = rec.priority.value
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(rec)
    
    # Display by priority
    for priority in ['critical', 'high', 'medium', 'low']:
        if priority in by_priority:
            priority_color = {
                'critical': 'red',
                'high': 'orange', 
                'medium': 'yellow',
                'low': 'blue'
            }[priority]
            
            console.print(f"\n[bold {priority_color}]{priority.upper()} Priority Recommendations[/bold {priority_color}]")
            
            for rec in by_priority[priority]:
                console.print(f"\n• [bold]{rec.title}[/bold]")
                console.print(f"  {rec.description}")
                console.print(f"  Confidence: {rec.confidence:.1%}")
                
                if rec.implementation_steps:
                    console.print("  Implementation:")
                    for step in rec.implementation_steps[:3]:
                        console.print(f"    - {step}")


def _display_code_suggestions(suggestions):
    """Display code completion suggestions."""
    if not suggestions:
        return
    
    suggestions_table = Table(title="Code Completion Suggestions")
    suggestions_table.add_column("Type")
    suggestions_table.add_column("Description") 
    suggestions_table.add_column("Confidence")
    
    for suggestion in suggestions:
        suggestions_table.add_row(
            suggestion['type'].title(),
            suggestion['description'],
            f"{suggestion['confidence']:.1%}"
        )
    
    console.print(suggestions_table)


def _display_health_status(health):
    """Display system health status."""
    status_color = {
        'healthy': 'green',
        'warning': 'yellow',
        'critical': 'red'
    }.get(health['status'], 'white')
    
    console.print(f"\n[bold {status_color}]System Status: {health['status'].upper()}[/bold {status_color}]")
    
    if health['checks']:
        checks_table = Table(title="Health Checks")
        checks_table.add_column("Component")
        checks_table.add_column("Status")
        
        for component, status in health['checks'].items():
            checks_table.add_row(component.title(), status)
        
        console.print(checks_table)


def _display_cache_stats(stats):
    """Display cache statistics."""
    overall = stats.get('overall', {})
    
    cache_table = Table(title="Cache Performance")
    cache_table.add_column("Metric")
    cache_table.add_column("Value")
    
    cache_table.add_row("Overall Hit Rate", f"{overall.get('overall_hit_rate', 0):.1%}")
    cache_table.add_row("Total Hits", str(overall.get('total_hits', 0)))
    cache_table.add_row("Total Misses", str(overall.get('total_misses', 0)))
    cache_table.add_row("Memory Usage", f"{overall.get('total_memory_usage_mb', 0):.1f} MB")
    
    console.print(cache_table)


def _display_metrics_summary(summary):
    """Display metrics summary."""
    metrics_table = Table(title="Metrics Summary")
    metrics_table.add_column("Metric")
    metrics_table.add_column("Value")
    
    metrics_table.add_row("Total Series", str(summary['total_series']))
    
    for metric_type, count in summary['metrics_by_type'].items():
        metrics_table.add_row(f"{metric_type.title()} Metrics", str(count))
    
    console.print(metrics_table)


def _display_benchmark_results(results):
    """Display benchmark results."""
    successful_results = [r for r in results['results'] if r['success']]
    
    if successful_results:
        durations = [r['duration'] for r in successful_results]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations) 
        max_duration = max(durations)
        
        benchmark_table = Table(title="Benchmark Results")
        benchmark_table.add_column("Metric")
        benchmark_table.add_column("Value")
        
        benchmark_table.add_row("Workload", results['workload'])
        benchmark_table.add_row("Successful Iterations", f"{len(successful_results)}/{results['iterations']}")
        benchmark_table.add_row("Average Duration", f"{avg_duration:.3f}s")
        benchmark_table.add_row("Min Duration", f"{min_duration:.3f}s")
        benchmark_table.add_row("Max Duration", f"{max_duration:.3f}s")
        benchmark_table.add_row("Throughput", f"{len(successful_results)/results['duration']:.2f} ops/sec")
        
        console.print(benchmark_table)
    else:
        console.print("[red]All benchmark iterations failed[/red]")


# Export the command group
__all__ = ['enterprise_ai']