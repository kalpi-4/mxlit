from typing import Callable

from mxlit.components.base import ComponentType, component


@component(ComponentType.IMAGE)
def image(url, width=None) -> tuple[dict, Callable]:
    """Display an image."""
    return ({"url": url, "width": width}, lambda: print(f"[Image: {url}]"))


@component(ComponentType.AUDIO)
def audio(url) -> tuple[dict, Callable]:
    """Display an audio player."""
    return ({"url": url}, lambda: print(f"[Audio: {url}]"))


@component(ComponentType.VIDEO)
def video(url) -> tuple[dict, Callable]:
    """Display a video player."""
    return ({"url": url}, lambda: print(f"[Video: {url}]"))


@component(ComponentType.LOGO)
def logo(url) -> tuple[dict, Callable]:
    """Display a logo image."""
    return ({"url": url}, lambda: print(f"[Logo: {url}]"))
