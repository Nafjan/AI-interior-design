"""Style renderer using Gemini 3.1 Flash Image via OpenRouter."""

import base64
import logging

import httpx

from app.ai_pipeline.prompts.minimal import MINIMAL_VARIANT_PROMPTS
from app.ai_pipeline.prompts.modern import MODERN_VARIANT_PROMPTS

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3.1-flash-image-preview"

STYLE_PROMPTS = {
    "modern": MODERN_VARIANT_PROMPTS,
    "minimal": MINIMAL_VARIANT_PROMPTS,
}


def _image_to_b64_url(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    b64 = base64.b64encode(image_bytes).decode()
    return f"data:{mime};base64,{b64}"


async def generate_styled_room(
    api_key: str,
    original_image_bytes: bytes,
    style: str,
    reference_image_bytes_list: list[bytes],
    variant_index: int = 0,
) -> bytes | None:
    """Generate a styled room image using Gemini 3.1 Flash Image via OpenRouter.

    Returns the generated image bytes, or None on failure.
    """
    prompts = STYLE_PROMPTS.get(style)
    if not prompts:
        logger.error("Unknown style: %s", style)
        return None

    prompt_text = prompts[variant_index % len(prompts)]

    # Build message content: text prompt + original room image + reference images
    content = [{"type": "text", "text": prompt_text}]
    
    # Add reference images if provided to influence the generation
    for ref_bytes in reference_image_bytes_list:
        content.append({
            "type": "image_url",
            "image_url": {"url": _image_to_b64_url(ref_bytes)}
        })
        
    # Always append the original room image last, as the primary subject
    content.append({
        "type": "image_url",
        "image_url": {"url": _image_to_b64_url(original_image_bytes)},
    })

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://ai-home-styling.com",
                    "X-Title": "AI Home Styling Platform",
                },
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": content}],
                },
            )
            response.raise_for_status()
            data = response.json()

            choices = data.get("choices", [])
            if not choices:
                logger.error("No choices in response: %s", data)
                return None

            message = choices[0].get("message", {})

            # Gemini image models return images in message.images[] array
            images = message.get("images", [])
            if images:
                for img in images:
                    if isinstance(img, dict):
                        url = img.get("image_url", {}).get("url", "")
                        if url.startswith("data:image"):
                            b64_data = url.split(",", 1)[1]
                            image_bytes = base64.b64decode(b64_data)
                            logger.info("Generated render: %d bytes", len(image_bytes))
                            return image_bytes

            # Fallback: check content field (some providers may embed images there)
            msg_content = message.get("content")
            if isinstance(msg_content, str) and msg_content.startswith("data:image"):
                b64_data = msg_content.split(",", 1)[1]
                return base64.b64decode(b64_data)

            if isinstance(msg_content, list):
                for part in msg_content:
                    if isinstance(part, dict) and part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url", "")
                        if url.startswith("data:image"):
                            b64_data = url.split(",", 1)[1]
                            return base64.b64decode(b64_data)

            logger.error("No image in response. Content: %s", repr(msg_content)[:200])
            return None

        except httpx.HTTPStatusError as e:
            logger.error("OpenRouter API error %s: %s", e.response.status_code, e.response.text[:500])
            return None
        except Exception as e:
            logger.error("Render generation failed: %s", e)
            return None
