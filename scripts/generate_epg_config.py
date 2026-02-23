import os
import glob
import re
from pathlib import Path

def parse_channels_xml(file_path):
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    matches = re.finditer(r'(<channel[^>]*>([^<]+)</channel>)', content)
    
    found_channels = []
    for match in matches:
        full_tag = match.group(1)
        channel_name = match.group(2).strip()
        
        # Extract xmltv_id
        xmltv_id_match = re.search(r'xmltv_id="([^"]+)"', full_tag)
        xmltv_id = xmltv_id_match.group(1) if xmltv_id_match else channel_name
        
        found_channels.append({
            'line': full_tag,
            'xmltv_id': xmltv_id,
            'name': channel_name
        })
    return found_channels

def main():
    # Define paths
    config_dir = Path("config/webgrabplus")
    siteini_dir = config_dir / "siteini.pack" / "China"
    output_config = config_dir / "WebGrab++.config.xml"
    
    if not siteini_dir.exists():
        raise SystemExit("siteini.pack/China not found")
    
    # Base config template
    config_content = """<?xml version="1.0"?>
<settings>
  <filename>/data/epg/custom_epg.xml</filename>
  <mode>v</mode>
  <postprocess grab="y" run="n">rex</postprocess>
  <user-agent>Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36</user-agent>
  <logging>on</logging>
  <retry time-out="5">4</retry>
  <timespan>8</timespan>
  <update>i</update>

  <!-- Auto-generated Channel List -->
"""
    
    # Priority list of sources to look for
    priority_sources = ["tv.cctv.com", "tv.cntv.cn", "tvsou.com"]
    
    added_xmltv_ids = set()
    channels_buffer = []

    # 1. Process sources in priority
    for source in priority_sources:
        xml_file = siteini_dir / f"{source}.channels.xml"
        
        channels = parse_channels_xml(xml_file)
        print(f"Found {len(channels)} channels in {source}")
        
        for ch in channels:
            if ch['xmltv_id'] in added_xmltv_ids:
                continue
            channels_buffer.append(f"  {ch['line']}")
            added_xmltv_ids.add(ch['xmltv_id'])

    # 2. Fallback scan
    if not channels_buffer:
        print("No priority sources found, scanning all .channels.xml...")
        for xml_file in siteini_dir.glob("*.channels.xml"):
            channels = parse_channels_xml(xml_file)
            for ch in channels:
                if ch['xmltv_id'] not in added_xmltv_ids:
                    channels_buffer.append(f"  {ch['line']}")
                    added_xmltv_ids.add(ch['xmltv_id'])

    # 3. Chunk and Write Configs
    MAX_CHANNELS = 18  # Safe limit under 20
    chunks = [channels_buffer[i:i + MAX_CHANNELS] for i in range(0, len(channels_buffer), MAX_CHANNELS)]
    
    if not chunks:
        chunks = [[]] # Handle empty case

    for idx, chunk in enumerate(chunks):
        chunk_config = f"""<?xml version="1.0"?>
<settings>
  <filename>/data/epg/custom_epg_{idx}.xml</filename>
  <mode>v</mode>
  <postprocess grab="y" run="n">rex</postprocess>
  <user-agent>Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36</user-agent>
  <logging>on</logging>
  <retry time-out="5">4</retry>
  <timespan>8</timespan>
  <update>i</update>

  <!-- Auto-generated Channel Chunk {idx} -->
"""
        chunk_config += "\n".join(chunk)
        chunk_config += "\n</settings>"
        
        chunk_file = config_dir / f"WebGrab++.config.{idx}.xml"
        chunk_file.write_text(chunk_config, encoding='utf-8')
        print(f"Generated WebGrab++.config.{idx}.xml with {len(chunk)} channels.")

    # Also generate full config for reference (optional, but good for backup)
    full_config = f"""<?xml version="1.0"?>
<settings>
  <filename>/data/epg/custom_epg_full.xml</filename>
  <mode>v</mode>
  <postprocess grab="y" run="n">rex</postprocess>
  <user-agent>Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36</user-agent>
  <logging>on</logging>
  <retry time-out="5">4</retry>
  <timespan>8</timespan>
  <update>i</update>

  <!-- Full Channel List (Reference) -->
"""
    full_config += "\n".join(channels_buffer)
    full_config += "\n</settings>"
    output_config.write_text(full_config, encoding='utf-8')
    print(f"Generated full WebGrab++.config.xml with {len(channels_buffer)} channels.")

if __name__ == "__main__":
    main()
