#!/usr/bin/env python3
"""
MQTT/UDP Receiver Manager with Auto-Reconnect
"""

import json
import threading
import time
import queue
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import logging

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

logger = logging.getLogger(__name__)


@dataclass
class SignalData:
    """Signal data packet"""
    device_id: str
    timestamp: float
    rssi: float
    variance: float
    motion: float
    energy: float
    confidence: float
    channel: int = 0
    packet_rate: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'device_id': self.device_id,
            'timestamp': self.timestamp,
            'rssi': self.rssi,
            'variance': self.variance,
            'motion': self.motion,
            'energy': self.energy,
            'confidence': self.confidence,
            'channel': self.channel,
            'packet_rate': self.packet_rate,
        }


class ReceiverManager:
    """Manages MQTT/UDP signal reception with auto-reconnect"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize receiver"""
        self.config = config
        self.queue: queue.Queue = queue.Queue(maxsize=1000)
        self.running = False
        self.connected = False
        self.reconnect_count = 0
        self.client = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start receiver"""
        if not self.config.get('enable', True):
            logger.warning("MQTT disabled in configuration")
            return

        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        logger.info("Receiver started")

    def stop(self) -> None:
        """Stop receiver"""
        self.running = False
        if self.client:
            try:
                self.client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
        logger.info("Receiver stopped")

    def _run(self) -> None:
        """Main receiver loop"""
        while self.running:
            try:
                self._connect_mqtt()
                if self.connected and self.client:
                    self.client.loop_forever(timeout=1.0)
            except Exception as e:
                logger.error(f"Receiver error: {e}")
                self._reconnect()
                time.sleep(self.config.get('reconnect_interval', 5))

    def _connect_mqtt(self) -> None:
        """Connect to MQTT broker"""
        if self.connected:
            return

        try:
            host = self.config.get('host', 'localhost')
            port = self.config.get('port', 1883)
            keepalive = self.config.get('keepalive', 60)

            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            logger.info(f"Connecting to MQTT: {host}:{port}")
            self.client.connect(host, port, keepalive)
            self.connected = True
            self.reconnect_count = 0
            logger.info("MQTT connected")

        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            self._reconnect()

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connect callback"""
        if rc == 0:
            logger.info("MQTT broker connected")
            topic = self.config.get('topic_base', 'tech_interactive')
            client.subscribe(f"{topic}/+/signal")
            self.connected = True
        else:
            logger.error(f"MQTT connection failed with code {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback"""
        logger.warning(f"MQTT disconnected (code: {rc})")
        self.connected = False
        self._reconnect()

    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            signal_data = SignalData(
                device_id=payload.get('device_id', 'unknown'),
                timestamp=payload.get('timestamp', time.time()),
                rssi=float(payload.get('rssi', 0)),
                variance=float(payload.get('variance', 0)),
                motion=float(payload.get('motion', 0)),
                energy=float(payload.get('energy', 0)),
                confidence=float(payload.get('confidence', 0)),
                channel=int(payload.get('channel', 0)),
                packet_rate=int(payload.get('packet_rate', 0)),
            )
            
            # Put in queue (drop oldest if full)
            try:
                self.queue.put_nowait(signal_data)
            except queue.Full:
                try:
                    self.queue.get_nowait()
                    self.queue.put_nowait(signal_data)
                except queue.Empty:
                    pass

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _reconnect(self) -> None:
        """Handle reconnection with exponential backoff"""
        with self._lock:
            max_attempts = self.config.get('max_reconnect_attempts', 10)
            if self.reconnect_count >= max_attempts:
                logger.error(f"Max reconnect attempts ({max_attempts}) reached")
                self.running = False
                return

            self.reconnect_count += 1
            wait_time = min(2 ** self.reconnect_count, 300)  # Max 5 minutes
            logger.info(f"Reconnecting... (attempt {self.reconnect_count}, wait {wait_time}s)")
            time.sleep(wait_time)

    def get_signal(self, timeout: float = 1.0) -> Optional[SignalData]:
        """Get next signal from queue"""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def queue_size(self) -> int:
        """Get queue size"""
        return self.queue.qsize()

    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connected and self.running
