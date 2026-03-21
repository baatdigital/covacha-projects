"""Tests para covacha_cli.py — CLI unificado."""
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    def test_parser_tiene_subcommands_principales(self):
        from covacha_cli import build_parser
        parser = build_parser()
        # Verificar que no falle al parsear subcommands conocidos
        args = parser.parse_args(["init"])
        assert args.command == "init"

    def test_parser_claim_con_task_id(self):
        from covacha_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["claim", "042"])
        assert args.command == "claim"
        assert args.task_id == "042"

    def test_parser_release_con_status(self):
        from covacha_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["release", "042", "--status", "blocked"])
        assert args.command == "release"
        assert args.task_id == "042"
        assert args.status == "blocked"


# ---------------------------------------------------------------------------
# run_cli — init
# ---------------------------------------------------------------------------


class TestInitSubcommand:
    def test_init_llama_init_node_config(self):
        from covacha_cli import run_cli
        fake_config = {
            "node_id": "test-node",
            "tenant": {"id": "t1"},
            "workspaces": [{"capabilities": ["backend"], "repos": []}],
        }
        with patch("covacha_cli.init_node_config", return_value=fake_config) as mock_init:
            run_cli(["--tenant", "t1", "init", "--org", "baatdigital"])
        mock_init.assert_called_once_with(
            tenant_id="t1", github_org="baatdigital", base_path=None,
        )


# ---------------------------------------------------------------------------
# run_cli — status
# ---------------------------------------------------------------------------


class TestStatusSubcommand:
    def test_status_delega_a_swarm_status(self):
        from covacha_cli import run_cli
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("covacha_cli.load_node_config", return_value=cfg), \
             patch("swarm_status.load_node_config", return_value=cfg), \
             patch("swarm_status.discover_nodes", return_value=[]), \
             patch("swarm_status.get_recent_messages", return_value=[]), \
             patch("swarm_status.is_task_unblocked", return_value=True), \
             patch("swarm_status.get_available_tasks", return_value=[]):
            # No debe lanzar excepcion
            run_cli(["--tenant", "t1", "status"])


# ---------------------------------------------------------------------------
# run_cli — claim
# ---------------------------------------------------------------------------


class TestClaimSubcommand:
    def test_claim_delega_a_claim_task(self):
        from covacha_cli import run_cli
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("covacha_cli.load_node_config", return_value=cfg), \
             patch("claim_task.load_node_config", return_value=cfg), \
             patch("claim_task.claim_task", return_value=True), \
             patch("claim_task.get_task", return_value=None), \
             patch("claim_task.update_node_status"), \
             patch("claim_task.heartbeat"), \
             patch("claim_task.is_task_unblocked", return_value=True), \
             patch("claim_task.get_branch_for_issue", return_value=None):
            run_cli(["--tenant", "t1", "claim", "042"])


# ---------------------------------------------------------------------------
# run_cli — stop
# ---------------------------------------------------------------------------


class TestStopSubcommand:
    def test_stop_deregistra_nodo(self):
        from covacha_cli import run_cli
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("covacha_cli.load_node_config", return_value=cfg), \
             patch("covacha_cli.deregister_node") as mock_dr:
            run_cli(["--tenant", "t1", "stop"])
        mock_dr.assert_called_once_with("t1", "n1")


# ---------------------------------------------------------------------------
# run_cli — start (placeholder)
# ---------------------------------------------------------------------------


class TestStartSubcommand:
    def test_start_muestra_placeholder(self, capsys):
        from covacha_cli import run_cli
        run_cli(["start"])
        captured = capsys.readouterr()
        assert "not implemented" in captured.out.lower()


# ---------------------------------------------------------------------------
# run_cli — eval (placeholder)
# ---------------------------------------------------------------------------


class TestEvalSubcommand:
    def test_eval_muestra_placeholder(self, capsys):
        from covacha_cli import run_cli
        run_cli(["eval", "--task", "042", "--type", "pre_release"])
        captured = capsys.readouterr()
        assert "not implemented" in captured.out.lower()


# ---------------------------------------------------------------------------
# run_cli — msg
# ---------------------------------------------------------------------------


class TestMsgSubcommand:
    def test_msg_sin_subcommand_muestra_ayuda(self, capsys):
        from covacha_cli import run_cli
        run_cli(["msg"])
        captured = capsys.readouterr()
        assert "send" in captured.out or "read" in captured.out


# ---------------------------------------------------------------------------
# run_cli — deps
# ---------------------------------------------------------------------------


class TestDepsSubcommand:
    def test_deps_check_llama_dependency_manager(self, capsys):
        from covacha_cli import run_cli
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("covacha_cli.load_node_config", return_value=cfg), \
             patch("covacha_cli.is_task_unblocked", return_value=True), \
             patch("covacha_cli.get_dependencies", return_value=[]):
            run_cli(["--tenant", "t1", "deps", "check", "--task", "042"])
        captured = capsys.readouterr()
        assert "DESBLOQUEADA" in captured.out


# ---------------------------------------------------------------------------
# run_cli — sin command muestra help
# ---------------------------------------------------------------------------


class TestNoCommand:
    def test_sin_command_no_falla(self, capsys):
        from covacha_cli import run_cli
        run_cli([])
        captured = capsys.readouterr()
        assert "covacha" in captured.out.lower() or "usage" in captured.out.lower()
