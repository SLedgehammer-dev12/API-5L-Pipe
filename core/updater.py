"""
Automatic Update Checker for API 5L PSL2 & BOTAŞ Pipe QA/QC Suite.
Queries GitHub Releases API to detect new versions and provide download links.
"""

import logging
import re
import ssl
import urllib.request
from typing import Any, Dict

import httpx

from version import __version__

log = logging.getLogger(__name__)

GITHUB_REPO = "SLedgehammer-dev12/API-5L-Pipe"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# Use the operating system trust store (Windows cert store / macOS keychain) in addition
# to the bundled certifi roots. This makes httpx honor corporate / proxy / antivirus CAs
# installed on the machine, resolving "self-signed certificate in certificate chain"
# errors during TLS verification. Guarded so a missing truststore never breaks the app.
try:
    import truststore
    truststore.inject_into_ssl()
    _HAVE_TRUSTSTORE = True
except Exception:
    _HAVE_TRUSTSTORE = False


def _active_proxy() -> str:
    """Best-effort summary of the active HTTPS proxy configuration."""
    try:
        proxies = urllib.request.getproxies()
        for k in ("https", "all", "http"):
            v = proxies.get(k)
            if v:
                return v
    except Exception:
        pass
    return "none"


def _certifi_ok() -> bool:
    """True if the bundled certifi CA bundle is present."""
    try:
        import certifi
        import os
        return os.path.exists(certifi.where())
    except Exception:
        return False

def parse_semver(version_str: str) -> tuple:
    """Extracts (major, minor, patch) integer tuple from version string."""
    clean = re.sub(r'^[^\d]*', '', version_str.strip())
    parts = clean.split('.')
    nums = []
    for p in parts[:3]:
        try:
            nums.append(int(re.search(r'\d+', p).group()))
        except (ValueError, AttributeError):
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)

def is_newer_version(current: str, latest: str) -> bool:
    """Returns True if latest version is strictly greater than current version."""
    return parse_semver(latest) > parse_semver(current)

async def check_for_updates() -> Dict[str, Any]:
    """
    Asynchronously checks GitHub for the latest release.
    Fails safely on network error or rate limit without crashing.
    """
    result = {
        "current_version": __version__,
        "latest_version": __version__,
        "update_available": False,
        "release_name": "",
        "release_notes": "",
        "html_url": f"https://github.com/{GITHUB_REPO}/releases",
        "published_at": "",
        "download_assets": {
            "windows_exe": None,
            "macos_dmg": None
        },
        "status": "up_to_date",
        "message": "Uygulamanız güncel."
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": f"API-5L-Pipe-App/{__version__}"
            }
            resp = await client.get(GITHUB_API_URL, headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                tag_name = data.get("tag_name", "").strip()
                latest_clean = tag_name.lstrip("vV")
                
                result["latest_version"] = latest_clean
                result["release_name"] = data.get("name", tag_name)
                result["release_notes"] = data.get("body", "")
                result["html_url"] = data.get("html_url", result["html_url"])
                result["published_at"] = data.get("published_at", "")

                # Extract download asset URLs
                assets = data.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    download_url = asset.get("browser_download_url")
                    if "windows" in name or name.endswith(".exe"):
                        result["download_assets"]["windows_exe"] = download_url
                    elif "macos" in name or name.endswith(".dmg"):
                        result["download_assets"]["macos_dmg"] = download_url

                # Compare versions
                if is_newer_version(__version__, latest_clean):
                    result["update_available"] = True
                    result["status"] = "update_available"
                    result["message"] = f"Yeni sürüm mevcut: v{latest_clean}"
                else:
                    result["update_available"] = False
                    result["status"] = "up_to_date"
                    result["message"] = f"v{__version__} en güncel sürümdür."
            elif resp.status_code == 404:
                result["status"] = "no_releases"
                result["message"] = "Henüz yayınlanmış bir sürüm bulunamadı."
            elif resp.status_code in (403, 429):
                result["status"] = "rate_limited"
                result["message"] = "GitHub API istek limiti aşıldı. Lütfen daha sonra tekrar deneyiniz."
            else:
                result["status"] = "server_error"
                result["message"] = f"GitHub API yanıt vermedi (HTTP {resp.status_code})."
    except Exception as e:
        # Detect a TLS certificate-verification failure anywhere in the exception chain
        # (httpx may wrap the underlying ssl error in httpx.ConnectError).
        is_ssl = False
        cause = e
        while cause is not None:
            if isinstance(cause, ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in str(cause):
                is_ssl = True
                break
            cause = cause.__cause__

        if is_ssl:
            # Corporate proxy / antivirus that inspects HTTPS with its own self-signed CA.
            log.error("Update check TLS verification failed: %s", e)
            log.error(
                "Diagnostics: truststore=%s active_proxy=%s certifi_bundle_ok=%s",
                _HAVE_TRUSTSTORE, _active_proxy(), _certifi_ok(),
            )
            result["status"] = "ssl_verify"
            result["message"] = (
                "Güncelleme kontrolü TLS doğrulamasında başarısız oldu (kurumsal güvenlik duvarı/"
                "proxy veya antivirüs sertifikası güvenilir değil). İşletim sistemi güven deposu "
                "(truststore) etkinleştirildi. Sorun sürerse ağ yöneticinizden kurumsal CA'nın "
                "Windows sertifika deposuna kurulmasını isteyin."
            )
        else:
            # Do NOT silently swallow: log the real failure so it can be diagnosed.
            log.error("Update check failed: %s", e)
            result["status"] = "offline"
            result["message"] = f"Güncelleme kontrolü yapılamadı: {e}"

    return result
