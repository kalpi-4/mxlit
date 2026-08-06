"""
Layout management for Mxlit V2 reactive architecture.
Handles one-time UI schema building with component IDs and geometries.
"""

import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ComponentSpec:
    """Specification for a UI component with geometry."""
    id: str
    type: str
    geometry: Dict[str, Any]  # x, y, width, height, etc.
    props: Dict[str, Any]     # component-specific properties
    children: List['ComponentSpec'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


class LayoutManager:
    """
    Manages the UI layout schema built during initialization phase.
    Components are registered with IDs and geometries instead of immediate rendering.
    """

    def __init__(self):
        self.components: Dict[str, ComponentSpec] = {}
        self.root_children: List[str] = []  # IDs of root-level components
        self.current_container_stack: List[str] = []  # Stack for nested containers
        self.next_geometry = {"x": 0, "y": 0, "width": 12, "height": 1}  # Default grid units

    def register_component(self, component_type: str, props: Dict[str, Any],
                          geometry: Optional[Dict[str, Any]] = None,
                          component_id: Optional[str] = None) -> str:
        """
        Register a component in the layout schema.
        Returns the component ID.
        """
        component_id = component_id or str(uuid.uuid4())

        if geometry is None:
            geometry = self.next_geometry.copy()
            # Auto-advance geometry for simple layouts
            self.next_geometry["y"] += self.next_geometry["height"]

        spec = ComponentSpec(
            id=component_id,
            type=component_type,
            geometry=geometry,
            props=props
        )

        self.components[component_id] = spec

        # Add to current container or root
        if self.current_container_stack:
            parent_id = self.current_container_stack[-1]
            self.components[parent_id].children.append(component_id)
        else:
            self.root_children.append(component_id)

        return component_id

    def start_container(self, container_type: str, props: Dict[str, Any],
                       geometry: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a container context (sidebar, columns, etc.).
        Returns the container ID.
        """
        container_id = self.register_component(container_type, props, geometry)
        self.current_container_stack.append(container_id)
        return container_id

    def end_container(self):
        """End the current container context."""
        if self.current_container_stack:
            self.current_container_stack.pop()

    def get_component_spec(self, component_id: str) -> Optional[ComponentSpec]:
        """Get a component specification by ID."""
        return self.components.get(component_id)

    def get_layout_schema(self) -> Dict[str, Any]:
        """
        Get the complete layout schema for serialization/initial rendering.
        """
        return {
            "components": {cid: spec.__dict__ for cid, spec in self.components.items()},
            "root_children": self.root_children
        }

    def update_component_geometry(self, component_id: str, geometry: Dict[str, Any]):
        """Update geometry for a component (for dynamic layouts if needed)."""
        if component_id in self.components:
            self.components[component_id].geometry.update(geometry)


# Global layout manager instance
layout_manager = LayoutManager()