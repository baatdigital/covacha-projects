"""Tests para node_config.py — configuracion local de nodo del Agent Swarm."""
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# generate_node_id
# ---------------------------------------------------------------------------

class TestGenerateNodeId:
    def test_generate_node_id_formato_correcto(self):
        """El node_id debe tener formato {username}-{hostname_limpio}."""
        from node_config import generate_node_id

        with patch("node_config.platform") as mock_plat, \
             patch.dict(os.environ, {"USER": "testuser"}):
            mock_plat.node.return_value = "My-MacBook-Pro.local"
            result = generate_node_id()

        assert result == "testuser-my-macbook-pro"

    def test_generate_node_id_sin_dominio(self):
        """Debe limpiar el .local del hostname."""
        from node_config import generate_node_id

        with patch("node_config.platform") as mock_plat, \
             patch.dict(os.environ, {"USER": "dev"}):
            mock_plat.node.return_value = "server-01"
            result = generate_node_id()

        assert result == "dev-server-01"


# ---------------------------------------------------------------------------
# detect_local_repos
# ---------------------------------------------------------------------------

class TestDetectLocalRepos:
    def test_detect_local_repos_encuentra_git_dirs(self, tmp_path: Path):
        """Debe encontrar directorios que contengan .git."""
        from node_config import detect_local_repos

        # Crear repos simulados con .git
        (tmp_path / "covacha-payment" / ".git").mkdir(parents=True)
        (tmp_path / "mf-core" / ".git").mkdir(parents=True)
        # Directorio sin .git (no es repo)
        (tmp_path / "random-dir").mkdir()

        result = detect_local_repos(str(tmp_path))

        assert len(result) == 2
        names = [r["name"] for r in result]
        assert "covacha-payment" in names
        assert "mf-core" in names

    def test_detect_local_repos_retorna_vacio_si_no_existe_base(self):
        """Retorna lista vacia si el directorio base no existe."""
        from node_config import detect_local_repos

        result = detect_local_repos("/ruta/que/no/existe/xyz")
        assert result == []

    def test_detect_local_repos_retorna_paths_absolutos(self, tmp_path: Path):
        """Los paths retornados deben ser absolutos."""
        from node_config import detect_local_repos

        (tmp_path / "my-repo" / ".git").mkdir(parents=True)
        result = detect_local_repos(str(tmp_path))

        assert len(result) == 1
        assert os.path.isabs(result[0]["path"])


# ---------------------------------------------------------------------------
# detect_capabilities
# ---------------------------------------------------------------------------

class TestDetectCapabilities:
    def test_detect_capabilities_backend_desde_covacha_repos(self):
        """Repos covacha-* deben inferir capability backend."""
        from node_config import detect_capabilities

        repos = [
            {"path": "/x/covacha-payment", "name": "covacha-payment"},
            {"path": "/x/covacha-core", "name": "covacha-core"},
        ]
        with patch("node_config.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            result = detect_capabilities(repos)

        assert "backend" in result

    def test_detect_capabilities_frontend_desde_mf_repos(self):
        """Repos mf-* deben inferir capability frontend."""
        from node_config import detect_capabilities

        repos = [
            {"path": "/x/mf-core", "name": "mf-core"},
            {"path": "/x/mf-marketing", "name": "mf-marketing"},
        ]
        with patch("node_config.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            result = detect_capabilities(repos)

        assert "frontend" in result

    def test_detect_capabilities_ops_desde_covacha_projects(self):
        """covacha-projects debe inferir capability ops."""
        from node_config import detect_capabilities

        repos = [
            {"path": "/x/covacha-projects", "name": "covacha-projects"},
        ]
        with patch("node_config.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            result = detect_capabilities(repos)

        assert "ops" in result

    def test_detect_capabilities_vacio_sin_repos(self):
        """Sin repos y sin herramientas, retorna lista vacia."""
        from node_config import detect_capabilities

        with patch("node_config.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            result = detect_capabilities([])

        assert result == []

    def test_detect_capabilities_testing_con_pytest(self):
        """Si pytest esta disponible, agrega capability testing."""
        from node_config import detect_capabilities

        with patch("node_config.shutil") as mock_shutil:
            mock_shutil.which.side_effect = (
                lambda cmd: "/usr/local/bin/pytest" if cmd == "pytest" else None
            )
            result = detect_capabilities([])

        assert "testing" in result


# ---------------------------------------------------------------------------
# load_node_config / save_node_config
# ---------------------------------------------------------------------------

class TestLoadSaveNodeConfig:
    def test_load_node_config_retorna_vacio_si_no_existe(self):
        """Retorna {} si ~/.covacha-node.yml no existe."""
        from node_config import load_node_config

        fake_path = Path("/tmp/no-existe-xyz-abc.yml")
        with patch("node_config.get_node_config_path", return_value=fake_path):
            result = load_node_config()

        assert result == {}

    def test_save_y_load_node_config_roundtrip(self, tmp_path: Path):
        """Guardar y luego cargar debe retornar el mismo config."""
        from node_config import save_node_config, load_node_config

        config_file = tmp_path / ".covacha-node.yml"
        original = {
            "node_id": "test-node",
            "tenant": {"id": "acme", "github_org": "acme"},
            "workspaces": [],
            "preferred_model": "sonnet",
        }

        with patch("node_config.get_node_config_path", return_value=config_file):
            save_node_config(original)
            loaded = load_node_config()

        assert loaded == original


# ---------------------------------------------------------------------------
# init_node_config
# ---------------------------------------------------------------------------

class TestInitNodeConfig:
    def test_init_node_config_genera_completo(self, tmp_path: Path):
        """init_node_config debe generar config con node_id, tenant, workspaces."""
        from node_config import init_node_config

        config_file = tmp_path / ".covacha-node.yml"
        fake_repos = [
            {"path": "/x/covacha-core", "name": "covacha-core"},
        ]

        with patch("node_config.get_node_config_path", return_value=config_file), \
             patch("node_config.generate_node_id", return_value="test-host"), \
             patch("node_config.detect_local_repos", return_value=fake_repos), \
             patch("node_config.detect_capabilities", return_value=["backend"]):
            result = init_node_config("baatdigital", "baatdigital", "/x")

        assert result["node_id"] == "test-host"
        assert result["tenant"]["id"] == "baatdigital"
        assert result["tenant"]["github_org"] == "baatdigital"
        assert len(result["workspaces"]) == 1
        assert result["workspaces"][0]["capabilities"] == ["backend"]
        assert result["preferred_model"] == "sonnet"
        assert result["max_concurrent_tasks"] == 1
        # Verificar que se guardo en disco
        assert config_file.exists()
