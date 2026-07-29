"""
MirrorLine — Clinical Mirror Imaging (Streamlit)
=================================================
On-device mirror/reflection tool for medical imaging tasks:
symmetry assessment, bilateral comparison, mirror-therapy composites, etc.

Run locally so patient images never leave the machine:
    pip install -r requirements.txt
    streamlit run mirrorline_app.py"""
MirrorLine — Clinical Mirror Imaging (Streamlit)
=================================================
On-device mirror/reflection tool for medical imaging tasks:
symmetry assessment, bilateral comparison, mirror-therapy composites, etc.

Run locally so patient images never leave the machine:
    pip install -r requirements.txt
    streamlit run mirrorline_app.py
"""

import io
from PIL import Image, ImageOps, ImageDraw
import streamlit as st

st.set_page_config(page_title="MirrorLine for Dr. Anand — Clinical Mirror Imaging",
                   page_icon="🪞", layout="wide")

# ----------------------------- styling -----------------------------
st.markdown("""
<style>
  .stApp {background:#0B0F14; color:#E7EEF4;}
  .block-container {padding-top:2.2rem; max-width:1150px;}
  h1 {letter-spacing:.04em;}
  .ml-tag {font-family:ui-monospace,Menlo,monospace; font-size:.72rem;
           letter-spacing:.14em; color:#5F707D; text-transform:uppercase;}
  .ml-accent {color:#35D9C5;}
  .ml-privacy {font-family:ui-monospace,Menlo,monospace; font-size:.72rem;
               color:#8A9AA8; border:1px solid #28353F; border-radius:8px;
               padding:.5rem .8rem; display:inline-block;}
  div[data-testid="stFileUploaderDropzone"] {background:#121A22; border:1px dashed #28353F;}
  /* Red, clearly-visible Upload button inside the dropzone */
  [data-testid="stFileUploaderDropzone"] button {
      background:#E03A2F !important; color:#FFFFFF !important;
      border:1px solid #E03A2F !important; border-radius:9px !important;
      font-weight:700 !important; opacity:1 !important;
  }
  [data-testid="stFileUploaderDropzone"] button:hover {
      background:#C42C22 !important; border-color:#C42C22 !important; color:#FFFFFF !important;
  }
  [data-testid="stFileUploaderDropzone"] button * {color:#FFFFFF !important;}
  .stDownloadButton button, .stButton button {border-radius:10px; font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='margin-bottom:.1rem;'>"
    "Mirror<span class='ml-accent'>Line</span>"
    "<span style='color:#8A9AA8; font-weight:400;'> for Dr. Anand</span>"
    "</h1>",
    unsafe_allow_html=True)
st.markdown("<span class='ml-tag'>Clinical mirror imaging · runs on device</span>",
            unsafe_allow_html=True)


# ----------------------------- core ops -----------------------------
def mirror(image: Image.Image, mode: str) -> Image.Image:
    """Return the mirrored/composited image for the chosen mode."""
    if mode == "Horizontal (L↔R)":
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    if mode == "Vertical (T↕B)":
        return image.transpose(Image.FLIP_TOP_BOTTOM)
    if mode == "Both / 180°":
        return image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    if mode == "Reflection composite":
        # original on top, vertical mirror joined below (mirror-therapy look)
        w, h = image.size
        flipped = image.transpose(Image.FLIP_TOP_BOTTOM)
        canvas = Image.new("RGB", (w, h * 2), (6, 9, 13))
        canvas.paste(image, (0, 0))
        canvas.paste(flipped, (0, h))
        return canvas
    return image


def draw_axis(image: Image.Image, mode: str) -> Image.Image:
    """Overlay the dashed reflection axis (preview only — not in the export)."""
    img = image.convert("RGB").copy()
    d = ImageDraw.Draw(img)
    w, h = img.size
    color = (53, 217, 197)
    lw = max(2, w // 500)
    dash, gap = max(8, w // 60), max(6, w // 90)

    def dashed_line(x0, y0, x1, y1):
        if x0 == x1:  # vertical
            y = y0
            while y < y1:
                d.line([(x0, y), (x0, min(y + dash, y1))], fill=color, width=lw)
                y += dash + gap
        else:         # horizontal
            x = x0
            while x < x1:
                d.line([(x, y0), (min(x + dash, x1), y0)], fill=color, width=lw)
                x += dash + gap

    if mode == "Horizontal (L↔R)":
        dashed_line(w // 2, 0, w // 2, h)
    elif mode == "Vertical (T↕B)":
        dashed_line(0, h // 2, w, h // 2)
    elif mode == "Both / 180°":
        dashed_line(w // 2, 0, w // 2, h)
        dashed_line(0, h // 2, w, h // 2)
    elif mode == "Reflection composite":
        dashed_line(0, h // 2, w, h // 2)  # seam sits at vertical mid-point
    return img


# ----------------------------- controls -----------------------------
with st.sidebar:
    st.markdown("### Controls")
    mode = st.radio(
        "Reflection mode",
        ["Horizontal (L↔R)", "Vertical (T↕B)", "Both / 180°", "Reflection composite"],
        help="Horizontal is the true mirror used for symmetry and bilateral "
             "comparison. Vertical is the water-reflection flip. Reflection "
             "composite joins the image to its mirror for mirror-therapy views.",
    )
    show_axis = st.checkbox("Show reflection axis (preview only)", value=True)

uploaded = st.file_uploader("Load an image", type=["jpg", "jpeg", "png", "webp", "bmp"])


# ----------------------------- render -----------------------------
if uploaded is None:
    st.info("Upload a photo to begin. JPG · PNG · WEBP supported.")
else:
    original = Image.open(uploaded)
    original = ImageOps.exif_transpose(original)  # respect camera orientation
    original = original.convert("RGB")

    result = mirror(original, mode)
    preview = draw_axis(result, mode) if show_axis else result

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Original**")
        st.image(original, use_container_width=True)
    with c2:
        st.markdown(f"**Mirrored — {mode}**")
        st.image(preview, use_container_width=True)

    st.caption(f"Output: {result.size[0]} × {result.size[1]} px · PNG, full resolution")

    # export the clean image (no axis overlay)
    buf = io.BytesIO()
    result.save(buf, format="PNG")
    st.download_button(
        "⬇ Save PNG",
        data=buf.getvalue(),
        file_name=f"mirror-{mode.split()[0].lower()}.png",
        mime="image/png",
        type="primary",
    )
"""

import io
from PIL import Image, ImageOps, ImageDraw
import streamlit as st

st.set_page_config(page_title="MirrorLine for Dr. Anand — Clinical Mirror Imaging",
                   page_icon="🪞", layout="wide")

# ----------------------------- styling -----------------------------
st.markdown("""
<style>
  .stApp {background:#0B0F14; color:#E7EEF4;}
  .block-container {padding-top:2.2rem; max-width:1150px;}
  h1 {letter-spacing:.04em;}
  .ml-tag {font-family:ui-monospace,Menlo,monospace; font-size:.72rem;
           letter-spacing:.14em; color:#5F707D; text-transform:uppercase;}
  .ml-accent {color:#35D9C5;}
  .ml-privacy {font-family:ui-monospace,Menlo,monospace; font-size:.72rem;
               color:#8A9AA8; border:1px solid #28353F; border-radius:8px;
               padding:.5rem .8rem; display:inline-block;}
  div[data-testid="stFileUploaderDropzone"] {background:#121A22; border:1px dashed #28353F;}
  /* Red, clearly-visible Upload button inside the dropzone */
  [data-testid="stFileUploaderDropzone"] button {
      background:#E03A2F !important; color:#FFFFFF !important;
      border:1px solid #E03A2F !important; border-radius:9px !important;
      font-weight:700 !important; opacity:1 !important;
  }
  [data-testid="stFileUploaderDropzone"] button:hover {
      background:#C42C22 !important; border-color:#C42C22 !important; color:#FFFFFF !important;
  }
  [data-testid="stFileUploaderDropzone"] button * {color:#FFFFFF !important;}
  .stDownloadButton button, .stButton button {border-radius:10px; font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='margin-bottom:.1rem;'>"
    "Mirror<span class='ml-accent'>Line</span>"
    "<span style='color:#8A9AA8; font-weight:400;'> for Dr. Anand</span>"
    "</h1>",
    unsafe_allow_html=True)
st.markdown("<span class='ml-tag'>Clinical mirror imaging · runs on device</span>",
            unsafe_allow_html=True)


# ----------------------------- core ops -----------------------------
def mirror(image: Image.Image, mode: str) -> Image.Image:
    """Return the mirrored/composited image for the chosen mode."""
    if mode == "Horizontal (L↔R)":
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    if mode == "Vertical (T↕B)":
        return image.transpose(Image.FLIP_TOP_BOTTOM)
    if mode == "Both / 180°":
        return image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    if mode == "Reflection composite":
        # original on top, vertical mirror joined below (mirror-therapy look)
        w, h = image.size
        flipped = image.transpose(Image.FLIP_TOP_BOTTOM)
        canvas = Image.new("RGB", (w, h * 2), (6, 9, 13))
        canvas.paste(image, (0, 0))
        canvas.paste(flipped, (0, h))
        return canvas
    return image


def draw_axis(image: Image.Image, mode: str) -> Image.Image:
    """Overlay the dashed reflection axis (preview only — not in the export)."""
    img = image.convert("RGB").copy()
    d = ImageDraw.Draw(img)
    w, h = img.size
    color = (53, 217, 197)
    lw = max(2, w // 500)
    dash, gap = max(8, w // 60), max(6, w // 90)

    def dashed_line(x0, y0, x1, y1):
        if x0 == x1:  # vertical
            y = y0
            while y < y1:
                d.line([(x0, y), (x0, min(y + dash, y1))], fill=color, width=lw)
                y += dash + gap
        else:         # horizontal
            x = x0
            while x < x1:
                d.line([(x, y0), (min(x + dash, x1), y0)], fill=color, width=lw)
                x += dash + gap

    if mode == "Horizontal (L↔R)":
        dashed_line(w // 2, 0, w // 2, h)
    elif mode == "Vertical (T↕B)":
        dashed_line(0, h // 2, w, h // 2)
    elif mode == "Both / 180°":
        dashed_line(w // 2, 0, w // 2, h)
        dashed_line(0, h // 2, w, h // 2)
    elif mode == "Reflection composite":
        dashed_line(0, h // 2, w, h // 2)  # seam sits at vertical mid-point
    return img


# ----------------------------- controls -----------------------------
with st.sidebar:
    st.markdown("### Controls")
    mode = st.radio(
        "Reflection mode",
        ["Horizontal (L↔R)", "Vertical (T↕B)", "Both / 180°", "Reflection composite"],
        help="Horizontal is the true mirror used for symmetry and bilateral "
             "comparison. Vertical is the water-reflection flip. Reflection "
             "composite joins the image to its mirror for mirror-therapy views.",
    )
    show_axis = st.checkbox("Show reflection axis (preview only)", value=True)

uploaded = st.file_uploader("Load an image", type=["jpg", "jpeg", "png", "webp", "bmp"])


# ----------------------------- render -----------------------------
if uploaded is None:
    st.info("Upload a photo to begin. JPG · PNG · WEBP supported.")
else:
    original = Image.open(uploaded)
    original = ImageOps.exif_transpose(original)  # respect camera orientation
    original = original.convert("RGB")

    result = mirror(original, mode)
    preview = draw_axis(result, mode) if show_axis else result

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Original**")
        st.image(original, use_container_width=True)
    with c2:
        st.markdown(f"**Mirrored — {mode}**")
        st.image(preview, use_container_width=True)

    st.caption(f"Output: {result.size[0]} × {result.size[1]} px · PNG, full resolution")

    # export the clean image (no axis overlay)
    buf = io.BytesIO()
    result.save(buf, format="PNG")
    st.download_button(
        "⬇ Save PNG",
        data=buf.getvalue(),
        file_name=f"mirror-{mode.split()[0].lower()}.png",
        mime="image/png",
        type="primary",
    )
