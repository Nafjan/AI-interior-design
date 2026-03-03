MODERN_PROMPT = """Transform this room into a modern living room design. Apply the following style guidelines:

- Clean lines and geometric forms
- Neutral palette (whites, grays, beiges) with warm accent colors (mustard, terracotta, navy)
- Natural materials: wood, leather, stone, linen
- Minimal clutter, curated accessories
- Good natural and artificial lighting
- Mid-century modern and contemporary furniture pieces

CRITICAL RULES:
- PRESERVE the exact room structure: walls, windows, doors, ceiling must stay in the same position
- PRESERVE the room's lighting direction and natural light sources
- PRESERVE the room dimensions and perspective
- Replace ONLY the furniture and decorative items
- The result must look like a professional interior design photograph
- Photorealistic quality, high resolution

Use the reference product images provided to place similar furniture items in the room. The furniture should match the style and proportions of the reference images."""

MODERN_VARIANT_PROMPTS = [
    MODERN_PROMPT + "\n\nVariant 1: Warm and inviting atmosphere with earth tones.",
    MODERN_PROMPT + "\n\nVariant 2: Cool and sophisticated with blue-gray accents.",
    MODERN_PROMPT + "\n\nVariant 3: Bright and airy with white and natural wood.",
]
