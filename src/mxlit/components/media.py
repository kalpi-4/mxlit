from mxlit.context import get_context

def image(image, width=None):
    """
    Display an image or list of images.
    `image` can be a URL string or a file path string.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "image",
            "url": image,  # Assuming string URL/path for now
            "width": width
        })
    else:
        print(f"[Image: {image}]")

def audio(data):
    """Display an audio player."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "audio",
            "url": data
        })
    else:
        print(f"[Audio: {data}]")

def video(data):
    """Display a video player."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "video",
            "url": data
        })
    else:
        print(f"[Video: {data}]")

def logo(image):
    """Display a logo."""
    ctx = get_context()
    if ctx:
        ctx.add_component({
            "type": "logo",
            "url": image
        })
    else:
        print(f"[Logo: {image}]")
