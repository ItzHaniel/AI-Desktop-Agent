#!/usr/bin/env python3
"""
Simple logging for Jarvis
"""

import logging
from datetime import datetime

def setup_logger(name="jarvis"):
    """Setup basic logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
