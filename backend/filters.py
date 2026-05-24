#!/usr/bin/env python3
"""
Signal Filter Chain: Hampel -> Median -> Kalman
"""

import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class HampelFilter:
    """Hampel outlier filter using median absolute deviation"""

    def __init__(self, window: int = 5, threshold: float = 3.0):
        """Initialize Hampel filter"""
        self.window = window
        self.threshold = threshold
        self.buffer = []

    def apply(self, value: float) -> float:
        """Apply Hampel filter"""
        self.buffer.append(value)
        if len(self.buffer) > self.window:
            self.buffer.pop(0)

        if len(self.buffer) < self.window:
            return value

        # Calculate median and MAD
        median = np.median(self.buffer)
        mad = np.median(np.abs(np.array(self.buffer) - median))
        
        # Check if value is outlier
        if mad > 0 and abs(value - median) > self.threshold * mad:
            return median  # Replace with median
        
        return value


class MedianFilter:
    """Median filter for spike rejection"""

    def __init__(self, window: int = 5):
        """Initialize median filter"""
        self.window = window
        self.buffer = []

    def apply(self, value: float) -> float:
        """Apply median filter"""
        self.buffer.append(value)
        if len(self.buffer) > self.window:
            self.buffer.pop(0)
        
        return float(np.median(self.buffer))


class KalmanFilter:
    """1D Kalman filter for optimal smoothing"""

    def __init__(self, q: float = 0.01, r: float = 0.1, x: float = 0.5, p: float = 1.0):
        """Initialize Kalman filter"""
        self.q = q  # Process noise
        self.r = r  # Measurement noise
        self.x = x  # State estimate
        self.p = p  # Estimate error
        self.initialized = False

    def update(self, measurement: float) -> float:
        """Update Kalman filter with new measurement"""
        if not self.initialized:
            self.x = measurement
            self.initialized = True
            return measurement

        # Predict
        self.p = self.p + self.q

        # Update
        k = self.p / (self.p + self.r)  # Kalman gain
        self.x = self.x + k * (measurement - self.x)
        self.p = (1 - k) * self.p

        return self.x


class FilterChain:
    """Complete filter chain: Hampel -> Median -> Kalman"""

    def __init__(self, config: dict):
        """Initialize filter chain"""
        self.config = config
        self.hampel = HampelFilter(
            window=config.get('hampel_window', 5),
            threshold=config.get('hampel_threshold', 3.0)
        ) if config.get('hampel_enable', True) else None

        self.median = MedianFilter(
            window=config.get('median_window', 5)
        ) if config.get('median_enable', True) else None

        self.kalman = KalmanFilter(
            q=config.get('kalman_q', 0.01),
            r=config.get('kalman_r', 0.1),
            x=config.get('kalman_x', 0.5),
            p=config.get('kalman_p', 1.0)
        ) if config.get('kalman_enable', True) else None

    def apply(self, value: float) -> float:
        """Apply complete filter chain"""
        result = value

        # Apply filters in sequence
        if self.hampel:
            result = self.hampel.apply(result)
        if self.median:
            result = self.median.apply(result)
        if self.kalman:
            result = self.kalman.update(result)

        return result

    def reset(self) -> None:
        """Reset all filters"""
        if self.hampel:
            self.hampel.buffer.clear()
        if self.median:
            self.median.buffer.clear()
        if self.kalman:
            self.kalman.initialized = False
