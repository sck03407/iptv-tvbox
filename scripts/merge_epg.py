import os
import glob
import re
from pathlib import Path

CHANNEL_RE = re.compile(r'(<channel id=".*?">.*?</channel>)', re.DOTALL)
PROGRAMME_RE = re.compile(r'(<programme start=".*?">.*?</programme>)', re.DOTALL)
CHANNEL_ID_RE = re.compile(r'id="([^"]+)"')

def main():
    epg_dir = Path("output/epg")
    output_file = epg_dir / "custom_epg.xml"
    
    # Find all partial EPG files (custom_epg_0.xml, custom_epg_1.xml, ...)
    partial_files = sorted(epg_dir.glob("custom_epg_*.xml"))
    
    if not partial_files:
        print("No partial EPG files found to merge.")
        return

    print(f"Found {len(partial_files)} partial EPG files. Merging...")

    # Header and Footer for XMLTV
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="WebGrab+Plus/w MDB &amp; REX Postprocess -- version V5.5.3.0 -- Jan van Straaten" generator-info-url="http://www.webgrabplus.com">\n'
    xml_footer = '</tv>'

    all_channels = []
    all_programmes = []
    
    seen_channel_ids = set()

    for p_file in partial_files:
        content = p_file.read_text(encoding='utf-8', errors='ignore')
        
        channels = CHANNEL_RE.findall(content)
        programmes = PROGRAMME_RE.findall(content)
        
        for ch in channels:
            id_match = CHANNEL_ID_RE.search(ch)
            if id_match:
                ch_id = id_match.group(1)
                if ch_id not in seen_channel_ids:
                    seen_channel_ids.add(ch_id)
                    all_channels.append(ch)
        
        all_programmes.extend(programmes)
        
        # Cleanup partial file
        # p_file.unlink() 

    # Write merged file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_header)
        f.write('\n'.join(all_channels))
        f.write('\n')
        f.write('\n'.join(all_programmes))
        f.write('\n')
        f.write(xml_footer)
    
    print(f"Successfully merged {len(all_channels)} channels and {len(all_programmes)} programmes into {output_file}")

if __name__ == "__main__":
    main()
