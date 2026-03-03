MINIMAL_PROMPT = """You are an expert interior designer and photorealistic 3D renderer. Transform the provided room image into a "Minimalist Living Room" while strictly adhering to the reference products provided.

<style_guidelines>
- Simplicity and function above all.
- Muted, monochromatic tones: whites, light grays, soft beiges.
- Open space with breathing room between pieces.
- Carefully curated essentials only - less is more.
- Clean surfaces, hidden storage.
- Subtle textures: linen, cotton, light wood.
- Organic shapes balanced with straight lines.
</style_guidelines>

<critical_constraints>
1. ARCHITECTURE: PRESERVE the exact room structure (walls, windows, doors, ceiling).
2. LIGHTING: PRESERVE the room's original lighting direction, natural light sources, and perspective.
3. CLEANUP: Remove ALL existing boxes, clutter, and old furniture from the original image.
4. LAYOUT: Place all furniture logically (e.g., coffee table in front of the sofa, rug under the seating area).
5. WALL DECOR: ALWAYS hang paintings and wall art directly on the walls at eye level. NEVER lean them on the floor.
6. REFERENCE MATCHING: You MUST use the provided reference images. The generated furniture MUST LOOK EXACTLY like the furniture in the reference images (perfectly matching style, color, and design). Do NOT invent random furniture designs.
7. QUALITY: The final output must be a high-resolution, photorealistic interior design photograph.
</critical_constraints>

Generate the styled room now."""

MINIMAL_VARIANT_PROMPTS = [
    MINIMAL_PROMPT + "\n\nVariant 1: Apply Scandinavian warmth with light wood and soft textiles.",
    MINIMAL_PROMPT + "\n\nVariant 2: Apply a Japanese-inspired zen feel with clean lines and natural elements.",
    MINIMAL_PROMPT + "\n\nVariant 3: Apply a contemporary minimal aesthetic with subtle contrast and curated art.",
]
