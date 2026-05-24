#!/usr/bin/env python3
"""
Test signal filters
"""

import unittest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.filters import HampelFilter, MedianFilter, KalmanFilter, FilterChain


class TestHampelFilter(unittest.TestCase):
    """Test Hampel filter"""

    def test_outlier_removal(self):
        """Test outlier removal"""
        f = HampelFilter(window=5, threshold=3.0)
        
        # Normal values
        for i in range(5):
            result = f.apply(1.0)
        
        # Outlier
        result = f.apply(10.0)
        self.assertLess(result, 5.0, "Outlier should be filtered")

    def test_normal_values(self):
        """Test normal value pass-through"""
        f = HampelFilter()
        result = f.apply(1.0)
        self.assertEqual(result, 1.0)


class TestMedianFilter(unittest.TestCase):
    """Test median filter"""

    def test_median_computation(self):
        """Test median computation"""
        f = MedianFilter(window=3)
        f.apply(1.0)
        f.apply(2.0)
        result = f.apply(3.0)
        self.assertEqual(result, 2.0, "Median of [1,2,3] should be 2")


class TestKalmanFilter(unittest.TestCase):
    """Test Kalman filter"""

    def test_initialization(self):
        """Test Kalman filter initialization"""
        f = KalmanFilter()
        result = f.update(1.0)
        self.assertEqual(result, 1.0, "First update should return measurement")

    def test_smoothing(self):
        """Test Kalman smoothing"""
        f = KalmanFilter(q=0.01, r=0.1)
        
        # Feed noisy signal
        values = [1.0, 1.2, 0.8, 1.1, 0.9, 1.0]
        results = [f.update(v) for v in values]
        
        # Check smoothing (should reduce variance)
        input_var = np.var(values)
        output_var = np.var(results)
        self.assertLess(output_var, input_var, "Kalman should reduce variance")


class TestFilterChain(unittest.TestCase):
    """Test complete filter chain"""

    def test_filter_chain(self):
        """Test filter chain"""
        config = {
            'hampel_enable': True,
            'hampel_window': 5,
            'hampel_threshold': 3.0,
            'median_enable': True,
            'median_window': 5,
            'kalman_enable': True,
            'kalman_q': 0.01,
            'kalman_r': 0.1,
        }
        
        chain = FilterChain(config)
        
        # Apply filter chain
        values = [1.0, 1.1, 0.9, 1.0, 1.2, 10.0, 1.1, 1.0]  # Outlier at index 5
        results = [chain.apply(v) for v in values]
        
        # Check that outlier was filtered
        self.assertLess(results[5], 5.0, "Chain should filter outlier")


if __name__ == "__main__":
    unittest.main()
