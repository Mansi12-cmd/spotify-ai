import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.services.memory_extraction_service import MemoryExtractionService
from app.services.groq_service import GroqService
from app.services.spotify_service import SpotifyService


class ChatService:

    def __init__(self, db: AsyncSession):

        self.db = db

        self.conversation_service = ConversationService(db)
        self.memory_service = MemoryService(db)
        self.memory_extraction_service = MemoryExtractionService()
        self.groq_service = GroqService()
        self.spotify_service = SpotifyService()

    async def create_conversation(
        self,
        user_id: uuid.UUID,
        title: str | None = None,
    ) -> Conversation:

        return await self.conversation_service.create_conversation(
            user_id=user_id,
            title=title,
        )

    async def process_message(
        self,
        conversation_id: uuid.UUID,
        content: str,
    ) -> Message:

        # ==================================================
        # 1. GET CONVERSATION
        # ==================================================

        conversation = (
            await self.conversation_service.get_conversation(
                conversation_id
            )
        )

        if conversation is None:
            raise ValueError(
                f"Conversation not found: {conversation_id}"
            )

        # ==================================================
        # 2. STORE USER MESSAGE
        # ==================================================

        user_message = (
            await self.conversation_service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=content,
            )
        )

        # ==================================================
        # 3. EXTRACT MEMORIES
        # ==================================================

        extracted_memories = (
            await self.memory_extraction_service.extract_memories(
                content
            )
        )

        # ==================================================
        # 4. STORE EXTRACTED MEMORIES
        # ==================================================

        for extracted in extracted_memories:

            existing_memory = (
                await self.memory_service.get_active_memory(
                    user_id=conversation.user_id,
                    predicate=extracted.predicate,
                    value=extracted.value,
                )
            )

            if existing_memory is not None:
                continue

            await self.memory_service.create_memory(
                user_id=conversation.user_id,
                predicate=extracted.predicate,
                value=extracted.value,
                confidence=extracted.confidence,
                source="llm_extraction",
                source_message_id=user_message.id,
            )

        # ==================================================
        # 5. RETRIEVE ACTIVE MEMORIES
        # ==================================================

        memories = (
            await self.memory_service.get_active_memories(
                user_id=conversation.user_id
            )
        )

        # ==================================================
        # 6. BUILD MEMORY CONTEXT
        # ==================================================

        memory_context = ""

        if memories:

            memory_lines = [
                "Known user preferences and facts:"
            ]

            for memory in memories:

                memory_lines.append(
                    f"- {memory.predicate}: {memory.value}"
                )

            memory_context = "\n".join(
                memory_lines
            )

        # ==================================================
        # 7. DETERMINE MUSIC REQUEST
        #
        # The classifier can now identify:
        #
        # - Explicit artist requests
        # - Memory-triggered artist requests
        # - Generic music requests
        # - Mood-based requests
        # - Lesser-known requests
        #
        # Example:
        #
        # Memory:
        #   when sad: Post Malone
        #
        # User:
        #   "I'm feeling sad"
        #
        # Result:
        #   needs_spotify = True
        #   artist = Post Malone
        #
        # Whereas:
        #
        # User:
        #   "I'm feeling happy"
        #
        # Result:
        #   needs_spotify = True
        #   artist = None
        #   search_query = "happy music"
        # ==================================================

        music_request = (
            await self.groq_service.determine_music_request(
                user_message=content,
                memory_context=memory_context,
            )
        )

        spotify_results = []
        spotify_context = ""

        # ==================================================
        # 8. SEARCH SPOTIFY
        # ==================================================

        if music_request.get("needs_spotify"):

            artist = music_request.get("artist")

            search_query = music_request.get(
                "search_query"
            )

            lesser_known = music_request.get(
                "lesser_known",
                False,
            )

            try:

                # --------------------------------------------------
                # 8A. ARTIST-SPECIFIC SEARCH
                #
                # Used when:
                #
                # - User explicitly names an artist
                # - Memory maps the request to an artist
                #
                # Example:
                #
                # "I'm feeling sad"
                #
                # Memory:
                # sad -> Post Malone
                # --------------------------------------------------

                if artist:

                    spotify_results = (
                        await self.spotify_service.search_artist_tracks(
                            artist_name=artist,
                            limit=10,
                        )
                    )

                # --------------------------------------------------
                # 8B. GENERIC MUSIC SEARCH
                #
                # Used when there is no artist-specific memory.
                #
                # Example:
                #
                # "I'm feeling happy"
                #
                # search_query:
                # "happy music"
                # --------------------------------------------------

                elif search_query:

                    spotify_results = (
                        await self.spotify_service.search_tracks(
                            query=search_query,
                            limit=10,
                        )
                    )

                # --------------------------------------------------
                # 8C. LESSER-KNOWN FILTERING
                # --------------------------------------------------

                if lesser_known and spotify_results:

                    spotify_results = sorted(
                        spotify_results,
                        key=lambda track: track.get(
                            "popularity",
                            0,
                        ),
                    )

                # --------------------------------------------------
                # 8D. SELECT THE BEST MATCH
                #
                # Groq returns the NUMBER of the best track.
                # We then move that exact Spotify result to #1.
                #
                # Using the numeric position is safer than trying
                # to match track names/artists returned by the LLM.
                # --------------------------------------------------

                selected_track_number = None

                if spotify_results:

                    selected_track_number = (
                        await self.groq_service.select_spotify_track(
                            user_message=content,
                            spotify_tracks=spotify_results,
                            memory_context=memory_context,
                        )
                    )

                # --------------------------------------------------
                # 8E. MOVE SELECTED TRACK TO FIRST POSITION
                # --------------------------------------------------

                if selected_track_number is not None:

                    selected_index = (
                        selected_track_number - 1
                    )

                    if 0 <= selected_index < len(
                        spotify_results
                    ):

                        selected_track = (
                            spotify_results.pop(
                                selected_index
                            )
                        )

                        spotify_results.insert(
                            0,
                            selected_track,
                        )

                # ==================================================
                # 9. BUILD REAL SPOTIFY CONTEXT
                # ==================================================

                spotify_context = ""

                if spotify_results:

                    spotify_lines = [
                        "REAL SPOTIFY TRACKS AVAILABLE FOR THIS RESPONSE:"
                    ]

                    for track in spotify_results:

                        artists = ", ".join(
                            track["artists"]
                        )

                        spotify_lines.append(
                            f"- {track['name']} | "
                            f"Artists: {artists} | "
                            f"Album: {track['album']} | "
                            f"Popularity: {track.get('popularity', 0)}"
                        )

                    spotify_context = "\n".join(
                        spotify_lines
                    )

            except Exception:
                # Continue without Spotify results if the search fails.
                spotify_results = []

        # ==================================================
        # 10. GENERATE ASSISTANT RESPONSE
        # ==================================================

        assistant_content = (
            await self.groq_service.generate_response(
                user_message=content,
                memory_context=memory_context,
                spotify_context=spotify_context,
            )
        )

        # ==================================================
        # 11. APPEND REAL SPOTIFY RESULTS
        #
        # The selected/recommended track has already been
        # moved to index 0 above, so it will always appear
        # first in this section.
        # ==================================================

        if spotify_results:

            assistant_content += (
                "\n\nSpotify results:\n"
            )

            for index, track in enumerate(
                spotify_results
            ):

                if index == 0:

                    assistant_content += (
                        f"- Recommended: "
                        f"{track['name']} by "
                        f"{', '.join(track['artists'])}\n"
                    )

                else:

                    assistant_content += (
                        f"- {track['name']} by "
                        f"{', '.join(track['artists'])}\n"
                    )

                assistant_content += (
                    f"  Album: {track['album']}\n"
                    f"  URL: {track['spotify_url']}\n"
                    f"  Album Art: "
                    f"{track.get('album_art') or ''}\n"
                )

        # ==================================================
        # 12. STORE ASSISTANT RESPONSE
        # ==================================================

        assistant_message = (
            await self.conversation_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content,
            )
        )

        return assistant_message