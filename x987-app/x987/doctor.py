"""
System diagnostics and health checks

PROVIDES: System health checks and dependency validation
DEPENDS: Standard library, x987.config:get_config, x987.utils.log:get_logger
CONSUMED BY: x987.cli.main:cmd_doctor function and startup
CONTRACT: Validates system can run the application with comprehensive checks
TECH CHOICE: Simple checks with clear error messages
RISK: Low - diagnostic checks are safe
"""

import sys
import importlib
from pathlib import Path
from typing import List, Dict, Any
import logging

from .config import get_config
from .utils.log import get_logger

logger = get_logger(__name__)

# =========================
# DIAGNOSTIC CHECKS
# =========================

def check_python_version() -> Dict[str, Any]:
    """Check Python version compatibility"""
    result = {
        "name": "Python Version",
        "status": "PASS",
        "details": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    if sys.version_info < (3, 10):
        result["status"] = "FAIL"
        result["details"] = f"Python {sys.version_info.major}.{sys.version_info.minor} is too old. Required: 3.10+"
    elif sys.version_info >= (3, 13):
        result["status"] = "WARN"
        result["details"] += " (Untested version, may have compatibility issues)"
    
    return result

def check_dependencies() -> Dict[str, Any]:
    """Check required dependencies are available"""
    required_packages = {
        "playwright": "Web scraping automation",
        "rich": "Terminal formatting and UI",
    }
    
    # Check for tomli/tomllib (built-in for Python 3.11+)
    if sys.version_info >= (3, 11):
        try:
            import tomllib
            required_packages["tomllib"] = "TOML parsing (built-in)"
        except ImportError:
            required_packages["tomli"] = "TOML parsing (fallback)"
    else:
        required_packages["tomli"] = "TOML parsing"
    
    missing_packages = []
    available_packages = []
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            available_packages.append(f"✓ {package}: {description}")
        except ImportError:
            missing_packages.append(f"✗ {package}: {description}")
    
    if missing_packages:
        status = "FAIL"
        details = "Missing packages:\n" + "\n".join(missing_packages)
    else:
        status = "PASS"
        details = "All required packages available:\n" + "\n".join(available_packages)
    
    return {
        "name": "Dependencies",
        "status": status,
        "details": details
    }

def check_playwright_browser() -> Dict[str, Any]:
    """Check if Playwright browser is installed"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Try to launch browser
            browser = p.chromium.launch(headless=True)
            browser.close()
            
        return {
            "name": "Playwright Browser",
            "status": "PASS",
            "details": "Chromium browser available and working"
        }
        
    except ImportError:
        return {
            "name": "Playwright Browser",
            "status": "FAIL",
            "details": "Playwright not installed"
        }
    except Exception as e:
        return {
            "name": "Playwright Browser",
            "status": "FAIL",
            "details": f"Browser launch failed: {e}"
        }

def check_directories() -> Dict[str, Any]:
    """Check required directories exist and are writable"""
    from .config import get_config_dir, get_data_dir, get_manual_csv_dir
    
    directories = [
        ("Config", get_config_dir()),
        ("Data", get_data_dir()),
        ("Manual CSV", get_manual_csv_dir())
    ]
    
    results = []
    all_good = True
    
    for name, path in directories:
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = path / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            
            results.append(f"✓ {name}: {path}")
            
        except Exception as e:
            results.append(f"✗ {name}: {path} - {e}")
            all_good = False
    
    return {
        "name": "Directories",
        "status": "PASS" if all_good else "FAIL",
        "details": "\n".join(results)
    }

def check_configuration() -> Dict[str, Any]:
    """Check configuration file and settings"""
    try:
        config = get_config()
        
        # Validate configuration
        errors = []
        
        # Check search URLs
        urls = config.get_search_urls()
        if not urls:
            errors.append("No search URLs configured")
        
        # Check fair value settings only if not in MSRP-only mode
        mode = config.get_pricing_mode() if hasattr(config, 'get_pricing_mode') else 'msrp_only'
        fv_config = config.get_fair_value_config()
        if mode != 'msrp_only':
            required_fv = ["base_value_usd", "year_step_usd", "s_premium_usd"]
            for key in required_fv:
                if key not in fv_config:
                    errors.append(f"Missing fair_value.{key}")
        
        if errors:
            return {
                "name": "Configuration",
                "status": "FAIL",
                "details": "Configuration errors:\n" + "\n".join(f"• {e}" for e in errors)
            }
        else:
            details = [
                f"Configuration loaded successfully",
                f"Pricing mode: {mode}",
                f"Search URLs: {len(urls)}"
            ]
            if mode != 'msrp_only':
                details.append(f"Fair value params: {len(fv_config)}")
            return {
                "name": "Configuration",
                "status": "PASS",
                "details": "\n".join(details)
            }
            
    except Exception as e:
        return {
            "name": "Configuration",
            "status": "FAIL",
            "details": f"Configuration error: {e}"
        }

def check_network_access() -> Dict[str, Any]:
    """Check basic network access"""
    import urllib.request
    import urllib.error
    
    test_urls = [
        "https://www.autotempest.com",
        "https://www.cars.com"
    ]
    
    results = []
    all_good = True
    
    for url in test_urls:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    results.append(f"✓ {url}: Accessible")
                else:
                    results.append(f"⚠ {url}: Status {response.status}")
                    all_good = False
        except Exception as e:
            results.append(f"✗ {url}: {e}")
            all_good = False
    
    return {
        "name": "Network Access",
        "status": "PASS" if all_good else "WARN",
        "details": "\n".join(results)
    }

# =========================
# MAIN DOCTOR FUNCTION
# =========================

def run_doctor() -> bool:
    """
    Run all system diagnostics
    
    Returns:
        True if all critical checks pass, False otherwise
    """
    logger.info("Running system diagnostics...")
    
    checks = [
        check_python_version,
        check_dependencies,
        check_playwright_browser,
        check_directories,
        check_configuration,
        check_network_access
    ]
    
    results = []
    critical_failures = 0
    
    print("\n" + "="*60)
    print("SYSTEM DIAGNOSTICS")
    print("="*60)
    
    for check_func in checks:
        result = check_func()
        results.append(result)
        
        # Print result
        status_icon = {
            "PASS": "✓",
            "WARN": "⚠",
            "FAIL": "✗"
        }.get(result["status"], "?")
        
        print(f"\n{status_icon} {result['name']}: {result['status']}")
        print(f"   {result['details']}")
        
        # Count failures
        if result["status"] == "FAIL":
            critical_failures += 1
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    warnings = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    print(f"Passed: {passed}")
    print(f"Warnings: {warnings}")
    print(f"Failed: {failed}")
    
    if critical_failures == 0:
        print("\n✓ All critical checks passed! System is ready.")
        success = True
    else:
        print(f"\n✗ {critical_failures} critical check(s) failed. Please fix before running.")
        success = False
    
    print("="*60)
    
    return success

def quick_check() -> bool:
    """Quick system check for startup"""
    try:
        # Just check Python version and dependencies
        python_ok = check_python_version()["status"] != "FAIL"
        deps_ok = check_dependencies()["status"] != "FAIL"
        return python_ok and deps_ok
    except Exception:
        return False

if __name__ == "__main__":
    # Set up basic logging for standalone execution
    logging.basicConfig(level=logging.INFO)
    success = run_doctor()
    sys.exit(0 if success else 1)
