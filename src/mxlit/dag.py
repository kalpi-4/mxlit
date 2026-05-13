"""
Reactive DAG (Directed Acyclic Graph) engine for Mxlit V2.
Manages dependencies between UI inputs and data processing callbacks.
"""

from typing import Dict, List, Set, Any, Callable
from collections import defaultdict, deque
import asyncio


class ReactiveDAG:
    """
    Manages reactive dependencies between UI components and data callbacks.
    Tracks which callbacks depend on which inputs and which outputs they produce.
    """

    def __init__(self):
        # input_key -> set of callback_ids that depend on it
        self.input_to_callbacks: Dict[str, Set[str]] = defaultdict(set)

        # callback_id -> callback info (from callback_registry)
        self.callbacks: Dict[str, Dict[str, Any]] = {}

        # output_id -> callback_id that produces it
        self.output_to_callback: Dict[str, str] = {}

        # Track execution state
        self.dirty_inputs: Set[str] = set()
        self.executed_callbacks: Set[str] = set()

    def register_callback(self, callback_id: str, inputs: List[str], outputs: List[str]):
        """Register a callback with its dependencies."""
        self.callbacks[callback_id] = {
            "inputs": inputs,
            "outputs": outputs
        }

        # Build reverse mappings
        for input_key in inputs:
            self.input_to_callbacks[input_key].add(callback_id)

        for output_id in outputs:
            self.output_to_callback[output_id] = callback_id

    def mark_input_dirty(self, input_key: str):
        """Mark an input as changed, invalidating dependent callbacks."""
        self.dirty_inputs.add(input_key)

    def get_callbacks_to_execute(self) -> List[str]:
        """
        Get the list of callbacks that need to be executed based on dirty inputs.
        Returns callbacks in topological order.
        """
        # Find all callbacks affected by dirty inputs
        affected_callbacks = set()
        for dirty_input in self.dirty_inputs:
            affected_callbacks.update(self.input_to_callbacks.get(dirty_input, set()))

        # For now, return in registration order (assuming no cycles)
        # TODO: Implement proper topological sorting for complex dependencies
        return list(affected_callbacks)

    async def execute_callbacks(self, callback_registry, session_state) -> Dict[str, Any]:
        """
        Execute the necessary callbacks and return component updates.
        """
        callbacks_to_run = self.get_callbacks_to_execute()
        updates = {}

        for callback_id in callbacks_to_run:
            if callback_id not in callback_registry.callbacks:
                continue

            callback_info = callback_registry.callbacks[callback_id]
            func = callback_info["func"]
            inputs = callback_info["inputs"]

            # Prepare arguments from session_state
            args = []
            for input_key in inputs:
                args.append(session_state.get(input_key))

            try:
                # Execute callback
                result = func(*args)
                if isinstance(result, dict):
                    updates.update(result)
                elif isinstance(result, (list, tuple)):
                    # Assume outputs are in same order as declared
                    for i, output_id in enumerate(callback_info["outputs"]):
                        if i < len(result):
                            updates[output_id] = result[i]
                else:
                    # Single output
                    if callback_info["outputs"]:
                        updates[callback_info["outputs"][0]] = result

            except Exception as e:
                # Log error but continue
                print(f"Error executing callback {callback_id}: {e}")

        # Clear dirty state
        self.dirty_inputs.clear()
        self.executed_callbacks.update(callbacks_to_run)

        return updates

    def reset(self):
        """Reset execution state for new request."""
        self.dirty_inputs.clear()
        self.executed_callbacks.clear()


# Global DAG instance
reactive_dag = ReactiveDAG()