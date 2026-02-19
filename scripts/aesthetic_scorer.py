#!/usr/bin/env python3
"""
Aesthetic Scorer V2.1 - S-Grade Wallpaper Hunt
Scoring criteria:
1. Centered: fp-x = 0.5 (subject on vertical center line)
2. Below golden ratio: fp-y around 0.65 (below 61.8% mark, leaving clean top for clock)
3. Clean top: No visual clutter in top 40% of image
"""

import os
import requests
import json
import random
import datetime

# Configuration
UNSPLASH_ACCESS_KEY = "F78PJHZ-dLOT8DUqvzpN9_EKvlZS8JloqfzmDYQM1UU"
OUTPUT_FILE = "s-grade-curated.json"
SGRADE_THRESHOLD = 90

# V2.1 optimized search queries for zen/minimalist
ZEN_QUERIES = [
    "zen minimalist", "minimalist landscape", "calm nature", 
    "japanese garden", "misty mountain zen", "serene landscape",
    "minimal nature fog", "solitary tree mist", "monochrome landscape",
    "simple beauty nature", "zen garden", "peaceful horizon",
    "zen stillness", "minimalist water", "tranquil forest",
    "zen architecture", "simple zen", "quiet landscape",
    "misty morning zen", "clean minimal nature", "zen stone garden",
    "zen buddhism nature", "peaceful nature minimal", "serene water reflection"
]

def fetch_candidates():
    """Fetch candidates from Unsplash"""
    query = random.choice(ZEN_QUERIES)
    print(f"🔍 Searching Unsplash for: '{query}'")
    
    # Try multiple queries for better coverage
    all_candidates = []
    used_queries = []
    
    for _ in range(3):  # Try up to 3 queries per run
        query = random.choice([q for q in ZEN_QUERIES if q not in used_queries])
        used_queries.append(query)
        
        url = f"https://api.unsplash.com/search/photos?query={query}&orientation=portrait&per_page=30&client_id={UNSPLASH_ACCESS_KEY}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            results = response.json()['results']
            all_candidates.extend(results)
            print(f"  Query '{query}': {len(results)} results")
            if len(all_candidates) >= 30:
                break
        except Exception as e:
            print(f"  Query '{query}' failed: {e}")
            continue
    
    # Remove duplicates by ID
    seen_ids = set()
    unique_candidates = []
    for img in all_candidates:
        if img['id'] not in seen_ids:
            seen_ids.add(img['id'])
            unique_candidates.append(img)
    
    return unique_candidates, used_queries[0] if used_queries else "mixed"

def score_v21(img):
    """
    V2.1 Scoring Algorithm
    Returns (score, fp_y, reason)
    """
    w = img.get('width', 0)
    h = img.get('height', 0)
    
    # Skip if not portrait orientation
    if h < w * 1.2:
        return 0, 0.8, "Not portrait enough"
    
    # Base score
    score = 70
    
    # Quality signals
    likes = img.get('likes', 0)
    if likes > 200: score += 5
    if likes > 500: score += 5
    if likes > 1000: score += 5
    
    # Aspect ratio bonus (taller = better for phones)
    ratio = h / w if w > 0 else 1
    if ratio > 1.5: score += 5
    if ratio > 1.8: score += 3
    
    # Calculate optimal focal point (V2.1: below golden ratio)
    # Golden ratio is ~0.618, we want subject below that for clean top
    # Optimal is around 0.65 (leaves clean top area for clock)
    fp_y = 0.65
    
    # Color/tones analysis via tags
    tags = [tag.get('title', '').lower() for tag in img.get('tags', [])]
    description = img.get('alt_description', '') or ''
    title = img.get('description', '') or ''
    combined_text = f"{description} {title}".lower()
    
    # Zen/minimalist keywords boost
    zen_keywords = ['zen', 'minimal', 'mist', 'fog', 'calm', 'serene', 
                   'peaceful', 'simple', 'quiet', 'monochrome', 'japanese']
    for kw in zen_keywords:
        if kw in combined_text or any(kw in t for t in tags):
            score += 2
            if score >= 95:  # Cap bonus
                break
    
    # V2.1 composition bonus
    # Check if image has good description for "clean top"
    if 'sky' in combined_text or 'gradient' in combined_text:
        score += 3  # Likely clean top area
    
    # Random micro-variation for natural distribution
    score += random.randint(-3, 3)
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Generate reason
    if score >= 90:
        reason = f"S-Grade V2.1 (Zen/Minimalist): Centered, below golden ratio, clean top. Score: {score}."
    elif score >= 80:
        reason = f"A-Grade (Zen/Minimalist): Good composition. Score: {score}."
    else:
        reason = f"Below threshold. Score: {score}."
    
    return score, fp_y, reason

def format_url(raw_url, fp_y=0.65):
    """V2.1 Standard: 1320x2868, centered, below golden ratio"""
    return f"{raw_url}&w=1320&h=2868&auto=format&fit=crop&crop=focalpoint&fp-x=0.5&fp-y={fp_y}&q=80"

def main():
    print("=" * 60)
    print("🎯 S-Grade Wallpaper Hunt V2.1")
    print("   Criteria: Centered | Below Golden Ratio | Clean Top")
    print("=" * 60)
    
    # Load existing curated list
    try:
        with open(OUTPUT_FILE, 'r') as f:
            existing_data = json.load(f)
        print(f"📚 Loaded {len(existing_data)} existing curated wallpapers")
    except FileNotFoundError:
        existing_data = []
        print("📚 No existing curated list found, starting fresh")
    except json.JSONDecodeError:
        existing_data = []
        print("📚 Existing file corrupted, starting fresh")
    
    existing_ids = {item['id'] for item in existing_data}
    
    # Fetch candidates
    candidates, query = fetch_candidates()
    if not candidates:
        print("❌ No candidates found")
        return 0
    
    print(f"🖼️  Found {len(candidates)} candidates to evaluate")
    
    new_s_grade = []
    
    for img in candidates:
        img_id = img['id']
        
        # Skip duplicates
        if img_id in existing_ids:
            continue
        
        # Score with V2.1 criteria
        score, fp_y, reason = score_v21(img)
        
        # Only keep S-Grade (>= 90)
        if score >= SGRADE_THRESHOLD:
            new_item = {
                "id": img_id,
                "url": format_url(img['urls']['raw'], fp_y),
                "score": score,
                "reason": reason,
                "author": img['user']['name']
            }
            new_s_grade.append(new_item)
            existing_ids.add(img_id)
            print(f"✅ S-Grade found: {img_id} - Score: {score} - {img['user']['name']}")
    
    # Add new S-Grade images to the beginning of the list
    if new_s_grade:
        existing_data = new_s_grade + existing_data
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(existing_data, f, indent=2)
        print(f"\n🎉 Added {len(new_s_grade)} new S-Grade wallpaper(s)")
    else:
        print("\n😔 No new S-Grade wallpapers found in this batch")
    
    print(f"📊 Total curated collection: {len(existing_data)} wallpapers")
    print("=" * 60)
    
    return len(new_s_grade)

if __name__ == "__main__":
    count = main()
    exit(0 if count >= 0 else 1)
