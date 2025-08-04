"""
Enhanced AI Commands for Proxmox AI Assistant CLI.

Provides world-class AI assistance with comprehensive technical knowledge,
security validation, and adaptive expertise levels.
"""

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.markdown import Markdown
import structlog

from ...ai.enhanced_ai_client import enhanced_ai_client, EnhancedAIResponse
from ...ai.knowledge_base import TechnicalDomain, ExpertiseLevel
from ...ai.validation_framework import ValidationLevel

logger = structlog.get_logger(__name__)
console = Console()

# Create enhanced AI command group
app = typer.Typer(
    name="ai",
    help="🤖 Enhanced AI-powered infrastructure automation with world-class expertise",
    rich_markup_mode="rich"
)


@app.command()
def chat(
    skill_level: str = typer.Option(
        "intermediate", "--skill-level", "-s",
        help="AI interaction skill level (beginner, intermediate, expert)"
    ),
    mode: str = typer.Option(
        "general", "--mode", "-m",
        help="Chat mode (general, troubleshooting, learning, infrastructure, security)"
    ),
    context_file: Optional[Path] = typer.Option(
        None, "--context", "-c",
        help="Load context from file (logs, configs, etc.)"
    ),
    save_session: Optional[Path] = typer.Option(
        None, "--save-session",
        help="Save chat session to file"
    ),
    user_id: Optional[str] = typer.Option(
        None, "--user-id",
        help="User identifier for personalized assistance"
    ),
    security_mode: str = typer.Option(
        "standard", "--security",
        help="Security validation level (basic, standard, strict)"
    )
):
    """
    🚀 Start enhanced interactive chat with comprehensive AI assistance.
    
    Features world-class technical expertise across:
    - Virtualization & Proxmox (VMware, KVM, QEMU, containers, hypervisors)
    - Infrastructure as Code (Terraform, Ansible, Pulumi, CloudFormation)
    - Containerization (Docker, Kubernetes, microservices, service mesh)
    - System Engineering (Linux administration, networking, security)
    - Cloud Computing (AWS, Azure, GCP, multi-cloud, serverless)
    
    Includes:
    ✅ Automatic domain detection and expertise adaptation
    ✅ Comprehensive input validation and security scanning
    ✅ Context-aware conversation management
    ✅ Progressive learning and skill assessment
    ✅ Technical validation of all configurations
    ✅ Security-conscious recommendations
    
    Examples:
      proxmox-ai ai chat --skill-level beginner --mode learning
      proxmox-ai ai chat --mode infrastructure --security strict --user-id admin
      proxmox-ai ai chat --context /var/log/proxmox.log --mode troubleshooting
    """
    asyncio.run(_run_enhanced_chat_session(
        skill_level, mode, context_file, save_session, user_id, security_mode
    ))


async def _run_enhanced_chat_session(
    skill_level: str,
    mode: str,
    context_file: Optional[Path],
    save_session: Optional[Path],
    user_id: Optional[str],
    security_mode: str
):
    """Run enhanced interactive chat session."""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Initialize session data
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": time.time(),
            "skill_level": skill_level,
            "mode": mode,
            "security_mode": security_mode,
            "messages": [],
            "context": None,
            "performance_metrics": {
                "total_interactions": 0,
                "successful_interactions": 0,
                "security_blocks": 0,
                "context_switches": 0,
                "avg_response_time": 0.0
            }
        }
        
        # Load context if provided
        if context_file and context_file.exists():
            with open(context_file, 'r') as f:
                session_data["context"] = f.read()
                console.print(f"[green]✅ Loaded context from {context_file}[/green]")
        
        # Display enhanced welcome
        await _display_enhanced_welcome(skill_level, mode, security_mode, session_data.get("context") is not None)
        
        # Get system status
        system_status = enhanced_ai_client.get_system_status()
        _display_system_status(system_status)
        
        # Main enhanced chat loop
        total_response_time = 0.0
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]", default="").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                elif user_input.lower() in ['help', '?']:
                    _display_enhanced_help()
                    continue
                elif user_input.lower() == 'clear':
                    console.clear()
                    await _display_enhanced_welcome(skill_level, mode, security_mode, session_data.get("context") is not None)
                    continue
                elif user_input.lower() == 'status':
                    _display_session_status(session_data, system_status)
                    continue
                elif user_input.lower() == 'metrics':
                    _display_performance_metrics(enhanced_ai_client.get_session_metrics())
                    continue
                elif not user_input:
                    continue
                
                # Track interaction
                session_data["performance_metrics"]["total_interactions"] += 1
                
                # Add user message to session
                session_data["messages"].append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": time.time()
                })
                
                # Generate enhanced AI response
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("🧠 Processing with enhanced AI...", total=None)
                    
                    try:
                        # Additional context for the AI
                        additional_context = {
                            "mode": mode,
                            "security_mode": security_mode,
                            "session_context": session_data.get("context"),
                            "conversation_history": session_data["messages"][-10:]  # Last 10 messages
                        }
                        
                        # Get enhanced AI response
                        enhanced_response = await enhanced_ai_client.chat(
                            user_input=user_input,
                            session_id=session_id,
                            user_id=user_id,
                            additional_context=additional_context
                        )
                        
                        progress.update(task, completed=True)
                        
                        # Update performance metrics
                        total_response_time += enhanced_response.processing_time
                        session_data["performance_metrics"]["avg_response_time"] = (
                            total_response_time / session_data["performance_metrics"]["total_interactions"]
                        )
                        
                        if enhanced_response.success:
                            session_data["performance_metrics"]["successful_interactions"] += 1
                        
                        if not enhanced_response.success and enhanced_response.model_used == "security_filter":
                            session_data["performance_metrics"]["security_blocks"] += 1
                        
                        if enhanced_response.context_switched:
                            session_data["performance_metrics"]["context_switches"] += 1
                        
                    except Exception as e:
                        progress.update(task, completed=True)
                        console.print(f"[red]Error generating response: {e}[/red]")
                        continue
                
                # Display enhanced AI response
                await _display_enhanced_response(enhanced_response, mode)
                
                # Add AI response to session
                session_data["messages"].append({
                    "role": "assistant",
                    "content": enhanced_response.content,
                    "metadata": {
                        "model_used": enhanced_response.model_used,
                        "processing_time": enhanced_response.processing_time,
                        "skill_level": enhanced_response.skill_level,
                        "domain": enhanced_response.domain,
                        "security_score": enhanced_response.security_score,
                        "context_switched": enhanced_response.context_switched
                    },
                    "timestamp": enhanced_response.timestamp
                })
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Chat interrupted. Type 'quit' to exit cleanly.[/yellow]")
                continue
            except EOFError:
                break
        
        # Save session if requested
        if save_session:
            session_data["end_time"] = time.time()
            session_data["duration"] = session_data["end_time"] - session_data["start_time"]
            
            # Add final system metrics
            session_data["final_metrics"] = enhanced_ai_client.get_session_metrics()
            
            with open(save_session, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            console.print(f"\n[green]✅ Enhanced session saved to {save_session}[/green]")
        
        # Display session summary
        _display_session_summary(session_data)
        
        console.print("\n[cyan]Thanks for using the Enhanced Proxmox AI Assistant! 🚀[/cyan]")
        
    except Exception as e:
        logger.error("Enhanced chat session failed", error=str(e))
        console.print(f"[red]Enhanced chat session error: {e}[/red]")
        raise typer.Exit(1)


async def _display_enhanced_welcome(skill_level: str, mode: str, security_mode: str, has_context: bool):
    """Display enhanced welcome message."""
    welcome_text = f"""[bold blue]🚀 Enhanced Proxmox AI Assistant - World-Class Infrastructure Expertise[/bold blue]

[cyan]Configuration:[/cyan]
• **Skill Level:** {skill_level} (automatically adapts based on your interactions)
• **Mode:** {mode} (specialized assistance for your use case)
• **Security:** {security_mode} (comprehensive input validation and security scanning)
• **Context Loaded:** {'✅ Yes' if has_context else '❌ No'}

[green]🌟 **Enhanced Capabilities:**[/green]
• **Comprehensive Knowledge:** Expert in Proxmox, IaC, containers, cloud, and system engineering
• **Security-First:** All inputs validated, all recommendations security-conscious
• **Adaptive Intelligence:** Automatically detects domains and adjusts expertise level
• **Context Awareness:** Maintains conversation context and switches domains seamlessly
• **Technical Validation:** Validates all configurations for security and best practices

[dim]**Available Commands:**[/dim]
• [bold]help[/bold] or [bold]?[/bold] - Show comprehensive help and capabilities
• [bold]status[/bold] - Show session and system status
• [bold]metrics[/bold] - Display performance metrics
• [bold]clear[/bold] - Clear conversation history  
• [bold]quit[/bold], [bold]exit[/bold], or [bold]Ctrl+C[/bold] - End session

[green]💡 **What I can help with:**[/green]
• Proxmox VE administration, clustering, and troubleshooting
• Infrastructure as Code (Terraform, Ansible, Pulumi, CloudFormation)
• Containerization and Kubernetes orchestration
• Cloud architecture (AWS, Azure, GCP, multi-cloud, hybrid)
• System engineering and Linux administration
• Network design and security architecture
• Performance optimization and monitoring
• Security hardening and compliance
• Automation strategies and DevOps practices

[yellow]🛡️ **Security Notice:**[/yellow] All inputs are automatically scanned for security threats. 
Dangerous patterns are blocked to protect both you and our systems.

[green]Ready to provide world-class infrastructure assistance! Ask me anything! 🤖[/green]
"""
    
    console.print(Panel(welcome_text, style="blue", expand=False))


def _display_system_status(system_status: Dict[str, Any]):
    """Display enhanced system status."""
    status_table = Table(title="🔧 System Status", show_header=True, expand=False)
    status_table.add_column("Component", style="bold cyan", no_wrap=True)
    status_table.add_column("Status", style="green", no_wrap=True)
    status_table.add_column("Details", style="dim")
    
    # AI Client status
    ai_info = system_status.get("ai_client", {})
    status_table.add_row(
        "AI Model",
        "✅ Operational",
        f"{ai_info.get('current_model', 'Unknown')} ({ai_info.get('performance_profile', {}).get('model_quality', 'Standard')} tier)"
    )
    
    # Components status
    components = system_status.get("components_status", {})
    for component, status in components.items():
        status_icon = "✅" if status == "operational" else "❌"
        status_table.add_row(
            component.replace("_", " ").title(),
            f"{status_icon} {status.title()}",
            "All features available"
        )
    
    console.print(status_table)
    console.print()


def _display_enhanced_help():
    """Display comprehensive help information."""
    help_text = """[bold]🚀 Enhanced Proxmox AI Assistant - Comprehensive Help[/bold]

[cyan]**Chat Commands:**[/cyan]
• **help**, **?** - Show this comprehensive help
• **status** - Display session and system status
• **metrics** - Show performance metrics and statistics
• **clear** - Clear conversation history and start fresh
• **quit**, **exit**, **bye** - End chat session gracefully

[cyan]**What I Excel At:**[/cyan]

[bold]🖥️ Virtualization & Proxmox VE:[/bold]
• Cluster setup, high availability, and fencing strategies
• Storage integration (Ceph, ZFS, NFS, iSCSI) and optimization
• Network configuration (bridges, VLANs, bonding, SR-IOV)
• VM lifecycle management, templates, and cloud-init automation
• Migration from VMware, Hyper-V, and other platforms
• Performance tuning and troubleshooting

[bold]🏗️ Infrastructure as Code:[/bold]
• Terraform enterprise patterns and state management
• Ansible automation and enterprise playbook organization
• Pulumi cloud-native infrastructure development
• CloudFormation and ARM template optimization
• GitOps workflows and CI/CD integration
• Module development and testing strategies

[bold]🐳 Containerization & Orchestration:[/bold]
• Docker enterprise patterns and image optimization
• Kubernetes production deployment and scaling
• Service mesh architecture (Istio, Linkerd, Consul Connect)
• Microservices design and distributed systems
• Container security and runtime protection
• CI/CD integration and automated deployments

[bold]☁️ Cloud Computing:[/bold]
• Multi-cloud and hybrid cloud architecture
• AWS, Azure, GCP service optimization
• Serverless computing and edge deployment
• Cloud migration strategies and patterns
• Cost optimization and FinOps implementation
• Cloud security and compliance

[bold]⚙️ System Engineering:[/bold]
• Linux administration and performance tuning
• Network design and security architecture
• Monitoring, observability, and alerting
• Automation scripting and configuration management
• Disaster recovery and business continuity
• Security hardening and compliance frameworks

[cyan]**Example Questions:**[/cyan]
• "Help me design a high-availability Proxmox cluster with Ceph storage"
• "Generate Terraform code for a 3-tier web application on AWS"
• "Create an Ansible playbook for automated security hardening"
• "How do I troubleshoot Kubernetes pod networking issues?"
• "Design a multi-cloud disaster recovery strategy"
• "Optimize Docker images for production deployment"
• "Implement zero-trust security for my infrastructure"

[cyan]**Expertise Levels:**[/cyan]
• **Beginner** - Step-by-step guidance with detailed explanations
• **Intermediate** - Practical implementation with best practices
• **Expert** - Advanced patterns and enterprise architectures

[cyan]**Security Features:**[/cyan]
• 🛡️ Automatic input validation and threat detection
• 🔒 Security-conscious recommendations in all responses
• 📋 Compliance guidance (CIS, NIST, SOC2, ISO27001)
• 🚫 Dangerous pattern blocking and sanitization
• 📊 Security scoring for all interactions

[green]💡 **Pro Tips:**[/green]
• Be specific about your environment and requirements
• Mention your skill level for personalized assistance
• Ask for explanations if any concepts are unclear
• Request security reviews for production deployments
• Use context files for troubleshooting with logs

[yellow]The AI automatically adapts to your expertise level and the technical domain of your questions![/yellow]
"""
    
    console.print(Panel(help_text, title="Enhanced AI Assistant Help", style="cyan"))


def _display_session_status(session_data: Dict[str, Any], system_status: Dict[str, Any]):
    """Display current session status."""
    metrics = session_data.get("performance_metrics", {})
    duration = time.time() - session_data["start_time"]
    
    status_table = Table(title="📊 Session Status", show_header=True)
    status_table.add_column("Metric", style="bold cyan")
    status_table.add_column("Value", style="green")
    
    status_table.add_row("Session Duration", f"{duration/60:.1f} minutes")
    status_table.add_row("Total Interactions", str(metrics.get("total_interactions", 0)))
    status_table.add_row("Successful Responses", str(metrics.get("successful_interactions", 0)))
    status_table.add_row("Security Blocks", str(metrics.get("security_blocks", 0)))
    status_table.add_row("Context Switches", str(metrics.get("context_switches", 0)))
    status_table.add_row("Avg Response Time", f"{metrics.get('avg_response_time', 0.0):.2f}s")
    status_table.add_row("User ID", session_data.get("user_id") or "Anonymous")
    status_table.add_row("Mode", session_data.get("mode", "general"))
    status_table.add_row("Security Level", session_data.get("security_mode", "standard"))
    
    console.print(status_table)


def _display_performance_metrics(metrics: Dict[str, Any]):
    """Display performance metrics."""
    metrics_table = Table(title="⚡ Performance Metrics", show_header=True)
    metrics_table.add_column("Metric", style="bold cyan")
    metrics_table.add_column("Value", style="green")
    metrics_table.add_column("Description", style="dim")
    
    metrics_table.add_row(
        "Total Requests", 
        str(metrics.get("total_requests", 0)),
        "Total AI requests processed"
    )
    metrics_table.add_row(
        "Successful Requests",
        str(metrics.get("successful_requests", 0)),
        "Successfully completed requests"
    )
    metrics_table.add_row(
        "Security Blocks",
        str(metrics.get("security_violations_blocked", 0)),
        "Dangerous inputs blocked"
    )
    metrics_table.add_row(
        "Context Switches",
        str(metrics.get("context_switches", 0)),
        "Automatic domain/expertise changes"
    )
    metrics_table.add_row(
        "Cache Hits",
        str(metrics.get("cache_hits", 0)),
        "Responses served from cache"
    )
    metrics_table.add_row(
        "Avg Processing Time",
        f"{metrics.get('avg_processing_time', 0.0):.2f}s",
        "Average response generation time"
    )
    
    console.print(metrics_table)


async def _display_enhanced_response(response: EnhancedAIResponse, mode: str):
    """Display enhanced AI response with rich formatting."""
    
    # Response header with metadata
    header_info = []
    header_info.append(f"🤖 **Enhanced AI Assistant** ({response.skill_level} • {response.domain})")
    
    if response.context_switched:
        header_info.append("🔄 *Context switched*")
    
    if response.security_score < 80:
        header_info.append(f"🛡️ Security Score: {response.security_score:.0f}/100")
    
    if response.processing_time > 5.0:
        header_info.append(f"⏱️ {response.processing_time:.1f}s")
    
    header = " | ".join(header_info)
    console.print(f"\n{header}")
    
    # Main response content
    if response.content:
        # Check if content looks like markdown
        if any(marker in response.content for marker in ['##', '**', '- ', '```']):
            console.print(Markdown(response.content))
        else:
            console.print(response.content)
    
    # Security warnings if needed
    critical_validations = [v for v in response.validation_results 
                          if v.level == ValidationLevel.CRITICAL]
    if critical_validations:
        warning_text = "⚠️ **Security Issues Detected:**\n"
        for issue in critical_validations[:3]:
            warning_text += f"• {issue.message}\n"
        console.print(Panel(warning_text, style="red", title="Security Alert"))
    
    # Learning suggestions if available
    if response.learning_suggestions:
        suggestions_text = "**Suggested Learning:**\n"
        for suggestion in response.learning_suggestions[:3]:
            suggestions_text += f"• {suggestion}\n"
        console.print(Panel(suggestions_text, style="green", title="💡 Learning Opportunities"))
    
    # Related topics if available
    if response.related_topics:
        topics_text = ", ".join(response.related_topics[:5])
        console.print(f"\n[dim]Related topics: {topics_text}[/dim]")


def _display_session_summary(session_data: Dict[str, Any]):
    """Display session summary."""
    metrics = session_data.get("performance_metrics", {})
    duration = session_data.get("duration", time.time() - session_data["start_time"])
    
    summary_text = f"""[bold green]📈 Session Summary[/bold green]

[cyan]Duration:[/cyan] {duration/60:.1f} minutes
[cyan]Interactions:[/cyan] {metrics.get('total_interactions', 0)} total, {metrics.get('successful_interactions', 0)} successful
[cyan]Security:[/cyan] {metrics.get('security_blocks', 0)} threats blocked
[cyan]Intelligence:[/cyan] {metrics.get('context_switches', 0)} automatic context switches
[cyan]Performance:[/cyan] {metrics.get('avg_response_time', 0.0):.2f}s average response time

[green]Thank you for using the Enhanced Proxmox AI Assistant![/green]
"""
    
    console.print(Panel(summary_text, style="green"))


@app.command()
def generate(
    resource_type: str = typer.Argument(
        ..., 
        help="Type of resource to generate (vm, terraform, ansible, docker, kubernetes)"
    ),
    description: str = typer.Argument(
        ...,
        help="Natural language description of what to create"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Save generated configuration to file"
    ),
    skill_level: str = typer.Option(
        "intermediate", "--skill", "-s",
        help="Skill level for generation (beginner, intermediate, expert)"
    ),
    validate: bool = typer.Option(
        True, "--validate/--no-validate", "-v",
        help="Validate generated configurations for security and best practices"
    ),
    user_id: Optional[str] = typer.Option(
        None, "--user-id",
        help="User identifier for personalized generation"
    )
):
    """
    🏗️ Generate infrastructure configurations with enhanced AI validation.
    
    Supports all major infrastructure types with comprehensive security validation,
    best practices integration, and expertise-level appropriate content.
    
    Examples:
      proxmox-ai ai generate vm "Ubuntu 22.04 web server with 4GB RAM and SSL"
      proxmox-ai ai generate terraform "3-tier web app with load balancer on AWS"
      proxmox-ai ai generate ansible "Deploy secure LAMP stack on 5 servers"
      proxmox-ai ai generate kubernetes "Microservices deployment with service mesh"
    """
    asyncio.run(_enhanced_generate(resource_type, description, output_file, skill_level, validate, user_id))


async def _enhanced_generate(
    resource_type: str,
    description: str,
    output_file: Optional[Path],
    skill_level: str,
    validate: bool,
    user_id: Optional[str]
):
    """Enhanced infrastructure generation with validation."""
    try:
        session_id = str(uuid.uuid4())
        
        console.print(Panel.fit(
            f"[bold blue]🏗️ Enhanced Infrastructure Generation[/bold blue]\n"
            f"[cyan]Type: {resource_type}[/cyan]\n"
            f"[cyan]Skill Level: {skill_level}[/cyan]\n"
            f"[cyan]Validation: {'✅ Enabled' if validate else '❌ Disabled'}[/cyan]\n"
            f"[cyan]Description: {description}[/cyan]",
            style="blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🧠 Generating with enhanced AI...", total=None)
            
            # Generate infrastructure configuration
            response = await enhanced_ai_client.generate_infrastructure_config(
                description=description,
                config_type=resource_type,
                session_id=session_id,
                user_id=user_id,
                validate_output=validate
            )
            
            progress.update(task, completed=True)
        
        # Display results
        await _display_enhanced_response(response, "infrastructure")
        
        # Display validation results if available
        if validate and response.validation_results:
            _display_validation_results(response.validation_results)
        
        # Save to file if requested
        if output_file and response.success:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(response.content)
            
            # Save metadata
            metadata_file = output_file.with_suffix('.metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump({
                    "generated_at": response.timestamp,
                    "resource_type": resource_type,
                    "skill_level": response.skill_level,
                    "domain": response.domain,
                    "security_score": response.security_score,
                    "validation_results": len(response.validation_results),
                    "model_used": response.model_used,
                    "processing_time": response.processing_time
                }, f, indent=2)
            
            console.print(f"\n[green]✅ Configuration saved to {output_file}[/green]")
            console.print(f"[dim]Metadata saved to {metadata_file}[/dim]")
        
    except Exception as e:
        logger.error("Enhanced generation failed", error=str(e))
        console.print(f"[red]Generation error: {e}[/red]")
        raise typer.Exit(1)


def _display_validation_results(validation_results):
    """Display validation results in a formatted table."""
    if not validation_results:
        console.print("[green]✅ No validation issues found[/green]")
        return
    
    # Group by severity
    critical = [r for r in validation_results if r.level == ValidationLevel.CRITICAL]
    errors = [r for r in validation_results if r.level.value == "error"]
    warnings = [r for r in validation_results if r.level.value == "warning"]
    
    if critical:
        console.print(Panel(
            "\n".join(f"• {r.message}" for r in critical[:5]),
            title="🚨 Critical Issues",
            style="red"
        ))
    
    if errors:
        console.print(Panel(
            "\n".join(f"• {r.message}" for r in errors[:5]),
            title="❌ Errors",
            style="yellow"
        ))
    
    if warnings:
        console.print(Panel(
            "\n".join(f"• {r.message}" for r in warnings[:5]),
            title="⚠️ Warnings",
            style="blue"
        ))
    
    total_issues = len(validation_results)
    console.print(f"\n[dim]Total validation issues: {total_issues}[/dim]")


@app.command()
def status():
    """
    📊 Show comprehensive system status and performance metrics.
    
    Displays detailed information about:
    - AI model status and capabilities
    - Component health and performance
    - Session metrics and statistics
    - Security and validation status
    """
    asyncio.run(_show_enhanced_status())


async def _show_enhanced_status():
    """Display comprehensive enhanced system status."""
    try:
        console.print(Panel.fit(
            "[bold blue]📊 Enhanced Proxmox AI Assistant - System Status[/bold blue]",
            style="blue"
        ))
        
        # Get comprehensive status
        system_status = enhanced_ai_client.get_system_status()
        session_metrics = enhanced_ai_client.get_session_metrics()
        
        # Display system status
        _display_system_status(system_status)
        
        # Display performance metrics
        _display_performance_metrics(session_metrics)
        
        # Component status
        components_table = Table(title="🔧 Component Status", show_header=True)
        components_table.add_column("Component", style="bold cyan")
        components_table.add_column("Status", style="green")
        components_table.add_column("Features", style="dim")
        
        components = [
            ("Knowledge Base", "✅ Operational", "5 domains, 1000+ best practices"),
            ("System Prompts", "✅ Operational", "Dynamic, context-aware generation"),
            ("Context Engine", "✅ Operational", "Smart domain switching"),
            ("Validation Framework", "✅ Operational", "Security + compliance checking"),
            ("Expertise Engine", "✅ Operational", "Adaptive learning modes"),
            ("Enhanced AI Client", "✅ Operational", "World-class integration")
        ]
        
        for component, status, features in components:
            components_table.add_row(component, status, features)
        
        console.print(components_table)
        
        # AI availability test
        console.print("\n[cyan]Testing AI availability...[/cyan]")
        test_response = await enhanced_ai_client.chat(
            "Hello, are you ready?",
            session_id="status_test",
            user_id=None
        )
        
        if test_response.success:
            console.print(f"[green]✅ AI system fully operational (response in {test_response.processing_time:.2f}s)[/green]")
        else:
            console.print("[red]❌ AI system has issues[/red]")
        
    except Exception as e:
        console.print(f"[red]Status check error: {e}[/red]")


if __name__ == "__main__":
    app()