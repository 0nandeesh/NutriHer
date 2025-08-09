import os
import re
import tempfile
import io
import streamlit as st
import yt_dlp
from groq import Groq
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

# ------- CONFIG -------
DOWNLOAD_DIR = "downloads"
GROQ_MAX_FILESIZE_BYTES = 250 * 1024 * 1024  # 250 MB
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Set via environment for security

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ------- UTILITIES -------

def sanitize_filename(name: str, max_len: int = 100) -> str:
    """Return a filesystem-safe version of *name*."""
    if not isinstance(name, str):
        return "unknown_video"
    safe = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_"))
    safe = safe.strip() or "unknown_video"
    return safe[:max_len]


def download_video(video_url: str, video_title: str):
    """Download *video_url* as an .mp4 that already includes audio.

    Returns (msg, filepath|None).
    """
    if not video_url:
        return "Invalid video URL", None

    safe_name = sanitize_filename(video_title)
    target_template = os.path.join(DOWNLOAD_DIR, f"{safe_name}.%(ext)s")

    # Check if we already downloaded
    for ext in (".mp4", ".mkv", ".webm"):
        candidate = os.path.join(DOWNLOAD_DIR, f"{safe_name}{ext}")
        if os.path.exists(candidate):
            return f"Video already exists → {candidate}", candidate

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": target_template,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        # Merge segments via ffmpeg automatically
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            final_path = ydl.prepare_filename(info)
            # If merging happened the extension may differ
            if not final_path.endswith(".mp4"):
                possible = os.path.splitext(final_path)[0] + ".mp4"
                if os.path.exists(possible):
                    final_path = possible
            if os.path.exists(final_path):
                return "✅ Video downloaded (audio+video)", final_path
            return "Download completed but file not found", None
    except Exception as e:
        return f"Error downloading video: {e}", None


def fetch_youtube_captions(video_url: str):
    """Return official YouTube captions when available."""
    match = re.search(r"(?:v=|/videos/|/embed/|youtu\.be/|/shorts/)([\w-]{11})", video_url)
    if not match:
        return "Could not extract video ID from URL"
    vid = match.group(1)
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(vid)
        transcript = None
        try:
            transcript = transcripts.find_transcript(["en"])
        except NoTranscriptFound:
            if transcripts._transcripts:
                transcript = transcripts.find_transcript(list(transcripts._transcripts))
        if transcript is None:
            return "No transcript available for this video."        
        text = "\n".join(part["text"] for part in transcript.fetch())
        return text.strip() or "Transcript found but empty."
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "No transcript found for this video."
    except Exception as e:
        return f"Error fetching captions: {e}"


def _download_audio_to_temp(video_url: str) -> tempfile.NamedTemporaryFile:
    """Download best audio track into a NamedTemporaryFile and return the handle."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp.name,  # yt_dlp will overwrite the temporary filename
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            # yt_dlp might have renamed the file due to metadata; locate the created file
            base, _ = os.path.splitext(tmp.name)
            for ext in (".m4a", ".webm", ".mp3", ".ogg", ".wav"):
                cand = base + ext
                if os.path.exists(cand):
                    tmp.close()
                    return open(cand, "rb")
        tmp.close()
    except Exception:
        tmp.close()
        raise
    raise RuntimeError("Audio download failed")


def transcribe_youtube(video_url: str, api_key: str = GROQ_API_KEY, model: str = "whisper-large-v3-turbo") -> str:
    """Transcribe a YouTube *video_url* using Groq Whisper **without storing permanent files**."""
    # 1) Try official captions first – fastest & free
    captions = fetch_youtube_captions(video_url)
    if captions and not captions.startswith("No transcript") and "disabled" not in captions.lower():
        return captions

    # 2) Fallback to Whisper transcription
    if not api_key:
        return "Groq API key not configured. Set GROQ_API_KEY env variable."

    try:
        temp_audio = _download_audio_to_temp(video_url)
        size = os.path.getsize(temp_audio.name)
        if size > GROQ_MAX_FILESIZE_BYTES:
            temp_audio.close()
            return f"Audio size {size / (1024*1024):.1f} MB exceeds {GROQ_MAX_FILESIZE_BYTES/(1024*1024)} MB limit."
        client = Groq(api_key=api_key)
        transcription = client.audio.transcriptions.create(
            file=temp_audio,
            model=model,
            response_format="text",
        )
        temp_audio.close()
        if isinstance(transcription, str):
            return transcription
        if hasattr(transcription, "text"):
            return transcription.text
        return str(transcription)
    except Exception as e:
        return f"Failed to transcribe via Groq: {e}"


# ------- STREAMLIT UI -------

st.set_page_config(page_title="🎬 VidRipper", layout="wide")
st.title("🎬 VidRipper – Download & Transcribe YouTube")

st.sidebar.markdown("## Enter YouTube URL")
input_url = st.sidebar.text_input("Video / Playlist / Channel URL")

if not input_url:
    st.info("Paste a YouTube URL in the sidebar to begin.")
    st.stop()

# Detect playlist or channel quickly; for brevity only single-video handling here
if "playlist?list=" not in input_url and not input_url.rstrip("/").endswith("/videos"):
    # Single video UI
    st.subheader("🎞️ Single Video")
    if st.button("⬇️ Download Video (.mp4)"):
        with st.spinner("Downloading video …"):
            msg, path = download_video(input_url, "video")
        if path:
            st.success(msg)
            with open(path, "rb") as vf:
                st.download_button("Download file", vf, file_name=os.path.basename(path))
        else:
            st.error(msg)

    if st.button("📝 Transcribe (Captions→Groq)"):
        with st.spinner("Transcribing …"):
            text = transcribe_youtube(input_url)
        if text.startswith("Error") or text.startswith("Failed"):
            st.error(text)
        else:
            st.text_area("Transcript", text, height=300)
            st.download_button("Save transcript", text, file_name="transcript.txt")
else:
    st.warning("Playlist & channel support coming soon in this streamlined demo.")