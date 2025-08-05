"""
Multi-Modal AI Engine for Infrastructure Visualization and Analysis.

This module provides advanced multi-modal AI capabilities that combine text processing
with diagram generation, infrastructure visualization, and visual analysis optimized
for Intel N150 hardware constraints.
"""

import os
import json
import time
import asyncio
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

import structlog
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow
import networkx as nx
import graphviz
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Visualization libraries
import seaborn as sns
from matplotlib.animation import FuncAnimation
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Optional dependencies for advanced features
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from ..core.hardware_detector import hardware_detector
from ..core.performance_monitor import PerformanceMonitor

logger = structlog.get_logger(__name__)


@dataclass
class VisualizationRequest:
    """Request for infrastructure visualization."""
    
    description: str
    visualization_type: str  # 'network', 'architecture', 'deployment', 'monitoring'
    complexity_level: str = "intermediate"  # 'beginner', 'intermediate', 'expert'
    output_format: str = "png"  # 'png', 'svg', 'interactive', 'ascii'
    style_theme: str = "professional"  # 'professional', 'minimal', 'dark', 'colorful'
    include_annotations: bool = True
    width: int = 1200
    height: int = 800
    dpi: int = 150


@dataclass 
class VisualizationResult:
    """Result of visualization generation."""
    
    image_data: Optional[bytes]
    image_path: Optional[str]
    description: str
    metadata: Dict[str, Any]
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    interactive_elements: Optional[Dict[str, Any]] = None


@dataclass
class InfrastructureComponent:
    """Infrastructure component for visualization."""
    
    name: str
    component_type: str  # 'vm', 'container', 'service', 'network', 'storage'
    position: Tuple[float, float]
    size: Tuple[float, float] = (100, 60)
    properties: Dict[str, Any] = None
    connections: List[str] = None
    status: str = "active"  # 'active', 'inactive', 'warning', 'error'
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.connections is None:
            self.connections = []


class InfrastructureDiagramGenerator:
    """Generate infrastructure diagrams with professional styling."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.color_schemes = self._initialize_color_schemes()
        self.component_icons = self._initialize_component_icons()
        
        # Optimize for Intel N150 - use simple rendering
        self.use_high_quality = hardware_detector.specs.available_memory_gb > 6.0
        
        logger.info(
            "Infrastructure diagram generator initialized",
            high_quality_rendering=self.use_high_quality,
            available_memory=hardware_detector.specs.available_memory_gb
        )
    
    def _initialize_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Initialize color schemes for different themes."""
        return {
            'professional': {
                'background': '#f8f9fa',
                'vm': '#4a90e2',
                'container': '#50c878',
                'service': '#ff6b35',
                'network': '#8a2be2',
                'storage': '#ffa500',
                'connection': '#666666',
                'text': '#333333',
                'accent': '#007acc'
            },
            'dark': {
                'background': '#2c3e50',
                'vm': '#3498db',
                'container': '#27ae60',
                'service': '#e74c3c',
                'network': '#9b59b6',
                'storage': '#f39c12',
                'connection': '#bdc3c7',
                'text': '#ecf0f1',
                'accent': '#1abc9c'
            },
            'minimal': {
                'background': '#ffffff',
                'vm': '#2c3e50',
                'container': '#34495e',
                'service': '#7f8c8d',
                'network': '#95a5a6',
                'storage': '#bdc3c7',
                'connection': '#95a5a6',
                'text': '#2c3e50',
                'accent': '#3498db'
            }
        }
    
    def _initialize_component_icons(self) -> Dict[str, str]:
        """Initialize ASCII icons for components (for low-resource mode)."""
        return {
            'vm': '🖥️',
            'container': '📦',
            'service': '⚙️',
            'network': '🌐',
            'storage': '💾',
            'database': '🗄️',
            'load_balancer': '⚖️',
            'firewall': '🛡️',
            'monitor': '📊'
        }
    
    async def generate_network_diagram(self, 
                                     components: List[InfrastructureComponent],
                                     request: VisualizationRequest) -> VisualizationResult:
        """Generate network topology diagram."""
        start_time = time.time()
        
        try:
            logger.info("Generating network diagram", components=len(components))
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(request.width/100, request.height/100), 
                                 dpi=request.dpi if self.use_high_quality else 72)
            
            # Set theme colors
            colors = self.color_schemes[request.style_theme]
            fig.patch.set_facecolor(colors['background'])
            ax.set_facecolor(colors['background'])
            
            # Draw components
            for component in components:
                self._draw_component(ax, component, colors)
            
            # Draw connections
            self._draw_connections(ax, components, colors)
            
            # Add title and labels
            if request.include_annotations:
                ax.set_title(f"Network Topology - {request.description}", 
                           fontsize=16, color=colors['text'], pad=20)
            
            # Remove axis
            ax.set_xlim(0, request.width)
            ax.set_ylim(0, request.height)
            ax.axis('off')
            
            # Save to bytes
            image_buffer = BytesIO()
            plt.tight_layout()
            plt.savefig(image_buffer, format=request.output_format, 
                       facecolor=colors['background'], 
                       bbox_inches='tight', 
                       dpi=request.dpi if self.use_high_quality else 72)
            plt.close()
            
            image_data = image_buffer.getvalue()
            image_buffer.close()
            
            processing_time = time.time() - start_time
            
            return VisualizationResult(
                image_data=image_data,
                image_path=None,
                description=f"Network diagram with {len(components)} components",
                metadata={
                    'components_count': len(components),
                    'visualization_type': 'network',
                    'theme': request.style_theme,
                    'dimensions': (request.width, request.height)
                },
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error("Network diagram generation failed", error=str(e))
            return VisualizationResult(
                image_data=None,
                image_path=None,
                description="Failed to generate network diagram",
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def _draw_component(self, ax, component: InfrastructureComponent, colors: Dict[str, str]):
        """Draw individual infrastructure component."""
        x, y = component.position
        width, height = component.size
        
        # Get component color
        component_color = colors.get(component.component_type, colors['accent'])
        
        # Draw component box
        if component.status == 'error':
            edge_color = '#e74c3c'
            line_width = 3
        elif component.status == 'warning':
            edge_color = '#f39c12'
            line_width = 2
        else:
            edge_color = component_color
            line_width = 1
        
        # Create rounded rectangle
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=5",
            facecolor=component_color,
            edgecolor=edge_color,
            linewidth=line_width,
            alpha=0.8
        )
        ax.add_patch(box)
        
        # Add component name
        ax.text(x, y, component.name, 
               ha='center', va='center', 
               fontsize=10, color='white', 
               weight='bold')
        
        # Add component type icon (if available)
        icon = self.component_icons.get(component.component_type, '⚡')
        ax.text(x, y - 20, icon, 
               ha='center', va='center', 
               fontsize=12)
    
    def _draw_connections(self, ax, components: List[InfrastructureComponent], colors: Dict[str, str]):
        """Draw connections between components."""
        component_positions = {comp.name: comp.position for comp in components}
        
        for component in components:
            if not component.connections:
                continue
                
            start_pos = component.position
            
            for connection in component.connections:
                if connection in component_positions:
                    end_pos = component_positions[connection]
                    
                    # Draw connection line
                    ax.plot([start_pos[0], end_pos[0]], 
                           [start_pos[1], end_pos[1]], 
                           color=colors['connection'], 
                           linewidth=2, 
                           alpha=0.7)
                    
                    # Add arrow
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    ax.annotate('', xy=end_pos, xytext=start_pos,
                              arrowprops=dict(arrowstyle='->', 
                                            color=colors['connection'],
                                            lw=1.5))
    
    async def generate_architecture_diagram(self, 
                                          description: str,
                                          request: VisualizationRequest) -> VisualizationResult:
        """Generate system architecture diagram from description."""
        start_time = time.time()
        
        try:
            logger.info("Generating architecture diagram", description=description[:100])
            
            # Parse description to extract components
            components = await self._parse_architecture_description(description)
            
            # Use GraphViz for professional architecture diagrams
            if self.use_high_quality:
                return await self._generate_graphviz_diagram(components, request)
            else:
                return await self._generate_simple_architecture(components, request)
                
        except Exception as e:
            logger.error("Architecture diagram generation failed", error=str(e))
            return VisualizationResult(
                image_data=None,
                image_path=None,
                description="Failed to generate architecture diagram",
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def _parse_architecture_description(self, description: str) -> List[InfrastructureComponent]:
        """Parse text description to extract architecture components."""
        components = []
        
        # Simple keyword-based parsing (can be enhanced with NLP)
        keywords = {
            'vm': ['vm', 'virtual machine', 'server', 'host'],
            'container': ['container', 'docker', 'pod', 'kubernetes'],
            'service': ['service', 'api', 'microservice', 'application'],
            'database': ['database', 'db', 'mysql', 'postgresql', 'mongodb'],
            'storage': ['storage', 'disk', 'volume', 'nfs', 'ceph'],
            'network': ['network', 'subnet', 'vlan', 'switch', 'router'],
            'load_balancer': ['load balancer', 'lb', 'proxy', 'nginx', 'haproxy'],
            'firewall': ['firewall', 'security', 'iptables', 'pfsense']
        }
        
        description_lower = description.lower()
        component_id = 0
        
        for comp_type, kwords in keywords.items():
            for keyword in kwords:
                if keyword in description_lower:
                    # Estimate position (simple grid layout)
                    row = component_id // 3
                    col = component_id % 3
                    x = 200 + col * 300
                    y = 200 + row * 200
                    
                    component = InfrastructureComponent(
                        name=f"{comp_type.title()}-{component_id}",
                        component_type=comp_type,
                        position=(x, y),
                        properties={'detected_from': keyword}
                    )
                    components.append(component)
                    component_id += 1
                    break  # Only add one component per type per keyword
        
        # If no components detected, create a basic setup
        if not components:
            components = [
                InfrastructureComponent("Web Server", "vm", (300, 400)),
                InfrastructureComponent("Database", "database", (600, 400)),
                InfrastructureComponent("Load Balancer", "load_balancer", (150, 200)),
            ]
            components[0].connections = ["Database"]
            components[2].connections = ["Web Server"]
        
        return components
    
    async def _generate_graphviz_diagram(self, 
                                       components: List[InfrastructureComponent],
                                       request: VisualizationRequest) -> VisualizationResult:
        """Generate professional diagram using GraphViz."""
        try:
            # Create GraphViz diagram
            dot = graphviz.Digraph(comment='Infrastructure Architecture')
            dot.attr(rankdir='TB', size='10,8', dpi='150')
            dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
            
            colors = self.color_schemes[request.style_theme]
            
            # Add nodes
            for component in components:
                color = colors.get(component.component_type, colors['accent'])
                dot.node(component.name, component.name, 
                        fillcolor=color, fontcolor='white')
            
            # Add edges
            for component in components:
                for connection in component.connections:
                    dot.edge(component.name, connection)
            
            # Render to bytes
            image_data = dot.pipe(format=request.output_format)
            
            return VisualizationResult(
                image_data=image_data,
                image_path=None,
                description=f"Architecture diagram with {len(components)} components",
                metadata={
                    'components_count': len(components),
                    'visualization_type': 'architecture',
                    'engine': 'graphviz'
                },
                processing_time=time.time(),
                success=True
            )
            
        except Exception as e:
            logger.warning("GraphViz diagram failed, falling back to simple", error=str(e))
            return await self._generate_simple_architecture(components, request)
    
    async def _generate_simple_architecture(self, 
                                          components: List[InfrastructureComponent],
                                          request: VisualizationRequest) -> VisualizationResult:
        """Generate simple architecture diagram for low-resource systems."""
        start_time = time.time()
        
        # Create simple matplotlib diagram
        fig, ax = plt.subplots(figsize=(10, 8), dpi=72)  # Low DPI for performance
        
        colors = self.color_schemes['minimal']  # Use minimal theme for performance
        fig.patch.set_facecolor(colors['background'])
        ax.set_facecolor(colors['background'])
        
        # Draw components in a simple grid
        for i, component in enumerate(components):
            row = i // 3
            col = i % 3
            x = 150 + col * 250
            y = 500 - row * 150
            
            # Simple rectangle
            rect = Rectangle((x-75, y-40), 150, 80, 
                           facecolor=colors.get(component.component_type, colors['accent']),
                           edgecolor=colors['text'],
                           alpha=0.8)
            ax.add_patch(rect)
            
            # Component name
            ax.text(x, y, component.name, ha='center', va='center',
                   fontsize=10, color=colors['text'], weight='bold')
        
        ax.set_xlim(0, 800)
        ax.set_ylim(0, 600)
        ax.axis('off')
        
        if request.include_annotations:
            ax.set_title(f"Architecture: {request.description}", 
                       fontsize=14, color=colors['text'])
        
        # Save to bytes
        image_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(image_buffer, format='png', facecolor=colors['background'])
        plt.close()
        
        image_data = image_buffer.getvalue()
        image_buffer.close()
        
        return VisualizationResult(
            image_data=image_data,
            image_path=None,
            description=f"Simple architecture with {len(components)} components",
            metadata={
                'components_count': len(components),
                'visualization_type': 'simple_architecture'
            },
            processing_time=time.time() - start_time,
            success=True
        )


class MultiModalAIEngine:
    """Multi-modal AI engine combining text and visual processing."""
    
    def __init__(self):
        self.diagram_generator = InfrastructureDiagramGenerator()
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize sentence transformer if available and memory allows
        self.semantic_model = None
        if (SENTENCE_TRANSFORMERS_AVAILABLE and 
            hardware_detector.specs.available_memory_gb > 4.0):
            try:
                # Use lightweight model for Intel N150
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Semantic similarity model loaded")
            except Exception as e:
                logger.warning("Failed to load semantic model", error=str(e))
        
        logger.info("Multi-modal AI engine initialized")
    
    async def process_multimodal_request(self, 
                                       text_input: str,
                                       image_input: Optional[bytes] = None,
                                       visualization_type: str = "auto") -> Dict[str, Any]:
        """Process multi-modal request combining text and optional image."""
        start_time = time.time()
        
        try:
            # Analyze text input
            text_analysis = await self._analyze_text_input(text_input)
            
            # Process image if provided
            image_analysis = None
            if image_input:
                image_analysis = await self._analyze_image_input(image_input)
            
            # Determine visualization type
            if visualization_type == "auto":
                visualization_type = self._determine_visualization_type(text_analysis)
            
            # Generate visualization
            visualization_request = VisualizationRequest(
                description=text_input,
                visualization_type=visualization_type,
                complexity_level="intermediate",
                style_theme="professional"
            )
            
            visualization_result = await self._generate_visualization(
                visualization_request, text_analysis
            )
            
            # Combine results
            result = {
                'text_analysis': text_analysis,
                'image_analysis': image_analysis,
                'visualization': visualization_result,
                'processing_time': time.time() - start_time,
                'success': True
            }
            
            # Add intelligent recommendations
            result['recommendations'] = await self._generate_intelligent_recommendations(
                text_analysis, image_analysis, visualization_result
            )
            
            return result
            
        except Exception as e:
            logger.error("Multi-modal processing failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    async def _analyze_text_input(self, text: str) -> Dict[str, Any]:
        """Analyze text input for infrastructure intent."""
        analysis = {
            'intent': 'unknown',
            'entities': [],
            'complexity': 'intermediate',
            'keywords': [],
            'infrastructure_type': 'general'
        }
        
        text_lower = text.lower()
        
        # Detect intent
        intent_keywords = {
            'create': ['create', 'build', 'deploy', 'setup', 'provision'],
            'visualize': ['show', 'display', 'diagram', 'visualize', 'draw'],
            'optimize': ['optimize', 'improve', 'enhance', 'tune'],
            'troubleshoot': ['fix', 'debug', 'troubleshoot', 'error', 'issue']
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                analysis['intent'] = intent
                break
        
        # Extract infrastructure entities
        infrastructure_keywords = {
            'vm': ['vm', 'virtual machine', 'server'],
            'container': ['container', 'docker', 'kubernetes', 'pod'],
            'network': ['network', 'subnet', 'vlan', 'firewall'],
            'storage': ['storage', 'disk', 'volume', 'backup'],
            'database': ['database', 'db', 'mysql', 'postgresql']
        }
        
        for entity_type, keywords in infrastructure_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                analysis['entities'].append(entity_type)
        
        # Determine infrastructure type
        if any(word in text_lower for word in ['kubernetes', 'k8s', 'container']):
            analysis['infrastructure_type'] = 'container'
        elif any(word in text_lower for word in ['vm', 'virtual', 'proxmox']):
            analysis['infrastructure_type'] = 'virtualization'
        elif any(word in text_lower for word in ['network', 'firewall', 'router']):
            analysis['infrastructure_type'] = 'networking'
        elif any(word in text_lower for word in ['storage', 'ceph', 'nfs']):
            analysis['infrastructure_type'] = 'storage'
        
        # Determine complexity
        complexity_indicators = {
            'beginner': ['simple', 'basic', 'easy', 'single'],
            'expert': ['advanced', 'complex', 'enterprise', 'cluster', 'ha', 'scalable']
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                analysis['complexity'] = level
                break
        
        # Extract specific keywords
        analysis['keywords'] = [word for word in text_lower.split() 
                              if len(word) > 3 and word.isalpha()]
        
        return analysis
    
    async def _analyze_image_input(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image input for infrastructure diagrams."""
        analysis = {
            'type': 'unknown',
            'components_detected': [],
            'layout': 'unknown',
            'color_scheme': 'unknown'
        }
        
        try:
            # Load image
            image = Image.open(BytesIO(image_data))
            
            # Basic image analysis
            analysis['dimensions'] = image.size
            analysis['format'] = image.format
            analysis['mode'] = image.mode
            
            # Simple color analysis
            if image.mode == 'RGB':
                # Get dominant colors
                colors = image.getcolors(maxcolors=256*256*256)
                if colors:
                    dominant_color = max(colors, key=lambda x: x[0])[1]
                    analysis['dominant_color'] = dominant_color
            
            # Detect if it's likely an infrastructure diagram
            # (This is a simplified approach - could be enhanced with ML)
            if any(keyword in str(image_data).lower() for keyword in ['diagram', 'network', 'server']):
                analysis['type'] = 'infrastructure_diagram'
            
        except Exception as e:
            logger.warning("Image analysis failed", error=str(e))
            analysis['error'] = str(e)
        
        return analysis
    
    def _determine_visualization_type(self, text_analysis: Dict[str, Any]) -> str:
        """Determine appropriate visualization type from text analysis."""
        intent = text_analysis.get('intent', 'unknown')
        entities = text_analysis.get('entities', [])
        infrastructure_type = text_analysis.get('infrastructure_type', 'general')
        
        # Map to visualization types
        if intent == 'visualize' or 'network' in entities:
            return 'network'
        elif infrastructure_type == 'container':
            return 'deployment'
        elif 'monitoring' in text_analysis.get('keywords', []):
            return 'monitoring'
        else:
            return 'architecture'
    
    async def _generate_visualization(self, 
                                    request: VisualizationRequest,
                                    text_analysis: Dict[str, Any]) -> VisualizationResult:
        """Generate appropriate visualization based on request."""
        if request.visualization_type == 'network':
            # Create sample components for network diagram
            components = await self.diagram_generator._parse_architecture_description(request.description)
            return await self.diagram_generator.generate_network_diagram(components, request)
        else:
            # Generate architecture diagram
            return await self.diagram_generator.generate_architecture_diagram(
                request.description, request
            )
    
    async def _generate_intelligent_recommendations(self,
                                                  text_analysis: Dict[str, Any],
                                                  image_analysis: Optional[Dict[str, Any]],
                                                  visualization_result: VisualizationResult) -> List[str]:
        """Generate intelligent recommendations based on analysis."""
        recommendations = []
        
        # Text-based recommendations
        intent = text_analysis.get('intent', 'unknown')
        complexity = text_analysis.get('complexity', 'intermediate')
        entities = text_analysis.get('entities', [])
        
        if intent == 'create':
            recommendations.append("Consider implementing backup strategies for your infrastructure")
            recommendations.append("Ensure proper security hardening for all components")
        
        if 'database' in entities:
            recommendations.append("Implement database replication for high availability")
            recommendations.append("Set up automated database backups")
        
        if 'network' in entities:
            recommendations.append("Configure network segmentation for improved security")
            recommendations.append("Implement network monitoring and alerting")
        
        if complexity == 'expert':
            recommendations.append("Consider implementing Infrastructure as Code for scalability")
            recommendations.append("Set up comprehensive monitoring and observability")
        elif complexity == 'beginner':
            recommendations.append("Start with simple configurations and gradually add complexity")
            recommendations.append("Use automated configuration management tools")
        
        # Image-based recommendations
        if image_analysis and visualization_result.success:
            recommendations.append("Your infrastructure diagram shows good component organization")
            if visualization_result.metadata.get('components_count', 0) > 5:
                recommendations.append("Consider grouping related components for better maintainability")
        
        # Performance recommendations for Intel N150
        if hardware_detector.specs.available_memory_gb < 6.0:
            recommendations.append("For optimal performance on your system, consider lightweight alternatives")
            recommendations.append("Use resource-efficient configurations to maximize performance")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def generate_interactive_dashboard(self, 
                                           infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interactive dashboard data for web interface."""
        try:
            # Create plotly dashboard components
            components = []
            
            # Infrastructure overview
            if 'components' in infrastructure_data:
                component_types = {}
                for comp in infrastructure_data['components']:
                    comp_type = comp.get('type', 'unknown')
                    component_types[comp_type] = component_types.get(comp_type, 0) + 1
                
                # Pie chart for component distribution
                pie_chart = go.Pie(
                    labels=list(component_types.keys()),
                    values=list(component_types.values()),
                    title="Infrastructure Components"
                )
                components.append({
                    'type': 'pie_chart',
                    'data': pie_chart.to_dict(),
                    'title': 'Component Distribution'
                })
            
            # Resource utilization (mock data for demo)
            if hardware_detector.specs:
                memory_usage = [70, 65, 80, 75, 85, 70, 75]  # Mock data
                cpu_usage = [45, 50, 60, 55, 70, 50, 60]     # Mock data
                
                resource_chart = go.Scatter(
                    x=list(range(7)),
                    y=memory_usage,
                    mode='lines+markers',
                    name='Memory Usage (%)',
                    line=dict(color='blue')
                )
                
                components.append({
                    'type': 'line_chart',
                    'data': resource_chart.to_dict(),
                    'title': 'Resource Utilization'
                })
            
            return {
                'success': True,
                'dashboard_components': components,
                'metadata': {
                    'generated_at': time.time(),
                    'component_count': len(components)
                }
            }
            
        except Exception as e:
            logger.error("Dashboard generation failed", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported input and output formats."""
        return {
            'input_formats': {
                'text': ['plain_text', 'markdown', 'yaml', 'json'],
                'image': ['png', 'jpg', 'jpeg', 'svg', 'gif'],
                'data': ['json', 'yaml', 'csv']
            },
            'output_formats': {
                'visualization': ['png', 'svg', 'pdf', 'interactive'],
                'data': ['json', 'yaml', 'csv'],
                'documentation': ['markdown', 'html', 'pdf']
            }
        }


# Global multimodal engine instance
multimodal_engine = None

def get_multimodal_engine() -> MultiModalAIEngine:
    """Get global multimodal engine instance."""
    global multimodal_engine
    
    if multimodal_engine is None:
        multimodal_engine = MultiModalAIEngine()
    
    return multimodal_engine


async def quick_visualize_infrastructure(description: str, 
                                       visualization_type: str = "auto",
                                       style: str = "professional") -> VisualizationResult:
    """Quick infrastructure visualization for CLI usage."""
    engine = get_multimodal_engine()
    
    request = VisualizationRequest(
        description=description,
        visualization_type=visualization_type,
        style_theme=style,
        complexity_level="intermediate"
    )
    
    text_analysis = await engine._analyze_text_input(description)
    return await engine._generate_visualization(request, text_analysis)


# Export main classes and functions
__all__ = [
    'MultiModalAIEngine',
    'InfrastructureDiagramGenerator',
    'VisualizationRequest',
    'VisualizationResult',
    'InfrastructureComponent',
    'get_multimodal_engine',
    'quick_visualize_infrastructure'
]