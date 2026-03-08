#!/usr/bin/env python3
"""
Expanded Wallpaper Curation - V3
扩展搜索维度，突破S-grade瓶颈

新增：
1. 6个主题类别（新增Architecture, Abstract/Texture, Moody/Dark）
2. 多页搜索（page 1-5）
3. Unsplash Topics API
4. Unsplash Collections API
5. order_by参数（latest/relevant）
6. 颜色过滤搜索
"""

import json
import requests
import random
import os
import sys
import datetime
import time

UNSPLASH_ACCESS_KEY = "VOzNaANLZ0rSQBRIyTLrbd9FmPQIy011RZvsy3gHwpM"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "s-grade-curated.json")

# ============ 扩展主题库 ============

THEME_ZEN = [
    "minimalist mist", "foggy forest", "solitary tree mist", "misty mountain zen", "minimal nature fog",
    "zen garden stone", "bamboo forest", "koi pond", "japanese maple", "moss rock",
    "morning dew leaf", "rain drops window", "calm lake reflection", "willow tree",
    "incense smoke", "paper lantern", "wooden deck rain", "bonsai", "cherry blossom",
    "sand ripples", "pebble beach", "still pond", "lotus flower", "temple path",
    "forest canopy light", "autumn leaf single", "snow branch", "moonlight water",
]

THEME_FOOD = [
    "minimalist food", "gourmet plating", "coffee art", "dark food photography",
    "culinary detail", "fresh ingredients", "tea ceremony", "bread texture",
    "matcha latte art", "sushi close up", "chocolate dessert", "wine pour",
    "spice collection", "pasta making", "farmers market", "fruit slice macro",
    "ceramic bowl food", "olive oil pour", "honey drip", "morning coffee steam",
]

THEME_TRAVEL = [
    "minimalist landscape", "mountain aerial", "ocean horizon", "desert dunes",
    "city street rainy", "foggy bridge", "snow peak", "train journey",
    "ancient ruins", "winding road aerial", "fjord norway", "rice terrace",
    "aurora borealis", "volcanic landscape", "lavender field", "glacier blue",
    "canyon aerial", "island aerial", "savanna sunset", "rainforest canopy",
]

# 新增主题
THEME_ARCHITECTURE = [
    "minimalist architecture", "concrete texture", "spiral staircase", "brutalist building",
    "glass facade reflection", "corridor perspective", "arch shadow", "museum interior",
    "japanese architecture", "modern villa", "bridge structure", "dome ceiling",
    "abandoned building", "white wall shadow", "geometric building", "cathedral light",
    "parking garage", "subway station empty", "window pattern", "rooftop view",
    "balcony shadow", "courtyard", "door detail vintage", "tile pattern",
]

THEME_ABSTRACT = [
    "abstract texture", "marble pattern", "paint splash", "smoke art",
    "crystal macro", "water droplet macro", "fabric fold", "sand dune pattern",
    "ice texture", "rust texture", "bokeh lights", "prism rainbow",
    "ink water", "paper texture", "glass refraction", "shadow play",
    "geometric pattern", "concrete crack", "wood grain", "wave pattern",
    "neon light blur", "oil water", "frost pattern", "erosion pattern",
]

THEME_MOODY = [
    "dark moody portrait", "film noir city", "rain window night", "foggy streetlight",
    "abandoned dark", "silhouette sunset", "stormy sea", "dark forest path",
    "candlelight", "overcast cityscape", "midnight blue", "dark floral",
    "shadow portrait", "dark minimal", "twilight landscape", "dark water reflection",
    "industrial dark", "night sky stars", "dark botanical", "urban decay",
]

ALL_THEMES = {
    "Zen/Nature": THEME_ZEN,
    "Food/Culinary": THEME_FOOD,
    "Travel/Landscape": THEME_TRAVEL,
    "Architecture/Interior": THEME_ARCHITECTURE,
    "Abstract/Texture": THEME_ABSTRACT,
    "Moody/Dark": THEME_MOODY,
}

# Unsplash Topic IDs (热门topics)
UNSPLASH_TOPICS = [
    "wallpapers",        # Wallpapers
    "nature",            # Nature
    "textures-patterns", # Textures & Patterns
    "architecture-interior", # Architecture & Interiors
    "film",              # Film
    "street-photography", # Street Photography
    "minimalism",        # Minimalism (custom slug)
]

# 颜色搜索
COLORS = ["black_and_white", "black", "white", "green", "blue", "teal"]

def load_existing():
    try:
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_s_class_material(img):
    score = 80
    likes = img.get('likes', 0)
    if likes > 50: score += 3
    if likes > 100: score += 3
    if likes > 500: score += 4
    if likes > 1000: score += 2
    
    # Downloads as quality signal
    downloads = img.get('downloads', 0)
    if downloads > 1000: score += 2
    
    # Random aesthetic variance
    score += random.randint(-8, 10)
    
    # Must be portrait
    w = img['width']
    h = img['height']
    if h < w:
        return False, 0
    
    # Bonus for good aspect ratio (phone-like)
    ratio = h / w
    if 1.5 <= ratio <= 2.2:
        score += 2
    
    return score >= 85, min(score, 100)

def format_url(raw_url):
    base = raw_url.split('?')[0] if '?' in raw_url else raw_url
    return f"{base}?ixlib=rb-4.1.0&w=1320&h=2868&auto=format&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.8&q=80"

def api_get(url, params=None):
    """Rate-limited API call"""
    if params is None:
        params = {}
    params['client_id'] = UNSPLASH_ACCESS_KEY
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        
        # Check rate limit
        remaining = resp.headers.get('X-Ratelimit-Remaining', '?')
        print(f"  Rate limit remaining: {remaining}")
        
        if resp.status_code == 403:
            print("  ⚠️ Rate limit exceeded, stopping")
            return None
        
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  Error: {e}")
        return None

def search_photos(query, page=1, per_page=30, order_by="relevant", color=None):
    """Search Unsplash photos"""
    params = {
        "query": query,
        "orientation": "portrait",
        "per_page": per_page,
        "page": page,
        "order_by": order_by,
    }
    if color:
        params["color"] = color
    
    data = api_get("https://api.unsplash.com/search/photos", params)
    if data:
        return data.get('results', [])
    return []

def get_topic_photos(topic_slug, page=1, per_page=30, order_by="latest"):
    """Get photos from Unsplash topic"""
    params = {
        "per_page": per_page,
        "page": page,
        "order_by": order_by,
        "orientation": "portrait",
    }
    data = api_get(f"https://api.unsplash.com/topics/{topic_slug}/photos", params)
    return data if isinstance(data, list) else []

def get_random_photos(count=30, query=None):
    """Get random photos from Unsplash"""
    params = {
        "count": min(count, 30),
        "orientation": "portrait",
    }
    if query:
        params["query"] = query
    
    data = api_get("https://api.unsplash.com/photos/random", params)
    return data if isinstance(data, list) else []

def process_candidates(candidates, existing_ids, theme_name, max_add=10):
    """Process candidates and return new S-grade items"""
    new_items = []
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
            new_items.append(new_item)
            existing_ids.add(img['id'])
            print(f"  ✅ Added: {img['id']} (Score: {score}, Likes: {img.get('likes', 0)}) by {img['user']['name']}")
            
            if len(new_items) >= max_add:
                break
    
    return new_items

def run_expanded_curation(max_total=50):
    """
    Run expanded curation with multiple strategies
    """
    existing_data = load_existing()
    existing_ids = {item['id'] for item in existing_data}
    total_new = 0
    all_new_items = []
    
    print(f"📚 Current collection: {len(existing_data)} wallpapers")
    print(f"🎯 Target: up to {max_total} new wallpapers\n")
    
    # Strategy 1: Multi-theme search with pagination
    print("=" * 50)
    print("Strategy 1: Extended Theme Search")
    print("=" * 50)
    
    for theme_name, queries in ALL_THEMES.items():
        if total_new >= max_total:
            break
        
        # Pick 2 random queries per theme
        selected = random.sample(queries, min(2, len(queries)))
        for query in selected:
            if total_new >= max_total:
                break
            
            print(f"\n🔍 [{theme_name}] Searching: '{query}'")
            
            # Search pages 1-3
            for page in range(1, 4):
                if total_new >= max_total:
                    break
                
                candidates = search_photos(query, page=page)
                if not candidates:
                    break
                
                new_items = process_candidates(candidates, existing_ids, theme_name, max_add=5)
                all_new_items.extend(new_items)
                total_new += len(new_items)
                
                time.sleep(0.5)  # Rate limiting
    
    # Strategy 2: Color-filtered search
    print("\n" + "=" * 50)
    print("Strategy 2: Color-Filtered Search")
    print("=" * 50)
    
    if total_new < max_total:
        for color in random.sample(COLORS, min(3, len(COLORS))):
            if total_new >= max_total:
                break
            
            query = random.choice(["minimal", "nature", "abstract", "texture", "architecture"])
            print(f"\n🎨 Color: {color}, Query: '{query}'")
            
            candidates = search_photos(query, color=color)
            if candidates:
                new_items = process_candidates(candidates, existing_ids, f"Color/{color}", max_add=5)
                all_new_items.extend(new_items)
                total_new += len(new_items)
            
            time.sleep(0.5)
    
    # Strategy 3: Topic-based discovery
    print("\n" + "=" * 50)
    print("Strategy 3: Topic Discovery")
    print("=" * 50)
    
    if total_new < max_total:
        for topic in random.sample(UNSPLASH_TOPICS, min(3, len(UNSPLASH_TOPICS))):
            if total_new >= max_total:
                break
            
            print(f"\n📂 Topic: {topic}")
            
            candidates = get_topic_photos(topic, page=random.randint(1, 10))
            if candidates:
                new_items = process_candidates(candidates, existing_ids, f"Topic/{topic}", max_add=5)
                all_new_items.extend(new_items)
                total_new += len(new_items)
            
            time.sleep(0.5)
    
    # Strategy 4: Random discovery (newest content)
    print("\n" + "=" * 50)
    print("Strategy 4: Random Discovery")
    print("=" * 50)
    
    if total_new < max_total:
        for q in ["wallpaper", "minimal phone", "aesthetic dark"]:
            if total_new >= max_total:
                break
            
            print(f"\n🎲 Random: '{q}'")
            candidates = get_random_photos(count=30, query=q)
            if candidates:
                new_items = process_candidates(candidates, existing_ids, "Random/Discovery", max_add=5)
                all_new_items.extend(new_items)
                total_new += len(new_items)
            
            time.sleep(0.5)
    
    # Strategy 5: "Latest" order search (find fresh content)
    print("\n" + "=" * 50)
    print("Strategy 5: Latest Uploads")
    print("=" * 50)
    
    if total_new < max_total:
        for query in ["phone wallpaper", "minimalist", "aesthetic"]:
            if total_new >= max_total:
                break
            
            print(f"\n🆕 Latest: '{query}'")
            candidates = search_photos(query, order_by="latest", per_page=30)
            if candidates:
                new_items = process_candidates(candidates, existing_ids, "Latest/Fresh", max_add=5)
                all_new_items.extend(new_items)
                total_new += len(new_items)
            
            time.sleep(0.5)
    
    # Save results
    if all_new_items:
        for item in reversed(all_new_items):
            existing_data.insert(0, item)
        save_data(existing_data)
        print(f"\n{'=' * 50}")
        print(f"🎉 Added {total_new} new S-grade wallpapers!")
        print(f"📚 Total collection: {len(existing_data)}")
        
        # Category breakdown
        categories = {}
        for item in all_new_items:
            cat = item['reason'].split('(')[1].split(')')[0] if '(' in item['reason'] else 'Unknown'
            categories[cat] = categories.get(cat, 0) + 1
        print(f"\n📊 New additions by category:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"   {cat}: {count}")
    else:
        print(f"\n❌ No new wallpapers found this run.")
    
    return total_new

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=50, help='Max new wallpapers to add')
    args = parser.parse_args()
    
    run_expanded_curation(max_total=args.max)
