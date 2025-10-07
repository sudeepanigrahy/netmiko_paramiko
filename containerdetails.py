import requests
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -------------------------------
# Infoblox WAPI info
# -------------------------------
WAPI_URL = "https://<infoblox_ip>/wapi/v2.12"
USER = "username"
PASS = "password"

# -------------------------------
# Step 1: List all network containers
# -------------------------------
def list_network_containers():
    url = f"{WAPI_URL}/networkcontainer"
    resp = requests.get(url, auth=HTTPBasicAuth(USER, PASS), verify=False)
    resp.raise_for_status()
    containers = resp.json()
    print("Available network containers:")
    for i, c in enumerate(containers, start=1):
        print(f"{i}. {_ref_short(c['_ref'])} -> {c.get('network')} ({c.get('comment', '')})")
    return containers

def _ref_short(ref):
    # shortens the _ref for display
    return ref.split(":")[1] if ":" in ref else ref

# -------------------------------
# Step 2: Pick a container (by number)
# -------------------------------
def pick_container(containers):
    choice = int(input("Enter the number of the container you want to query: "))
    return containers[choice - 1]['_ref']

# -------------------------------
# Step 3: List all networks in that container
# -------------------------------
def list_networks_in_container(container_ref):
    url = f"{WAPI_URL}/network"
    params = {"network_container": container_ref}
    resp = requests.get(url, auth=HTTPBasicAuth(USER, PASS), params=params, verify=False)
    resp.raise_for_status()
    networks = resp.json()
    if not networks:
        print("No networks found in this container.")
        return
    print(f"Networks in container {_ref_short(container_ref)}:")
    for net in networks:
        print(f"- {net['network']}")

# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    containers = list_network_containers()
    container_ref = pick_container(containers)
    list_networks_in_container(container_ref)
