import uuid
from datetime import datetime
import streamlit as st

def format_bytes(size_bytes: int) -> str:
    """Format size in bytes into human readable string (KB, MB, GB)."""
    if size_bytes <= 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    p = float(size_bytes)
    while p >= 1024.0 and i < len(size_name) - 1:
        p /= 1024.0
        i += 1
    return f"{p:.2f} {size_name[i]}"

def format_datetime(iso_str: str) -> str:
    """Format ISO datetime string into human readable format."""
    if not iso_str:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d %b %Y, %H:%M:%S")
    except Exception:
        return iso_str

def generate_image_id(prefix: str = "IMG") -> str:
    """Generate unique image ID using timestamp and short UUID."""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    short_uuid = str(uuid.uuid4())[:6].upper()
    return f"{prefix}-{ts}-{short_uuid}"

def inject_custom_css():
    """Inject modern premium custom CSS styling into Streamlit UI."""
    css = """
    <style>
    /* Global Container Styles */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    /* Header Gradient Banner */
    .studio-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
        color: #ffffff;
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .studio-header h1 {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 6px;
    }
    .studio-header p {
        color: #c7d2fe;
        font-size: 1rem;
        margin: 0;
    }

    /* Metric Cards */
    .metric-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        border-color: #6366f1;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f9fafb;
    }
    .metric-subtitle {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 4px;
    }

    /* Status Badges */
    .status-badge-online {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-badge-offline {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Section Cards */
    .content-box {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    /* Footer */
    .studio-footer {
        text-align: center;
        padding: 24px;
        color: #6b7280;
        font-size: 0.85rem;
        border-top: 1px solid #374151;
        margin-top: 40px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
