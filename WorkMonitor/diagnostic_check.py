#!/usr/bin/env python3
"""
Diagnostic script to verify WorkMonitor application integrity
This script performs static analysis without launching the GUI
"""

import ast
import sys
from pathlib import Path

def check_method_exists(tree, class_name, method_name):
    """Check if a method exists in a class"""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return True
    return False

def check_button_creation(tree):
    """Check if buttons are created in setup_ui"""
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'setup_ui':
            # Convert to source to search for button creation
            buttons_found = {
                'dashboard_btn': False,
                'admin_btn': False,
                'minimize_btn': False,
                'shutdown_btn': False
            }

            # Check if Button widgets are created
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Assign):
                    for target in subnode.targets:
                        if isinstance(target, ast.Name):
                            if target.id in buttons_found:
                                buttons_found[target.id] = True

            for btn_name, found in buttons_found.items():
                if not found:
                    issues.append(f"Button '{btn_name}' not found in setup_ui")

            return issues

    issues.append("setup_ui method not found")
    return issues

def check_admin_panel_class(tree):
    """Check AdminPanel class structure"""
    issues = []
    admin_panel_found = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'AdminPanel':
            admin_panel_found = True

            # Check for __init__ method
            init_found = False
            create_widgets_found = False

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name == '__init__':
                        init_found = True
                    elif item.name == 'create_widgets':
                        create_widgets_found = True

            if not init_found:
                issues.append("AdminPanel missing __init__ method")
            if not create_widgets_found:
                issues.append("AdminPanel missing create_widgets method")

    if not admin_panel_found:
        issues.append("AdminPanel class not found")

    return issues

def check_show_admin_panel(tree):
    """Check show_admin_panel method implementation"""
    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'show_admin_panel':
            # Check if AdminPanel is instantiated
            admin_panel_created = False
            has_error_handling = False

            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Name) and subnode.func.id == 'AdminPanel':
                        admin_panel_created = True
                if isinstance(subnode, ast.Try):
                    has_error_handling = True

            if not admin_panel_created:
                issues.append("show_admin_panel does not create AdminPanel instance")
            if not has_error_handling:
                issues.append("show_admin_panel lacks error handling")

            return issues

    issues.append("show_admin_panel method not found")
    return issues

def analyze_window_geometry(source_code):
    """Analyze window geometry settings"""
    issues = []

    # Check main window geometry
    if 'self.root.geometry(' in source_code:
        import re
        match = re.search(r'self\.root\.geometry\(["\'](\d+)x(\d+)["\']', source_code)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            print(f"✓ Main window geometry: {width}x{height}")

            # Check if height is sufficient (should be at least 900)
            if height < 900:
                issues.append(f"Window height {height}px may be too small for all content")
        else:
            issues.append("Could not parse main window geometry")
    else:
        issues.append("Main window geometry not set")

    return issues

def main():
    """Run all diagnostic checks"""
    script_path = Path(__file__).parent / "src" / "work_monitor.py"

    if not script_path.exists():
        print(f"❌ ERROR: work_monitor.py not found at {script_path}")
        return 1

    print("="*70)
    print("WorkMonitor Application Diagnostic Check")
    print("="*70)
    print()

    # Read and parse the source code
    with open(script_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"❌ CRITICAL: Syntax error in work_monitor.py: {e}")
        return 1

    print("✓ Source code syntax is valid")
    print()

    all_issues = []

    # Check 1: Button creation
    print("CHECK 1: Button Creation in setup_ui")
    print("-" * 70)
    button_issues = check_button_creation(tree)
    if button_issues:
        for issue in button_issues:
            print(f"  ⚠ {issue}")
            all_issues.append(issue)
    else:
        print("  ✓ All required buttons found in setup_ui")
    print()

    # Check 2: AdminPanel class structure
    print("CHECK 2: AdminPanel Class Structure")
    print("-" * 70)
    admin_issues = check_admin_panel_class(tree)
    if admin_issues:
        for issue in admin_issues:
            print(f"  ⚠ {issue}")
            all_issues.append(issue)
    else:
        print("  ✓ AdminPanel class structure is correct")
    print()

    # Check 3: show_admin_panel method
    print("CHECK 3: show_admin_panel Method")
    print("-" * 70)
    show_admin_issues = check_show_admin_panel(tree)
    if show_admin_issues:
        for issue in show_admin_issues:
            print(f"  ⚠ {issue}")
            all_issues.append(issue)
    else:
        print("  ✓ show_admin_panel method is correctly implemented")
    print()

    # Check 4: Window geometry
    print("CHECK 4: Window Geometry Analysis")
    print("-" * 70)
    geometry_issues = analyze_window_geometry(source_code)
    if geometry_issues:
        for issue in geometry_issues:
            print(f"  ⚠ {issue}")
            all_issues.append(issue)
    else:
        print("  ✓ Window geometry settings are appropriate")
    print()

    # Check 5: Method existence
    print("CHECK 5: Required Methods Existence")
    print("-" * 70)
    required_methods = [
        ('WorkMonitorApp', 'open_dashboard'),
        ('WorkMonitorApp', 'show_admin_panel'),
        ('WorkMonitorApp', 'minimize_to_tray'),
        ('WorkMonitorApp', 'shutdown_program'),
        ('AdminPanel', 'save_settings'),
    ]

    for class_name, method_name in required_methods:
        exists = check_method_exists(tree, class_name, method_name)
        if exists:
            print(f"  ✓ {class_name}.{method_name} exists")
        else:
            issue = f"{class_name}.{method_name} method not found"
            print(f"  ❌ {issue}")
            all_issues.append(issue)
    print()

    # Summary
    print("="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)

    if all_issues:
        print(f"❌ Found {len(all_issues)} issue(s):")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        print()
        print("⚠ APPLICATION HAS ISSUES - DO NOT PUSH")
        return 1
    else:
        print("✓ All diagnostic checks passed")
        print("✓ Code structure appears correct")
        print()
        print("⚠ Note: This diagnostic only checks code structure.")
        print("⚠ Actual runtime testing is still required.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
