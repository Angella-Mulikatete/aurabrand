import os
import requests
import urllib.parse
from src.state import BrandContext

def generate_image(prompt: str, brand: BrandContext, output_path: str) -> str:
    """
    Generates a brand-aligned visual asset using the free Pollinations AI API.
    Does not require API keys or billing quotas.
    """
    # Enhance prompt with brand style
    enhanced_prompt = f"""
    A professional, high-quality image for the brand '{brand.name}'.
    Subject: {prompt}
    Style: {brand.tone} tone. Minimalist, clean, modern corporate aesthetics.
    Brand colors: heavily features {brand.primary_color}.
    """
    
    import time
    try:
        print(f"--- [Skill: Generating Image for '{prompt[:30]}...'] ---")
        
        # URL Encode the prompt for Pollinations
        encoded_prompt = urllib.parse.quote(enhanced_prompt.replace("\n", " ").strip())
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true"
        
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as handler:
                    handler.write(response.content)
                    
                print(f"✅ Image saved to: {output_path}")
                return os.path.abspath(output_path)
            elif response.status_code == 429:
                print(f"⚠️ Rate limited. Retrying in 3 seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(3)
            else:
                print(f"❌ Image generation failed with status: {response.status_code}")
                return ""
        
        print("❌ Failed after max retries")
        return ""
            
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        # Return empty string to allow the system to fallback to text placeholder
        return ""
