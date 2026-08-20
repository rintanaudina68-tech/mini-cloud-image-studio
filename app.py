import io
from datetime import datetime
import streamlit as st
from PIL import Image

from config.settings import settings
from services.s3_service import s3_service
from services.dynamodb_service import dynamodb_service
from services.image_service import image_service
from utils.helpers import (
    format_bytes,
    format_datetime,
    generate_image_id,
    inject_custom_css
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Mini Cloud Image Studio",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Styling
inject_custom_css()

def initialize_cloud_services():
    """Attempt automatic startup initialization for local S3 bucket and DynamoDB table."""
    s3_connected, s3_msg = s3_service.check_connection()
    db_connected, db_msg = dynamodb_service.check_connection()

    s3_ready = False
    db_ready = False

    if s3_connected:
        s3_ready, _ = s3_service.ensure_bucket_exists()
    if db_connected:
        db_ready, _ = dynamodb_service.ensure_table_exists()

    return {
        "s3_connected": s3_connected,
        "s3_ready": s3_ready,
        "s3_msg": s3_msg,
        "db_connected": db_connected,
        "db_ready": db_ready,
        "db_msg": db_msg,
    }

# Run Service Check
cloud_status = initialize_cloud_services()

# =====================================================================
# SIDEBAR NAVIGATION & CLOUD DIAGNOSTICS
# =====================================================================
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/cloud-storage.png", width=70)
    st.title("Mini Cloud Studio")
    st.caption("Cloud Computing Remedial Assignment")
    
    st.divider()
    
    navigation = st.radio(
        "Navigation Menu",
        options=["📊 Dashboard", "📤 Upload Image", "🎨 Image Studio", "🖼️ Gallery & History", "⚙️ Cloud Status"],
        index=0
    )
    
    st.divider()
    
    st.markdown("### ☁️ Environment Status")
    
    if cloud_status["s3_connected"]:
        st.markdown('S3 Endpoint: <span class="status-badge-online">ONLINE</span>', unsafe_allow_html=True)
    else:
        st.markdown('S3 Endpoint: <span class="status-badge-offline">OFFLINE</span>', unsafe_allow_html=True)

    if cloud_status["db_connected"]:
        st.markdown('DynamoDB: <span class="status-badge-online">ONLINE</span>', unsafe_allow_html=True)
    else:
        st.markdown('DynamoDB: <span class="status-badge-offline">OFFLINE</span>', unsafe_allow_html=True)

    st.caption(f"S3: `{settings.S3_ENDPOINT_URL}`")
    st.caption(f"DynamoDB: `{settings.DYNAMODB_ENDPOINT_URL}`")

    st.divider()
    st.markdown("**Student Identity**")
    student_nim = st.text_input("NIM Mahasiswa", value="32602400035", placeholder="e.g., 32602400035", help="Masukkan NIM Anda untuk watermark otomatis")

# Header Banner
st.markdown(
    f"""
    <div class="studio-header">
        <h1>Mini Cloud Image Studio</h1>
        <p>A Cloud-Native Image Processing & Metadata Management System powered by Python, Streamlit, Boto3, S3, & DynamoDB</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Global Cloud Warning if services are unavailable
if not cloud_status["s3_connected"] or not cloud_status["db_connected"]:
    st.warning(
        "⚠️ **Environment Cloud Lokal Belum Siap / Belum Dijalankan!**\n\n"
        "Beberapa fitur cloud storage dan database membutuhkan container local cloud (MinIO / LocalStack).\n"
        "Silakan jalankan Docker Compose dengan perintah:\n\n"
        "```bash\ndocker compose up -d\n```\n"
        "Jika Anda belum menjalankan Docker, Anda masih dapat memicu auto-reconnect di menu **⚙️ Cloud Status** setelah Docker diaktifkan."
    )

# =====================================================================
# TAB 1: DASHBOARD
# =====================================================================
if navigation == "📊 Dashboard":
    st.subheader("📊 System Dashboard & Cloud Statistics")
    
    # Load Stats from DynamoDB and S3
    metadata_list = []
    s3_objects = []
    if cloud_status["db_connected"]:
        metadata_list, _ = dynamodb_service.list_image_metadata()
    if cloud_status["s3_connected"]:
        s3_objects, _ = s3_service.list_images()

    total_images = len(metadata_list)
    processed_images = len([m for m in metadata_list if m.get("operation") != "Original Upload"])
    total_bytes = sum([int(m.get("file_size", 0)) for m in metadata_list])

    # Top Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Uploaded</div>
                <div class="metric-value">{total_images}</div>
                <div class="metric-subtitle">Images in DynamoDB</div>
            </div>
            """, unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Processed Images</div>
                <div class="metric-value">{processed_images}</div>
                <div class="metric-subtitle">Manipulations performed</div>
            </div>
            """, unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Cloud Storage Used</div>
                <div class="metric-value">{format_bytes(total_bytes)}</div>
                <div class="metric-subtitle">Total S3 payload</div>
            </div>
            """, unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">S3 Bucket Objects</div>
                <div class="metric-value">{len(s3_objects)}</div>
                <div class="metric-subtitle">Bucket: {settings.S3_BUCKET_NAME}</div>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Information & Quick Actions
    col_info, col_arch = st.columns([1, 1])
    
    with col_info:
        st.markdown("### 🛠️ Configured Cloud Services")
        st.info(
            f"**S3 Bucket:** `{settings.S3_BUCKET_NAME}`\n\n"
            f"**DynamoDB Table:** `{settings.DYNAMODB_TABLE_NAME}` (Key: `image_id`)\n\n"
            f"**S3 Endpoint:** `{settings.S3_ENDPOINT_URL}`\n\n"
            f"**DynamoDB Endpoint:** `{settings.DYNAMODB_ENDPOINT_URL}`"
        )

    with col_arch:
        st.markdown("### 🏗️ Application Architecture")
        st.markdown(
            """
            ```text
            Streamlit Web UI (Browser)
                     │
                     ▼
            Python Backend (Pillow + Boto3)
                     │
             ┌───────┴───────┐
             ▼               ▼
          S3 Bucket      DynamoDB
       (Image Objects)   (Metadata)
             │               │
             └───────┬───────┘
                     ▼
             MinIO / LocalStack
            ```
            """
        )

    st.divider()
    st.markdown("### 🕒 Recent Activity & Image Index")
    if metadata_list:
        table_data = []
        for m in metadata_list[:8]:
            table_data.append({
                "Image ID": m.get("image_id"),
                "File Name": m.get("file_name"),
                "Operation": m.get("operation"),
                "Format": f"{m.get('original_format')} ➔ {m.get('processed_format')}",
                "Resolution": f"{m.get('width')}x{m.get('height')}",
                "Size": format_bytes(int(m.get("file_size", 0))),
                "Uploaded At": format_datetime(m.get("uploaded_at"))
            })
        st.dataframe(table_data, use_container_width=True)
    else:
        st.info("Belum ada data gambar yang tersimpan. Silakan upload gambar pertama Anda pada menu **Upload Image**.")

# =====================================================================
# TAB 2: UPLOAD IMAGE
# =====================================================================
elif navigation == "📤 Upload Image":
    st.subheader("📤 Upload New Image to Cloud Storage")
    
    uploaded_file = st.file_uploader(
        "Pilih file gambar untuk di-upload (PNG, JPG, JPEG, WEBP):",
        type=list(settings.ALLOWED_EXTENSIONS)
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        is_valid, img, err_msg = image_service.validate_and_open(file_bytes)

        if not is_valid:
            st.error(f"❌ Validation Error: {err_msg}")
        else:
            col_prev, col_meta = st.columns([1, 1])

            with col_prev:
                st.markdown("#### 🖼️ Image Preview")
                st.image(img, use_column_width=True, caption=uploaded_file.name)

            with col_meta:
                st.markdown("#### 📋 Extracted File Information")
                meta = image_service.get_metadata(img, uploaded_file.name, len(file_bytes))
                
                st.write(f"**Filename:** `{meta['file_name']}`")
                st.write(f"**Dimensions:** `{meta['width']} x {meta['height']} px`")
                st.write(f"**Format:** `{meta['original_format']}`")
                st.write(f"**Color Mode:** `{meta['mode']}`")
                st.write(f"**File Size:** `{format_bytes(meta['file_size'])}`")

                st.divider()

                if st.button("☁️ Upload to S3 & DynamoDB", type="primary", use_container_width=True):
                    if not cloud_status["s3_connected"] or not cloud_status["db_connected"]:
                        st.error("❌ Gagal upload: Environment cloud lokal tidak terhubung.")
                    else:
                        with st.spinner("Mengunggah gambar ke S3 & menyimpan metadata ke DynamoDB..."):
                            image_id = generate_image_id()
                            ext = meta['original_format'].lower()
                            object_key = f"originals/{image_id}.{ext}"

                            # 1. Upload Object to S3
                            content_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                            s3_ok, s3_err = s3_service.upload_image(file_bytes, object_key, content_type)

                            if not s3_ok:
                                st.error(f"❌ Upload S3 Gagal: {s3_err}")
                            else:
                                # 2. Save Metadata to DynamoDB
                                db_record = {
                                    "image_id": image_id,
                                    "file_name": meta["file_name"],
                                    "object_key": object_key,
                                    "original_format": meta["original_format"],
                                    "processed_format": meta["original_format"],
                                    "operation": "Original Upload",
                                    "width": meta["width"],
                                    "height": meta["height"],
                                    "file_size": meta["file_size"],
                                    "uploaded_at": datetime.now().isoformat(),
                                    "status": "Active"
                                }
                                db_ok, db_err = dynamodb_service.save_image_metadata(db_record)

                                if db_ok:
                                    st.success(f"✅ Gambar berhasil di-upload!\n\n**Image ID:** `{image_id}`\n\n**S3 Object Key:** `{object_key}`")
                                    st.balloons()
                                else:
                                    st.error(f"❌ Menyimpan metadata DynamoDB Gagal: {db_err}")

# =====================================================================
# TAB 3: IMAGE STUDIO (MANIPULATION)
# =====================================================================
elif navigation == "🎨 Image Studio":
    st.subheader("🎨 Image Manipulation & Filter Studio")

    if not cloud_status["s3_connected"] or not cloud_status["db_connected"]:
        st.error("❌ Environment Cloud Lokal belum aktif. Sambungkan MinIO / LocalStack terlebih dahulu.")
    else:
        # Load image metadata list from DynamoDB
        metadata_list, _ = dynamodb_service.list_image_metadata()

        if not metadata_list:
            st.info("Belum ada gambar yang tersedia di cloud. Silakan upload gambar terlebih dahulu di tab **Upload Image**.")
        else:
            # Select image from Cloud Storage
            image_options = {f"{m['file_name']} ({m['image_id']}) - {m['operation']}": m for m in metadata_list}
            selected_option = st.selectbox("Pilih Gambar dari Cloud Storage:", options=list(image_options.keys()))

            selected_meta = image_options[selected_option]

            # Download selected image from S3
            raw_bytes, download_err = s3_service.download_image(selected_meta["object_key"])

            if not raw_bytes:
                st.error(f"❌ Gagal mengunduh gambar dari S3: {download_err}")
            else:
                is_valid, current_img, _ = image_service.validate_and_open(raw_bytes)
                
                if not is_valid or current_img is None:
                    st.error("❌ Gagal memuat gambar untuk diolah.")
                else:
                    st.divider()
                    
                    # Sidebar / Controls for Image Processing Operation
                    col_source, col_process = st.columns([1, 1])

                    with col_source:
                        st.markdown("#### 📷 Gambar Asal")
                        st.image(current_img, use_column_width=True)
                        st.caption(
                            f"ID: `{selected_meta['image_id']}` | "
                            f"Format: `{selected_meta['processed_format']}` | "
                            f"Dimensi: `{current_img.width}x{current_img.height} px`"
                        )

                    with col_process:
                        st.markdown("#### ⚙️ Pilih Operasi Manipulasi")
                        
                        operation = st.selectbox(
                            "Operasi Processing:",
                            ["Resize", "Grayscale", "Sepia", "Invert", "Watermark", "Format Converter"]
                        )

                        processed_img = None
                        target_format = selected_meta.get("processed_format", "PNG")

                        # Operation specific controls
                        if operation == "Resize":
                            st.markdown("##### 📐 Resize Parameters")
                            keep_aspect = st.checkbox("Pertahankan Aspect Ratio", value=True)
                            new_w = st.number_input("Lebar Baru (Width px):", min_value=10, max_value=4000, value=current_img.width)
                            
                            if keep_aspect and current_img.width > 0:
                                calculated_h = int(current_img.height * (new_w / current_img.width))
                                st.info(f"Tinggi dihitung otomatis: `{calculated_h} px`")
                                new_h = calculated_h
                            else:
                                new_h = st.number_input("Tinggi Baru (Height px):", min_value=10, max_value=4000, value=current_img.height)

                            processed_img = image_service.resize(current_img, new_w, new_h, keep_aspect)

                        elif operation == "Grayscale":
                            st.markdown("##### 🌓 Grayscale Filter")
                            st.info("Mengubah warna gambar menjadi hitam-putih (Grayscale).")
                            processed_img = image_service.grayscale(current_img)

                        elif operation == "Sepia":
                            st.markdown("##### ☕ Sepia Filter")
                            st.info("Memberikan efek warna sepia klasik pada gambar.")
                            processed_img = image_service.sepia(current_img)

                        elif operation == "Invert":
                            st.markdown("##### 🔄 Invert Color Filter")
                            st.info("Membalikkan spektrum warna gambar (Invert Colors).")
                            processed_img = image_service.invert(current_img)

                        elif operation == "Watermark":
                            st.markdown("##### 🏷️ Watermark Configuration")
                            custom_watermark = st.text_input(
                                "Teks Watermark (Opsional):",
                                value="Uploaded via Mini Cloud Image Studio"
                            )
                            nim_input = st.text_input("NIM Mahasiswa:", value=student_nim, placeholder="Contoh: 312010001")
                            
                            processed_img = image_service.watermark(
                                current_img,
                                text=custom_watermark,
                                nim=nim_input
                            )

                        elif operation == "Format Converter":
                            st.markdown("##### 🔄 Format Converter")
                            target_format = st.radio(
                                "Pilih Target Format:",
                                options=["PNG", "JPEG", "WEBP"],
                                index=0
                            )
                            processed_img = current_img.copy()

                    # Result Preview Section
                    if processed_img is not None:
                        st.divider()
                        st.markdown("### 👁️ Hasil Processing & Preview")

                        res_bytes, res_mime = image_service.convert_to_bytes(processed_img, target_format)
                        
                        r_col1, r_col2 = st.columns([1, 1])
                        with r_col1:
                            st.image(processed_img, use_column_width=True, caption=f"Hasil Operasi: {operation}")
                        
                        with r_col2:
                            st.markdown("#### 📊 Metadata Hasil Processing")
                            st.write(f"**Operasi:** `{operation}`")
                            st.write(f"**Format Target:** `{target_format}`")
                            st.write(f"**Dimensi Baru:** `{processed_img.width} x {processed_img.height} px`")
                            st.write(f"**Ukuran File Hasil:** `{format_bytes(len(res_bytes))}`")

                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            if st.button("💾 Simpan Hasil Manipulasi ke S3 & DynamoDB", type="primary", use_container_width=True):
                                with st.spinner("Menyimpan hasil ke S3 & meng-update database..."):
                                    new_image_id = generate_image_id("PROC")
                                    ext = target_format.lower()
                                    new_object_key = f"processed/{new_image_id}.{ext}"

                                    # Upload processed bytes to S3
                                    s3_ok, s3_err = s3_service.upload_image(res_bytes, new_object_key, res_mime)

                                    if not s3_ok:
                                        st.error(f"❌ Upload S3 Hasil Gagal: {s3_err}")
                                    else:
                                        # Save metadata item to DynamoDB
                                        db_record = {
                                            "image_id": new_image_id,
                                            "file_name": f"processed_{selected_meta['file_name']}",
                                            "object_key": new_object_key,
                                            "original_format": selected_meta.get("original_format", "PNG"),
                                            "processed_format": target_format,
                                            "operation": f"{operation}",
                                            "width": processed_img.width,
                                            "height": processed_img.height,
                                            "file_size": len(res_bytes),
                                            "uploaded_at": datetime.now().isoformat(),
                                            "status": "Processed"
                                        }
                                        db_ok, db_err = dynamodb_service.save_image_metadata(db_record)

                                        if db_ok:
                                            st.success(f"✅ Hasil manipulasi berhasil disimpan ke S3!\n\n**New ID:** `{new_image_id}`")
                                            st.balloons()
                                        else:
                                            st.error(f"❌ Simpan metadata ke DynamoDB Gagal: {db_err}")

# =====================================================================
# TAB 4: GALLERY & HISTORY
# =====================================================================
elif navigation == "🖼️ Gallery & History":
    st.subheader("🖼️ Cloud Image Gallery & History")

    if not cloud_status["db_connected"]:
        st.error("❌ DynamoDB tidak terhubung. Tidak dapat menampilkan gallery.")
    else:
        metadata_list, _ = dynamodb_service.list_image_metadata()

        if not metadata_list:
            st.info("Gallery kosong. Belum ada gambar yang disimpan di database.")
        else:
            st.write(f"Total Gambar Tersimpan: **{len(metadata_list)}**")
            st.divider()

            # Render Cards Grid
            cols = st.columns(3)
            for idx, item in enumerate(metadata_list):
                col = cols[idx % 3]
                with col:
                    st.markdown(
                        f"""
                        <div class="content-box">
                            <h4 style="margin:0 0 8px 0; color:#f3f4f6;">{item.get('file_name', 'Unknown')}</h4>
                            <p style="font-size:0.8rem; color:#9ca3af; margin-bottom:4px;">ID: <code>{item.get('image_id')}</code></p>
                            <p style="font-size:0.8rem; color:#9ca3af; margin-bottom:4px;">Op: <b style="color:#818cf8;">{item.get('operation')}</b></p>
                            <p style="font-size:0.8rem; color:#9ca3af; margin-bottom:4px;">Format: {item.get('original_format')} ➔ <b>{item.get('processed_format')}</b></p>
                            <p style="font-size:0.8rem; color:#9ca3af; margin-bottom:4px;">Dimensi: {item.get('width')}x{item.get('height')} px | Size: {format_bytes(int(item.get('file_size',0)))}</p>
                            <p style="font-size:0.75rem; color:#6b7280;">Upload: {format_datetime(item.get('uploaded_at'))}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Action buttons for View, Download, Delete
                    btn_col1, btn_col2, btn_col3 = col.columns(3)

                    # View Button
                    with btn_col1:
                        if st.button("🔍 View", key=f"view_{item['image_id']}", use_container_width=True):
                            raw_bytes, _ = s3_service.download_image(item["object_key"])
                            if raw_bytes:
                                st.image(raw_bytes, caption=item["file_name"], use_column_width=True)

                    # Download Button
                    with btn_col2:
                        raw_bytes, _ = s3_service.download_image(item["object_key"])
                        if raw_bytes:
                            ext = item.get("processed_format", "PNG").lower()
                            st.download_button(
                                label="📥 Save",
                                data=raw_bytes,
                                file_name=f"{item['image_id']}.{ext}",
                                mime=f"image/{ext}",
                                key=f"dl_{item['image_id']}",
                                use_container_width=True
                            )

                    # Delete Button
                    with btn_col3:
                        if st.button("🗑️ Delete", key=f"del_{item['image_id']}", type="secondary", use_container_width=True):
                            s3_ok, _ = s3_service.delete_image(item["object_key"])
                            db_ok, _ = dynamodb_service.delete_image_metadata(item["image_id"])
                            if s3_ok and db_ok:
                                st.success("Dihapus!")
                                st.rerun()
                            else:
                                st.error("Gagal menghapus.")

# =====================================================================
# TAB 5: CLOUD STATUS & DIAGNOSTICS
# =====================================================================
elif navigation == "⚙️ Cloud Status":
    st.subheader("⚙️ Cloud Environment Diagnostics & Setup Guide")

    st.markdown("### 🔌 Connection Status")
    
    col_s3_stat, col_db_stat = st.columns(2)
    with col_s3_stat:
        st.markdown("#### Amazon S3 / MinIO Status")
        st.write(f"**Endpoint URL:** `{settings.S3_ENDPOINT_URL}`")
        st.write(f"**Bucket Name:** `{settings.S3_BUCKET_NAME}`")
        if cloud_status["s3_connected"]:
            st.success(f"✅ S3 Connected! ({cloud_status['s3_msg']})")
        else:
            st.error(f"❌ S3 Disconnected ({cloud_status['s3_msg']})")

    with col_db_stat:
        st.markdown("#### Amazon DynamoDB Status")
        st.write(f"**Endpoint URL:** `{settings.DYNAMODB_ENDPOINT_URL}`")
        st.write(f"**Table Name:** `{settings.DYNAMODB_TABLE_NAME}`")
        if cloud_status["db_connected"]:
            st.success(f"✅ DynamoDB Connected! ({cloud_status['db_msg']})")
        else:
            st.error(f"❌ DynamoDB Disconnected ({cloud_status['db_msg']})")

    st.divider()

    if st.button("🔄 Trigger Connection Re-check & Auto-Init", type="primary"):
        with st.spinner("Re-checking cloud endpoints and initializing buckets/tables..."):
            st.rerun()

    st.divider()
    st.markdown("### 🐳 Docker Compose Quick Setup Guide")
    st.markdown(
        """
        Jika endpoint cloud lokal belum **ONLINE**, Anda dapat menyalakannya di terminal dengan perintah berikut:

        ```bash
        # 1. Jalankan Container MinIO & DynamoDB Local
        docker compose up -d

        # 2. Verifikasi container running
        docker compose ps
        ```

        Aplikasi Streamlit ini akan membuat S3 Bucket (`mini-cloud-image-studio`) dan DynamoDB Table (`MiniCloudImages`) secara **otomatis** tanpa perlu intervensi manual.
        """
    )

# Global Studio Footer
st.markdown(
    """
    <div class="studio-footer">
        Mini Cloud Image Studio &bull; Remidi Cloud Computing &bull; Built with Streamlit, Boto3, S3, & DynamoDB
    </div>
    """,
    unsafe_allow_html=True
)
