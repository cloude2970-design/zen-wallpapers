import json
import requests
import random
import os
import datetime

# Configuration
UNSPLASH_ACCESS_KEY = "F78PJHZ-dLOT8DUqvzpN9_EKvlZS8JloqfzmDYQM1UU"
OUTPUT_FILE = "s-grade-curated.json"

# Themes
THEME_ZEN = [
    "zen", "minimal", "calm nature", "fog", "still water", 
    "japanese garden", "monochrome landscape", "misty forest", 
    "meditation", "simple beauty"
]
THEME_FOOD = [
    "minimalist food", "gourmet plating", "coffee art", "dark food photography", 
    "culinary detail", "fresh ingredients", "tea ceremony", "bread texture", 
    "chefs table", "wine glass"
]
THEME_TRAVEL = [
    "minimalist landscape", "mountain aerial", "ocean horizon", "desert dunes", 
    "city street rainy", "foggy bridge", "snow peak", "train journey", 
    "lighthouse", "cliff edge"
]

def get_current_theme_queries():
    hour = datetime.datetime.now().hour
    # Rotate based on hour: 0=Zen, 1=Food, 2=Travel
    idx = hour % 3
    if idx == 0:
        print(f"Hour {hour}: Theme Zen/Nature")
        return THEME_ZEN, "Zen/Nature"
    elif idx == 1:
        print(f"Hour {hour}: Theme Food/Culinary")
        return THEME_FOOD, "Food/Culinary"
    else:
        print(f"Hour {hour}: Theme Travel/Landscape")
        return THEME_TRAVEL, "Travel/Landscape"

def fetch_candidates():
    queries, theme_name = get_current_theme_queries()
    query = random.choice(queries)
    print(f"Searching for: {query}")
    
    url = f"https://api.unsplash.com/search/photos?query={query}&orientation=portrait&per_page=30&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['results'], theme_name
    except Exception as e:
        print(f"Error fetching data: {e}")
        return [], theme_name

def is_s_class_material(img):
    # Heuristic for S-Class (Simulated AI Scoring)
    # In a real scenario, this would use a vision model.
    # Here we randomize slightly but favor high likes/downloads as a proxy for quality.
    
    score = 80 # Base score
    
    # Bonus for popularity
    if img['likes'] > 100: score += 5
    if img['likes'] > 500: score += 5
    
    # Random fluctuation for "Aesthetic AI" simulation
    score += random.randint(-10, 10)
    
    # Filter by aspect ratio (roughly portrait)
    w = img['width']
    h = img['height']
    if h < w: return False, 0 # Skip landscapes
    
    return score >= 85, score

def format_url(raw_url):
    # V2.1 Standard: 1320x2868, fp-x=0.5, fp-y=0.8 (safe default for bottom heavy)
    return f"{raw_url}&w=1320&h=2868&auto=format&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.8&q=80"

def main():
    # Load existing
    try:
        with open(OUTPUT_FILE, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []
    
    existing_ids = {item['id'] for item in existing_data}
    
    candidates, theme_name = fetch_candidates()
    new_additions = 0
    
    for img in candidates:
        if img['id'] in existing_ids:
            continue
            
        is_good, score = is_s_class_material(img)
        if is_good:
            new_item = {
                "id": img['id'],
                "url": format_url(img['urls']['raw']),
                "score": score,
                "reason": f"Automated Curation ({theme_name}): High aesthetic score ({score}).",
                "author": img['user']['name']
            }
            existing_data.insert(0, new_item) # Add to top
            existing_ids.add(img['id'])
            new_additions += 1
            print(f"Added: {img['id']} (Score: {score})")
            
            if new_additions >= 5: # Limit to 5 per run to keep it curated
                break
    
    # Save back
    if new_additions > 0:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(existing_data, f, indent=2)
        print(f"Successfully added {new_additions} new wallpapers.")
    else:
        print("No new wallpapers added this run.")

if __name__ == "__main__":
    main()
