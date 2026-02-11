import json
import re

INPUT_FILE = 'zen-wallpapers/s-grade-curated.json'
OUTPUT_FILE = 'zen-wallpapers/s-grade-curated.json'

# V3.1 Standard: 1440x2560 (9:16)
TARGET_W = 1440
TARGET_H = 2560

def optimize_url(url):
    # Replace or append width
    if 'w=' in url:
        url = re.sub(r'w=\d+', f'w={TARGET_W}', url)
    else:
        url += f'&w={TARGET_W}'
        
    # Replace or append height
    if 'h=' in url:
        url = re.sub(r'h=\d+', f'h={TARGET_H}', url)
    else:
        url += f'&h={TARGET_H}'
        
    # Ensure crop mode is focalpoint
    if 'fit=crop' not in url:
        url += '&fit=crop'
    if 'crop=focalpoint' not in url:
        url += '&crop=focalpoint'
        
    # Ensure fp-x is centered (0.5) if missing
    if 'fp-x=' not in url:
        url += '&fp-x=0.5'
        
    # Ensure fp-y exists (default to 0.75 "grounded" if missing)
    if 'fp-y=' not in url:
        url += '&fp-y=0.75'
        
    return url

try:
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    original_count = len(data)
    updated_count = 0
    
    for item in data:
        old_url = item.get('url', '')
        new_url = optimize_url(old_url)
        
        if new_url != old_url:
            item['url'] = new_url
            updated_count += 1
            
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Optimization Complete.")
    print(f"Total Images: {original_count}")
    print(f"Updated: {updated_count}")
    print(f"Standard Applied: {TARGET_W}x{TARGET_H} (Focal Point Crop)")

except Exception as e:
    print(f"Error: {e}")
