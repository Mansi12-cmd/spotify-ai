import base64

import httpx

from app.config import settings


class SpotifyService:

    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_BASE_URL = "https://api.spotify.com/v1"

    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET

    async def get_access_token(self) -> str:

        credentials = (
            f"{self.client_id}:{self.client_secret}"
        )

        encoded_credentials = base64.b64encode(
            credentials.encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "client_credentials",
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                self.TOKEN_URL,
                headers=headers,
                data=data,
            )

            response.raise_for_status()

            result = response.json()

        return result["access_token"]

    async def search_tracks(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict]:

        access_token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        params = {
            "q": query,
            "type": "track",
            "limit": min(limit, 10),
        }

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.API_BASE_URL}/search",
                headers=headers,
                params=params,
            )

            response.raise_for_status()

            data = response.json()

        tracks = (
            data.get("tracks", {})
            .get("items", [])
        )

        return [
            {
                "id": track["id"],
                "name": track["name"],
                "artists": [
                    artist["name"]
                    for artist in track["artists"]
                ],
                "album": track["album"]["name"],
                "spotify_url": track["external_urls"]["spotify"],
                "album_art": (
                    track["album"]["images"][0]["url"]
                    if track["album"].get("images")
                    else None
                ),
                "popularity": track.get(
                    "popularity",
                    0,
                ),
            }
            for track in tracks
        ]

    async def search_artist_tracks(
        self,
        artist_name: str,
        limit: int = 10,
    ) -> list[dict]:

        tracks = await self.search_tracks(
            query=f'artist:"{artist_name}"',
            limit=limit,
        )

        artist_name_normalized = (
            artist_name.strip().lower()
        )

        filtered_tracks = []

        for track in tracks:

            artist_names = [
                artist.strip().lower()
                for artist in track["artists"]
            ]

            if artist_name_normalized in artist_names:

                filtered_tracks.append(track)

        return filtered_tracks