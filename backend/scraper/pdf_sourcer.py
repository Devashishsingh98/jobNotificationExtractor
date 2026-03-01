"""PDF sourcer — tries to find original PDFs from official government websites.

Given URLs extracted from a Telegram post, attempts to locate the original
notification PDF from the official source rather than a watermarked copy.
"""

import httpx
from urllib.parse import urlparse
from typing import Optional


# Official government domain patterns
OFFICIAL_DOMAINS = [
    "upsc.gov.in",
    "ssc.nic.in",
    "ssc.gov.in",
    "rbi.org.in",
    "ibps.in",
    "nta.ac.in",
    "indianrailways.gov.in",
    "rrbcdg.gov.in",
    "joinindianarmy.nic.in",
    "indiannavy.nic.in",
    "indianairforce.nic.in",
    "drdo.gov.in",
    "isro.gov.in",
    "sail.co.in",
    "ongcindia.com",
    "ntpc.co.in",
    "aai.aero",
    "sbi.co.in",
    "nabard.org",
    "licindia.in",
    "epfindia.gov.in",
    "fci.gov.in",
    # State PSC domains
    "bpsc.bih.nic.in",
    "uppsc.up.nic.in",
    "mppsc.mp.gov.in",
    "rpsc.rajasthan.gov.in",
    "pscwbonline.gov.in",
    "kpsc.kar.nic.in",
    "tnpsc.gov.in",
    "appsc.gov.in",
    "tspsc.gov.in",
    "hppsc.hp.gov.in",
    "ukpsc.gov.in",
    "cgpsc.cg.gov.in",
    "jpsc.gov.in",
    "gpsc.gujarat.gov.in",
    "mpsc.gov.in",
]

# Common Telegram channel watermark domains to skip
WATERMARK_DOMAINS = [
    "t.me",
    "telegram.me",
    "sarkariresult.com",
    "freejobalert.com",
    "employmentnews.gov.in",
]


def is_official_domain(url: str) -> bool:
    """Check if URL belongs to an official government domain."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return any(
            domain == d or domain.endswith("." + d)
            for d in OFFICIAL_DOMAINS
        )
    except Exception:
        return False


def is_pdf_url(url: str) -> bool:
    """Check if URL likely points to a PDF."""
    return url.lower().endswith(".pdf") or "pdf" in url.lower()


async def find_original_pdf(urls: list[str]) -> dict:
    """
    From a list of URLs extracted from a Telegram post,
    find the original PDF from an official source.

    Returns:
        {
            "original_pdf_url": str | None,
            "official_website_url": str | None,
        }
    """
    official_pdf = None
    official_website = None
    any_pdf = None

    for url in urls:
        # Skip watermark/telegram domains
        try:
            parsed = urlparse(url)
            if any(d in parsed.netloc.lower() for d in WATERMARK_DOMAINS):
                continue
        except Exception:
            continue

        if is_official_domain(url):
            if is_pdf_url(url):
                official_pdf = url
                break  # Best case: official PDF link
            else:
                official_website = url
        elif is_pdf_url(url) and not any_pdf:
            any_pdf = url

    # If we found an official website but no PDF, try to verify the PDF link
    if not official_pdf and official_website:
        official_pdf = await try_resolve_pdf(official_website)

    return {
        "original_pdf_url": official_pdf,
        "official_website_url": official_website or (
            # If we have a PDF but no website, extract the base domain
            _get_base_url(official_pdf) if official_pdf else None
        ),
    }


async def try_resolve_pdf(website_url: str) -> Optional[str]:
    """
    Try to find a PDF link on an official website page.
    Makes a HEAD request to check if the URL itself is a PDF.
    """
    try:
        async with httpx.AsyncClient(
            timeout=10.0, follow_redirects=True, verify=False
        ) as client:
            response = await client.head(website_url)
            content_type = response.headers.get("content-type", "")
            if "pdf" in content_type.lower():
                return website_url
    except Exception:
        pass

    return None


def _get_base_url(url: str) -> Optional[str]:
    """Extract base URL from a full URL."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None
