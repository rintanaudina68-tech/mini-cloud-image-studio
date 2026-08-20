import io
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance
from typing import Tuple, Optional, Dict, Any
from config.settings import settings

class ImageService:
    """Service wrapper for Pillow image processing operations."""

    @staticmethod
    def validate_and_open(file_bytes: bytes) -> Tuple[bool, Optional[Image.Image], str]:
        """Validate input file bytes and return opened Pillow Image object."""
        try:
            if not file_bytes:
                return False, None, "File content is empty."
            
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()  # Verify integrity
            
            # Reopen after verify() because Pillow requires reopening after verify
            img = Image.open(io.BytesIO(file_bytes))
            
            fmt = (img.format or "").lower()
            if fmt == "jpg":
                fmt = "jpeg"
                
            if fmt not in settings.ALLOWED_EXTENSIONS:
                return False, None, f"Unsupported format '{fmt}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"

            return True, img, "Image validation passed."
        except Exception as e:
            return False, None, f"Invalid or corrupted image file: {str(e)}"

    @staticmethod
    def get_metadata(img: Image.Image, file_name: str, file_size: int) -> Dict[str, Any]:
        """Extract metadata dictionary from opened Pillow Image."""
        fmt = (img.format or "PNG").upper()
        if fmt == "JPG":
            fmt = "JPEG"
        return {
            "file_name": file_name,
            "width": img.width,
            "height": img.height,
            "original_format": fmt,
            "processed_format": fmt,
            "file_size": file_size,
            "mode": img.mode
        }

    @staticmethod
    def resize(img: Image.Image, target_w: int, target_h: int, keep_aspect: bool = True) -> Image.Image:
        """Resize image with option to preserve aspect ratio."""
        if keep_aspect:
            img_copy = img.copy()
            img_copy.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            return img_copy
        else:
            return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    @staticmethod
    def grayscale(img: Image.Image) -> Image.Image:
        """Convert image to grayscale."""
        return ImageOps.grayscale(img)

    @staticmethod
    def sepia(img: Image.Image) -> Image.Image:
        """Apply warm retro sepia color filter to image."""
        rgb_img = img.convert("RGB")
        width, height = rgb_img.size
        pixels = rgb_img.load()

        sepia_img = Image.new("RGB", (width, height))
        sepia_pixels = sepia_img.load()

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)

                sepia_pixels[x, y] = (
                    min(255, tr),
                    min(255, tg),
                    min(255, tb)
                )

        return sepia_img

    @staticmethod
    def invert(img: Image.Image) -> Image.Image:
        """Invert color channels of the image."""
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            rgb_img = Image.merge("RGB", (r, g, b))
            inverted_rgb = ImageOps.invert(rgb_img)
            r_inv, g_inv, b_inv = inverted_rgb.split()
            return Image.merge("RGBA", (r_inv, g_inv, b_inv, a))
        else:
            rgb_img = img.convert("RGB")
            return ImageOps.invert(rgb_img)

    @staticmethod
    def watermark(img: Image.Image, text: str = "", nim: str = "") -> Image.Image:
        """Add text watermark to bottom-right corner of the image."""
        if not text:
            nim_str = f" - NIM: {nim}" if nim else ""
            text = f"Uploaded via Mini Cloud Image Studio{nim_str}"
        elif nim and nim not in text:
            text = f"{text} - NIM: {nim}"

        img_copy = img.convert("RGBA").copy()
        txt_layer = Image.new("RGBA", img_copy.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Scale font size according to image dimensions
        font_size = max(16, int(min(img.width, img.height) * 0.04))
        try:
            # Attempt to use standard truetype font
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        # Calculate bounding box of text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Calculate margin and position (bottom right)
        margin = max(10, int(font_size * 0.5))
        x = img.width - text_w - margin
        y = img.height - text_h - margin

        if x < 0: x = margin
        if y < 0: y = margin

        # Draw semi-transparent background box for contrast
        padding = 6
        draw.rectangle(
            [x - padding, y - padding, x + text_w + padding, y + text_h + padding],
            fill=(0, 0, 0, 140)
        )

        # Draw white text
        draw.text((x, y), text, fill=(255, 255, 255, 230), font=font)

        out = Image.alpha_composite(img_copy, txt_layer)
        if img.mode != "RGBA":
            out = out.convert(img.mode)
        return out

    @staticmethod
    def convert_to_bytes(img: Image.Image, target_format: str = "PNG") -> Tuple[bytes, str]:
        """Export Pillow image to bytes in the specified format (PNG, JPEG, WEBP)."""
        fmt = target_format.upper()
        if fmt == "JPG":
            fmt = "JPEG"

        buffer = io.BytesIO()

        # Handle format specific mode requirements
        if fmt == "JPEG" and img.mode in ("RGBA", "P", "LA"):
            export_img = img.convert("RGB")
        else:
            export_img = img

        export_img.save(buffer, format=fmt, quality=92 if fmt in ("JPEG", "WEBP") else None)
        bytes_data = buffer.getvalue()

        mime_types = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "WEBP": "image/webp"
        }
        mime = mime_types.get(fmt, "image/png")

        return bytes_data, mime

image_service = ImageService()
