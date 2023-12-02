import requests

page_url = "https://www.fedex.com/fedextrack/?trknbr=774233588310&trkqual=2460276000~774233588310~FX"
headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(page_url, headers=headers)
if response.status_code != 200:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

print(response.content)