import os
import requests

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer " + os.environ["RENDER_API_KEY"],
}


def create_postgres(name, owner_workspace_id):
    url = "https://api.render.com/v1/postgres"
    payload = {
        # "databaseName": "randomly generated",
        # "databaseUser": "randomly generated",
        "enableHighAvailability": False,
        "name": name,
        "ownerId": owner_workspace_id,
        "plan": "free",
        # "region": "ohio",  # use default region
        "version": "16",
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    return data


def delete_postgres(postgres_id):
    url = f"https://api.render.com/v1/postgres/{postgres_id}"
    response = requests.delete(url, headers=headers)
    return response


def update_env_var(env_var_key, env_var_value, service_id):
    url = f"https://api.render.com/v1/services/{service_id}/env-vars/{env_var_key}"
    payload = {"value": env_var_value}
    response = requests.put(url, json=payload, headers=headers)
    return response


def list_workspaces():
    url = "https://api.render.com/v1/owners?limit=20"
    response = requests.get(url, headers=headers)
    return response


def get_owner_id():
    resp = list_workspaces()
    return resp.json()[0]["owner"]["id"]


def get_default_workspace_id():
    owner_id = get_owner_id()
    url = f"https://api.render.com/v1/owners/{owner_id}"
    response = requests.get(url, headers=headers)
    return response.json()["id"]


def list_postgres_instances():
    url = "https://api.render.com/v1/postgres?includeReplicas=true&limit=20"
    response = requests.get(url, headers=headers)
    return response.json()


def get_postgres_by_name(name):
    instances = list_postgres_instances()
    for instance in instances:
        postgres = instance["postgres"]
        if postgres["name"] == name:
            return postgres
    raise ValueError(f"No Postgres instance found with name: {name}")


def get_postgres_id_by_name(name):
    postgres = get_postgres_by_name(name)
    return postgres["id"]


def delete_postgres_instance_by_name(name):
    postgres_id = get_postgres_id_by_name(name=name)
    return delete_postgres(postgres_id=postgres_id)
