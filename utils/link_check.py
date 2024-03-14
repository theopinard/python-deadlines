import requests
from urllib.parse import urlparse


def check_link_availability(url, start):
    """
    Checks if a URL is available. If not, tries to retrieve an archived version from the Wayback Machine.
    """
    if url.startswith("https://web.archive.org") or url.startswith("http://web.archive.org"):
        return url
    try:
        response = requests.get(url, allow_redirects=True)
        final_url = response.url
        # Check if the final URL is within the same domain as the original URL
        if urlparse(url).netloc == urlparse(final_url).netloc and final_url != url:
            print(f"URL {url} was redirected within the same domain to: {final_url}")
            return final_url  # Use the final URL for the rest of the process
        elif response.status_code != 200:
            print(
                f"Link {url} is not available (status code: {response.status_code}). Trying to find an archived version..."
            )
        else:
            return url
    except requests.RequestException as e:
        print(f"An error occurred: {e}. Trying to find an archived version...")

    # Try to get an archived version from the Wayback Machine
    archive_url = f"https://archive.org/wayback/available?url={url}&timestamp={start.strftime('%Y%m%d%H%M%S')}"
    try:
        archive_response = requests.get(archive_url)
        if archive_response.status_code == 200:
            data = archive_response.json()
            if (
                data["archived_snapshots"]
                and data["archived_snapshots"]["closest"]
                and data["archived_snapshots"]["closest"]["available"]
            ):
                archived_url = data["archived_snapshots"]["closest"]["url"]
                print(f"Found archived version: {archived_url}")
                return archived_url
            else:
                print("No archived version found.")
                return url
        else:
            print("Failed to retrieve archived version.")
            return url
    except requests.RequestException as e:
        print(f"An error occurred while retrieving the archived version: {e}")
        return url
