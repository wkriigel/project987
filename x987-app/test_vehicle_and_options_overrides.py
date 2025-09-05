#!/usr/bin/env python3
"""
Minimal tests for vehicle catalog detection and generation-aware option overrides.
Run with: python x987-app/test_vehicle_and_options_overrides.py
"""

import sys

def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"{msg} Expected {b}, got {a}")


def test_vehicle_detection():
    from x987.vehicles import detect_model_and_trim

    # 911
    m, t = detect_model_and_trim("2018 Porsche 911 Carrera 4S", 2018)
    assert_eq((m, t), ("911", "Carrera 4S"), "911 Carrera 4S detection failed")

    m, t = detect_model_and_trim("2007 Porsche 911 Targa", 2007)
    assert_eq((m, t), ("911", "Targa"), "911 Targa detection failed")

    # Macan
    m, t = detect_model_and_trim("2020 Porsche Macan GTS", 2020)
    assert_eq((m, t), ("Macan", "GTS"), "Macan GTS detection failed")

    # Boxster/Cayman
    m, t = detect_model_and_trim("2014 Porsche Boxster GTS", 2014)
    assert_eq((m, t), ("Boxster", "GTS"), "Boxster GTS detection failed")

    m, t = detect_model_and_trim("2015 Porsche Cayman GT4", 2015)
    assert_eq((m, t), ("Cayman", "GT4"), "Cayman GT4 detection failed")

    # Panamera
    m, t = detect_model_and_trim("2018 Porsche Panamera 4S", 2018)
    assert_eq((m, t), ("Panamera", "4S"), "Panamera 4S detection failed")

    # Taycan
    m, t = detect_model_and_trim("2022 Porsche Taycan 4S Cross Turismo", 2022)
    assert_eq((m, t), ("Taycan", "4S"), "Taycan 4S detection failed")


def test_options_overrides_911():
    from x987.options import OptionsDetector

    detector = OptionsDetector()

    text = "Sport Chrono, PASM, sport exhaust, X51 Power Kit, PCM Navigation, BOSE, 19\" wheels"
    summary = detector.get_detailed_options_summary(text, None, model="911", year=2007)

    # Expect override values per 997.1 (same as 996/997.2 in config):
    # Chrono 920 + PASM 1990 + PSE 2400 + X51 15000 + PCM 3070 + BOSE 1390 + Wheels 2000
    expected = 920 + 1990 + 2400 + 15000 + 3070 + 1390 + 2000
    assert_eq(summary.get('total_value'), expected, "911 override total mismatch")


def test_options_overrides_macan():
    from x987.options import OptionsDetector

    detector = OptionsDetector()

    text = "PASM, 0P9 exhaust, 8LH Sport Chrono, PDLS 8JU, BOSE 9VL, PCM I8T"
    summary = detector.get_detailed_options_summary(text, None, model="Macan", year=2020)

    # PASM 1390 + PSE 1590 + Chrono 1360 + PDLS (Bi-Xenon id) 770 + BOSE 990 + PCM 1730
    expected = 1390 + 1590 + 1360 + 770 + 990 + 1730
    assert_eq(summary.get('total_value'), expected, "Macan override total mismatch")


def main():
    try:
        test_vehicle_detection()
        test_options_overrides_911()
        test_options_overrides_macan()
        print("OK: vehicle detection and options overrides")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

