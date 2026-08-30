import json

with open("next_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def find_keys(obj, target, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if target.lower() in k.lower():
                print(f"Found key at {path}.{k}")
            find_keys(v, target, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_keys(item, target, f"{path}[{i}]")

print("Searching for 'expense'...")
find_keys(data, "expense")
print("Searching for 'return'...")
find_keys(data, "return")
print("Searching for 'nav'...")
find_keys(data, "nav")
print("Searching for 'holding'...")
find_keys(data, "holding")
