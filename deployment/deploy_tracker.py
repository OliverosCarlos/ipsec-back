import requests

DEFAULT_BASE_URL = "http://localhost:9000"
DEFAULT_PROJECT_NAME = "core backend"


class DeployTracker:

    def __init__(self, base_url=DEFAULT_BASE_URL, project_name=DEFAULT_PROJECT_NAME):
        self.base_url = base_url.rstrip("/")
        self.project_name = project_name

    def update_step_status(self, step_code, status, status_info=""):
        url = f"{self.base_url}/api/steps/status"
        payload = {
            "project_name": self.project_name,
            "step_code": step_code,
            "status": status,
            "status_info": status_info,
        }
        response = requests.patch(url, json=payload)
        response.raise_for_status()
        return response.json()

    def reset(self, step_code):
        url = f"{self.base_url}/api/steps/reset/{step_code}"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()

    def add_substep(self, step_code, info, status):
        url = f"{self.base_url}/api/substeps/by-step-code"
        payload = {
            "step_code": step_code,
            "info": info,
            "status": status,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def success(self, step_code, info):
        return self.add_substep(step_code, info, status="success")

    def error(self, step_code, info):
        return self.add_substep(step_code, info, status="error")

    def warning(self, step_code, info):
        return self.add_substep(step_code, info, status="warning")

    def start(self, step_code, status_info=""):
        return self.update_step_status(step_code, status="in-progress", status_info=status_info)

    def complete(self, step_code, status_info=""):
        return self.update_step_status(step_code, status="completed", status_info=status_info)

    def fail(self, step_code, status_info=""):
        return self.update_step_status(step_code, status="failed", status_info=status_info)
