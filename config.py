#!/usr/bin/env python3
"""
Configuration Manager for TECH INTERACTIVE
Loads and validates esp32_tech_interactive.ini
"""

import configparser
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import os

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for TECH INTERACTIVE system"""

    def __init__(self, config_file: str = "esp32_tech_interactive.ini"):
        """Initialize configuration from INI file"""
        self.config_file = Path(config_file)
        self.parser = configparser.ConfigParser()
        self.data: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from INI file"""
        if not self.config_file.exists():
            logger.error(f"Config file not found: {self.config_file}")
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        try:
            self.parser.read(self.config_file)
            self._parse_all_sections()
            logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _parse_all_sections(self) -> None:
        """Parse all sections from config file"""
        for section in self.parser.sections():
            self.data[section] = dict(self.parser.items(section))

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with type conversion"""
        try:
            value = self.parser.get(section, key)
            return self._convert_type(value)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if default is not None:
                return default
            logger.warning(f"Config key not found: {section}.{key}")
            return default

    def get_bool(self, section: str, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        try:
            return self.parser.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

    def get_int(self, section: str, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return self.parser.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

    def get_float(self, section: str, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        try:
            return self.parser.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

    def get_list(self, section: str, key: str, default: Optional[list] = None) -> list:
        """Get comma-separated list configuration value"""
        try:
            value = self.parser.get(section, key)
            return [x.strip() for x in value.split(',')]
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default if default is not None else []

    @staticmethod
    def _convert_type(value: str) -> Any:
        """Auto-convert string value to appropriate type"""
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value.lower() in ('false', 'no', 'off', '0'):
            return False
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def get_device_config(self) -> Dict[str, Any]:
        """Get device configuration"""
        return {
            'name': self.get('device', 'name', 'tech-interactive-node-01'),
            'device_id': self.get('device', 'device_id', 'ESP32-001'),
            'location': self.get('device', 'location', 'unknown'),
        }

    def get_wifi_config(self) -> Dict[str, Any]:
        """Get WiFi configuration"""
        return {
            'ssid': self.get('wifi', 'ssid', ''),
            'password': self.get('wifi', 'password', ''),
            'mode': self.get('wifi', 'mode', 'sta'),
            'connect_timeout': self.get_int('wifi', 'connect_timeout', 20),
            'reconnect_interval': self.get_int('wifi', 'reconnect_interval', 10),
        }

    def get_mqtt_config(self) -> Dict[str, Any]:
        """Get MQTT configuration"""
        return {
            'enable': self.get_bool('mqtt', 'enable', True),
            'host': self.get('mqtt', 'host', '192.168.1.20'),
            'port': self.get_int('mqtt', 'port', 1883),
            'keepalive': self.get_int('mqtt', 'keepalive', 60),
            'username': self.get('mqtt', 'username', ''),
            'password': self.get('mqtt', 'password', ''),
            'topic_base': self.get('mqtt', 'topic_base', 'tech_interactive'),
            'qos': self.get_int('mqtt', 'qos', 1),
            'connect_timeout': self.get_int('mqtt', 'connect_timeout', 10),
            'reconnect_interval': self.get_int('mqtt', 'reconnect_interval', 5),
            'max_reconnect_attempts': self.get_int('mqtt', 'max_reconnect_attempts', 10),
        }

    def get_signal_config(self) -> Dict[str, Any]:
        """Get signal acquisition configuration"""
        return {
            'sample_rate': self.get_int('signal_acquisition', 'sample_rate', 100),
            'channels': self.get_list('signal_acquisition', 'channels', [1, 6, 11]),
            'channel_hop': self.get_bool('signal_acquisition', 'channel_hop', True),
            'heartbeat_interval_ms': self.get_int('signal_acquisition', 'heartbeat_interval_ms', 1000),
        }

    def get_dsp_config(self) -> Dict[str, Any]:
        """Get DSP configuration"""
        return {
            'kalman_enable': self.get_bool('signal_processing', 'kalman_enable', True),
            'kalman_q': self.get_float('signal_processing', 'kalman_q', 0.01),
            'kalman_r': self.get_float('signal_processing', 'kalman_r', 0.1),
            'median_enable': self.get_bool('signal_processing', 'median_filter_enable', True),
            'median_window': self.get_int('signal_processing', 'median_window', 5),
            'hampel_enable': self.get_bool('signal_processing', 'hampel_enable', True),
            'hampel_threshold': self.get_float('signal_processing', 'hampel_threshold', 3.0),
            'fft_enable': self.get_bool('signal_processing', 'fft_enable', True),
            'fft_size': self.get_int('signal_processing', 'fft_size', 256),
        }

    def get_detection_config(self) -> Dict[str, Any]:
        """Get detection configuration"""
        return {
            'presence_enable': self.get_bool('presence_detection', 'enable', True),
            'presence_confidence_gate': self.get_float('presence_detection', 'confidence_gate', 0.95),
            'presence_timeout': self.get_int('presence_detection', 'presence_timeout', 12),
            'motion_enable': self.get_bool('motion_detection', 'enable', True),
            'motion_threshold': self.get_float('motion_detection', 'motion_threshold', 0.12),
            'motion_debounce': self.get_int('motion_detection', 'motion_debounce', 3),
            'breathing_enable': self.get_bool('breathing_detection', 'enable', True),
            'breathing_low': self.get_float('breathing_detection', 'breathing_low_hz', 0.10),
            'breathing_high': self.get_float('breathing_detection', 'breathing_high_hz', 0.50),
            'heart_enable': self.get_bool('heart_detection', 'enable', True),
            'heart_low': self.get_float('heart_detection', 'heart_low_hz', 0.80),
            'heart_high': self.get_float('heart_detection', 'heart_high_hz', 2.0),
        }

    def validate(self) -> bool:
        """Validate critical configuration values"""
        errors = []
        
        # Validate WiFi
        if not self.get('wifi', 'ssid'):
            errors.append("WiFi SSID not configured")
        
        # Validate MQTT
        if self.get_bool('mqtt', 'enable', True):
            if not self.get('mqtt', 'host'):
                errors.append("MQTT host not configured")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True


def get_config() -> Config:
    """Get global config instance"""
    return Config()
