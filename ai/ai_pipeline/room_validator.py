import base64
import logging

import httpx

logger = logging.getLogger(__name__)

async def validate_room(api_key: str, image_bytes: bytes) -> dict:
    """
    Validate if the uploaded image is a valid room using Google Cloud Vision API.
    Checks for labels and SafeSearch.
    """
    if not api_key:
        logger.warning("No GOOGLE_CLOUD_API_KEY provided. Skipping room validation.")
        return {"valid": True, "room_type": "unknown", "confidence": 1.0}

    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    b64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "requests": [
            {
                "image": {"content": b64_image},
                "features": [
                    {"type": "LABEL_DETECTION", "maxResults": 10},
                    {"type": "SAFE_SEARCH_DETECTION"}
                ]
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            responses = data.get("responses", [])
            if not responses:
                return {"valid": False, "error": "No response from Vision API"}
                
            result = responses[0]
            
            # 1. SafeSearch validation
            safe_search = result.get("safeSearchAnnotation", {})
            for category in ["adult", "violence", "medical", "racy"]:
                if safe_search.get(category) in ["LIKELY", "VERY_LIKELY"]:
                    return {"valid": False, "error": f"Image flagged for {category} content."}
                    
            # 2. Label validation (must contain room-related labels)
            labels = result.get("labelAnnotations", [])
            label_descriptions = [label["description"].lower() for label in labels]
            
            room_keywords = ["room", "interior design", "furniture", "floor", "wall", "ceiling", "living room", "bedroom"]
            is_room = any(keyword in label for label in label_descriptions for keyword in room_keywords)
            
            if not is_room:
                return {"valid": False, "error": "Image does not appear to be an indoor room."}
                
            return {"valid": True, "room_type": "living_room", "confidence": 0.9}
            
    except Exception as e:
        logger.error(f"Vision API error: {e}")
        # In POC, if API fails, we might just allow it or reject. Let's allow but log.
        return {"valid": True, "room_type": "unknown", "confidence": 1.0, "error": str(e)}
