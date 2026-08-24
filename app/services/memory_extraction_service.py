import json

from groq import AsyncGroq
from pydantic import BaseModel, Field, ValidationError

from app.config import settings


class ExtractedMemory(BaseModel):
    predicate: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)


class MemoryExtractionService:

    def __init__(self):
        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.GROQ_MODEL

    async def extract_memories(
        self,
        content: str,
    ) -> list[ExtractedMemory]:

        prompt = f"""
You are a memory extraction system for a personalized music assistant.

Analyze the user's message and extract information that would be
useful to remember for future conversations.

Extract:
- stable music preferences
- favorite artists
- favorite genres
- preferred languages
- preferred moods
- disliked artists or genres
- explicit user facts relevant to music
- CONDITIONAL music preferences

A conditional music preference is especially important.

For example:

"When I am sad, I like listening to Post Malone."

means:

PREFERS_ARTIST_WHEN_MOOD:
"sad -> Post Malone"

Similarly:

"When I am happy, I like The Script."

means:

PREFERS_ARTIST_WHEN_MOOD:
"happy -> The Script"

Another example:

"When I'm angry I listen to Linkin Park."

means:

PREFERS_ARTIST_WHEN_MOOD:
"angry -> Linkin Park"

Another example:

"I listen to Arijit Singh when I'm feeling romantic."

means:

PREFERS_ARTIST_WHEN_MOOD:
"romantic -> Arijit Singh"

IMPORTANT:
Preserve the relationship between the mood and the artist.
Do NOT convert conditional preferences into a generic
PREFERS_ARTIST memory.

For example, DO NOT turn:

"When I am happy, I like The Script."

into:

PREFERS_ARTIST: "The Script"

Instead use:

PREFERS_ARTIST_WHEN_MOOD: "happy -> The Script"

This distinction is important because the assistant should only
use The Script automatically when the user is expressing the
corresponding mood.

Use concise predicate names such as:

- PREFERS_ARTIST
- PREFERS_GENRE
- PREFERS_LANGUAGE
- PREFERS_MOOD
- PREFERS_DECADE
- DISLIKES_ARTIST
- DISLIKES_GENRE
- DISLIKES_LANGUAGE
- PREFERS_ARTIST_WHEN_MOOD
- PREFERS_GENRE_WHEN_MOOD

For ordinary preferences:

"I really love electronic music."

→ PREFERS_GENRE: "electronic music"

"I love hip hop."

→ PREFERS_GENRE: "hip hop"

"I listen to Arijit Singh a lot."

→ PREFERS_ARTIST: "Arijit Singh"

For conditional preferences:

"When I am sad, I like Post Malone."

→ PREFERS_ARTIST_WHEN_MOOD: "sad -> Post Malone"

"When I am happy, I like The Script."

→ PREFERS_ARTIST_WHEN_MOOD: "happy -> The Script"

"When I'm driving, I like rock music."

→ PREFERS_GENRE_WHEN_MOOD: "driving -> rock music"

Do NOT extract:

- temporary requests
- questions
- information about other people
- general statements that are not about the user
- information that is only implied
- conversational filler
- recommendations made by the assistant
- songs or artists merely mentioned by the user without expressing
  a preference for them

The information must come from the user's own statement.

Return an empty memories array if there is nothing worth remembering.

Return ONLY valid JSON in this exact format:

{{
    "memories": [
        {{
            "predicate": "PREFERS_ARTIST",
            "value": "Arijit Singh",
            "confidence": 0.95
        }}
    ]
}}

For a conditional preference:

{{
    "memories": [
        {{
            "predicate": "PREFERS_ARTIST_WHEN_MOOD",
            "value": "happy -> The Script",
            "confidence": 0.98
        }}
    ]
}}

If there is nothing worth remembering:

{{
    "memories": []
}}

User message:
{content}
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
            response_format={
                "type": "json_object"
            },
        )

        raw_content = (
            response.choices[0].message.content
            or "{}"
        )

        try:

            parsed = json.loads(raw_content)

            if isinstance(parsed, dict):
                memories = parsed.get(
                    "memories",
                    [],
                )

            elif isinstance(parsed, list):
                memories = parsed

            else:
                memories = []

            extracted_memories = []

            for memory in memories:

                try:

                    validated_memory = (
                        ExtractedMemory.model_validate(
                            memory
                        )
                    )

                    extracted_memories.append(
                        validated_memory
                    )

                except ValidationError:
                    continue

            return extracted_memories

        except (
            json.JSONDecodeError,
            TypeError,
        ):
            return []