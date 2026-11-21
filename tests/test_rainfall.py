"""tests/test_rainfall.py

Unit tests for rain_at(pixel, date) against ground truth lineage values:
- Pixel 17 (2017-08-13..16) = [20.9257, 15.6943, 15.6943, 5.1048]
- Pixel 12 (2022-05-04..07) = [7.3688, 7.3688, 3.5267, 0.0]
- Pixel 32 (2021-11-19..21) = [8.3808, 6.2856, 0.0]
- Pixel 12, 13, 20 (2022-09-03..07) as in B.1 table
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from pipeline.build_station_validation import rain_at

def test_rain_at_pixel_17_aug_2017():
    dates = ["2017-08-13", "2017-08-14", "2017-08-15", "2017-08-16"]
    expected = [20.9257, 15.6943, 15.6943, 5.1048]
    actual = [round(rain_at(17, d), 4) for d in dates]
    assert actual == expected, f"Pixel 17 Aug 2017 mismatch: {actual} != {expected}"

def test_rain_at_pixel_12_may_2022():
    dates = ["2022-05-04", "2022-05-05", "2022-05-06", "2022-05-07"]
    expected = [7.3688, 7.3688, 3.5267, 0.0]
    actual = [round(rain_at(12, d), 4) for d in dates]
    assert actual == expected, f"Pixel 12 May 2022 mismatch: {actual} != {expected}"

def test_rain_at_pixel_32_nov_2021():
    dates = ["2021-11-19", "2021-11-20", "2021-11-21"]
    expected = [8.3808, 6.2856, 0.0]
    actual = [round(rain_at(32, d), 4) for d in dates]
    assert actual == expected, f"Pixel 32 Nov 2021 mismatch: {actual} != {expected}"

def test_rain_at_sep_2022_b1_table():
    dates = ["2022-09-03", "2022-09-04", "2022-09-05", "2022-09-06", "2022-09-07"]
    
    # Pixel 12
    exp_12 = [0.0, 23.1269, 15.4179, 19.1131, 28.6696]
    act_12 = [round(rain_at(12, d), 4) for d in dates]
    assert act_12 == exp_12, f"Pixel 12 Sep 2022 mismatch: {act_12} != {exp_12}"

    # Pixel 13
    exp_13 = [0.0, 29.5587, 19.7058, 15.3968, 30.7936]
    act_13 = [round(rain_at(13, d), 4) for d in dates]
    assert act_13 == exp_13, f"Pixel 13 Sep 2022 mismatch: {act_13} != {exp_13}"

    # Pixel 20
    exp_20 = [0.0, 30.8514, 20.5676, 13.3375, 26.6751]
    act_20 = [round(rain_at(20, d), 4) for d in dates]
    assert act_20 == exp_20, f"Pixel 20 Sep 2022 mismatch: {act_20} != {exp_20}"

def test_rain_at_city_wide_max():
    # Test city wide max across all 37 pixels
    assert round(rain_at("ALL", "2017-09-25"), 4) == 19.2932
    assert round(rain_at("ALL", "2017-09-26"), 4) == 26.1346
    assert round(rain_at("ALL", "2017-09-27"), 4) == 20.3386
    assert round(rain_at("ALL", "2017-09-28"), 4) == 18.3983
