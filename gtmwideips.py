import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GTM_HOST = "https://192.168.1.245"
USERNAME = "admin"
PASSWORD = "your_password"

# All Wide IP record types to check
WIDEIP_TYPES = ["a", "aaaa", "cname", "mx", "naptr", "srv"]

def get_offline_wideips(host, username, password):
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False
    session.headers.update({"Content-Type": "application/json"})

    offline_wips = []

    for wip_type in WIDEIP_TYPES:
        url = f"{host}/mgmt/tm/gtm/wideip/{wip_type}/stats"

        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # 404 is expected if no WIPs of that type exist
            if response.status_code == 404:
                continue
            print(f"[ERROR] {wip_type.upper()} - {e}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not reach GTM: {e}")
            break

        data = response.json()
        entries = data.get("entries", {})

        for key, val in entries.items():
            nested = val.get("nestedStats", {}).get("entries", {})

            # Extract fields from the nested stats structure
            name = nested.get("tmName", {}).get("description", "unknown")
            availability = nested.get("status.availabilityState", {}).get("description", "")
            enabled = nested.get("status.enabledState", {}).get("description", "")
            reason = nested.get("status.statusReason", {}).get("description", "")

            if availability == "offline":
                offline_wips.append({
                    "name": name,
                    "type": wip_type.upper(),
                    "availability": availability,
                    "enabled": enabled,
                    "reason": reason,
                })

    return offline_wips


def main():
    print(f"Connecting to GTM: {GTM_HOST}\n")
    offline = get_offline_wideips(GTM_HOST, USERNAME, PASSWORD)

    if not offline:
        print("No offline Wide IPs found.")
        return

    print(f"{'NAME':<50} {'TYPE':<8} {'ENABLED':<12} {'REASON'}")
    print("-" * 110)
    for wip in offline:
        print(f"{wip['name']:<50} {wip['type']:<8} {wip['enabled']:<12} {wip['reason']}")

    print(f"\nTotal offline Wide IPs: {len(offline)}")

    # Optional: dump to JSON
    with open("offline_wideips.json", "w") as f:
        json.dump(offline, f, indent=2)
    print("Results saved to offline_wideips.json")


if __name__ == "__main__":
    main()
