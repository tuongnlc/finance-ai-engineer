from __future__ import annotations

import base64
import io
import json
import mimetypes
import random
import shutil
import urllib.request
from pathlib import Path

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

PICTURE_FOLDER = Path(st.secrets.get("PICTURE_DIR"))

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
REFRESH_SECONDS = 5
IMAGE_LIST_TTL_SECONDS = 60
IMAGE_CACHE_ENTRIES = 32


def _debug_event(hypothesis_id: str, location: str, msg: str, data: dict | None = None) -> None:
    payload = {
        "sessionId": "img-render-missing",
        "runId": "post-fix",
        "hypothesisId": hypothesis_id,
        "location": location,
        "msg": f"[DEBUG] {msg}",
        "data": data or {},
    }
    debug_url = "http://127.0.0.1:7777/event"
    env_path = Path(".dbg/img-render-missing.env")
    try:
        if env_path.is_file():
            for line in env_path.read_text().splitlines():
                if line.startswith("DEBUG_SERVER_URL="):
                    debug_url = line.split("=", 1)[1].strip()
    except Exception:
        pass
    try:
        request = urllib.request.Request(
            debug_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(request, timeout=1).read()
    except Exception:
        pass


@st.cache_data(show_spinner=False, ttl=IMAGE_LIST_TTL_SECONDS)
def load_images() -> list[Path]:
    images = sorted(
        path
        for path in PICTURE_FOLDER.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    # #region debug-point A:load-images
    _debug_event("A", "img_render.py:24", "load_images completed", {"count": len(images), "picture_dir": str(PICTURE_FOLDER)})
    # #endregion
    return images


def pick_random_image(images: list[Path], session_key: str = "last_image") -> Path | None:
    if not images:
        return None

    last_image = st.session_state.get(session_key)
    if len(images) == 1:
        choice = images[0]
    else:
        filtered = [image for image in images if str(image) != last_image]
        choice = random.choice(filtered or images)

    st.session_state[session_key] = str(choice)
    return choice


@st.cache_data(show_spinner=False, max_entries=IMAGE_CACHE_ENTRIES)
def build_image_data_url(image_path: Path, modified_time_ns: int) -> str:
    try:
        del modified_time_ns
        mime_type, _ = mimetypes.guess_type(image_path.name)
        mime_type = mime_type or "application/octet-stream"
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        # #region debug-point B:image-data-url
        _debug_event("B", "img_render.py:58", "build_image_data_url completed", {"image": str(image_path), "mime_type": mime_type, "encoded_len": len(encoded)})
        # #endregion
        return f"data:{mime_type};base64,{encoded}"
    except Exception as exc:
        # #region debug-point B:image-data-url-error
        _debug_event("B", "img_render.py:62", "build_image_data_url failed", {"image": str(image_path), "error": repr(exc)})
        # #endregion
        raise


@st.cache_data(show_spinner=False, max_entries=IMAGE_CACHE_ENTRIES)
def build_blurred_background_data_url(image_path: Path, modified_time_ns: int) -> str:
    del modified_time_ns
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image.thumbnail((1600, 1600))
        # image = image.filter(ImageFilter.GaussianBlur(radius=18))
        # image = ImageEnhance.Brightness(image).enhance(0.6)
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=80)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/webp;base64,{encoded}"


def get_background_url() -> str | None:
    images = load_images()
    bg_image = pick_random_image(images, session_key="last_bg_image")
    if bg_image is None:
        # #region debug-point D:bg-fallback
        _debug_event("D", "img_render.py:70", "background fallback selected", {"reason": "no-image"})
        # #endregion
        return None
    # #region debug-point D:bg-selected
    _debug_event("D", "img_render.py:73", "background image selected", {"image": str(bg_image)})
    # #endregion
    return build_blurred_background_data_url(bg_image, bg_image.stat().st_mtime_ns)


def build_background_style(bg_url: str | None) -> str:
    background_image = f'linear-gradient(rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0.18)), url("{bg_url}")' if bg_url else "none"
    return f"""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
        background-image: {background_image};
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """


def delete_picture() -> None:
    image_path_str = st.session_state.get("image_to_delete") or st.session_state.get("current_image")
    if not image_path_str:
        st.warning("Khong co anh nao duoc chon de xoa")
        return
    image_path = Path(image_path_str)
    try:
        if image_path.is_file():
            image_path.unlink()
            load_images.clear()
            build_image_data_url.clear()
            st.session_state.pop("current_image", None)
            st.session_state.pop("last_image", None)
            st.session_state.pop("last_bg_image", None)
            st.session_state.pop("image_to_delete", None)
            st.toast(f"Da xoa anh: {image_path.name}", icon="🗑️")
        else:
            st.warning(f"File khong ton tai: {image_path}")
    except Exception as exc:
        st.error(f"Loi khi xoa anh: {exc}")


def delete_folder() -> None:
    image_path_str = st.session_state.get("folder_to_delete") or st.session_state.get("current_image")
    if not image_path_str:
        st.warning("Khong co anh nao duoc chon de xoa folder")
        return
    image_path = Path(image_path_str)
    target_folder = image_path.parent
    try:
        pic_root_resolved = PICTURE_FOLDER.resolve()
        target_resolved = target_folder.resolve()
        if not target_folder.is_dir():
            st.warning(f"Folder khong ton tai: {target_folder}")
            return
        if target_resolved == pic_root_resolved:
            st.warning("Khong the xoa folder goc PICTURE_DIR. Chi xoa folder con chua anh.")
            return
        if pic_root_resolved not in target_resolved.parents:
            st.warning(f"Folder {target_folder} nam ngoai PICTURE_DIR, tu choi xoa.")
            return
        shutil.rmtree(target_folder)
        load_images.clear()
        build_image_data_url.clear()
        st.session_state.pop("current_image", None)
        st.session_state.pop("last_image", None)
        st.session_state.pop("last_bg_image", None)
        st.session_state.pop("folder_to_delete", None)
        st.toast(f"Da xoa folder: {target_folder.name}", icon="🗂️")
    except Exception as exc:
        st.error(f"Loi khi xoa folder: {exc}")

st.set_page_config(page_title="Random Image Viewer", layout="wide")

st.markdown(
    """
    <style>
    section[data-testid="stMain"],
    section[data-testid="stMain"] .block-container,
    .stApp,
    .stApp .main,
    [data-testid="stAppViewContainer"] {
        background-color: transparent !important;
    }
    .viewer-frame {
        height: 82vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .viewer-frame img {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
    }
    [data-testid="stCaptionContainer"] {
        text-align: center;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex;
        justify-content: center;
    }
    .btn-delete-image button[kind="secondary"] {
        background-color: #22c55e !important;
        color: #ffffff !important;
        border-color: #16a34a !important;
        font-weight: 600;
    }
    .btn-delete-image button[kind="secondary"]:hover {
        background-color: #16a34a !important;
        border-color: #15803d !important;
        color: #ffffff !important;
    }
    .btn-delete-folder button[kind="secondary"] {
        background-color: #0ea5e9 !important;
        color: #ffffff !important;
        border-color: #0284c7 !important;
        font-weight: 600;
    }
    .btn-delete-folder button[kind="secondary"]:hover {
        background-color: #0284c7 !important;
        border-color: #0369a1 !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    st.markdown(build_background_style(get_background_url()), unsafe_allow_html=True)
except Exception:
    pass

_, col_img, col_folder, _ = st.columns([1, 2, 2, 1], gap="large")
with col_img:
    with st.container():
        st.markdown("<div class='btn-delete-image'>", unsafe_allow_html=True)
        confirm_del_img = st.button("Xoá ảnh", key="delete_image_btn", use_container_width=True, help="Xoá file ảnh hiện tại khỏi ổ cứng")
        st.markdown("</div>", unsafe_allow_html=True)
with col_folder:
    with st.container():
        st.markdown("<div class='btn-delete-folder'>", unsafe_allow_html=True)
        confirm_del_folder = st.button("Xoá folder ảnh ", key="delete_folder_btn", use_container_width=True, help="Xoá thư mục chứa ảnh hiện tại")
        st.markdown("</div>", unsafe_allow_html=True)

if confirm_del_img:
    cur_img = st.session_state.get("current_image")
    if cur_img:
        st.session_state["image_to_delete"] = cur_img
        delete_picture()
        st.rerun()

if confirm_del_folder:
    cur_img = st.session_state.get("current_image")
    if cur_img:
        st.session_state["folder_to_delete"] = cur_img
        delete_folder()
        st.rerun()


@st.fragment(run_every=f"{REFRESH_SECONDS}s")
def render_image_viewer() -> None:
    # #region debug-point D:fragment-start
    _debug_event("D", "img_render.py:238", "render_image_viewer start", {"last_image": st.session_state.get("last_image"), "last_bg_image": st.session_state.get("last_bg_image")})
    # #endregion
    images = load_images()
    current_image = pick_random_image(images)

    if not images or current_image is None:
        # #region debug-point A:viewer-no-image
        _debug_event("A", "img_render.py:244", "viewer has no image to render", {"count": len(images)})
        # #endregion
        st.warning(f"Khong tim thay anh trong {PICTURE_FOLDER}")
    else:
        st.session_state["current_image"] = str(current_image)
        image_url = build_image_data_url(
            current_image,
            current_image.stat().st_mtime_ns,
        )
        # #region debug-point C:viewer-selected
        _debug_event("C", "img_render.py:252", "viewer image selected", {"image": str(current_image), "image_url_prefix": image_url[:32]})
        # #endregion
        st.markdown(
            f'<div class="viewer-frame"><img src="{image_url}" alt="{current_image.name}"></div>',
            unsafe_allow_html=True,
        )
        folder_name = current_image.parent.name
        img_name = current_image.name.split(".")[0]
        st.caption(f"Folder: {folder_name} -------------  Iamge: {img_name}")

    try:
        st.markdown(build_background_style(get_background_url()), unsafe_allow_html=True)
        # #region debug-point C:bg-layer-rendered
        _debug_event("C", "img_render.py:262", "background layer rendered", {})
        # #endregion
    except Exception as exc:
        # #region debug-point D:bg-layer-error
        _debug_event("D", "img_render.py:266", "background layer render failed", {"error": repr(exc)})
        # #endregion
        pass


render_image_viewer()
