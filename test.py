import requests

url = "https://airtable.com/v0.3/table/tblSU7Og1vvYkfnkX/listRowsMatchingNameAndFilters"

payload = {
    # Paste the JSON payload you captured here
}

headers = {
    "Content-Type": "application/json"
}

r = requests.post(url, json=payload, headers=headers)

print(r.status_code)
print(r.text[:500])