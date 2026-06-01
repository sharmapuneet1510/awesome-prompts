"""C4 Diagram Agent: Generate C4 context, container, and component diagrams."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from context_builder.agents.base_agent import BaseAgent
from context_builder.models import (
    AgentOutput,
    ExecutionContext,
    Node,
    NodeType,
    Edge,
    EdgeType,
    Report,
)


class C4DiagramAgent(BaseAgent):
    """Generate C4 model diagrams for architecture visualization.

    Responsibilities:
    - Generate C4 context diagram (system boundaries)
    - Generate C4 container diagram (major system components)
    - Generate C4 component diagrams (internal architecture)
    - All diagrams use Mermaid syntax
    - Export c4-context.mmd, c4-container.mmd, c4-component-*.mmd files

    The C4 diagrams provide standardized architecture visualization at
    multiple abstraction levels, suitable for stakeholder communication.

    Attributes:
        logger: Logger instance for diagram generation
    """

    def __init__(self):
        """Initialize the C4DiagramAgent."""
        super().__init__(name="C4DiagramAgent")
        self.systems: List[Dict[str, Any]] = []
        self.containers: List[Dict[str, Any]] = []
        self.components: List[Dict[str, Any]] = []

    def execute(self, context: ExecutionContext) -> AgentOutput:
        """Generate C4 diagrams from the graph.

        Args:
            context: ExecutionContext containing the graph.

        Returns:
            AgentOutput with diagram generation results.
        """
        if not self.validate_context(context):
            return AgentOutput(
                status="error",
                message="Invalid execution context",
                errors=["ExecutionContext is None"],
            )

        if not context.graph:
            return AgentOutput(
                status="error",
                message="Missing graph in context",
                errors=["Graph not initialized"],
            )

        try:
            # Identify systems (main system and external systems)
            main_system, external_systems = self._identify_systems(context)

            # Identify containers (major components)
            containers = self._identify_containers(context)

            # Identify components (internal modules)
            components = self._identify_components(context)

            # Generate C4 diagrams
            artifacts = self._generate_c4_diagrams(
                context, main_system, external_systems, containers, components
            )

            # Create report
            self._create_report(context, main_system, external_systems, containers)

            metrics = {
                "main_system": main_system["name"] if main_system else "Unknown",
                "external_systems": len(external_systems),
                "containers": len(containers),
                "components": len(components),
                "diagrams_generated": len(artifacts),
            }

            return AgentOutput(
                status="success",
                message=f"Generated C4 diagrams ({len(artifacts)} artifacts)",
                artifacts=artifacts,
                metrics=metrics,
            )

        except Exception as e:
            self.logger.error(f"C4 diagram generation failed: {str(e)}")
            return AgentOutput(
                status="error",
                message="C4 diagram generation failed",
                errors=[str(e)],
            )

    def _identify_systems(
        self, context: ExecutionContext
    ) -> tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """Identify main system and external systems.

        Args:
            context: ExecutionContext with graph.

        Returns:
            Tuple of (main_system, external_systems).
        """
        main_system = None
        external_systems = []

        # Main system: the primary repository/workspace
        if context.workspace_config:
            main_system = {
                "id": "main_system",
                "name": context.workspace_config.name,
                "description": context.workspace_config.description,
                "type": "system",
            }

        # External systems: external APIs and data sources
        for node in context.graph.nodes:
            if node.type == NodeType.EXTERNAL_API:
                external_systems.append(
                    {
                        "id": node.id,
                        "name": node.name,
                        "type": "external_system",
                    }
                )

        return main_system, external_systems

    def _identify_containers(self, context: ExecutionContext) -> List[Dict[str, Any]]:
        """Identify containers (major system components).

        Args:
            context: ExecutionContext with graph.

        Returns:
            List of container objects.
        """
        containers = []
        container_types = {
            NodeType.DATABASE,
            NodeType.MIDDLEWARE,
            NodeType.MODULE,
            NodeType.PACKAGE,
        }

        seen_containers: Set[str] = set()

        for node in context.graph.nodes:
            if node.type in container_types and node.id not in seen_containers:
                containers.append(
                    {
                        "id": node.id,
                        "name": node.name,
                        "type": node.type.value.lower(),
                        "description": f"{node.type.value.title()} component",
                    }
                )
                seen_containers.add(node.id)

        self.containers = containers
        return containers

    def _identify_components(self, context: ExecutionContext) -> List[Dict[str, Any]]:
        """Identify components (internal modules/classes).

        Args:
            context: ExecutionContext with graph.

        Returns:
            List of component objects.
        """
        components = []
        component_types = {
            NodeType.CLASS,
            NodeType.INTERFACE,
            NodeType.METHOD,
        }

        seen_components: Set[str] = set()

        for node in context.graph.nodes:
            if node.type in component_types and node.id not in seen_components:
                # Limit to high-level components
                if node.type in [NodeType.CLASS, NodeType.INTERFACE]:
                    components.append(
                        {
                            "id": node.id,
                            "name": node.name,
                            "type": node.type.value.lower(),
                            "module": node.module,
                        }
                    )
                    seen_components.add(node.id)

        self.components = components
        return components

    def _generate_c4_diagrams(
        self,
        context: ExecutionContext,
        main_system: Optional[Dict[str, Any]],
        external_systems: List[Dict[str, Any]],
        containers: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
    ) -> List[Path]:
        """Generate all C4 diagrams.

        Args:
            context: ExecutionContext with workspace config.
            main_system: Main system definition.
            external_systems: List of external systems.
            containers: List of containers.
            components: List of components.

        Returns:
            List of generated diagram file paths.
        """
        artifacts = []

        if not context.workspace_config or not context.workspace_config.context_root:
            return artifacts

        context_root = context.workspace_config.context_root

        # Generate C4 Context Diagram
        context_mermaid = self._generate_context_diagram(
            main_system, external_systems
        )
        context_path = context_root / "c4-context.mmd"
        context_path.write_text(context_mermaid)
        artifacts.append(context_path)
        context.generated_files.append(context_path)

        # Generate C4 Container Diagram
        container_mermaid = self._generate_container_diagram(
            main_system, containers
        )
        container_path = context_root / "c4-container.mmd"
        container_path.write_text(container_mermaid)
        artifacts.append(container_path)
        context.generated_files.append(container_path)

        # Generate C4 Component Diagrams (one per container with many components)
        for i, container in enumerate(containers[:3]):  # Limit to 3 component diagrams
            component_mermaid = self._generate_component_diagram(container, components)
            component_path = (
                context_root / f"c4-component-{i+1:02d}-{container['name']}.mmd"
            )
            component_path.write_text(component_mermaid)
            artifacts.append(component_path)
            context.generated_files.append(component_path)

        return artifacts

    def _generate_context_diagram(
        self,
        main_system: Optional[Dict[str, Any]],
        external_systems: List[Dict[str, Any]],
    ) -> str:
        """Generate C4 Context Diagram in Mermaid syntax.

        Args:
            main_system: Main system definition.
            external_systems: List of external systems.

        Returns:
            Mermaid diagram syntax.
        """
        lines = [
            "graph TB",
            "    subgraph System",
            f'        Main["<b>{main_system["name"]}</b><br/>{main_system["description"]}"]',
            "    end",
        ]

        # Add external systems
        for i, ext_sys in enumerate(external_systems[:5]):  # Limit to 5 external systems
            ext_name = ext_sys["name"].replace(" ", "<br/>")
            lines.append(
                f'    Ext{i}["<b>{ext_sys["name"]}</b><br/>External System"]'
            )

        # Add interactions
        for i in range(min(len(external_systems), 5)):
            lines.append(f"    Main <-->|API Call| Ext{i}")

        # Add users
        lines.append('    User["👤 User"]')
        lines.append('    User -->|Uses| Main')

        # Styling
        lines.append("    style Main fill:#438dd5,stroke:#333,color:#fff")
        for i in range(min(len(external_systems), 5)):
            lines.append(f"    style Ext{i} fill:#999,stroke:#333,color:#fff")
        lines.append("    style User fill:#08427B,stroke:#333,color:#fff")

        return "\n".join(lines)

    def _generate_container_diagram(
        self,
        main_system: Optional[Dict[str, Any]],
        containers: List[Dict[str, Any]],
    ) -> str:
        """Generate C4 Container Diagram in Mermaid syntax.

        Args:
            main_system: Main system definition.
            containers: List of containers.

        Returns:
            Mermaid diagram syntax.
        """
        lines = [
            "graph TB",
            "    subgraph System",
        ]

        # Add containers
        for i, container in enumerate(containers[:6]):  # Limit to 6 containers
            icon = self._get_container_icon(container["type"])
            lines.append(
                f'        C{i}["{icon} {container["name"]}<br/>{container["type"]}"]'
            )

        lines.append("    end")

        # Add container connections
        for i in range(len(containers) - 1):
            if i < 5:  # Only add some connections to avoid clutter
                lines.append(f"        C{i} --> C{i+1}")

        # Styling
        for i in range(min(len(containers), 6)):
            color = self._get_container_color(containers[i]["type"])
            lines.append(f"        style C{i} fill:{color},stroke:#333,color:#fff")

        return "\n".join(lines)

    def _generate_component_diagram(
        self, container: Dict[str, Any], components: List[Dict[str, Any]]
    ) -> str:
        """Generate C4 Component Diagram for a specific container.

        Args:
            container: Container to generate components for.
            components: List of available components.

        Returns:
            Mermaid diagram syntax.
        """
        lines = [
            "graph TB",
            f'    subgraph {container["name"].replace(" ", "")}',
        ]

        # Filter components for this container and limit
        filtered_components = [
            c for c in components
            if c.get("module", "").startswith(container["name"][:3])
        ][:8]

        if not filtered_components:
            # Use all components if no filtering worked
            filtered_components = components[:8]

        # Add components
        for i, comp in enumerate(filtered_components):
            icon = self._get_component_icon(comp["type"])
            lines.append(f'        Comp{i}["{icon} {comp["name"]}"]')

        lines.append("    end")

        # Add component interactions
        for i in range(len(filtered_components) - 1):
            lines.append(f"        Comp{i} --> Comp{i+1}")

        # Styling
        for i in range(len(filtered_components)):
            lines.append(f"        style Comp{i} fill:#85BBF0,stroke:#333,color:#000")

        return "\n".join(lines)

    def _get_container_icon(self, container_type: str) -> str:
        """Get icon for container type.

        Args:
            container_type: Type of container.

        Returns:
            Icon emoji or character.
        """
        icons = {
            "database": "💾",
            "middleware": "📨",
            "module": "📦",
            "package": "📦",
        }
        return icons.get(container_type, "⚙️")

    def _get_component_icon(self, component_type: str) -> str:
        """Get icon for component type.

        Args:
            component_type: Type of component.

        Returns:
            Icon emoji or character.
        """
        icons = {
            "class": "🔷",
            "interface": "🔶",
            "method": "⚡",
        }
        return icons.get(component_type, "•")

    def _get_container_color(self, container_type: str) -> str:
        """Get color for container type.

        Args:
            container_type: Type of container.

        Returns:
            Hex color code.
        """
        colors = {
            "database": "#85BBF0",
            "middleware": "#F08080",
            "module": "#90EE90",
            "package": "#90EE90",
        }
        return colors.get(container_type, "#438DD5")

    def _create_report(
        self,
        context: ExecutionContext,
        main_system: Optional[Dict[str, Any]],
        external_systems: List[Dict[str, Any]],
        containers: List[Dict[str, Any]],
    ) -> None:
        """Create C4 diagram report.

        Args:
            context: ExecutionContext to add report to.
            main_system: Main system definition.
            external_systems: List of external systems.
            containers: List of containers.
        """
        report_content = f"""# C4 Diagram Report

## System Overview

### Main System
- **Name**: {main_system["name"] if main_system else "Unknown"}
- **Description**: {main_system["description"] if main_system else "N/A"}

### External Systems
- **Count**: {len(external_systems)}

"""
        for ext_sys in external_systems[:10]:
            report_content += f"- {ext_sys['name']}\n"

        report_content += f"""
## Containers ({len(containers)})

"""
        for container in containers:
            report_content += f"- **{container['name']}** ({container['type']})\n"

        report_content += """
## Diagrams Generated

- `c4-context.mmd` - System context diagram (system boundaries)
- `c4-container.mmd` - Container diagram (major components)
- `c4-component-*.mmd` - Component diagrams (internal modules)

## Architecture Insights

The C4 model provides standardized architecture visualization:
1. **Context Level**: Shows the system in relation to users and external systems
2. **Container Level**: Shows major system components and their relationships
3. **Component Level**: Shows internal structure within containers
"""

        context.reports["c4_diagram_report"] = Report(
            name="c4-diagrams",
            content=report_content,
            metrics={
                "main_system": main_system["name"] if main_system else "Unknown",
                "external_systems": len(external_systems),
                "containers": len(containers),
                "components": len(self.components),
            },
        )
