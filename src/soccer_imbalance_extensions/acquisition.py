from __future__ import annotations

import hashlib
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import requests

from .data import write_json

RELEASE_API = "https://api.github.com/repos/JoaoFgds/soccer-scraper/releases/tags/reproducibility-v1"
PILOT_URLS = {
    "chelsea_schedule_2024": "https://www.transfermarkt.com.br/fc-chelsea/spielplan/verein/631/saison_id/2024",
    "premier_league_market_2024": "https://www.transfermarkt.com.br/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=2024",
}
USER_AGENT = "soccer-imbalance-extensions/0.1 (academic reproducibility pilot; contact via repository)"


def _download(session: requests.Session, url: str, path: Path) -> dict:
    if path.exists():
        content = path.read_bytes()
        return {"cached": True, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
    response = session.get(url, timeout=60)
    response.raise_for_status()
    content = response.content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return {"cached": False, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


def fetch_reference(destination: Path) -> dict:
    """Download public release assets to ignored local storage and verify API digests."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    release = session.get(RELEASE_API, timeout=60)
    release.raise_for_status()
    metadata = release.json()
    wanted = {"analysis-inputs-v1.zip", "soccer-scraper-bronze-v1.zip"}
    records = []
    for asset in metadata["assets"]:
        if asset["name"] not in wanted:
            continue
        archive = destination / "downloads" / asset["name"]
        record = _download(session, asset["browser_download_url"], archive)
        expected = (asset.get("digest") or "").removeprefix("sha256:")
        record.update({"name": asset["name"], "url": asset["browser_download_url"], "expected_sha256": expected})
        if expected and record["sha256"] != expected:
            raise ValueError(f"Checksum mismatch for {asset['name']}")
        extract_to = destination / "extracted" / asset["name"].removesuffix(".zip")
        marker = extract_to / ".complete"
        if not marker.exists():
            extract_to.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(extract_to)
            marker.write_text(record["sha256"] + "\n", encoding="utf-8")
        record["extract_to"] = str(extract_to)
        records.append(record)
    result = {"release": metadata["html_url"], "tag": metadata["tag_name"], "assets": records}
    write_json(destination / "reference_acquisition.json", result)
    return result


def collect_transfermarkt_pilot(cache: Path, report: Path, delay_seconds: float = 3.0) -> dict:
    """Fetch two representative pages; retain HTML only in ignored local cache."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (compatible; soccer-imbalance-extensions research pilot)",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.7",
        }
    )
    records = []
    for index, (name, url) in enumerate(PILOT_URLS.items()):
        if index:
            time.sleep(delay_seconds)
        path = cache / f"{name}.html"
        record = _download(session, url, path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        record.update(
            {
                "name": name,
                "url": url,
                "accessed_at": datetime.now(UTC).isoformat(),
                "contains_schedule_fields": all(token in text for token in ["Chelsea", "Southampton", "2024"]),
                "contains_market_fields": "Marktwert" in text or "Valor de mercado" in text,
                "redistribution": "HTML cache is local-only and ignored by Git; only metadata is published.",
            }
        )
        records.append(record)
    result = {
        "pilot": records,
        "request_count": len(records),
        "access_date": datetime.now(UTC).date().isoformat(),
    }
    write_json(report, result)
    return result
