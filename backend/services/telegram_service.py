import logging
from typing import Dict, Any, List, Optional
import requests

from backend.config import Settings, settings

logger = logging.getLogger(__name__)

DISCLAIMER_HEADER = (
    "⚠️ EXPERIMENTAL DEMO — HISTORICAL/SIMULATED SUSCEPTIBILITY RANKING.\n"
    "NOT A FLOOD FORECAST OR EMERGENCY WARNING.\n"
    "Relative susceptibility ranking only; not flood probabilities."
)

class TelegramService:
    """
    Demo/Sandbox-only Telegram integration.
    Disabled by default. Intended solely for private developer demonstration
    using historical replay data or clearly labelled simulated data.
    """
    def __init__(self, cfg: Settings = settings):
        self.cfg = cfg
        self._sent_dates: set = set()

    def format_demo_message(
        self,
        date_str: str,
        summary: Dict[str, Any],
        top_cells: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Formats a demo message with mandatory disclaimers and summary statistics.
        Can be used without sending actual network requests.
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
        url = f"https://api.telegram.org/bot{self.cfg.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": self.cfg.TELEGRAM_CHAT_ID,
            "text": formatted_text,
            "parse_mode": "HTML"
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                self._sent_dates.add(date_str)
                return {"sent": True, "date": date_str, "status_code": 200}
            else:
                logger.error(f"Telegram API error: {resp.status_code} - {resp.text}")
                return {"sent": False, "status_code": resp.status_code, "error": resp.text}
        except Exception as e:
            logger.error(f"Failed to deliver Telegram demo message: {str(e)}")
            return {"sent": False, "error": str(e)}

telegram_service = TelegramService()
