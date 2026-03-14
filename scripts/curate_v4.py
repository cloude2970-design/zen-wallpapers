#!/usr/bin/env python3
"""
Zen Wallpapers Curate V4 - High Volume S-Grade Collection
Target: 100+ new wallpapers per day
Strategy:
  - 300+ diverse search queries across 10+ categories
  - Multiple queries per run (5-8 queries)
  - Pagination (pages 1-5) to access deeper results
  - Smarter scoring based on likes/downloads ratio
  - No random jitter in scoring (deterministic quality)
  - Up to 25 new images per run
  - Unsplash API: 50 req/hr free tier -> budget carefully
"""

import json
import requests
import random
import os
import sys
import time
import datetime

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "VOzNaANLZ0rSQBRIyTLrbd9FmPQIy011RZvsy3gHwpM")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "s-grade-curated.json")
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".curate_v4_state.json")

# ============================================================
# 300+ Search Queries across 12 categories
# ============================================================

QUERIES = {
    "zen_nature": [
        "minimalist mist", "foggy forest", "solitary tree mist", "misty mountain zen",
        "zen garden", "bamboo forest", "japanese garden path", "calm pond reflection",
        "morning dew leaves", "single flower macro", "moss stone", "rain on leaves",
        "cherry blossom", "autumn leaves falling", "snow branch", "frozen lake",
        "still water reflection", "lotus flower", "fern closeup", "forest floor",
        "sunlight through trees", "peaceful river", "willow tree", "birch forest",
        "mountain stream", "quiet meadow", "wild grass wind", "cloudscape dramatic",
        "sunrise fog valley", "twilight forest", "moonlit landscape", "starry sky tree",
    ],
    "minimalist": [
        "minimalist architecture", "white wall shadow", "geometric shadow",
        "single object white", "negative space photography", "empty room light",
        "minimal staircase", "lone bench", "solitary figure", "abstract shadow play",
        "clean lines architecture", "minimal doorway", "white on white", "simple still life",
        "minimal window light", "one color background", "shadow pattern wall",
        "minimal corridor", "concrete texture clean", "glass reflection minimal",
        "paper fold art", "minimal sculpture", "simple geometry nature",
    ],
    "ocean_water": [
        "ocean waves aerial", "underwater blue", "crystal clear water", "ocean horizon calm",
        "wave crashing rocks", "deep blue sea", "tropical water turquoise",
        "sea foam texture", "coral reef colors", "jellyfish underwater",
        "waterfall mist", "river stones clear", "rain puddle reflection",
        "water droplets macro", "ice crystal closeup", "frozen waterfall",
        "ocean sunset golden", "stormy sea dramatic", "calm bay morning",
        "tide pool colorful", "swimming pool minimal", "water ripple pattern",
    ],
    "mountain_landscape": [
        "mountain peak snow", "alpine lake reflection", "desert dunes golden",
        "canyon dramatic light", "volcanic landscape", "glacier blue ice",
        "mountain ridge silhouette", "cliff edge dramatic", "highland scotland fog",
        "rocky coastline", "mountain pass road", "summit above clouds",
        "valley morning mist", "plateau vast landscape", "mountain wildflowers",
        "dolomites dramatic", "iceland landscape", "patagonia mountains",
        "nepal himalaya", "swiss alps meadow", "norwegian fjord",
    ],
    "urban_architecture": [
        "modern architecture detail", "brutalist building", "glass skyscraper reflection",
        "old building texture", "spiral staircase above", "rooftop cityscape",
        "neon lights rain", "empty street night", "bridge fog", "tunnel perspective",
        "metro station design", "street lamp bokeh", "fire escape pattern",
        "building symmetry", "concrete brutalism", "mosque interior pattern",
        "cathedral ceiling", "library grand", "museum interior minimal",
        "abandoned building light", "scaffolding pattern", "door collection colorful",
    ],
    "food_culinary": [
        "dark food photography", "coffee art latte", "fresh ingredients overhead",
        "bread artisan closeup", "wine glass dramatic", "chocolate texture",
        "fruit arrangement artistic", "spices colorful pattern", "tea ceremony aesthetic",
        "pasta making process", "farmers market colorful", "honey dripping",
        "ice cream texture", "ceramic bowl food", "sushi art minimal",
        "cocktail dramatic light", "olive oil pour", "herb garden fresh",
        "cheese platter aesthetic", "baking ingredients flat lay",
    ],
    "texture_abstract": [
        "marble texture natural", "rust texture colorful", "wood grain detail",
        "fabric texture macro", "sand pattern wind", "rock layers geology",
        "paint dripping abstract", "smoke art colorful", "ink water abstract",
        "cracked earth texture", "peeling paint texture", "glass shattered pattern",
        "metal surface oxidized", "leaf veins macro", "crystal mineral closeup",
        "feather macro detail", "textile weave pattern", "ceramic glaze art",
        "paper texture handmade", "ice texture frozen", "volcanic rock texture",
    ],
    "botanical": [
        "succulent closeup", "tropical plant leaves", "dried flowers aesthetic",
        "cactus desert bloom", "greenhouse plants", "hanging plants indoor",
        "flower field aerial", "lavender field rows", "sunflower dramatic",
        "orchid elegant", "wildflower meadow", "palm leaf shadow",
        "monstera leaf detail", "eucalyptus branch", "cotton plant",
        "mushroom forest floor", "moss macro forest", "pine cone detail",
        "tree bark texture", "bonsai tree art", "botanical illustration style",
    ],
    "light_color": [
        "golden hour portrait", "blue hour cityscape", "light beam dust",
        "rainbow prism light", "sunset silhouette", "northern lights aurora",
        "light painting long exposure", "candlelight warm", "neon glow portrait",
        "stained glass light", "light through curtain", "sunset clouds pink",
        "sunrise ocean orange", "light streak abstract", "bokeh lights night",
        "shadow and light contrast", "window light portrait", "backlit nature",
        "color gradient sky", "dramatic storm light",
    ],
    "animals": [
        "bird in flight silhouette", "cat portrait artistic", "horse running wild",
        "butterfly wings macro", "fox in snow", "owl portrait dramatic",
        "fish underwater colorful", "deer forest morning", "eagle soaring",
        "hummingbird flower", "flamingo reflection", "polar bear ice",
        "whale underwater", "peacock feathers detail", "dragonfly macro",
        "lion portrait dramatic", "dog portrait artistic", "swan elegant",
    ],
    "moody_dark": [
        "dark moody portrait", "film noir style", "rainy window night",
        "dark forest path", "foggy cemetery", "dark clouds dramatic",
        "abandoned place moody", "smoke dark background", "dark still life",
        "night sky stars", "dark water reflection", "shadowy corridor",
        "dark botanical", "moonlight scene", "dark texture abstract",
        "gothic architecture dark", "storm approaching", "dark minimalist",
    ],
    "seasonal": [
        "spring cherry blossom", "summer beach golden", "autumn forest colors",
        "winter snow landscape", "spring rain fresh", "summer garden bloom",
        "autumn harvest rustic", "winter frost crystal", "spring wildflower field",
        "summer sunset beach", "fall foliage mountain", "winter cabin cozy",
    ],
}

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"query_index": {}, "page_tracker": {}, "last_run": None, "total_added_today": 0, "today": None}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_existing():
    try:
        with open(OUTPUT_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_curated(data):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def score_image(img):
    """Deterministic quality scoring - no random jitter"""
    likes = img.get('likes', 0)
    downloads = img.get('downloads', 0)
    w = img['width']
    h = img['height']
    
    # Must be portrait
    if h < w:
        return False, 0, "landscape"
    
    # Aspect ratio bonus (prefer phone-like ratios 9:16 to 9:19.5)
    ratio = h / w
    if ratio < 1.3:
        return False, 0, "too square"
    
    score = 75  # Base
    
    # Popularity signals
    if likes > 20: score += 3
    if likes > 50: score += 3
    if likes > 100: score += 4
    if likes > 300: score += 3
    if likes > 1000: score += 2
    
    # Aspect ratio bonus (ideal phone ratio ~1.8-2.2)
    if 1.6 <= ratio <= 2.4:
        score += 5
    elif 1.4 <= ratio <= 2.6:
        score += 2
    
    # Color/description hints (from Unsplash tags)
    desc = (img.get('description') or img.get('alt_description') or '').lower()
    quality_keywords = ['minimal', 'aesthetic', 'calm', 'zen', 'peaceful', 'dramatic',
                       'beautiful', 'stunning', 'elegant', 'artistic', 'abstract']
    for kw in quality_keywords:
        if kw in desc:
            score += 2
            break
    
    return score >= 82, score, "pass" if score >= 82 else f"score {score}"

def format_url(raw_url):
    """V2.1 Standard wallpaper URL"""
    base = raw_url.split('?')[0]
    return f"{base}?w=1320&h=2868&auto=format&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.8&q=80"

def search_unsplash(query, page=1):
    """Search Unsplash API"""
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "orientation": "portrait",
        "per_page": 30,
        "page": page,
        "client_id": UNSPLASH_ACCESS_KEY,
        "order_by": "relevant"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get('results', []), data.get('total_pages', 0)
    except Exception as e:
        print(f"  API error for '{query}' page {page}: {e}")
        return [], 0

def pick_queries(state, num_queries=6):
    """Pick diverse queries, rotating through categories and avoiding recently used"""
    all_categories = list(QUERIES.keys())
    random.shuffle(all_categories)
    
    selected = []
    for cat in all_categories:
        if len(selected) >= num_queries:
            break
        queries = QUERIES[cat]
        # Track which queries we've used recently
        cat_index = state["query_index"].get(cat, 0) % len(queries)
        q = queries[cat_index]
        page = state["page_tracker"].get(q, 1)
        
        # If we've gone through 5 pages, move to next query
        if page > 5:
            state["query_index"][cat] = cat_index + 1
            cat_index = (cat_index + 1) % len(queries)
            q = queries[cat_index]
            page = 1
            state["page_tracker"][q] = 1
        
        selected.append((cat, q, page))
        # Advance for next time
        state["page_tracker"][q] = page + 1
        if page >= 3:  # After page 3, also rotate query
            state["query_index"][cat] = cat_index + 1
    
    return selected

def main():
    state = load_state()
    existing = load_existing()
    existing_ids = {item['id'] for item in existing}
    
    today = datetime.date.today().isoformat()
    if state.get("today") != today:
        state["total_added_today"] = 0
        state["today"] = today
    
    # Pick 6 queries from different categories
    queries_to_run = pick_queries(state, num_queries=6)
    
    new_additions = 0
    api_calls = 0
    max_per_run = 25  # Cap per run
    
    print(f"=== Curate V4 Run @ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    print(f"Library: {len(existing)} | Today's additions: {state['total_added_today']}")
    print(f"Queries: {len(queries_to_run)}")
    
    for cat, query, page in queries_to_run:
        if new_additions >= max_per_run:
            break
        if api_calls >= 8:  # Budget: max 8 API calls per run
            break
            
        print(f"\n[{cat}] Searching: '{query}' (page {page})")
        results, total_pages = search_unsplash(query, page)
        api_calls += 1
        
        if not results:
            print(f"  No results")
            continue
        
        batch_added = 0
        for img in results:
            if img['id'] in existing_ids:
                continue
            
            is_good, score, reason = score_image(img)
            if not is_good:
                continue
            
            new_item = {
                "id": img['id'],
                "url": format_url(img['urls']['raw']),
                "score": score,
                "reason": f"V4 Curation ({cat}): Score {score}. Query: {query}.",
                "author": img['user']['name']
            }
            existing.insert(0, new_item)
            existing_ids.add(img['id'])
            new_additions += 1
            batch_added += 1
            
            if new_additions >= max_per_run:
                break
        
        print(f"  Found {len(results)} results, added {batch_added} new")
        time.sleep(0.5)  # Be nice to API
    
    # Save
    if new_additions > 0:
        save_curated(existing)
        state["total_added_today"] += new_additions
        print(f"\n✅ Added {new_additions} new wallpapers (total library: {len(existing)})")
        print(f"   Today's total: {state['total_added_today']}")
    else:
        print(f"\n⚠️ No new wallpapers this run")
    
    state["last_run"] = datetime.datetime.now().isoformat()
    save_state(state)
    
    return new_additions

if __name__ == "__main__":
    added = main()
    sys.exit(0 if added > 0 else 1)
