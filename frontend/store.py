"""
Shared file-based store so multiple browser tabs share the same data.
Writes to repair_genie_store.json in the frontend directory.
"""
import json
import os
import time
import filelock

STORE_PATH = os.path.join(os.path.dirname(__file__), "repair_genie_store.json")
LOCK_PATH  = STORE_PATH + ".lock"

DEFAULTS = {
    "chat_media": {},       # msg_key -> base64 encoded bytes
    "contractor_profiles": {},   # id -> profile dict
    "homeowner_profiles":  {},   # id -> profile dict
    "job_requests":        {},   # job_id -> job dict
    "job_messages":        {},   # job_id -> [message, ...]
    "job_status":          {},   # job_id -> "pending"|"accepted"|"declined"
}


def _read() -> dict:
    if not os.path.exists(STORE_PATH):
        return {k: dict(v) for k, v in DEFAULTS.items()}
    try:
        with open(STORE_PATH) as f:
            data = json.load(f)
        # Fill missing keys
        for k, v in DEFAULTS.items():
            if k not in data:
                data[k] = dict(v)
        return data
    except (json.JSONDecodeError, OSError):
        return {k: dict(v) for k, v in DEFAULTS.items()}


def _write(data: dict):
    with filelock.FileLock(LOCK_PATH, timeout=3):
        with open(STORE_PATH, "w") as f:
            json.dump(data, f, indent=2)


def get() -> dict:
    return _read()


def save_contractor_profile(profile: dict):
    data = _read()
    data["contractor_profiles"][profile["id"]] = profile
    _write(data)


def save_homeowner_profile(profile: dict):
    data = _read()
    data["homeowner_profiles"][profile["id"]] = profile
    _write(data)


def get_contractor_profiles() -> list:
    return list(_read()["contractor_profiles"].values())


def get_homeowner_profile(profile_id: str) -> dict:
    return _read()["homeowner_profiles"].get(profile_id, {})


def save_job_request(job: dict):
    data = _read()
    data["job_requests"][job["id"]] = job
    _write(data)


def get_jobs_for_contractor(contractor_id: str) -> list:
    jobs = _read()["job_requests"]
    return [j for j in jobs.values() if contractor_id in j.get("sent_to", [])]


def get_job(job_id: str) -> dict:
    return _read()["job_requests"].get(job_id, {})


def get_messages(job_id: str) -> list:
    return _read()["job_messages"].get(job_id, [])


def add_message(job_id: str, message: dict):
    data = _read()
    if job_id not in data["job_messages"]:
        data["job_messages"][job_id] = []
    data["job_messages"][job_id].append(message)
    _write(data)


def set_job_status(job_id: str, status: str):
    data = _read()
    data["job_status"][job_id] = status
    _write(data)


def get_job_status(job_id: str) -> str:
    return _read()["job_status"].get(job_id, "pending")


def reset():
    """Clear all data — useful for testing."""
    _write({k: {} for k in DEFAULTS})


def set_contractor_complete(job_id: str):
    """Contractor marks work as done."""
    data = _read()
    if job_id not in data["job_requests"]:
        return
    data["job_requests"][job_id]["contractor_complete"] = True
    _write(data)


def set_homeowner_confirmed(job_id: str):
    """Homeowner confirms resolution."""
    data = _read()
    if job_id not in data["job_requests"]:
        return
    data["job_requests"][job_id]["homeowner_confirmed"] = True
    data["job_status"][job_id] = "resolved"
    _write(data)


def is_fully_resolved(job: dict) -> bool:
    return job.get("contractor_complete", False) and job.get("homeowner_confirmed", False)

def save_media(msg_key: str, filename: str, data_b64: str):
    """Store base64-encoded file data."""
    d = _read()
    if "chat_media" not in d:
        d["chat_media"] = {}
    d["chat_media"][msg_key] = {"filename": filename, "data": data_b64}
    _write(d)


def get_media(msg_key: str) -> dict:
    d = _read()
    return d.get("chat_media", {}).get(msg_key, {})

