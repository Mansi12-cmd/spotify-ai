import json

from groq import AsyncGroq

from app.config import settings


class GroqService:

    def __init__(self):
        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.GROQ_MODEL

    async def generate_response(
        self,
        user_message: str,
        memory_context: str = "",
        spotify_context: str = "",
    ) -> str:

        system_instruction = f"""
You are a personalized music assistant.

USER MEMORY:
{memory_context}

Use memory when it is relevant to the user's current message.

Do not claim that the user likes something unless it is supported
by the memory or current conversation.

If the user asks about their music taste, summarize it using memory.

If recommending music, use the user's memories and current mood when relevant.

IMPORTANT SPOTIFY RULES:

{spotify_context}

If REAL SPOTIFY TRACKS are provided above:

- Only recommend tracks that appear in the provided tracks.
- Only mention artists that appear in the provided tracks.
- Do not invent songs or artists.
- Prefer a concise, natural recommendation.
- Keep the response focused on the user's request.

If no Spotify tracks are provided:

- Do NOT tell the user that Spotify data is missing.
- Do NOT mention internal retrieval, Spotify context,
  Spotify availability, tools, APIs, or system limitations.
- Do NOT say things such as:
  "I don't have Spotify tracks available."
  "No Spotify data was supplied."
  "I can't pull up tracks."
- Respond naturally to the user's message.
- If the user expressed a mood, acknowledge the mood and
  respond conversationally rather than exposing system details.

RESPONSE STYLE:

Keep responses concise and conversational.

When the user is asking for a song recommendation, use a
"suggestion" style rather than a long explanation.

Prefer this general structure:

"Since you're feeling [mood], I'd go with **[Track] — [Artist]**.
[One short sentence explaining why it fits.]"

Do not add unnecessary disclaimers such as:
"I don't have a Spotify list handy."
"I can't point you to specific songs."
"You can search Spotify yourself."

If real Spotify tracks are available, the assistant has the
Spotify data it needs.

Do not ask the user to provide a Spotify list.

If Spotify data is empty, do not invent a track. In that case,
briefly explain that there are no retrieved Spotify tracks
available for this request.

Do not output a separate "Spotify results" section.
The application will append the actual Spotify results separately.
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction.strip(),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content or ""

    async def determine_spotify_intent(
        self,
        user_message: str,
        memory_context: str = "",
    ) -> dict:

        system_instruction = f"""
You are the music retrieval planner for a personalized
music assistant.

USER MEMORY:
{memory_context}

Determine whether the user's request requires actual
Spotify music retrieval.

Return ONLY valid JSON:

{{
    "needs_spotify": true or false,
    "search_query": "Spotify search query" or null,
    "search_type": "track" or "artist" or "album" or null,
    "selection_criteria": "description of what the returned tracks should satisfy" or null
}}

Rules:

- Use needs_spotify=false for questions about the user's
  preferences, music taste, memories, or general conversation.

- Use needs_spotify=true when the user wants actual songs,
  artists, albums, playlists, or recommendations.

- search_query must contain ONLY things that Spotify can
  meaningfully search for.

- Do NOT put subjective requirements such as "lesser known",
  "underrated", "best", "sad", "good for driving", etc.
  into the search query unless they represent an actual
  searchable concept.

- Put subjective requirements into selection_criteria.

- Resolve references using the conversation and memory.

- If the user explicitly names an artist, song, album, or
  genre, prioritize it.

Example:

User:
"Find Post Malone songs"

{{
    "needs_spotify": true,
    "search_query": "Post Malone",
    "search_type": "track",
    "selection_criteria": "Post Malone tracks"
}}

Example:

User:
"What are some of his lesser known songs?"

Memory:
"User likes Post Malone"

{{
    "needs_spotify": true,
    "search_query": "Post Malone",
    "search_type": "track",
    "selection_criteria": "Prefer lesser-known Post Malone tracks rather than his most popular songs"
}}

Example:

User:
"Recommend some chill songs I'd like"

Memory:
"User likes Post Malone, hip hop and melodic rap"

{{
    "needs_spotify": true,
    "search_query": "melodic hip hop",
    "search_type": "track",
    "selection_criteria": "Chill tracks matching the user's remembered musical preferences"
}}

Example:

User:
"What kind of music do I like?"

{{
    "needs_spotify": false,
    "search_query": null,
    "search_type": null,
    "selection_criteria": null
}}

Do not invent preferences that are not supported by the
memory or current conversation.
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction.strip(),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0,
        )

        raw_response = (
            response.choices[0].message.content or "{}"
        ).strip()

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError:
            return {
                "needs_spotify": False,
                "search_query": None,
                "search_type": None,
                "selection_criteria": None,
            }

        needs_spotify = bool(
            result.get("needs_spotify", False)
        )

        search_query = result.get("search_query")
        search_type = result.get("search_type")
        selection_criteria = result.get("selection_criteria")

        if not needs_spotify:
            search_query = None
            search_type = None
            selection_criteria = None

        if search_query is not None:
            search_query = str(search_query).strip() or None

        if search_type is not None:
            search_type = str(search_type).strip() or None

        if selection_criteria is not None:
            selection_criteria = (
                str(selection_criteria).strip() or None
            )

        return {
            "needs_spotify": needs_spotify,
            "search_query": search_query,
            "search_type": search_type,
            "selection_criteria": selection_criteria,
        }

    async def generate_spotify_search(
        self,
        user_message: str,
        memory_context: str = "",
    ) -> dict:

        system_instruction = f"""
You are a music search planner.

Your job is to convert the user's request into a Spotify
search request.

USER MEMORY:
{memory_context}

Return ONLY valid JSON in exactly this structure:

{{
    "query": "string",
    "search_type": "track" | "artist" | "album"
}}

Rules:

- The query must contain only real, searchable music entities
  or concepts.

- If the user is asking for songs by a specific artist,
  include the artist name in the query.

- If the user asks for lesser-known, underrated, deep-cut,
  obscure, or non-mainstream songs by an artist, search for
  that artist's tracks.

- Do NOT put words like "lesser known" or "underrated" into
  the Spotify query because Spotify cannot reliably search
  by those concepts.

- If the user refers to an artist from the conversation or
  memory, resolve that artist explicitly.

- Never invent artist names, song titles, albums, or genres.

- Prefer an artist-specific query when the request is about
  an artist's catalog.

- search_type should normally be "track" when the user wants
  songs.
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction.strip(),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0,
        )

        raw_response = (
            response.choices[0].message.content or "{}"
        ).strip()

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError:
            return {
                "query": "",
                "search_type": "track",
                "artist": None,
            }

        return {
            "query": str(
                result.get("query", "")
            ).strip(),
            "search_type": result.get(
                "search_type",
                "track",
            ),
            "artist": (
                str(result["artist"]).strip()
                if result.get("artist")
                else None
            ),
        }

    async def determine_music_request(
        self,
        user_message: str,
        memory_context: str = "",
    ) -> dict:

        system_instruction = f"""
You are a music intent classifier for a personalized music assistant.

USER MEMORY:
{memory_context}

Determine whether the user's message would benefit from
actual Spotify music retrieval.

Return ONLY valid JSON:

{{
    "needs_spotify": true or false,
    "artist": "artist name" or null,
    "search_query": "Spotify search query" or null,
    "lesser_known": true or false
}}

IMPORTANT RULES:

1. needs_spotify=true when the user wants:
   - songs
   - tracks
   - artists
   - albums
   - playlists
   - music recommendations
   - music for a mood
   - music based on how they are feeling
   - something to listen to

2. A mood statement can be a music request when it is
   reasonably relevant to music.

   Examples:

   "I am feeling sad"
   "I'm feeling happy"
   "I'm angry today"
   "I need something relaxing"
   "I'm feeling nostalgic"

   These should normally result in:
   needs_spotify=true

3. If the user's mood or request matches a remembered
   music preference, use that preference.

   Example memory:
   "when sad: Post Malone"

   User:
   "I'm feeling sad"

   Return:

   {{
       "needs_spotify": true,
       "artist": "Post Malone",
       "search_query": "Post Malone",
       "lesser_known": false
   }}

4. If the user expresses a mood but there is NO matching
   artist preference in memory, still set needs_spotify=true.

   Example:

   User:
   "I'm feeling happy"

   If there is no happy-related artist preference:

   {{
       "needs_spotify": true,
       "artist": null,
       "search_query": "happy music",
       "lesser_known": false
   }}

5. If the user explicitly names an artist, use that artist.

   Example:

   "Give me some Post Malone"

   {{
       "needs_spotify": true,
       "artist": "Post Malone",
       "search_query": "Post Malone",
       "lesser_known": false
   }}

6. If the user asks for lesser-known, underrated,
   hidden gem, deep cut, obscure, or non-mainstream
   songs, set lesser_known=true.

7. Do NOT put subjective terms such as:
   "lesser known"
   "underrated"
   "best"
   "hidden gems"

   into search_query.

8. search_query must be something Spotify can meaningfully
   search for.

9. If the request is about the user's music taste,
   memories, preferences, or general conversation rather
   than actually finding music, use:

   needs_spotify=false

   Example:

   "What kind of music do I like?"

   {{
       "needs_spotify": false,
       "artist": null,
       "search_query": null,
       "lesser_known": false
   }}

10. Never invent an artist based on unsupported memory.

11. If there is no matching memory, prefer a generic
    searchable query rather than inventing personalization.

Examples:

User:
"I am feeling sad"

Memory:
"when sad: Post Malone"

Return:
{{
    "needs_spotify": true,
    "artist": "Post Malone",
    "search_query": "Post Malone",
    "lesser_known": false
}}

User:
"I am feeling happy"

Memory:
"User likes Post Malone"

Return:
{{
    "needs_spotify": true,
    "artist": null,
    "search_query": "happy music",
    "lesser_known": false
}}

User:
"Give me some lesser known Post Malone songs"

Return:
{{
    "needs_spotify": true,
    "artist": "Post Malone",
    "search_query": "Post Malone",
    "lesser_known": true
}}

User:
"What kind of music do I like?"

Return:
{{
    "needs_spotify": false,
    "artist": null,
    "search_query": null,
    "lesser_known": false
}}

Return ONLY JSON.
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction.strip(),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0,
        )

        raw_response = (
            response.choices[0].message.content or "{}"
        ).strip()

        try:
            result = json.loads(raw_response)

        except json.JSONDecodeError:

            return {
                "needs_spotify": False,
                "artist": None,
                "search_query": None,
                "lesser_known": False,
            }

        needs_spotify = bool(
            result.get("needs_spotify", False)
        )

        artist = result.get("artist")
        search_query = result.get("search_query")

        lesser_known = bool(
            result.get("lesser_known", False)
        )

        if artist is not None:
            artist = str(artist).strip() or None

        if search_query is not None:
            search_query = (
                str(search_query).strip() or None
            )

        if not needs_spotify:
            artist = None
            search_query = None
            lesser_known = False

        return {
            "needs_spotify": needs_spotify,
            "artist": artist,
            "search_query": search_query,
            "lesser_known": lesser_known,
        }

    async def select_spotify_track(
        self,
        user_message: str,
        spotify_tracks: list[dict],
        memory_context: str = "",
    ) -> int | None:

        if not spotify_tracks:
            return None

        track_lines = []

        for index, track in enumerate(
            spotify_tracks,
            start=1,
        ):
            artists = ", ".join(
                track.get("artists", [])
            )

            track_lines.append(
                f"{index}. {track.get('name', '')} | "
                f"Artist: {artists} | "
                f"Album: {track.get('album', '')} | "
                f"Popularity: {track.get('popularity', 0)}"
            )

        spotify_track_list = "\n".join(
            track_lines
        )

        system_instruction = f"""
You select the ONE Spotify track that should be the
primary recommendation for the user's current request.

USER MEMORY:
{memory_context}

AVAILABLE REAL SPOTIFY TRACKS:

{spotify_track_list}

Rules:

- You MUST choose exactly one track from the list.
- NEVER invent a track.
- Consider the user's current request, mood, and relevant memories.
- The numbered list above is the source of truth.
- Return ONLY valid JSON.
- Return the NUMBER of the selected track.
- Do not return the track name.
- Do not return the artist name.

Example:

If the best recommendation is track number 4:

{{
    "track_number": 4
}}

Return ONLY JSON.
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction.strip(),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0,
        )

        raw_response = (
            response.choices[0].message.content or "{}"
        ).strip()

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError:
            return None

        track_number = result.get("track_number")

        try:
            track_number = int(track_number)
        except (TypeError, ValueError):
            return None

        if not 1 <= track_number <= len(spotify_tracks):
            return None

        return track_number