#!/usr/bin/env python3
"""Debug script to test artifact download with detailed logging."""

import asyncio
import httpx
from notebooklm_tools.core.auth import AuthManager
from notebooklm_tools.core.client import NotebookLMClient

async def debug_download():
    """Test download with request/response logging."""

    # Initialize client
    auth = AuthManager()
    profile = auth.load_profile()

    print(f"📦 Profile cookies type: {type(profile.cookies)}")
    if isinstance(profile.cookies, list):
        print(f"   List with {len(profile.cookies)} items")
        if len(profile.cookies) > 0:
            print(f"   First cookie sample: {profile.cookies[0]}")
        # Check for SID cookie
        has_sid = any(c.get("name") == "SID" for c in profile.cookies)
        print(f"   Has SID cookie: {has_sid}")
    elif isinstance(profile.cookies, dict):
        print(f"   Dict with {len(profile.cookies)} keys")
        print(f"   Keys (first 10): {list(profile.cookies.keys())[:10]}")
        print(f"   Has SID cookie: {'SID' in profile.cookies}")

    client = NotebookLMClient(
        cookies=profile.cookies,
        csrf_token=profile.csrf_token,
        session_id=profile.session_id
    )

    print()

    notebook_id = "4085e211-fdb0-4802-b973-b43b9f99b6f7"
    artifact_id = "6d526585-d2b0-4ca1-955f-b3d2a4932200"  # Audio

    # Get artifacts to find URL
    artifacts = client._list_raw(notebook_id)

    # Find audio artifact
    audio_artifact = None
    for a in artifacts:
        if isinstance(a, list) and len(a) > 0 and a[0] == artifact_id:
            audio_artifact = a
            break

    if not audio_artifact:
        print(f"Artifact {artifact_id} not found")
        return

    print(f"Artifact ID: {audio_artifact[0]}")
    print(f"Artifact Type: {audio_artifact[2] if len(audio_artifact) > 2 else 'N/A'}")
    print(f"Artifact Status: {audio_artifact[4] if len(audio_artifact) > 4 else 'N/A'}")

    # Extract URL from metadata[6][5]
    try:
        metadata = audio_artifact[6]
        media_list = metadata[5]
        url = None

        if isinstance(media_list, list):
            for item in media_list:
                if isinstance(item, list) and len(item) > 2 and "audio" in str(item[2]):
                    url = item[0]
                    break
            if not url and len(media_list) > 0 and isinstance(media_list[0], list):
                url = media_list[0][0]

        if not url:
            print("❌ No download URL found in metadata")
            return

        print(f"\n🔗 Download URL: {url[:100]}...")

    except (IndexError, TypeError, KeyError) as e:
        print(f"❌ Error extracting URL: {type(e).__name__}: {e}")
        return

    # Test download with logging
    cookies = client._get_httpx_cookies()
    print(f"\n🍪 Cookies count: {len(list(cookies.jar))}")
    print(f"🍪 Cookie domains:")
    domains = {}
    for cookie in list(cookies.jar):
        domain = cookie.domain or "None"
        domains[domain] = domains.get(domain, 0) + 1
    for domain, count in domains.items():
        print(f"   - {domain}: {count} cookies")

    print(f"\n📋 SID cookie details:")
    for cookie in list(cookies.jar):
        if cookie.name == "SID":
            print(f"   - SID: domain={cookie.domain}, value={cookie.value[:20]}..., path={cookie.path}")

    print(f"\n📋 First 5 cookies:")
    for cookie in list(cookies.jar)[:5]:
        print(f"   - {cookie.name}: domain={cookie.domain}, path={cookie.path}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://notebooklm.google.com/"
    }

    print(f"\n📤 Test 1: Get first response WITHOUT following redirects...")

    async with httpx.AsyncClient(
        cookies=cookies,
        headers=headers,
        follow_redirects=False,
        timeout=120.0
    ) as http_client:
        try:
            response = await http_client.get(url)
            print(f"   Status: {response.status_code}")
            if response.status_code in (301, 302, 303, 307, 308):
                redirect_url = response.headers.get('location', 'None')
                print(f"   Redirects to: {redirect_url[:100]}...")
        except Exception as e:
            print(f"   Error: {type(e).__name__}: {e}")

    print(f"\n📤 Test 2: Follow redirects with max=20...")

    async with httpx.AsyncClient(
        cookies=cookies,
        headers=headers,
        follow_redirects=True,
        timeout=120.0,
        max_redirects=20
    ) as http_client:
        try:
            response = await http_client.get(url)
            print(f"\n✅ Response status: {response.status_code}")
            print(f"📋 Content-Type: {response.headers.get('content-type')}")
            print(f"📏 Content-Length: {len(response.content)} bytes")
            print(f"🔄 Redirect history: {len(response.history)} redirects")

            for i, r in enumerate(response.history):
                print(f"   Redirect {i+1}: {r.status_code} -> {r.headers.get('location', 'N/A')[:80]}")

        except httpx.TooManyRedirects as e:
            print(f"\n❌ Too many redirects!")
            print(f"   Exceeded max_redirects=20")
            print(f"   This suggests a redirect loop, likely due to auth issues")
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(debug_download())
