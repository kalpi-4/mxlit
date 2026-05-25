from mxlit.context import get_context

def image(image, width=None, class_: str = ""):
    """Display an image.

    Args:
        image: A URL or file-path string pointing to the image.
        width: Optional CSS width value (e.g. ``'200px'``, ``'50%'``).
        class_: Optional Tailwind utility classes applied to the <img> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "image", "url": image, "width": width, "class_": class_})
    else:
        print(f"[Image: {image}]")

def audio(data, class_: str = ""):
    """Display an audio player.

    Args:
        data: A URL or file-path string pointing to the audio file.
        class_: Optional Tailwind utility classes applied to the <audio> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "audio", "url": data, "class_": class_})
    else:
        print(f"[Audio: {data}]")

def video(data, class_: str = ""):
    """Display a video player.

    Args:
        data: A URL or file-path string pointing to the video file.
        class_: Optional Tailwind utility classes applied to the <video> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "video", "url": data, "class_": class_})
    else:
        print(f"[Video: {data}]")

def logo(image, class_: str = ""):
    """Display a logo image.

    Args:
        image: A URL or file-path string pointing to the logo.
        class_: Optional Tailwind utility classes applied to the <img> element.
    """
    ctx = get_context()
    if ctx:
        ctx.add_component({"type": "logo", "url": image, "class_": class_})
    else:
        print(f"[Logo: {image}]")
