"""Tests para model_selector.py"""
import pytest


class TestSelectModel:
    def test_labels_vacios_retorna_default(self):
        from model_selector import select_model
        from config import MODEL_DEFAULT
        model, justification = select_model([])
        assert model == MODEL_DEFAULT
        assert justification != ""

    def test_label_backend_retorna_sonnet(self):
        from model_selector import select_model
        from config import MODEL_SONNET
        model, _ = select_model(["backend"])
        assert model == MODEL_SONNET

    def test_label_frontend_retorna_sonnet(self):
        from model_selector import select_model
        from config import MODEL_SONNET
        model, _ = select_model(["frontend"])
        assert model == MODEL_SONNET

    def test_label_research_retorna_haiku(self):
        from model_selector import select_model
        from config import MODEL_HAIKU
        model, _ = select_model(["research"])
        assert model == MODEL_HAIKU

    def test_label_docs_retorna_haiku(self):
        from model_selector import select_model
        from config import MODEL_HAIKU
        model, _ = select_model(["docs"])
        assert model == MODEL_HAIKU

    def test_label_architecture_retorna_opus(self):
        from model_selector import select_model
        from config import MODEL_OPUS
        model, _ = select_model(["architecture"])
        assert model == MODEL_OPUS

    def test_opus_tiene_prioridad_sobre_sonnet(self):
        from model_selector import select_model
        from config import MODEL_OPUS
        model, _ = select_model(["backend", "architecture"])
        assert model == MODEL_OPUS

    def test_sonnet_tiene_prioridad_sobre_haiku(self):
        from model_selector import select_model
        from config import MODEL_SONNET
        model, _ = select_model(["docs", "feature"])
        assert model == MODEL_SONNET

    def test_justificacion_no_vacia(self):
        from model_selector import select_model
        _, justification = select_model(["backend"])
        assert len(justification) > 0

    def test_labels_case_insensitive(self):
        from model_selector import select_model
        from config import MODEL_HAIKU
        model, _ = select_model(["RESEARCH"])
        assert model == MODEL_HAIKU


class TestGetModelForOperation:
    def test_bootstrap_retorna_haiku(self):
        from model_selector import get_model_for_operation
        from config import MODEL_HAIKU
        assert get_model_for_operation("bootstrap") == MODEL_HAIKU

    def test_sync_retorna_haiku(self):
        from model_selector import get_model_for_operation
        from config import MODEL_HAIKU
        assert get_model_for_operation("sync") == MODEL_HAIKU

    def test_claim_retorna_haiku(self):
        from model_selector import get_model_for_operation
        from config import MODEL_HAIKU
        assert get_model_for_operation("claim") == MODEL_HAIKU

    def test_release_retorna_haiku(self):
        from model_selector import get_model_for_operation
        from config import MODEL_HAIKU
        assert get_model_for_operation("release") == MODEL_HAIKU

    def test_team_status_retorna_haiku(self):
        from model_selector import get_model_for_operation
        from config import MODEL_HAIKU
        assert get_model_for_operation("team_status") == MODEL_HAIKU

    def test_operacion_desconocida_retorna_default(self):
        from model_selector import get_model_for_operation
        from config import MODEL_DEFAULT
        assert get_model_for_operation("desconocida") == MODEL_DEFAULT
