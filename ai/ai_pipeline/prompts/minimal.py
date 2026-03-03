MINIMAL_PROMPT = """Transform this room into a minimalist living room design. Apply the following style guidelines:

- Simplicity and function above all
- Muted, monochromatic tones: whites, light grays, soft beiges
- Open space with breathing room between pieces
- Carefully curated essentials only - less is more
- Clean surfaces, hidden storage
- Subtle textures: linen, cotton, light wood
- Organic shapes balanced with straight lines

CRITICAL RULES:
- PRESERVE the exact room structure: walls, windows, doors, ceiling must stay in the same position
- PRESERVE the room's lighting direction and natural light sources
- PRESERVE the room dimensions and perspective
- Replace ONLY the furniture and decorative items
- The result must look like a professional interior design photograph
- Photorealistic quality, high resolution

Use the reference product images provided to place similar furniture items in the room. The furniture should match the style and proportions of the reference images."""

MINIMAL_VARIANT_PROMPTS = [
    MINIMAL_PROMPT + "\n\nVariant 1: Scandinavian warmth with light wood and soft textiles.",
    MINIMAL_PROMPT + "\n\nVariant 2: Japanese-inspired zen with clean lines and natural elements.",
    MINIMAL_PROMPT + "\n\nVariant 3: Contemporary minimal with subtle contrast and curated art.",
]
