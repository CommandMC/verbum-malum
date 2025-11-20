import argparse
import importlib
import json
import os
import platform
import time

from pathlib import Path
from typing import Optional

import requests


APP_NAME = "VerbumMalum"
VERSION = "v0.1.0"

SESSION = requests.Session()
SESSION.headers["User-Agent"] = f"{APP_NAME}/{VERSION}"


def get_cache_dir() -> Path:
    running_os = platform.system()
    match running_os:
        case "Linux":
            return (
                Path(os.environ.get("XDG_STATE_HOME", "~/.local/state")).expanduser()
                / APP_NAME
            )
        case "Windows":
            return (
                Path(os.environ.get("LOCALAPPDATA", "~/AppData/Local")).expanduser()
                / "Temp"
                / APP_NAME
            )
        case _:
            raise ValueError(f"Unsupported platform: {running_os}")


def ensure_dns_file() -> Path:
    dns_file = get_cache_dir() / "dns.json"

    def download() -> None:
        res = SESSION.get("https://data.iana.org/rdap/dns.json")
        res.raise_for_status()

        dns_file.parent.mkdir(parents=True, exist_ok=True)
        dns_file.write_bytes(res.content)

    do_download = True
    if dns_file.exists():
        stat = dns_file.stat()
        file_age_days = (time.time() - stat.st_mtime) / (60 * 60 * 24)
        if file_age_days < 7:
            do_download = False

    if do_download:
        download()

    return dns_file


def get_tld_rdap_server(tld: str) -> str:
    dns_file = ensure_dns_file()
    dns_entries: dict = json.loads(dns_file.read_text())
    for service in dns_entries.get("services"):
        supported_tlds, service_urls = service
        if any(filter(lambda x: x == tld, supported_tlds)):
            return service_urls[0].rstrip("/")
    raise ValueError(f'No RDAP server found for TLD "{tld}"')


def lookup_domain(domain: str, server: str) -> dict:
    res = SESSION.get(f"{server}/domain/{domain}")
    res.raise_for_status()
    return res.json()


def lookup_registrar(links: list) -> Optional[dict]:
    for link in links:
        link: dict
        is_relevant = link.get("rel") in {"related", "registration"}
        href = link.get("href")
        if not is_relevant or not href:
            continue

        request_kwargs = {
            "url": href,
            "headers": {
                # Aliyun / Dominet (HK) Limited requires these to be set, otherwise they send us malicious responses
                "Accept": "application/json, application/rdap+json",
                "Accept-Language": "en-US,en;q=0.5",
            },
        }

        try:
            res = SESSION.get(**request_kwargs)
        except requests.exceptions.SSLError:
            # Nicenic can't do SSL
            print(f"Failed to connect to {href} with SSL. Retrying without it")
            request_kwargs["verify"] = False
            urllib3 = importlib.import_module("urllib3")
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            res = SESSION.get(**request_kwargs)

        res.raise_for_status()
        result = res.json()

        return result
    return None


def format_json(obj: dict) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="The domain to add an entry for")
    args = parser.parse_args()
    domain: str = args.domain
    tld = domain.split(".")[-1]
    first_letter = domain[0].lower()

    tld_server = get_tld_rdap_server(tld)
    print(f"Found TLD server: {tld_server}")
    registry_result = lookup_domain(domain, tld_server)

    out_dir = Path(f"entries/{first_letter}/{domain}/")
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "registry_response.json").write_text(format_json(registry_result))

    registrar_result = lookup_registrar(registry_result.get("links", []))
    if registrar_result:
        (out_dir / "registrar_response.json").write_text(format_json(registrar_result))

    print(f"Wrote entry to {out_dir}")


if __name__ == "__main__":
    main()
