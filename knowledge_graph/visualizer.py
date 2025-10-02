"""
GIRAFFE Agent Knowledge Graph Visualization and Export Tools
Advanced visualization and export capabilities for cancer genomics knowledge graphs
"""

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import os
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeGraphVisualizer:
    """
    Comprehensive visualization tools for GIRAFFE knowledge graphs
    """
    
    def __init__(self, knowledge_graph):
        """
        Initialize visualizer with a knowledge graph
        
        Args:
            knowledge_graph: GiraffeKnowledgeGraph instance
        """
        self.kg = knowledge_graph
        self.color_mapping = {
            'gene': '#FF6B6B',           # Red
            'variant': '#4ECDC4',        # Teal
            'disease': '#45B7D1',        # Blue
            'protein': '#96CEB4',        # Green
            'pathway': '#FFEAA7',        # Yellow
            'drug': '#DDA0DD',           # Plum
            'sample': '#FFB347',         # Peach
            'patient': '#87CEEB',        # Sky Blue
            'publication': '#D3D3D3'     # Light Gray
        }
        
        self.shape_mapping = {
            'gene': 'circle',
            'variant': 'square',
            'disease': 'triangle-up',
            'protein': 'diamond',
            'pathway': 'pentagon',
            'drug': 'hexagon',
            'sample': 'circle',
            'patient': 'circle',
            'publication': 'square'
        }
    
    def create_interactive_plot(self, layout: str = 'spring', 
                              filter_entity_types: List[str] = None,
                              highlight_path: List[str] = None,
                              output_file: str = None) -> go.Figure:
        """
        Create interactive Plotly visualization of the knowledge graph
        
        Args:
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai', 'shell')
            filter_entity_types: List of entity types to include
            highlight_path: List of entity IDs to highlight as a path
            output_file: File path to save the HTML visualization
            
        Returns:
            Plotly Figure object
        """
        # Filter graph if needed
        if filter_entity_types:
            nodes_to_include = []
            for node_id, data in self.kg.graph.nodes(data=True):
                if data.get('type') in filter_entity_types:
                    nodes_to_include.append(node_id)
            
            subgraph = self.kg.graph.subgraph(nodes_to_include)
        else:
            subgraph = self.kg.graph
        
        if subgraph.number_of_nodes() == 0:
            logger.warning("No nodes to visualize")
            return go.Figure()
        
        # Calculate layout
        if layout == 'spring':
            pos = nx.spring_layout(subgraph, k=1, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(subgraph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(subgraph)
        elif layout == 'shell':
            # Group nodes by type for shell layout
            shells = []
            entity_types = set(data.get('type', 'unknown') for _, data in subgraph.nodes(data=True))
            for entity_type in entity_types:
                shell = [node for node, data in subgraph.nodes(data=True) 
                        if data.get('type') == entity_type]
                if shell:
                    shells.append(shell)
            pos = nx.shell_layout(subgraph, nlist=shells)
        else:
            pos = nx.spring_layout(subgraph)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in subgraph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Edge information for hover
            edge_type = edge[2].get('type', 'unknown')
            edge_info.append(f"{edge[0]} → {edge[1]} ({edge_type})")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces by entity type
        node_traces = []
        
        for entity_type in set(data.get('type', 'unknown') for _, data in subgraph.nodes(data=True)):
            # Get nodes of this type
            nodes_of_type = [(node, data) for node, data in subgraph.nodes(data=True) 
                           if data.get('type') == entity_type]
            
            if not nodes_of_type:
                continue
            
            node_x = []
            node_y = []
            node_text = []
            node_info = []
            node_colors = []
            
            for node, data in nodes_of_type:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Node label
                node_text.append(data.get('id', node))
                
                # Node hover information
                info = f"<b>{node}</b><br>"
                info += f"Type: {entity_type}<br>"
                
                # Add properties to hover info
                for key, value in data.items():
                    if key not in ['type', 'id', 'added_timestamp']:
                        info += f"{key}: {value}<br>"
                
                # Add connectivity info
                neighbors = list(subgraph.neighbors(node))
                info += f"Connections: {len(neighbors)}"
                
                node_info.append(info)
                
                # Color nodes based on highlight path
                if highlight_path and node in highlight_path:
                    node_colors.append('#FF0000')  # Red for highlighted path
                else:
                    node_colors.append(self.color_mapping.get(entity_type, '#888888'))
            
            # Create trace for this entity type
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                hovertext=node_info,
                marker=dict(
                    size=10,
                    color=node_colors,
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                name=entity_type.title(),
                showlegend=True
            )
            
            node_traces.append(node_trace)
        
        # Create the figure
        fig = go.Figure(
            data=[edge_trace] + node_traces,
            layout=go.Layout(
                title=f'GIRAFFE Knowledge Graph: {self.kg.name}',
                titlefont_size=16,
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text=f"Nodes: {subgraph.number_of_nodes()}, Edges: {subgraph.number_of_edges()}",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
        )
        
        # Save to file if requested
        if output_file:
            fig.write_html(output_file)
            logger.info(f"Interactive visualization saved to {output_file}")
        
        return fig
    
    def create_static_plot(self, layout: str = 'spring', 
                          figsize: Tuple[int, int] = (12, 8),
                          output_file: str = None) -> plt.Figure:
        """
        Create static matplotlib visualization
        
        Args:
            layout: Layout algorithm
            figsize: Figure size tuple
            output_file: File path to save the image
            
        Returns:
            Matplotlib Figure object
        """
        # Calculate layout
        if layout == 'spring':
            pos = nx.spring_layout(self.kg.graph, k=1, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(self.kg.graph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.kg.graph)
        else:
            pos = nx.spring_layout(self.kg.graph)
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Draw edges
        nx.draw_networkx_edges(
            self.kg.graph, pos, 
            edge_color='gray', 
            alpha=0.6, 
            width=0.5,
            ax=ax
        )
        
        # Draw nodes by type
        entity_types = set(data.get('type', 'unknown') for _, data in self.kg.graph.nodes(data=True))
        
        for entity_type in entity_types:
            nodes_of_type = [node for node, data in self.kg.graph.nodes(data=True) 
                           if data.get('type') == entity_type]
            
            if nodes_of_type:
                nx.draw_networkx_nodes(
                    self.kg.graph, pos,
                    nodelist=nodes_of_type,
                    node_color=self.color_mapping.get(entity_type, '#888888'),
                    node_size=300,
                    alpha=0.8,
                    label=entity_type.title(),
                    ax=ax
                )
        
        # Draw labels
        labels = {node: data.get('id', node)[:10] for node, data in self.kg.graph.nodes(data=True)}
        nx.draw_networkx_labels(self.kg.graph, pos, labels, font_size=8, ax=ax)
        
        # Customize plot
        ax.set_title(f'GIRAFFE Knowledge Graph: {self.kg.name}', fontsize=16, fontweight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        ax.axis('off')
        
        plt.tight_layout()
        
        # Save to file if requested
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Static visualization saved to {output_file}")
        
        return fig
    
    def create_statistics_dashboard(self, output_file: str = None) -> go.Figure:
        """
        Create a dashboard with graph statistics and metrics
        
        Args:
            output_file: File path to save the HTML dashboard
            
        Returns:
            Plotly Figure object with subplots
        """
        # Get graph statistics
        stats = self.kg.get_graph_statistics()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Entity Type Distribution', 'Relationship Type Distribution',
                           'Node Degree Distribution', 'Graph Metrics'),
            specs=[[{"type": "pie"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "table"}]]
        )
        
        # Entity type distribution pie chart
        entity_counts = stats.get('entity_counts', {})
        if entity_counts:
            fig.add_trace(
                go.Pie(
                    labels=list(entity_counts.keys()),
                    values=list(entity_counts.values()),
                    marker=dict(colors=[self.color_mapping.get(et, '#888888') for et in entity_counts.keys()])
                ),
                row=1, col=1
            )
        
        # Relationship type distribution pie chart
        relationship_counts = stats.get('relationship_counts', {})
        if relationship_counts:
            fig.add_trace(
                go.Pie(
                    labels=list(relationship_counts.keys()),
                    values=list(relationship_counts.values())
                ),
                row=1, col=2
            )
        
        # Node degree distribution
        degrees = dict(self.kg.graph.degree())
        degree_values = list(degrees.values())
        
        if degree_values:
            fig.add_trace(
                go.Histogram(
                    x=degree_values,
                    nbinsx=20,
                    marker_color='skyblue'
                ),
                row=2, col=1
            )
        
        # Graph metrics table
        metrics_data = [
            ['Total Nodes', stats.get('total_nodes', 0)],
            ['Total Edges', stats.get('total_edges', 0)],
            ['Graph Density', f"{stats.get('density', 0):.4f}"],
            ['Is Connected', stats.get('is_connected', False)],
            ['Average Degree', f"{np.mean(degree_values) if degree_values else 0:.2f}"],
            ['Max Degree', f"{max(degree_values) if degree_values else 0}"],
            ['Min Degree', f"{min(degree_values) if degree_values else 0}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value']),
                cells=dict(values=[[row[0] for row in metrics_data],
                                 [row[1] for row in metrics_data]])
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text=f"GIRAFFE Knowledge Graph Dashboard: {self.kg.name}",
            showlegend=False,
            height=800
        )
        
        # Save to file if requested
        if output_file:
            fig.write_html(output_file)
            logger.info(f"Statistics dashboard saved to {output_file}")
        
        return fig
    
    def export_to_cytoscape(self, output_file: str) -> bool:
        """
        Export graph to Cytoscape-compatible JSON format
        
        Args:
            output_file: Path to save Cytoscape JSON file
            
        Returns:
            True if export was successful
        """
        try:
            cytoscape_data = {
                "elements": {
                    "nodes": [],
                    "edges": []
                }
            }
            
            # Add nodes
            for node_id, data in self.kg.graph.nodes(data=True):
                node_element = {
                    "data": {
                        "id": node_id,
                        "label": data.get('id', node_id),
                        "type": data.get('type', 'unknown'),
                        **{k: str(v) for k, v in data.items() if k not in ['id', 'type']}
                    }
                }
                cytoscape_data["elements"]["nodes"].append(node_element)
            
            # Add edges
            edge_counter = 0
            for source, target, data in self.kg.graph.edges(data=True):
                edge_element = {
                    "data": {
                        "id": f"edge_{edge_counter}",
                        "source": source,
                        "target": target,
                        "type": data.get('type', 'unknown'),
                        **{k: str(v) for k, v in data.items() if k not in ['type']}
                    }
                }
                cytoscape_data["elements"]["edges"].append(edge_element)
                edge_counter += 1
            
            # Save to file
            with open(output_file, 'w') as f:
                json.dump(cytoscape_data, f, indent=2)
            
            logger.info(f"Cytoscape export saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to Cytoscape format: {e}")
            return False
    
    def export_to_gephi(self, output_file: str) -> bool:
        """
        Export graph to Gephi-compatible GEXF format
        
        Args:
            output_file: Path to save GEXF file
            
        Returns:
            True if export was successful
        """
        try:
            # NetworkX can directly write GEXF format
            nx.write_gexf(self.kg.graph, output_file)
            logger.info(f"Gephi export saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to Gephi format: {e}")
            return False
    
    def create_subgraph_visualization(self, center_node: str, radius: int = 2,
                                    output_file: str = None) -> go.Figure:
        """
        Create visualization of a subgraph around a specific node
        
        Args:
            center_node: Node ID to center the subgraph around
            radius: Maximum distance from center node to include
            output_file: File path to save the visualization
            
        Returns:
            Plotly Figure object
        """
        if not self.kg.graph.has_node(center_node):
            logger.error(f"Node {center_node} not found in graph")
            return go.Figure()
        
        # Get subgraph within radius
        try:
            subgraph_nodes = nx.single_source_shortest_path_length(
                self.kg.graph, center_node, cutoff=radius
            ).keys()
            subgraph = self.kg.graph.subgraph(subgraph_nodes)
        except Exception as e:
            logger.error(f"Failed to create subgraph: {e}")
            return go.Figure()
        
        # Create temporary KG visualizer for subgraph
        temp_kg = type('TempKG', (), {
            'graph': subgraph,
            'name': f"Subgraph around {center_node}"
        })()
        
        temp_visualizer = KnowledgeGraphVisualizer(temp_kg)
        
        # Create visualization with highlighted center node
        fig = temp_visualizer.create_interactive_plot(
            highlight_path=[center_node],
            output_file=output_file
        )
        
        return fig


class KnowledgeGraphExporter:
    """
    Export knowledge graph to various formats for different applications
    """
    
    def __init__(self, knowledge_graph):
        """
        Initialize exporter with knowledge graph
        
        Args:
            knowledge_graph: GiraffeKnowledgeGraph instance
        """
        self.kg = knowledge_graph
    
    def export_to_csv(self, output_dir: str) -> bool:
        """
        Export graph as CSV files (nodes.csv and edges.csv)
        
        Args:
            output_dir: Directory to save CSV files
            
        Returns:
            True if export was successful
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Export nodes
            nodes_data = []
            for node_id, data in self.kg.graph.nodes(data=True):
                node_row = {'node_id': node_id, **data}
                nodes_data.append(node_row)
            
            nodes_df = pd.DataFrame(nodes_data)
            nodes_file = os.path.join(output_dir, 'nodes.csv')
            nodes_df.to_csv(nodes_file, index=False)
            
            # Export edges
            edges_data = []
            for source, target, data in self.kg.graph.edges(data=True):
                edge_row = {'source': source, 'target': target, **data}
                edges_data.append(edge_row)
            
            edges_df = pd.DataFrame(edges_data)
            edges_file = os.path.join(output_dir, 'edges.csv')
            edges_df.to_csv(edges_file, index=False)
            
            logger.info(f"CSV export completed in {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False
    
    def export_summary_report(self, output_file: str) -> bool:
        """
        Export comprehensive text summary report
        
        Args:
            output_file: Path to save the report
            
        Returns:
            True if export was successful
        """
        try:
            stats = self.kg.get_graph_statistics()
            
            report = f"""
GIRAFFE Knowledge Graph Summary Report
=====================================
Generated: {datetime.now().isoformat()}
Graph Name: {self.kg.name}

GRAPH STATISTICS
----------------
Total Nodes: {stats.get('total_nodes', 0)}
Total Edges: {stats.get('total_edges', 0)}
Density: {stats.get('density', 0):.4f}
Connected: {stats.get('is_connected', False)}

ENTITY TYPE DISTRIBUTION
------------------------
"""
            
            for entity_type, count in stats.get('entity_counts', {}).items():
                percentage = (count / stats.get('total_nodes', 1)) * 100
                report += f"{entity_type.title()}: {count} ({percentage:.1f}%)\n"
            
            report += "\nRELATIONSHIP TYPE DISTRIBUTION\n"
            report += "------------------------------\n"
            
            for rel_type, count in stats.get('relationship_counts', {}).items():
                percentage = (count / stats.get('total_edges', 1)) * 100
                report += f"{rel_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n"
            
            # Add top connected nodes
            degrees = dict(self.kg.graph.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
            
            report += "\nTOP CONNECTED NODES\n"
            report += "-------------------\n"
            
            for node, degree in top_nodes:
                node_type = self.kg.graph.nodes[node].get('type', 'unknown')
                report += f"{node} ({node_type}): {degree} connections\n"
            
            # Save report
            with open(output_file, 'w') as f:
                f.write(report)
            
            logger.info(f"Summary report saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create summary report: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # This would be used with an actual knowledge graph instance
    pass