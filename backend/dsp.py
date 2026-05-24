#!/usr/bin/env python3
"""
Digital Signal Processing for TECH INTERACTIVE
"""

import numpy as np
from scipy import signal as scipy_signal
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DSPProcessor:
    """DSP processing pipeline"""

    def __init__(self, config: dict, sample_rate: float = 100.0):
        """Initialize DSP processor"""
        self.config = config
        self.sample_rate = sample_rate
        self.buffer = np.array([])
        self.fft_size = config.get('fft_size', 256)

    def detrend(self, signal: np.ndarray) -> np.ndarray:
        """Remove linear trend from signal"""
        if len(signal) < 2:
            return signal
        return scipy_signal.detrend(signal)

    def compute_fft(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute FFT"""
        if len(signal) == 0:
            return np.array([]), np.array([])
        
        # Pad to fft_size
        if len(signal) < self.fft_size:
            signal = np.pad(signal, (0, self.fft_size - len(signal)))
        else:
            signal = signal[:self.fft_size]

        # Apply Hann window
        windowed = signal * scipy_signal.hann(len(signal))
        
        # Compute FFT
        fft_result = np.fft.fft(windowed)
        freqs = np.fft.fftfreq(len(windowed), 1/self.sample_rate)
        
        return freqs[:len(freqs)//2], np.abs(fft_result[:len(fft_result)//2])

    def bandpass_filter(self, signal: np.ndarray, low_hz: float, high_hz: float) -> np.ndarray:
        """Apply bandpass filter"""
        if len(signal) < 2:
            return signal
        
        # Normalize frequencies
        nyquist = self.sample_rate / 2
        low = low_hz / nyquist
        high = high_hz / nyquist
        
        # Clamp to valid range
        low = np.clip(low, 0.001, 0.999)
        high = np.clip(high, low + 0.001, 0.999)
        
        try:
            b, a = scipy_signal.butter(4, [low, high], btype='band')
            return scipy_signal.filtfilt(b, a, signal)
        except Exception as e:
            logger.error(f"Bandpass filter error: {e}")
            return signal

    def extract_energy(self, signal: np.ndarray) -> float:
        """Extract signal energy"""
        if len(signal) == 0:
            return 0.0
        return float(np.sqrt(np.mean(signal ** 2)))

    def extract_variance(self, signal: np.ndarray) -> float:
        """Extract signal variance"""
        if len(signal) == 0:
            return 0.0
        return float(np.var(signal))

    def extract_motion(self, signal: np.ndarray) -> float:
        """Extract motion metric (rate of change)"""
        if len(signal) < 2:
            return 0.0
        diff = np.diff(signal)
        return float(np.sqrt(np.mean(diff ** 2)))

    def extract_dominant_frequency(self, signal: np.ndarray) -> float:
        """Extract dominant frequency"""
        freqs, magnitudes = self.compute_fft(signal)
        if len(freqs) == 0:
            return 0.0
        idx = np.argmax(magnitudes)
        return float(freqs[idx]) if idx < len(freqs) else 0.0

    def process(self, signal: np.ndarray) -> dict:
        """Process signal and extract features"""
        if len(signal) == 0:
            return {
                'energy': 0.0,
                'variance': 0.0,
                'motion': 0.0,
                'dominant_freq': 0.0,
            }

        # Detrend
        detrended = self.detrend(signal)
        
        # Extract features
        energy = self.extract_energy(detrended)
        variance = self.extract_variance(detrended)
        motion = self.extract_motion(detrended)
        dominant_freq = self.extract_dominant_frequency(detrended)

        return {
            'energy': energy,
            'variance': variance,
            'motion': motion,
            'dominant_freq': dominant_freq,
        }
