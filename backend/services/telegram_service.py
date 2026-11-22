"""
Private Telegram Demonstration Bot Service
===========================================
Academic research prototype demonstrating automated spatial summary dispatch
for authorized project evaluators.

CRITICAL SAFETY DIRECTIVES:
1. Private academic demonstration only; strictly NOT an operational flood warning system.
2. Interaction is restricted to explicitly authorized demo chat IDs.
3. Bot tokens are loaded strictly from server-side environment variables and NEVER
   exposed to frontend clients, logged, or committed.
4. Output represents relative spatial susceptibility rankings, NOT flood probabilities.
"""

import logging
import urllib.request
import urllib.error
import json
from typing import Dict, Any, List, Optional, Set

from backend.config import Settings, settings

logger = logging.getLogger(__name__)

DISCLAIMER_HEADER = (
    "⚠️ EXPERIMENTAL DEMO — HISTORICAL/SIMULATED SUSCEPTIBILITY RANKING.\n"
    "NOT A FLOOD FORECAST OR EMERGENCY WARNING.\n"
    "Relative susceptibility ranking only; not flood probabilities."
)


class TelegramService:
    """
    Manages private demonstration bot commands, authorization checks,
    message formatting, and Telegram Bot API communication.
    """

    def __init__(self, cfg: Settings = settings):
        self.cfg = cfg
        self._sent_dates: set = set()
        self._custom_sender = None  # Hook for deterministic unit testing

    @property
    def authorized_chat_ids(self) -> Set[str]:
        """Returns set of authorized chat IDs from configuration."""
        auth_set = set()
        if self.cfg.TELEGRAM_CHAT_ID:
            auth_set.add(str(self.cfg.TELEGRAM_CHAT_ID).strip())
        if self.cfg.TELEGRAM_AUTHORIZED_CHAT_IDS:
            for cid in self.cfg.TELEGRAM_AUTHORIZED_CHAT_IDS.split(","):
                cleaned = cid.strip()
                if cleaned:
                    auth_set.add(cleaned)
        return auth_set

    def is_authorized(self, chat_id: Any) -> bool:
        """Verifies if the given chat ID is authorized for private demo access."""
        auth_ids = self.authorized_chat_ids
        if not auth_ids:
            # If no chat IDs are configured yet, reject live execution for safety
            return False
        return str(chat_id).strip() in auth_ids

    def get_public_status(self) -> Dict[str, Any]:
        """
        Returns safe, non-sensitive configuration status for the API and frontend.
        Never exposes the bot token!
        """
        is_token_configured = bool(self.cfg.TELEGRAM_BOT_TOKEN and len(self.cfg.TELEGRAM_BOT_TOKEN) > 5)
        has_auth_chats = len(self.authorized_chat_ids) > 0

        return {
            "enabled": self.cfg.TELEGRAM_ENABLED,
            "configured": is_token_configured and has_auth_chats,
            "token_configured": is_token_configured,
            "bot_username": self.cfg.TELEGRAM_BOT_USERNAME,
            "authorized_chats_count": len(self.authorized_chat_ids),
            "mode": "private_academic_demo",
            "safety_rule": "Private demonstration only. Automated operational emergency alerts are strictly forbidden.",
            "available_commands": ["/start", "/help", "/status", "/demo [YYYY-MM-DD]"]
        }

    def format_demo_message(
        self,
        date_str: str,
        summary: Dict[str, Any],
        top_cells: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Formats a demonstration alert message with mandatory safety disclaimers,
        rank-based thresholds, top cell telemetry, and explanatory notes.
        """
        high_cnt = summary.get("high_count", 0)
        mod_cnt = summary.get("moderate_count", 0)
        none_cnt = summary.get("none_count", 0)
        total_cells = summary.get("total_cells_scored", 0)
        top_cell = summary.get("top_ranked_cell") or {}

        top_cell_str = "N/A"
        if top_cell:
            top_cell_str = (
                f"Cell #{top_cell.get('cell_id')} (Ward {top_cell.get('ward')}), "
                f"Score: {top_cell.get('score', 0):.4f}"
            )

        msg_lines = [
            DISCLAIMER_HEADER,
            "--------------------------------------------------",
            f"📅 Historical Replay Date: {date_str}",
            f"Mode: {summary.get('data_mode', 'historical_replay')}",
            f"Grid Cells Scored: {total_cells}",
            "",
            "📊 Relative Alert Levels (Rank-Based Thresholds):",
            f"  • High (Top 150 cells): {high_cnt}",
            f"  • Moderate (Ranks 151-300): {mod_cnt}",
            f"  • None (Remaining): {none_cnt}",
            "",
            f"📍 Highest Susceptibility Cell: {top_cell_str}",
            f"📈 Average Score: {summary.get('average_score', 0):.4f}",
            "--------------------------------------------------",
            "Notice: This demonstration uses historical data from September 2022. "
            "Never use this model for operational flood warning or life safety decisions."
        ]

        if top_cells:
            msg_lines.append("")
            msg_lines.append("Top 5 Cells:")
            for c in top_cells[:5]:
                msg_lines.append(
                    f"  Rank #{c.get('rank')}: Cell {c.get('cell_id')} (Ward {c.get('ward')}) - Score {c.get('score', 0):.4f}"
                )

        return "\n".join(msg_lines)

    # -------------------------------------------------------------------------
    # Command Implementations
    # -------------------------------------------------------------------------

    def handle_command_start(self) -> str:
        """Handles the /start command."""
        return (
            "👋 Welcome to the N²M Flood Prediction Model Research Demo Bot.\n\n"
            "This bot is a private academic engineering demonstration developed for Greater Bengaluru, India.\n\n"
            "⚠️ IMPORTANT SCIENTIFIC DISCLAIMER:\n"
            "• This is an experimental research prototype, NOT a certified municipal flood warning system.\n"
            "• Outputs represent daily relative spatial susceptibility rankings across 3,026 cells (~500m mesh), "
            "NOT physical inundation depths or predicted flood probabilities.\n"
            "• It must NEVER be used for emergency public evacuations or operational safety decisions.\n\n"
            "Type /help to view available demonstration commands."
        )

    def handle_command_help(self) -> str:
        """Handles the /help command."""
        return (
            "📖 N²M Research Demo Bot — Available Commands:\n\n"
            "• /start — Overview of the research project and scientific disclaimers.\n"
            "• /help — List this command manual.\n"
            "• /status — Check connection status, telemetry streams, and research mode.\n"
            "• /demo — Generate an experimental demonstration alert for benchmark date 2022-09-08.\n"
            "• /demo <YYYY-MM-DD> — Generate an alert for a specific September 2022 replay date (e.g. /demo 2022-09-05).\n\n"
            "Note: Access is restricted to authorized project evaluators."
        )

    def handle_command_status(self, rainfall_status: Optional[Dict[str, Any]] = None) -> str:
        """Handles the /status command."""
        now_utc = "Available on request"
        rf_provider = "Open-Meteo Weather API (~11 km regional reanalysis)"
        rf_status_str = "Offline / Sandbox Mode"

        if rainfall_status:
            rf_status_str = "Online (Live / Cached Telemetry)" if rainfall_status.get("is_live") else "Offline / Isolated"

        return (
            "⚙️ N²M Research System Status:\n\n"
            "• System Mode: Private Academic Demonstration\n"
            "• Access Control: Restricted to Authorized Evaluators\n"
            "• Replay Model: XGBoost Holdout (E2022_09, scale_pos_weight=89.16)\n"
            "• Replay Dataset: 24 Days (2022-08-22 to 2022-09-14, 3,026 cells)\n"
            f"• Meteorological Context: {rf_provider}\n"
            f"• Live Rainfall Stream: {rf_status_str}\n"
            "• Public Emergency Dispatch: DISCONNECTED (SAFE)\n\n"
            "⚠️ Research Note: All displayed scores are empirical relative rankings and must not be treated as live operational forecasts."
        )

    def handle_command_demo(
        self,
        date_str: str,
        summary: Dict[str, Any],
        top_cells: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Handles the /demo command."""
        return self.format_demo_message(date_str, summary, top_cells)

    def send_demo_message(
        self,
        date_str: str,
        summary: Dict[str, Any],
        top_cells: Optional[List[Dict[str, Any]]] = None,
        force_duplicate: bool = False
    ) -> Dict[str, Any]:
        """
        Sends a private demonstration message via Telegram bot if enabled.
        Safe defaults:
        - Refuses if TELEGRAM_ENABLED is False
        - Refuses if bot token or chat ID is missing
        - Avoids duplicate messages unless force_duplicate is True
        """
        if not self.cfg.TELEGRAM_ENABLED:
            return {
                "sent": False,
                "reason": "Telegram integration is disabled by default. Set TELEGRAM_ENABLED=true and configure credentials to enable.",
                "demo_message": self.format_demo_message(date_str, summary, top_cells)
            }

        if not self.cfg.TELEGRAM_BOT_TOKEN or not self.cfg.TELEGRAM_CHAT_ID:
            return {
                "sent": False,
                "reason": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.",
                "demo_message": self.format_demo_message(date_str, summary, top_cells)
            }

        if date_str in self._sent_dates and not force_duplicate:
            return {
                "sent": False,
                "reason": f"Demo message for date {date_str} was already sent in this session. Avoid duplicate demo alerts.",
                "date": date_str
            }

        formatted_text = self.format_demo_message(date_str, summary, top_cells)
        res = self.dispatch_telegram_message(chat_id=self.cfg.TELEGRAM_CHAT_ID, text=formatted_text)
        if res.get("sent"):
            self._sent_dates.add(date_str)
        return res

    def process_incoming_update(
        self,
        update: Dict[str, Any],
        replay_service_fn=None,
        rainfall_status: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parses an incoming Telegram update, checks authorization, dispatches
        commands, and returns the response payload.
        """
        message = update.get("message", {})
        chat = message.get("chat", {})
        chat_id = str(chat.get("id", "")).strip()
        text = str(message.get("text", "")).strip()

        if not chat_id:
            return {"status": "error", "message": "No chat ID found in update"}

        # 1. Authorization Gate
        if not self.is_authorized(chat_id):
            logger.warning(f"Unauthorized Telegram command attempt from chat ID [REDACTED].")
            unauth_msg = (
                "⛔ Access Restricted:\n"
                "This bot is a private academic research prototype for the N²M Flood Prediction Model. "
                "Interaction is restricted to explicitly authorized project evaluators."
            )
            return {
                "status": "unauthorized",
                "chat_id": chat_id,
                "response_text": unauth_msg
            }

        # 2. Command Dispatcher
        parts = text.split()
        cmd = parts[0].lower() if parts else ""

        if cmd == "/start":
            reply = self.handle_command_start()
        elif cmd == "/help":
            reply = self.handle_command_help()
        elif cmd == "/status":
            reply = self.handle_command_status(rainfall_status)
        elif cmd == "/demo":
            # Optional date argument (defaults to 2022-09-08)
            req_date = parts[1] if len(parts) > 1 else "2022-09-08"
            if replay_service_fn:
                try:
                    summary, top_cells = replay_service_fn(req_date)
                    reply = self.handle_command_demo(req_date, summary, top_cells)
                except Exception as e:
                    reply = (
                        f"❌ Error generating demo alert for date '{req_date}': {str(e)}\n\n"
                        f"Available historical replay range is 2022-08-22 to 2022-09-14."
                    )
            else:
                reply = (
                    f"⚠️ Demonstration alert for {req_date} (Replay service disconnected in this context).\n"
                    f"Use /status to verify pipeline status."
                )
        else:
            reply = (
                f"Unknown command '{text}'. Type /help to view available demonstration commands."
            )

        return {
            "status": "success",
            "chat_id": chat_id,
            "command": cmd,
            "response_text": reply
        }

    def dispatch_telegram_message(self, chat_id: str, text: str) -> Dict[str, Any]:
        """
        Sends an HTTP message via the Telegram Bot API.
        Never prints or exposes the token in logs!
        """
        if self._custom_sender:
            return self._custom_sender(chat_id, text)

        if not self.cfg.TELEGRAM_ENABLED:
            return {
                "sent": False,
                "reason": "Telegram integration is disabled by default. Set TELEGRAM_ENABLED=true in .env to enable."
            }

        if not self.cfg.TELEGRAM_BOT_TOKEN:
            return {
                "sent": False,
                "reason": "Missing TELEGRAM_BOT_TOKEN in environment configuration."
            }

        if not self.is_authorized(chat_id):
            return {
                "sent": False,
                "reason": f"Target chat ID is not in the authorized participants list."
            }

        url = f"https://api.telegram.org/bot{self.cfg.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                return {
                    "sent": True,
                    "chat_id": chat_id,
                    "telegram_response": resp_data
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            logger.error(f"Telegram API HTTP error {e.code}: {error_body}")
            return {
                "sent": False,
                "status_code": e.code,
                "error": error_body
            }
        except Exception as e:
            logger.error(f"Failed to deliver Telegram message: {str(e)}")
            return {
                "sent": False,
                "error": str(e)
            }


telegram_service = TelegramService()
