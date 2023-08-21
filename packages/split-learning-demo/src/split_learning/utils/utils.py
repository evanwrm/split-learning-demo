from pathlib import Path

# paths


def project_path() -> Path:
    return Path(__file__).resolve().parents[1]


def project_root_path() -> Path:
    return project_path().parents[1]


def workspace_root_path() -> Path:
    return project_root_path().parents[1]


def config_path() -> Path:
    return workspace_root_path() / "configs"


def data_path() -> Path:
    return workspace_root_path() / "data"


def docs_path() -> Path:
    return workspace_root_path() / "docs"


def model_path() -> Path:
    return project_root_path() / "models"
