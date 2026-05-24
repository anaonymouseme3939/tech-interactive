#!/usr/bin/env python3
"""
System Launcher and Node Discovery
"""

import sys
import logging
from pathlib import Path
from config import Config
from logger import init_logger, get_logger


def setup_environment() -> None:
    """Setup Python environment and paths"""
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))


def initialize_system() -> tuple:
    """Initialize all system components"""
    # Setup logging first
    logger_system = init_logger(log_dir="logs", level=logging.INFO)
    logger = get_logger("launcher")

    logger.info("Starting TECH INTERACTIVE system...")

    # Load configuration
    try:
        config = Config("esp32_tech_interactive.ini")
        config.validate()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    return config, logger_system


def discover_nodes(config: Config) -> list:
    """Discover available ESP32 nodes"""
    logger = get_logger("launcher")
    nodes = []

    # Get MQTT config
    mqtt_config = config.get_mqtt_config()

    if mqtt_config['enable']:
        logger.info(f"MQTT enabled: {mqtt_config['host']}:{mqtt_config['port']}")
        # Nodes will be discovered via MQTT
        nodes.append({
            'type': 'mqtt',
            'host': mqtt_config['host'],
            'port': mqtt_config['port'],
            'topic': mqtt_config['topic_base']
        })
    else:
        logger.warning("MQTT not enabled, no nodes will be discovered")

    logger.info(f"Discovered {len(nodes)} node(s)")
    return nodes


def launch_dashboard(config: Config) -> None:
    """Launch dashboard"""
    logger = get_logger("launcher")
    logger.info("Launching dashboard...")

    try:
        from dashboard.window import DashboardWindow
        from PySide6.QtWidgets import QApplication
        import sys

        app = QApplication(sys.argv)
        window = DashboardWindow(config)
        window.show()
        sys.exit(app.exec())

    except ImportError as e:
        logger.error(f"Failed to import dashboard: {e}")
        logger.error("Make sure PySide6 is installed: pip install -r requirements.txt")
        raise
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")
        raise


if __name__ == "__main__":
    setup_environment()
    config, logger_system = initialize_system()
    nodes = discover_nodes(config)
    launch_dashboard(config)
