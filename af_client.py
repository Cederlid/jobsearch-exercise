import os
import json
import requests

BASE_URL = "https://jobsearch.api.jobtechdev.se"
SEARCH_ENDPOINT = f"{BASE_URL}/search"

os.makedirs("raw", exist_ok=True)


def _get_ads(params: dict) -> dict:
    """
    Gör en GET-förfrågan till JobSearch API.
    - params: dictionary med query-parametrar
    - returnerar: JSON som Python-dict
    """
    headers = {"accept": "application/json"}

    try:
        response = requests.get(
            SEARCH_ENDPOINT,
            headers=headers,
            params=params,
            timeout=10 
        )
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fel vid API-anrop: {e}")
        raise


def fetch_all_ads(published_after: str, region: str) -> list:
    """
    Hämtar alla annonser enligt filter:
     - publiceringsdatum efter 'published_after'
     - plats = region
     Hanterar paginering med offset/limit.
    Returnerar en lista med alla träffar.
    """
    all_hits = []
    limit = 100   # Max antal per request
    offset = 0    # Börja på första sidan

    while True:
        params = {
            "published-after": published_after,  # ISO8601-format: YYYY-MM-DD
            "region": region,                   # Stockholm-regionens kod enligt API
            "limit": limit,
            "offset": offset,
            "sort": "published.desc"            # sortera nyast först (om API stöder detta)
        }

        print(f"Hämtar annonser... offset={offset}")
        data = _get_ads(params)

        hits = data.get("hits", [])
        all_hits.extend(hits)

        total = data.get("total", {}).get("value", 0)
        print(f"   Hämtade {len(hits)} / {total}")

        # Avsluta loopen om vi inte fick fler träffar
        if offset + limit >= total:
            break

        # Annars hämta nästa sida
        offset += limit

    return all_hits


def save_raw_json(data: dict, filename: str):
    """
    Sparar hela JSON-svaret till en fil i katalogen raw/.
    """
    filepath = os.path.join("raw", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Sparade resultat till {filepath}")


def main():
    # Steg 1: sätt filter
    published_after = "2025-08-19"   # korrekt ISO-format
    region = "Stockholm"             # OBS: kontrollera i API-dokumentation exakt fältnamn/kod

    # Steg 2: hämta alla annonser
    all_hits = fetch_all_ads(published_after, region)

    # Steg 3: spara hela rå-svaret
    raw_data = {"hits": all_hits}
    save_raw_json(raw_data, "af_stockholm_after_2025-08-19.json")


if __name__ == "__main__":
    main()
