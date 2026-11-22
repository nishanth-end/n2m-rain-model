"""
Automated Test Suite for Private Telegram Demonstration Bot
============================================================
Verifies server-side token protection, authorization restrictions,
command processing (/start, /help, /status, /demo), dispatch safeguards,
and API endpoints.
"""

import pytest
from backend.main import (
    app,
    get_telegram_status,
    handle_telegram_webhook,
    send_telegram_demo,
    TelegramSendDemoRequest
)
from backend.services.telegram_service import TelegramService, telegram_service, DISCLAIMER_HEADER
from backend.config import Settings


class TestTelegramConfigurationAndSafety:
    """Verifies token confidentiality and default sandbox safety."""

    def test_default_service_is_disabled_and_safe(self):
        status = telegram_service.get_public_status()
        assert status["mode"] == "private_academic_demo"
        assert "safety_rule" in status
        assert "available_commands" in status
        # Token must NEVER be in status response
        assert "token" not in str(status).lower() or "token_configured" in status

    def test_token_redaction_in_string_representations(self):
        cfg = Settings(
            TELEGRAM_ENABLED=True,
            TELEGRAM_BOT_TOKEN="SECRET_SUPER_CONFIDENTIAL_TOKEN_12345",
            TELEGRAM_CHAT_ID="99999"
        )
        svc = TelegramService(cfg=cfg)
        status = svc.get_public_status()
        assert "SECRET_SUPER_CONFIDENTIAL_TOKEN_12345" not in str(status)


class TestTelegramAuthorizationGate:
    """Verifies that only explicitly authorized demo chat IDs are granted access."""

    def test_unauthorized_chat_id_rejected(self):
        cfg = Settings(
            TELEGRAM_ENABLED=True,
            TELEGRAM_BOT_TOKEN="dummy_token_12345",
            TELEGRAM_CHAT_ID="123456",
            TELEGRAM_AUTHORIZED_CHAT_IDS="789012,345678"
        )
        svc = TelegramService(cfg=cfg)

        assert svc.is_authorized("123456") is True
        assert svc.is_authorized("789012") is True
        assert svc.is_authorized("345678") is True
        assert svc.is_authorized("999999") is False
        assert svc.is_authorized("attacker_chat") is False

    def test_process_update_rejects_unauthorized_user(self):
        cfg = Settings(
            TELEGRAM_ENABLED=True,
            TELEGRAM_BOT_TOKEN="dummy_token",
            TELEGRAM_CHAT_ID="11111"
        )
        svc = TelegramService(cfg=cfg)
        update = {
            "update_id": 1001,
            "message": {
                "chat": {"id": 99999},  # Unauthorized
                "text": "/demo"
            }
        }
        res = svc.process_incoming_update(update)
        assert res["status"] == "unauthorized"
        assert "Access Restricted" in res["response_text"]
        assert "authorized project evaluators" in res["response_text"]


class TestTelegramCommands:
    """Verifies command processing (/start, /help, /status, /demo)."""

    @pytest.fixture
    def authorized_svc(self):
        cfg = Settings(
            TELEGRAM_ENABLED=True,
            TELEGRAM_BOT_TOKEN="valid_mock_token_12345",
            TELEGRAM_CHAT_ID="55555"
        )
        return TelegramService(cfg=cfg)

    def test_command_start(self, authorized_svc):
        update = {"message": {"chat": {"id": 55555}, "text": "/start"}}
        res = authorized_svc.process_incoming_update(update)
        assert res["status"] == "success"
        assert "N²M Flood Prediction Model" in res["response_text"]
        assert "NOT a certified municipal flood warning" in res["response_text"]
        assert "relative spatial susceptibility" in res["response_text"]

    def test_command_help(self, authorized_svc):
        update = {"message": {"chat": {"id": 55555}, "text": "/help"}}
        res = authorized_svc.process_incoming_update(update)
        assert res["status"] == "success"
        assert "/start" in res["response_text"]
        assert "/help" in res["response_text"]
        assert "/status" in res["response_text"]
        assert "/demo" in res["response_text"]

    def test_command_status(self, authorized_svc):
        update = {"message": {"chat": {"id": 55555}, "text": "/status"}}
        res = authorized_svc.process_incoming_update(
            update,
            rainfall_status={"is_live": True}
        )
        assert res["status"] == "success"
        assert "Private Academic Demonstration" in res["response_text"]
        assert "XGBoost Holdout" in res["response_text"]
        assert "24 Days" in res["response_text"]
        assert "DISCONNECTED (SAFE)" in res["response_text"]

    def test_command_demo_with_mock_replay_fn(self, authorized_svc):
        def mock_replay_fn(d_str):
            summary = {
                "high_count": 150,
                "moderate_count": 150,
                "none_count": 2726,
                "total_cells_scored": 3026,
                "average_score": 0.0198,
                "data_mode": "historical_replay",
                "top_ranked_cell": {"cell_id": 722, "ward": 150, "score": 0.2191}
            }
            top_cells = [
                {"rank": 1, "cell_id": 722, "ward": 150, "score": 0.2191},
                {"rank": 2, "cell_id": 783, "ward": 150, "score": 0.2106}
            ]
            return summary, top_cells

        update = {"message": {"chat": {"id": 55555}, "text": "/demo 2022-09-08"}}
        res = authorized_svc.process_incoming_update(update, replay_service_fn=mock_replay_fn)
        assert res["status"] == "success"
        msg = res["response_text"]
        assert "EXPERIMENTAL DEMO" in msg
        assert "2022-09-08" in msg
        assert "High (Top 150 cells): 150" in msg
        assert "Moderate (Ranks 151-300): 150" in msg
        assert "Cell #722" in msg


class TestMessageDispatchSafeguards:
    """Verifies that messages are strictly confined to authorized sandbox chats."""

    def test_dispatch_refuses_when_disabled(self):
        cfg = Settings(TELEGRAM_ENABLED=False)
        svc = TelegramService(cfg=cfg)
        res = svc.dispatch_telegram_message(chat_id="12345", text="Test")
        assert res["sent"] is False
        assert "disabled by default" in res["reason"]

    def test_dispatch_refuses_unauthorized_chat(self):
        cfg = Settings(
            TELEGRAM_ENABLED=True,
            TELEGRAM_BOT_TOKEN="token",
            TELEGRAM_CHAT_ID="12345"
        )
        svc = TelegramService(cfg=cfg)
        res = svc.dispatch_telegram_message(chat_id="99999", text="Test")
        assert res["sent"] is False
        assert "not in the authorized" in res["reason"]

    def test_mock_dispatch_to_authorized_chat(self):
        cfg = Settings(
            TELEGRAM_ENABLED=True,
            TELEGRAM_BOT_TOKEN="token",
            TELEGRAM_CHAT_ID="12345"
        )
        svc = TelegramService(cfg=cfg)
        sent_messages = []

        def mock_sender(cid, text):
            sent_messages.append({"chat_id": cid, "text": text})
            return {"sent": True, "chat_id": cid}

        svc._custom_sender = mock_sender
        res = svc.dispatch_telegram_message(chat_id="12345", text="Hello N²M")
        assert res["sent"] is True
        assert len(sent_messages) == 1
        assert sent_messages[0]["chat_id"] == "12345"
        assert sent_messages[0]["text"] == "Hello N²M"


class TestTelegramEndpoints:
    """Verifies FastAPI endpoints for Telegram management."""

    def test_get_telegram_status_endpoint(self):
        res = get_telegram_status()
        assert "enabled" in res
        assert "mode" in res
        assert res["mode"] == "private_academic_demo"

    def test_webhook_endpoint(self):
        update_payload = {
            "update_id": 50,
            "message": {
                "chat": {"id": 99999},  # Unauthorized
                "text": "/help"
            }
        }
        res = handle_telegram_webhook(update=update_payload)
        assert res["status"] == "unauthorized"
        assert "Access Restricted" in res["response_text"]

    def test_send_demo_endpoint(self):
        req = TelegramSendDemoRequest(date="2022-09-08")
        res = send_telegram_demo(req)
        assert "formatted_message" in res
        assert "EXPERIMENTAL DEMO" in res["formatted_message"]
        # Default environment is TELEGRAM_ENABLED=False
        assert res["sent"] is False
