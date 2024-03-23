import requests
from urllib.parse import urlparse
from datetime import date, timedelta
from tqdm import tqdm


def check_link_availability(url, start):
    """
    Checks if a URL is available. If not, tries to retrieve an archived version from the Wayback Machine.
    """
    if url.startswith("https://web.archive.org") or url.startswith("http://web.archive.org"):
        return url
    if start > date.today() - timedelta(days=5 * 365):
        try:
            response = requests.get(url, allow_redirects=True)
            final_url = response.url
            # Check if the final URL is within the same domain as the original URL
            if urlparse(url).netloc == urlparse(final_url).netloc and final_url != url:
                tqdm.write(f"URL {url} was redirected within the same domain to: {final_url}")
                if "?" in final_url and not "?" in url:
                    tqdm.write("Warning: The final URL contains a query string, but the original URL does not.")
                    return url
                return final_url  # Use the final URL for the rest of the process
            elif response.status_code != 200:
                tqdm.write(
                    f"Link {url} is not available (status code: {response.status_code}). Trying to find an archived version..."
                )
            else:
                return url
        except requests.RequestException as e:
            tqdm.write(f"An error occurred: {e}. Trying to find an archived version...")

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
                archived_url = data["archived_snapshots"]["closest"]["url"].replace(":80/", "/")
                if archived_url[4] == ":":
                    archived_url = archived_url[:4] + "s" + archived_url[4:]
                tqdm.write(f"Found archived version: {archived_url}")
                return archived_url
            else:
                tqdm.write("No archived version found.")
                return url
        else:
            tqdm.write("Failed to retrieve archived version.")
            return url
    except requests.RequestException as e:
        tqdm.write(f"An error occurred while retrieving the archived version: {e}")
        return url
