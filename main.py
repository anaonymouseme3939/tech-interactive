#!/usr/bin/env python3
"""
TECH INTERACTIVE Main Entry Point
WiFi Spatial Intelligence Observatory
"""

import sys
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from logger import init_logger, get_logger
from launcher import initialize_system, discover_nodes, launch_dashboard


def main():
    """Main entry point"""
    try:
        # Initialize system
        config, logger_system = initialize_system()
        logger = get_logger("main")

        # Log system info
        device_config = config.get_device_config()
        logger.info(f"Device: {device_config['name']}")
        logger.info(f"Device ID: {device_config['device_id']}")
        logger.info(f"Location: {device_config['location']}")

        # Discover nodes
        nodes = discover_nodes(config)
        logger.info(f"Found {len(nodes)} node(s)")

        # Launch dashboard
        logger.info("Starting TECH INTERACTIVE dashboard...")
        launch_dashboard(config)

    except KeyboardInterrupt:
        logger = get_logger("main")
        logger.info("System shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger = get_logger("main")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
