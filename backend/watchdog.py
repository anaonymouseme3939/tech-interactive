#!/usr/bin/env python3
"""
Watchdog System for Sensor Health Monitoring
"""

import threading
import time
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class Watchdog:
    """Monitors sensor health and triggers recovery on timeout"""

    def __init__(self, timeout: float = 5.0, on_timeout: Optional[Callable] = None):
        """Initialize watchdog"""
        self.timeout = timeout
        self.on_timeout = on_timeout
        self.last_heartbeat = time.time()
        self.running = False
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start watchdog"""
        self.running = True
        self.last_heartbeat = time.time()
        thread = threading.Thread(target=self._watch, daemon=True)
        thread.start()
        logger.info(f"Watchdog started (timeout: {self.timeout}s)")

    def stop(self) -> None:
        """Stop watchdog"""
        self.running = False
        logger.info("Watchdog stopped")

    def heartbeat(self) -> None:
        """Record a heartbeat"""
        with self._lock:
            self.last_heartbeat = time.time()

    def _watch(self) -> None:
        """Watch thread"""
        while self.running:
            time.sleep(self.timeout / 2)
            
            with self._lock:
                elapsed = time.time() - self.last_heartbeat
            
            if elapsed > self.timeout:
                logger.warning(f"Watchdog timeout! ({elapsed:.1f}s > {self.timeout}s)")
                if self.on_timeout:
                    try:
                        self.on_timeout()
                    except Exception as e:
                        logger.error(f"Timeout handler error: {e}")
                self.last_heartbeat = time.time()

    def get_last_heartbeat(self) -> float:
        """Get time since last heartbeat"""
        with self._lock:
            return time.time() - self.last_heartbeat
