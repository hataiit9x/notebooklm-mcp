import sys
sys.path.insert(0, 'src')

from notebooklm_tools.core.client import NotebookLMClient
import html as html_module
import json
import re

# Test extraction directly without initializing client
html = '<div data-app-data="{&quot;quiz&quot;:[{&quot;question&quot;:&quot;test&quot;}]}"></div>'

match = re.search(r'data-app-data="([^"]+)"', html)
assert match, "Pattern should match"

encoded_json = match.group(1)
decoded_json = html_module.unescape(encoded_json)
data = json.loads(decoded_json)

assert data == {"quiz": [{"question": "test"}]}, f"Expected quiz data, got {data}"
print("✓ Extraction works")
