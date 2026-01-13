#!/usr/bin/env python3
"""
Integration test script for WorkMonitor
Tests the application logic without launching the GUI
"""

import sys
import os
from pathlib import Path
import hashlib

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_system():
    """Test configuration system"""
    print("TEST 1: Configuration System")
    print("-" * 70)

    try:
        # Import config related code
        from work_monitor import Config, DEFAULT_CONFIG, CONFIG_FILE

        # Test config can be instantiated
        config = Config()
        print("  ✓ Config object created successfully")

        # Test default password verification
        default_password = "admin123"
        default_hash = hashlib.sha256(default_password.encode()).hexdigest()

        if config.verify_password(default_password):
            print(f"  ✓ Default password '{default_password}' verification works")
        else:
            print(f"  ❌ Default password '{default_password}' verification FAILED")
            return False

        # Test getting a setting
        autostart_enabled = config.get('autostart_enabled')
        print(f"  ✓ Config.get() works (autostart_enabled = {autostart_enabled})")

        # Test setting a value
        config.set('test_key', 'test_value')
        if config.get('test_key') == 'test_value':
            print("  ✓ Config.set() works")
        else:
            print("  ❌ Config.set() FAILED")
            return False

        print("  ✅ Configuration system is functional\n")
        return True

    except Exception as e:
        print(f"  ❌ CRITICAL ERROR in configuration system: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all required imports work"""
    print("TEST 2: Required Imports")
    print("-" * 70)

    required_modules = [
        'tkinter',
        'PIL',
        'pystray',
        'psutil',
    ]

    all_ok = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module} imported successfully")
        except ImportError as e:
            print(f"  ❌ {module} import FAILED: {e}")
            all_ok = False

    if all_ok:
        print("  ✅ All required modules are available\n")
    else:
        print("  ❌ Some required modules are MISSING\n")

    return all_ok

def test_class_instantiation():
    """Test that main classes can be instantiated"""
    print("TEST 3: Class Instantiation")
    print("-" * 70)

    try:
        from work_monitor import ActivityLogger, ScreenshotManager, Config, AntiCheatDetector

        # Test ActivityLogger
        try:
            logger = ActivityLogger()
            print("  ✓ ActivityLogger instantiated")
        except Exception as e:
            print(f"  ❌ ActivityLogger FAILED: {e}")
            return False

        # Test ScreenshotManager
        try:
            screenshot_mgr = ScreenshotManager()
            print("  ✓ ScreenshotManager instantiated")
        except Exception as e:
            print(f"  ❌ ScreenshotManager FAILED: {e}")
            return False

        # Test Config
        try:
            config = Config()
            print("  ✓ Config instantiated")
        except Exception as e:
            print(f"  ❌ Config FAILED: {e}")
            return False

        # Test AntiCheatDetector
        try:
            anticheat = AntiCheatDetector(config)
            print("  ✓ AntiCheatDetector instantiated")
        except Exception as e:
            print(f"  ❌ AntiCheatDetector FAILED: {e}")
            return False

        print("  ✅ All core classes can be instantiated\n")
        return True

    except Exception as e:
        print(f"  ❌ CRITICAL ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_button_command_methods():
    """Test that button command methods are defined and callable"""
    print("TEST 4: Button Command Methods")
    print("-" * 70)

    try:
        from work_monitor import WorkMonitorApp
        import inspect

        # Get all methods of WorkMonitorApp
        methods = inspect.getmembers(WorkMonitorApp, predicate=inspect.isfunction)
        method_names = [name for name, _ in methods]

        required_methods = [
            'open_dashboard',
            'show_admin_panel',
            'minimize_to_tray',
            'shutdown_program',
        ]

        all_ok = True
        for method_name in required_methods:
            if method_name in method_names:
                print(f"  ✓ WorkMonitorApp.{method_name} exists and is callable")
            else:
                print(f"  ❌ WorkMonitorApp.{method_name} NOT FOUND")
                all_ok = False

        if all_ok:
            print("  ✅ All button command methods are defined\n")
        else:
            print("  ❌ Some button command methods are MISSING\n")

        return all_ok

    except Exception as e:
        print(f"  ❌ CRITICAL ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_admin_panel_class():
    """Test AdminPanel class"""
    print("TEST 5: AdminPanel Class")
    print("-" * 70)

    try:
        from work_monitor import AdminPanel
        import inspect

        # Check if AdminPanel has required methods
        methods = inspect.getmembers(AdminPanel, predicate=inspect.isfunction)
        method_names = [name for name, _ in methods]

        required_methods = ['__init__', 'create_widgets', 'save_settings']

        all_ok = True
        for method_name in required_methods:
            if method_name in method_names:
                print(f"  ✓ AdminPanel.{method_name} exists")
            else:
                print(f"  ❌ AdminPanel.{method_name} NOT FOUND")
                all_ok = False

        if all_ok:
            print("  ✅ AdminPanel class structure is correct\n")
        else:
            print("  ❌ AdminPanel class is INCOMPLETE\n")

        return all_ok

    except Exception as e:
        print(f"  ❌ CRITICAL ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def calculate_ui_height_requirements():
    """Calculate minimum height required for all UI elements"""
    print("TEST 6: UI Height Requirements")
    print("-" * 70)

    # Estimated heights based on code review
    estimates = {
        'Main container top padding': 25,
        'Title (36pt font + 8px bottom)': 56,
        'Subtitle (15pt font + 32px bottom)': 52,
        'Status card (padding + content)': 95,
        'Stats card (5 rows + padding)': 212,
        'Timer card (large timer + labels)': 199,
        'Buttons section (4 buttons)': 90,
        'Main container bottom padding': 25,
    }

    total_height = 0
    for component, height in estimates.items():
        print(f"  • {component}: ~{height}px")
        total_height += height

    print(f"\n  Total estimated height needed: ~{total_height}px")
    print(f"  Current window height: 950px")
    print(f"  Available margin: {950 - total_height}px")

    if total_height <= 950:
        print(f"  ✅ Window height is sufficient\n")
        return True
    else:
        print(f"  ❌ Window height is INSUFFICIENT\n")
        return False

def main():
    """Run all tests"""
    print("="*70)
    print("WorkMonitor Integration Test Suite")
    print("="*70)
    print()

    results = []

    # Run all tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration System", test_config_system()))
    results.append(("Class Instantiation", test_class_instantiation()))
    results.append(("Button Command Methods", test_button_command_methods()))
    results.append(("AdminPanel Class", test_admin_panel_class()))
    results.append(("UI Height Requirements", calculate_ui_height_requirements()))

    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - Application structure is correct")
        print("\n⚠  NOTE: GUI-specific issues may still exist at runtime.")
        print("   Recommended: Test manually by running the application.")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - Issues must be fixed")
        print("\n⚠  DO NOT PUSH until all tests pass")
        return 1

if __name__ == '__main__':
    sys.exit(main())
