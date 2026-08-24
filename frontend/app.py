import html
import requests
import streamlit as st
from urllib.parse import quote_plus
import os

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Spotify AI",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.html(
    """
    <style>

    :root {
        --green: #1DB954;
        --green-hover: #1ED760;
        --bg: #121212;
        --surface: #181818;
        --surface-hover: #222222;
        --border: #2A2A2A;
        --white: #FFFFFF;
        --secondary: #B3B3B3;
        --muted: #6A6A6A;
    }

    .stApp {
        background: var(--bg);
        color: var(--white);
    }

    html, body {
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Helvetica,
            Arial,
            sans-serif;
    }

    header[data-testid="stHeader"] {
        display: none;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1280px;
        padding: 28px 36px 80px 36px !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--white) !important;
    }

    p {
        color: var(--secondary);
    }

    .section-title {
        color: var(--white);
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: var(--secondary);
        font-size: 14px;
        margin-bottom: 22px;
    }

    .topbar {
        height: 58px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .spotify-logo {
        width: 34px;
        height: 34px;
        background: var(--green);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000;
        font-size: 20px;
        font-weight: 900;
    }

    .brand-name {
        font-size: 21px;
        font-weight: 750;
        color: var(--white);
    }

    .brand-ai {
        color: var(--secondary);
        font-weight: 500;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 7px 12px;
        border: 1px solid #303030;
        border-radius: 999px;
        background: var(--surface);
        color: var(--secondary);
        font-size: 12px;
        font-weight: 600;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        background: var(--green);
        border-radius: 50%;
    }

    .hero {
        background:
            radial-gradient(
                circle at 85% 20%,
                rgba(29,185,84,0.18),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #181818 0%,
                #121212 70%
            );

        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 42px;
        margin-bottom: 26px;
    }

    .hero-eyebrow {
        color: var(--green);
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
    }

    .hero-title {
        color: var(--white);
        font-size: 38px;
        line-height: 1.1;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .hero-text {
        color: var(--secondary);
        font-size: 15px;
        line-height: 1.65;
        max-width: 650px;
    }

    .user-bar,
    .card,
    .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    .user-bar {
        padding: 13px 17px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }

    .user-label,
    .stat-label {
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: .7px;
    }

    .user-id {
        color: var(--white);
        font-size: 13px;
        font-weight: 600;
    }

    .stat-card {
        padding: 18px;
    }

    .stat-value {
        color: var(--white);
        font-size: 24px;
        font-weight: 800;
    }

    .stat-label {
        margin-top: 4px;
    }

    .card {
        padding: 18px;
    }

    .card-title {
        color: var(--white);
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .card-subtitle {
        color: var(--secondary);
        font-size: 12px;
        line-height: 1.5;
    }

    .divider {
        height: 1px;
        background: var(--border);
        margin: 24px 0;
    }

    .chip-label {
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: .8px;
        margin-bottom: 8px;
    }

    .footer {
        text-align: center;
        color: #505050;
        font-size: 11px;
        margin-top: 50px;
    }

    div[data-testid="stChatMessage"] {
        background: transparent !important;
    }

    div[data-testid="stChatMessageContent"] {
        color: var(--white) !important;
    }

    div[data-testid="stChatInput"] textarea {
        background: var(--white) !important;
        color: #000 !important;
        -webkit-text-fill-color: #000 !important;
        border: none !important;
        border-radius: 999px !important;
    }

    .stButton > button {
        border-radius: 999px !important;
        border: none !important;
        min-height: 42px !important;
        font-weight: 750 !important;
        font-size: 13px !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--green) !important;
        color: #000 !important;
    }

    .stButton > button[kind="secondary"] {
        background: #282828 !important;
        color: var(--white) !important;
    }

    </style>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "logged_in": False,
    "user_id": None,
    "username": None,
    "conversation_id": None,
    "messages": [],
    "last_search": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    return html.escape(str(value), quote=True)


def backend_available():
    try:
        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=3,
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


def extract_artists(track):
    artists = track.get("artists")

    if isinstance(artists, list):

        names = []

        for artist in artists:

            if isinstance(artist, dict):
                name = artist.get("name")

                if name:
                    names.append(str(name))

            else:
                names.append(str(artist))

        if names:
            return ", ".join(names)

    elif artists:
        return str(artists)

    artist = track.get("artist")

    if isinstance(artist, dict):
        return str(
            artist.get(
                "name",
                "Unknown artist",
            )
        )

    if artist:
        return str(artist)

    return "Unknown artist"


# ============================================================
# EXTRACT SPOTIFY URL
# ============================================================

def extract_spotify_url(track):
    """
    Supports multiple possible backend response formats.
    """

    # --------------------------------------------------------
    # Direct spotify_url
    # --------------------------------------------------------

    url = track.get("spotify_url")

    if url:
        return str(url)

    # --------------------------------------------------------
    # Direct url
    # --------------------------------------------------------

    url = track.get("url")

    if url and "spotify" in str(url).lower():
        return str(url)

    # --------------------------------------------------------
    # href
    # --------------------------------------------------------

    href = track.get("href")

    if href and "spotify" in str(href).lower():
        return str(href)

    # --------------------------------------------------------
    # external_urls
    # --------------------------------------------------------

    external_urls = track.get("external_urls")

    if isinstance(external_urls, dict):

        spotify = external_urls.get("spotify")

        if spotify:
            return str(spotify)

    # --------------------------------------------------------
    # nested track object
    # --------------------------------------------------------

    nested_track = track.get("track")

    if isinstance(nested_track, dict):

        nested_url = extract_spotify_url(
            nested_track
        )

        if nested_url:
            return nested_url

    # --------------------------------------------------------
    # Spotify URI
    # --------------------------------------------------------

    uri = track.get("uri")

    if uri and str(uri).startswith("spotify:track:"):

        track_id = str(uri).split(
            "spotify:track:",
            1
        )[1]

        return f"https://open.spotify.com/track/{track_id}"

    # --------------------------------------------------------
    # Spotify ID
    # --------------------------------------------------------

    track_id = track.get("id")

    if track_id:

        # Only treat it as a track ID when this object
        # appears to be a Spotify track.
        object_type = str(
            track.get(
                "type",
                "track"
            )
        ).lower()

        if object_type == "track":

            return (
                "https://open.spotify.com/track/"
                + quote_plus(str(track_id))
            )

    return ""


# ============================================================
# EXTRACT ALBUM ART
# ============================================================

def extract_album_art(track):
    """
    Supports multiple Spotify/backend response formats.
    """

    # --------------------------------------------------------
    # Direct album_art
    # --------------------------------------------------------

    album_art = track.get("album_art")

    if album_art:
        return str(album_art)

    # --------------------------------------------------------
    # image
    # --------------------------------------------------------

    image = track.get("image")

    if image:
        return str(image)

    # --------------------------------------------------------
    # image_url
    # --------------------------------------------------------

    image_url = track.get("image_url")

    if image_url:
        return str(image_url)

    # --------------------------------------------------------
    # images
    # --------------------------------------------------------

    images = track.get("images")

    if isinstance(images, list) and images:

        first = images[0]

        if isinstance(first, dict):

            url = first.get("url")

            if url:
                return str(url)

        elif isinstance(first, str):
            return first

    # --------------------------------------------------------
    # nested album
    # --------------------------------------------------------

    album = track.get("album")

    if isinstance(album, dict):

        album_images = album.get("images")

        if (
            isinstance(album_images, list)
            and album_images
        ):

            first = album_images[0]

            if isinstance(first, dict):

                url = first.get("url")

                if url:
                    return str(url)

            elif isinstance(first, str):

                return first

        # Some APIs return image directly in album
        album_image = album.get("image")

        if album_image:
            return str(album_image)

        album_art = album.get("album_art")

        if album_art:
            return str(album_art)

    return ""


# ============================================================
# NORMALIZE SPOTIFY RESULT
# ============================================================

def normalize_track(track):
    """
    Converts whatever the backend gives us into one
    predictable structure for the UI.
    """

    if not isinstance(track, dict):
        return None

    name = (
        track.get("name")
        or track.get("track_name")
        or track.get("title")
        or "Unknown track"
    )

    artists = extract_artists(track)

    # Album
    album = track.get("album")

    if isinstance(album, dict):

        album_name = (
            album.get("name")
            or album.get("title")
            or "Unknown album"
        )

    else:

        album_name = (
            album
            or track.get("album_name")
            or "Unknown album"
        )

    spotify_url = extract_spotify_url(track)

    # --------------------------------------------------------
    # If backend doesn't provide an exact Spotify URL,
    # create a Spotify search URL.
    #
    # This means the card NEVER gets stuck showing
    # "Spotify link unavailable".
    # --------------------------------------------------------

    if not spotify_url:

        search_string = (
            f"{name} {artists}"
        )

        spotify_url = (
            "https://open.spotify.com/search/"
            + quote_plus(search_string)
        )

    album_art = extract_album_art(track)

    return {
        "name": str(name),
        "artists": str(artists),
        "album": str(album_name),
        "spotify_url": spotify_url,
        "album_art": album_art,
    }


# ============================================================
# SPOTIFY SEARCH
# ============================================================

def spotify_search(query):

    try:

        response = requests.get(
            f"{BACKEND_URL}/spotify/search",
            params={"query": query},
            timeout=15,
        )

        if response.status_code == 200:

            data = response.json()

            results = data.get(
                "results",
                []
            )

            normalized = []

            for result in results:

                track = normalize_track(result)

                if track:
                    normalized.append(track)

            return normalized

    except requests.RequestException:
        pass

    return []


# ============================================================
# LOGIN
# ============================================================

def start_session(username):

    try:

        response = requests.post(
            f"{BACKEND_URL}/login",
            json={
                "username": username.strip()
            },
            timeout=10,
        )

        if response.status_code != 200:

            try:

                detail = response.json().get(
                    "detail",
                    "Unable to log in.",
                )

            except Exception:

                detail = response.text

            return False, detail

        data = response.json()

        user_id = data["user_id"]
        is_new_user = data["is_new_user"]

        conversation_response = requests.post(
            f"{BACKEND_URL}/conversations",
            json={
                "user_id": user_id,
                "title": "Spotify AI Session",
            },
            timeout=10,
        )

        if conversation_response.status_code != 200:

            try:

                detail = conversation_response.json().get(
                    "detail",
                    "Unable to create conversation.",
                )

            except Exception:

                detail = conversation_response.text

            return False, detail

        conversation = conversation_response.json()

        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.username = username.strip()
        st.session_state.conversation_id = conversation["id"]

        if is_new_user:

            welcome = (
                f"Hey {username.strip()}! 👋 "
                "Welcome to Spotify AI. "
                "I'm your personal music assistant. "
                "Tell me what you're in the mood for, "
                "or ask me for a recommendation."
            )

        else:

            welcome = (
                f"Welcome back, {username.strip()}! 👋 "
                "Ready to find some music?"
            )

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": welcome,
            }
        ]

        return True, None

    except requests.RequestException as exc:

        return False, (
            f"Backend connection failed: {exc}"
        )


# ============================================================
# CHAT
# ============================================================

def send_message(content):

    try:

        response = requests.post(
            f"{BACKEND_URL}/conversations/"
            f"{st.session_state.conversation_id}/messages",
            json={
                "content": content
            },
            timeout=60,
        )

        if response.status_code == 200:

            data = response.json()

            return data.get(
                "content",
                "I couldn't generate a response.",
            )

        try:

            detail = response.json().get(
                "detail",
                "Backend returned an error.",
            )

        except Exception:

            detail = response.text

        return f"Backend error: {detail}"

    except requests.RequestException as exc:

        return f"Connection error: {exc}"


# ============================================================
# PARSE SPOTIFY RESULTS FROM LLM RESPONSE
# ============================================================

def parse_spotify_results(content):

    if not content:
        return [], content

    marker = "Spotify results:"

    if marker not in content:
        return [], content

    before, spotify_section = content.split(
        marker,
        1
    )

    tracks = []
    current = None

    for line in spotify_section.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("- "):

            if current:
                tracks.append(current)

            track_text = stripped[2:].strip()

            if " by " in track_text:

                name, artists = track_text.split(
                    " by ",
                    1
                )

            else:

                name = track_text
                artists = "Unknown artist"

            current = {
                "name": name.strip(),
                "artists": artists.strip(),
                "album": "Unknown album",
                "spotify_url": "",
                "album_art": "",
            }

        elif stripped.lower().startswith("album:"):

            if current:

                current["album"] = stripped[
                    len("Album:"):
                ].strip()

        elif stripped.lower().startswith("url:"):
            if current:
                current["spotify_url"] = stripped[len("URL:"):].strip()

        elif stripped.lower().startswith("album art:"):
            if current:
                current["album_art"] = stripped[len("Album Art:"):].strip()

    if current:
        tracks.append(current)

    normalized = []

    for track in tracks:

        normalized_track = normalize_track(track)

        if normalized_track:
            normalized.append(
                normalized_track
            )

    return normalized, before.rstrip()


# ============================================================
# ALBUM ART ENRICHMENT
# ============================================================

def enrich_with_album_art(tracks):

    return tracks


# ============================================================
# SPOTIFY CARD
# ============================================================

def render_spotify_cards(tracks):

    if not tracks:
        return

    for index, raw_track in enumerate(
        tracks,
        start=1
    ):

        track = normalize_track(raw_track)

        if not track:
            continue

        name = safe_text(
            track["name"]
        )

        artists = safe_text(
            track["artists"]
        )

        album = safe_text(
            track["album"]
        )

        url = safe_text(
            track["spotify_url"]
        )

        album_art = safe_text(
            track["album_art"]
        )

        # ----------------------------------------------------
        # Album artwork
        # ----------------------------------------------------

        if album_art:

            art = f"""
                <img
                    src="{album_art}"
                    alt="{name}"
                    style="
                        width:90px;
                        height:90px;
                        min-width:90px;
                        max-width:90px;
                        min-height:90px;
                        max-height:90px;
                        object-fit:cover;
                        border-radius:8px;
                        display:block;
                    "
                >
            """

        else:

            art = """
                <div
                    style="
                        width:90px;
                        height:90px;
                        min-width:90px;
                        flex:0 0 90px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        background:#282828;
                        border-radius:8px;
                        font-size:27px;
                    "
                >
                    🎵
                </div>
            """

        # ----------------------------------------------------
        # Spotify indicator
        # ----------------------------------------------------

        spotify_link = f"""
            <div
                style="
                    color:#1DB954;
                    font-size:11px;
                    font-weight:750;
                    margin-top:7px;
                "
            >
                ▶ Open in Spotify
            </div>
        """

        # ----------------------------------------------------
        # ENTIRE CARD IS THE LINK
        # ----------------------------------------------------

        card = f"""
        <a
            href="{url}"
            target="_blank"
            rel="noopener noreferrer"
            style="
                display:flex;
                width:100%;
                box-sizing:border-box;
                flex-direction:row;
                align-items:center;
                gap:16px;

                background:#181818;
                border:1px solid #2A2A2A;
                border-radius:12px;

                padding:13px 15px;
                margin:0 0 10px 0;

                overflow:hidden;

                color:#FFFFFF;
                text-decoration:none;

                transition:
                    background 0.15s ease,
                    border-color 0.15s ease,
                    transform 0.15s ease;
            "

            onmouseover="
                this.style.background='#222222';
                this.style.borderColor='#3A3A3A';
            "

            onmouseout="
                this.style.background='#181818';
                this.style.borderColor='#2A2A2A';
            "
        >

            {art}

            <div
                style="
                    flex:1 1 auto;
                    min-width:0;
                    overflow:hidden;
                "
            >

                <div
                    style="
                        color:#6A6A6A;
                        font-size:10px;
                        font-weight:700;
                        margin-bottom:3px;
                    "
                >
                    #{index}
                </div>

                <div
                    style="
                        color:#FFFFFF;
                        font-size:15px;
                        font-weight:700;
                        line-height:1.35;
                        margin:0 0 5px 0;

                        overflow:hidden;
                        text-overflow:ellipsis;
                        white-space:nowrap;
                    "
                >
                    {name}
                </div>

                <div
                    style="
                        color:#B3B3B3;
                        font-size:12px;
                        line-height:1.5;

                        overflow:hidden;
                        text-overflow:ellipsis;
                        white-space:nowrap;
                    "
                >
                    <strong style="color:#FFFFFF;">
                        Artist:
                    </strong>

                    {artists}
                </div>

                <div
                    style="
                        color:#777777;
                        font-size:11px;
                        line-height:1.45;
                        margin-top:2px;

                        overflow:hidden;
                        text-overflow:ellipsis;
                        white-space:nowrap;
                    "
                >
                    Album: {album}
                </div>

                {spotify_link}

            </div>

        </a>
        """

        st.html(card)


# ============================================================
# LOGIN SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.html(
        """
        <div
            class="hero"
            style="
                max-width:620px;
                margin:90px auto 26px auto;
            "
        >

            <div
                class="spotify-logo"
                style="margin-bottom:22px;"
            >
                ♪
            </div>

            <div
                class="hero-title"
                style="font-size:28px;"
            >
                Your music, with memory.
            </div>

            <div class="hero-text">
                Spotify AI connects your conversations
                with persistent personalization, so
                recommendations become more relevant
                over time.
            </div>

        </div>
        """
    )

    col_left, col_main, col_right = st.columns(
        [1, 2, 1]
    )

    with col_main:

        if backend_available():

            st.html(
                """
                <div
                    style="
                        text-align:center;
                        margin-bottom:12px;
                    "
                >
                    <span class="status-pill">
                        <span class="status-dot"></span>
                        Online
                    </span>
                </div>
                """
            )

        else:

            st.error(
                "Backend API is offline. "
                "Start FastAPI before continuing."
            )

        username = st.text_input(
            "Username",
            placeholder="Enter Your First Name",
        )

        if st.button(
            "Start Session",
            type="primary",
            use_container_width=True,
        ):

            if not username.strip():

                st.warning(
                    "Enter a username first."
                )

            else:

                with st.spinner(
                    "Starting your music session..."
                ):

                    success, error = start_session(
                        username.strip()
                    )

                if success:

                    st.rerun()

                else:

                    st.error(error)

    st.html(
        """
        <div class="footer">
            Spotify AI · Context-aware music personalization
        </div>
        """
    )

    st.stop()


# ============================================================
# MAIN APPLICATION
# ============================================================

user_id = st.session_state.user_id


# ============================================================
# TOP BAR
# ============================================================

st.html(
    """
    <div class="topbar">

        <div class="brand">

            <div class="spotify-logo">
                ♪
            </div>

            <div class="brand-name">
                Spotify
                <span class="brand-ai">
                    AI
                </span>
            </div>

        </div>

        <span class="status-pill">

            <span class="status-dot"></span>

            Online

        </span>

    </div>
    """
)


# ============================================================
# USER BAR
# ============================================================

left, right = st.columns(
    [0.78, 0.22]
)

with left:

    st.html(
        f"""
        <div class="user-bar">

            <div>

                <div class="user-label">
                    Active user
                </div>

                <div class="user-id">
                    {safe_text(user_id)}
                </div>

            </div>

            <div
                style="
                    color:#1DB954;
                    font-size:12px;
                    font-weight:700;
                "
            >
                ● Personalized
            </div>

        </div>
        """
    )

with right:

    if st.button(
        "Sign out",
        use_container_width=True,
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.last_search = []

        st.rerun()


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="hero">

        <div class="hero-eyebrow">
            Context-aware music assistant
        </div>

        <div class="hero-title">
            Your music,<br>
            with memory.
        </div>

        <div class="hero-text">
            Talk naturally about what you like.
            Spotify AI remembers relevant preferences
            and uses them to make future conversations
            and recommendations more personal.
        </div>

    </div>
    """
)


# ============================================================
# STATS
# ============================================================

stat1, stat2, stat3 = st.columns(3)

with stat1:

    st.html(
        f"""
        <div class="stat-card">

            <div class="stat-value">
                {len(st.session_state.messages)}
            </div>

            <div class="stat-label">
                Conversation messages
            </div>

        </div>
        """
    )

with stat2:

    st.html(
        """
        <div class="stat-card">

            <div class="stat-value">
                Active
            </div>

            <div class="stat-label">
                AI session
            </div>

        </div>
        """
    )

with stat3:

    st.html(
        """
        <div class="stat-card">

            <div class="stat-value">
                Spotify
            </div>

            <div class="stat-label">
                Recommendation engine
            </div>

        </div>
        """
    )


st.html(
    '<div class="divider"></div>'
)


# ============================================================
# TABS
# ============================================================

tab_chat, tab_music = st.tabs(
    [
        "🤖  AI Assistant",
        "🎵  Spotify",
    ]
)


# ============================================================
# AI CHAT
# ============================================================

with tab_chat:

    st.html(
        """
        <div class="section-title">
            AI Assistant
        </div>

        <div class="section-subtitle">
            Tell me what you're listening to,
            what you're feeling, or what you want
            to discover.
        </div>
        """
    )

    st.html(
        '<div class="chip-label">Try asking</div>'
    )

    q1, q2, q3, q4 = st.columns(4)

    quick_prompt = None

    with q1:

        if st.button(
            "🎵 Recommend music",
            use_container_width=True,
        ):

            quick_prompt = (
                "Recommend some music for me."
            )

    with q2:

        if st.button(
            "🏋️ Workout playlist",
            use_container_width=True,
        ):

            quick_prompt = (
                "Recommend energetic songs "
                "for a workout."
            )

    with q3:

        if st.button(
            "😌 Something relaxing",
            use_container_width=True,
        ):

            quick_prompt = (
                "Recommend relaxing music for me."
            )

    with q4:

        if st.button(
            "🎤 My favorite artist",
            use_container_width=True,
        ):

            quick_prompt = (
                "What do you know about "
                "my music preferences?"
            )

    st.html("<br>")

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            content = message["content"]

            if message["role"] == "assistant":

                spotify_tracks, clean_content = (
                    parse_spotify_results(content)
                )

                if clean_content:

                    st.markdown(
                        clean_content
                    )

                if spotify_tracks:

                    spotify_tracks = (
                        enrich_with_album_art(
                            spotify_tracks
                        )
                    )

                    st.html(
                        """
                        <div
                            style="
                                color:#B3B3B3;
                                font-size:12px;
                                margin-top:12px;
                                margin-bottom:8px;
                            "
                        >
                            Spotify results:
                        </div>
                        """
                    )

                    render_spotify_cards(
                        spotify_tracks
                    )

            else:

                st.markdown(content)

    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    user_prompt = st.chat_input(
        "What do you want to listen to?"
    )

    final_prompt = (
        quick_prompt
        or user_prompt
    )

    if final_prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": final_prompt,
            }
        )

        with st.chat_message("user"):

            st.markdown(
                final_prompt
            )

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                reply = send_message(
                    final_prompt
                )

            spotify_tracks, clean_content = (
                parse_spotify_results(
                    reply
                )
            )

            if clean_content:

                st.markdown(
                    clean_content
                )

            if spotify_tracks:

                spotify_tracks = (
                    enrich_with_album_art(
                        spotify_tracks
                    )
                )

                st.html(
                    """
                    <div
                        style="
                            color:#B3B3B3;
                            font-size:12px;
                            margin-top:12px;
                            margin-bottom:8px;
                        "
                    >
                        Spotify results:
                    </div>
                    """
                )

                render_spotify_cards(
                    spotify_tracks
                )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )

        st.rerun()


# ============================================================
# SPOTIFY SEARCH TAB
# ============================================================

with tab_music:

    st.html(
        """
        <div class="section-title">
            Spotify Discovery
        </div>

        <div class="section-subtitle">
            Search the Spotify catalogue through
            your FastAPI backend.
        </div>
        """
    )

    search_col, button_col = st.columns(
        [0.82, 0.18]
    )

    with search_col:

        search_query = st.text_input(
            "Search",
            placeholder="Artist, song, album...",
            label_visibility="collapsed",
        )

    with button_col:

        search_clicked = st.button(
            "Search",
            type="primary",
            use_container_width=True,
        )

    if search_clicked:

        if not search_query.strip():

            st.warning(
                "Enter something to search."
            )

        else:

            with st.spinner(
                "Searching Spotify..."
            ):

                results = spotify_search(
                    search_query.strip()
                )

            st.session_state.last_search = (
                results
            )

    results = st.session_state.last_search

    if results:

        st.html(
            f"""
            <div
                style="
                    color:#B3B3B3;
                    font-size:12px;
                    margin:18px 0 12px 0;
                "
            >
                Showing {len(results[:10])}
                results
            </div>
            """
        )

        render_spotify_cards(
            results[:10]
        )

    else:

        st.html(
            """
            <div
                class="card"
                style="
                    text-align:center;
                    padding:50px 20px;
                "
            >

                <div
                    style="
                        font-size:32px;
                        margin-bottom:12px;
                    "
                >
                    🎧
                </div>

                <div class="card-title">
                    Discover something new
                </div>

                <div class="card-subtitle">
                    Search for an artist, track,
                    or album to explore Spotify
                    results.
                </div>

            </div>
            """
        )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">
        Spotify AI · Your music, with memory.
             © Copyright Shantanu Das
    </div>
    """
)