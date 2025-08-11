import streamlit as st
import requests
import os

# ====== CONFIGURATION ======
API_BASE_URL = "http://3.106.196.221:8000"
 # Change this to your deployed FastAPI URL
# ===========================

st.set_page_config(page_title="Video Downloader", page_icon="📥", layout="centered")

st.title("📥 Video Downloader")
st.markdown("Download videos in different resolutions from your FastAPI service.")

# Input fields
url = st.text_input("🔗 Enter video URL", placeholder="Paste video link here...")
filename = st.text_input("📝 Optional: Filename for download (without extension)")

# Resolution dropdown
resolution = st.selectbox(
    "📹 Select Resolution",
    ["1080", "720", "480", "360", "240"],
    index=1  # Default is 720p
)

if st.button("⬇️ Download Video"):
    if not url.strip():
        st.error("Please enter a valid video URL.")
    else:
        with st.spinner("Downloading... Please wait."):
            try:
                # Prepare form data
                data = {
                    "url": url.strip(),
                    "resolution": resolution
                }
                if filename.strip():
                    data["filename"] = filename.strip()

                # Call FastAPI endpoint
                response = requests.post(
                    f"{API_BASE_URL}/download",
                    data=data,
                    stream=True
                )

                if response.status_code == 200:
                    # Get suggested filename from headers
                    content_disp = response.headers.get("Content-Disposition", "")
                    suggested_name = f"{filename.strip() or 'downloaded_video'}.mp4"
                    if 'filename=' in content_disp:
                        suggested_name = content_disp.split("filename=")[-1].strip('"')

                    # Avoid overwriting existing file
                    base_name, ext = os.path.splitext(suggested_name)
                    counter = 1
                    while os.path.exists(suggested_name):
                        suggested_name = f"{base_name}_{counter}{ext}"
                        counter += 1

                    # Save the video locally
                    with open(suggested_name, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    st.success(f"✅ Downloaded successfully as `{suggested_name}`")
                    st.video(suggested_name)

                else:
                    try:
                        error_msg = response.json().get("detail", "Unknown error")
                    except:
                        error_msg = response.text
                    st.error(f"❌ Error {response.status_code}: {error_msg}")

            except Exception as e:
                st.error(f"⚠️ Request failed: {e}")
