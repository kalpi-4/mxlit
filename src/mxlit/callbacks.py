"""
Reactive callback system for Mxlit V2.
Decorators and utilities for defining data processing functions with dependencies.
"""

from typing import List, Dict, Any, Callable
import inspect


class CallbackRegistry:
    """Registry for reactive callbacks and their dependencies."""

    def __init__(self):
        self.callbacks: Dict[str, Dict[str, Any]] = {}  # callback_id -> callback info

    def register_callback(self, func: Callable, inputs: List[str], outputs: List[str]) -> str:
        """
        Register a callback function with its input/output dependencies.
        Returns callback ID.
        """
        callback_id = f"{func.__module__}.{func.__name__}"

        self.callbacks[callback_id] = {
            "func": func,
            "inputs": inputs,
            "outputs": outputs,
            "signature": inspect.signature(func)
        }

        return callback_id

    def get_callback(self, callback_id: str) -> Dict[str, Any]:
        """Get callback info by ID."""
        return self.callbacks.get(callback_id)

    def get_all_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered callbacks."""
        return self.callbacks.copy()


# Global callback registry
callback_registry = CallbackRegistry()


def callback(inputs: List[str], outputs: List[str]):
    """
    Decorator to mark a function as a reactive callback.

    @mt.callback(inputs=["filter_id"], outputs=["chart_id"])
    def update_chart(filter_value):
        # Process data and return updates
        return {"chart_id": processed_data}
    """
    def decorator(func: Callable):
        callback_registry.register_callback(func, inputs, outputs)
        # Also register with DAG immediately for dynamic registration
        from mxlit.dag import reactive_dag
        callback_id = f"{func.__module__}.{func.__name__}"
        reactive_dag.register_callback(callback_id, inputs, outputs)
        return func
    return decorator