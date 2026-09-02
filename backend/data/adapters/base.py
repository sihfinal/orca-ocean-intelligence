"""
Base Data Service Adapter for External Oceanographic & Meteorological Sources
ISRO SIH 2026 - Problem Statement 26176
"""

import time
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("blue_orbit.data.adapter")

class BaseDataServiceAdapter(ABC):
    """
    Abstract base class for real data source adapters.
    Enforces timeout, bounded retries, provenance tracking, and safe failure handling.
    """
    def __init__(
        self,
        source_name: str,
        organization: str,
        base_url: str,
        timeout_seconds: float = 8.0,
        max_retries: int = 2
    ):
        self.source_name = source_name
        self.organization = organization
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    async def _safe_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes HTTP GET with explicit timeout, bounded retries, and clean error handling.
        Never throws unhandled network exceptions to caller.
        """
        url = f"{self.base_url}{endpoint}" if endpoint.startswith("/") else f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        try:
                            return {"success": True, "data": resp.json(), "status_code": 200}
                        except Exception:
                            logger.warning("[%s] Non-JSON payload received from %s", self.source_name, url)
                            return {
                                "success": False,
                                "error": "Non-JSON payload returned by data source",
                                "status_code": 502
                            }
                    else:
                        logger.warning(
                            "[%s] Non-200 response (%d): %s",
                            self.source_name, resp.status_code, resp.text[:200]
                        )
                        return {
                            "success": False,
                            "error": f"HTTP {resp.status_code}: {resp.text[:150]}",
                            "status_code": resp.status_code
                        }
            except httpx.TimeoutException as exc:
                last_error = f"Connection timeout ({self.timeout_seconds}s)"
                logger.warning("[%s] Timeout attempt %d: %s", self.source_name, attempt + 1, exc)
            except httpx.RequestError as exc:
                last_error = f"Network connection error: {type(exc).__name__}"
                logger.warning("[%s] Request failure attempt %d: %s", self.source_name, attempt + 1, exc)
            except Exception as exc:
                last_error = f"Unexpected client error: {type(exc).__name__}"
                logger.error("[%s] Unexpected error: %s", self.source_name, exc, exc_info=True)
                break

            if attempt < self.max_retries:
                await asyncio.sleep(0.5 * (attempt + 1))

        return {
            "success": False,
            "error": last_error or "Unknown failure communicating with data source",
            "status_code": 504 if "timeout" in str(last_error).lower() else 502
        }
