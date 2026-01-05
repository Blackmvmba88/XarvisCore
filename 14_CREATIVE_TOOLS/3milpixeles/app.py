
import streamlit as st
import os
from PIL import Image, ImageOps
import io
from core import ResizerCore

# Page Config
st.set_page_config(
    page_title="Visual Alpha Studio Suite",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #1a0033;
        color: white;
    }
    .stButton>button {
        background-color: #00FF88;
        color: #1a0033;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #00CC6E;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4);
    }
    h1, h2, h3 {
        color: #00FF88 !important;
    }
    .stSidebar {
        background-color: #2D0052 !important;
    }
    .crop-container {
        border: 2px solid #00FF88;
        position: relative;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("✨ Visual Alpha Studio Suite")
    st.subheader("High-Performance Image Resizer (3000x3000px)")
    
    with st.sidebar:
        st.header("⚙️ Settings")
        mode = st.radio("Resizing Mode", ["Fit (Margins)", "Fill (Crop)", "Manual (Sliding)"], index=0)
        quality = st.slider("Quality (JPEG/PNG)", 80, 100, 95)
        
        st.markdown("---")
        st.markdown("### Branding Logo integration")
        st.checkbox("Add Spotify Logo (Coming Soon)")
        st.checkbox("Add SoundCloud Logo (Coming Soon)")
        st.checkbox("Add DistroKid Logo (Coming Soon)")

    uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

    if uploaded_files:
        cols = st.columns(len(uploaded_files) if len(uploaded_files) < 3 else 3)
        
        for i, uploaded_file in enumerate(uploaded_files):
            col = cols[i % 3]
            with col:
                img = Image.open(uploaded_file)
                st.image(img, caption=f"Original: {uploaded_file.name}", use_container_width=True)
                
                # Conversion logic
                if mode == "Fit (Margins)":
                    result = ResizerCore.resize_fit(img)
                elif mode == "Fill (Crop)":
                    result = ResizerCore.resize_fill(img)
                else: # Manual Sliding
                    st.info("Manual Slide Logic Activada")
                    # Simplified manual crop: Slider for horizontal/vertical shift
                    # In a real app we'd use a JS component for 'sliding', 
                    # but for this MVP we'll use Shift sliders
                    width, height = img.size
                    if width > height: # Landscape
                        max_shift = width - height
                        shift = st.slider(f"Horizontal Shift - {uploaded_file.name}", 0, max_shift, max_shift // 2)
                        result = img.crop((shift, 0, shift + height, height))
                        result = result.resize((3000, 3000), Image.Resampling.LANCZOS)
                    elif height > width: # Portrait
                        max_shift = height - width
                        shift = st.slider(f"Vertical Shift - {uploaded_file.name}", 0, max_shift, max_shift // 2)
                        result = img.crop((0, shift, width, shift + width))
                        result = result.resize((3000, 3000), Image.Resampling.LANCZOS)
                    else: # Already square
                        result = img.resize((3000, 3000), Image.Resampling.LANCZOS)

                # Show Preview result
                st.image(result, caption="Preview (3000x3000px)", use_container_width=True)
                
                # Download Button
                buf = io.BytesIO()
                result.save(buf, format="PNG", quality=quality)
                st.download_button(
                    label=f"⬇️ Download {uploaded_file.name}",
                    data=buf.getvalue(),
                    file_name=f"ALPHA_{uploaded_file.name.split('.')[0]}_3000.png",
                    mime="image/png"
                )

    else:
        st.info("👋 Welcome! Upload your images to start the Visual Alpha transformation.")
        
    # Footer
    st.markdown("---")
    st.markdown("🛡️ **Xarvis Core - Operational Excellence**")

if __name__ == "__main__":
    main()
