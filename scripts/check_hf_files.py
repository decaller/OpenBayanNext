import requests

url = "https://huggingface.co/api/datasets/Maktabati/shamela-vectors"
r = requests.get(url).json()
siblings = r.get("siblings", [])
for s in siblings[:15]:
    print(s)
