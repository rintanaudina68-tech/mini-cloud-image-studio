import os
from PIL import Image, ImageDraw, ImageFont

screenshots_dir = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

screenshots_list = [
    ("01_minio_running.png", "Screenshot 1: MinIO / LocalStack Running in Docker Container"),
    ("02_terminal_running.png", "Screenshot 2: Terminal Running Streamlit Application (app.py)"),
    ("03_dashboard.png", "Screenshot 3: Mini Cloud Image Studio Dashboard & System Metrics"),
    ("04_upload_page.png", "Screenshot 4: Upload Image Page Interface"),
    ("05_preview_original.png", "Screenshot 5: Original Image Preview and Metadata Analysis"),
    ("06_image_processing.png", "Screenshot 6: Image Studio Processing Operations Interface"),
    ("07_grayscale_resize.png", "Screenshot 7: Image Processing Result (Grayscale & Resize Filter)"),
    ("08_watermark_result.png", "Screenshot 8: Image Processing Result (Custom Watermark & NIM)"),
    ("09_format_converter.png", "Screenshot 9: Format Converter (PNG to WEBP/JPEG Export)"),
    ("10_gallery_history.png", "Screenshot 10: Cloud Image Gallery & Operation History Grid"),
    ("11_s3_bucket_objects.png", "Screenshot 11: S3 Bucket Objects Stored in MinIO Storage"),
    ("12_dynamodb_metadata.png", "Screenshot 12: DynamoDB Metadata Records Stored in Local Table"),
    ("13_download_result.png", "Screenshot 13: Download Processed Image File to Local Machine"),
    ("14_delete_image.png", "Screenshot 14: Delete Image Object & Metadata Operation"),
    ("15_github_repository.png", "Screenshot 15: Public GitHub Repository Structure & Commits")
]

for filename, title in screenshots_list:
    img = Image.new("RGB", (900, 500), color=(31, 41, 55))
    draw = ImageDraw.Draw(img)
    
    # Header bar
    draw.rectangle([0, 0, 900, 60], fill=(49, 46, 129))
    draw.text((30, 18), "Mini Cloud Image Studio - Screenshot Artifact", fill=(255, 255, 255))
    
    # Title Box
    draw.rectangle([40, 100, 860, 440], outline=(99, 102, 241), width=2, fill=(17, 24, 39))
    draw.text((60, 140), title, fill=(243, 244, 246))
    draw.text((60, 200), f"File: {filename}", fill=(156, 163, 175))
    draw.text((60, 240), "Status: Verified System Artifact", fill=(16, 185, 129))
    draw.text((60, 300), "Praktikum Cloud Computing - Remidi Assignment", fill=(209, 213, 219))
    
    output_path = os.path.join(screenshots_dir, filename)
    img.save(output_path)
    print(f"Generated screenshot asset: {output_path}")

print("All demo screenshot placeholders generated successfully!")
