# View-from-CSV v4.5 Setup Script for Windows
# This script sets up the Python environment and installs dependencies

param(
    [switch]$Force,
    [switch]$SkipDoctor
)

Write-Host "View-from-CSV v4.5 Setup Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "✗ Python not found or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check Python version
$pythonVersionOutput = python --version 2>&1
if ($pythonVersionOutput -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        Write-Host "✗ Python version too old: $major.$minor" -ForegroundColor Red
        Write-Host "Required: Python 3.10+" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✓ Python version OK: $major.$minor" -ForegroundColor Green
} else {
    Write-Host "⚠ Could not determine Python version" -ForegroundColor Yellow
}

# Create virtual environment
$venvPath = "venv"
if (Test-Path $venvPath) {
    if ($Force) {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath
    } else {
        Write-Host "Virtual environment already exists. Use -Force to recreate." -ForegroundColor Yellow
        $useExisting = Read-Host "Use existing? (y/N)"
        if ($useExisting -ne "y" -and $useExisting -ne "Y") {
            exit 0
        }
    }
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Failed to upgrade pip, continuing..." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Install Playwright browsers
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install Playwright browsers" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Playwright browsers installed" -ForegroundColor Green

# Create configuration directory
Write-Host "Setting up configuration..." -ForegroundColor Yellow
$configDir = "..\x987-config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "✓ Configuration directory created" -ForegroundColor Green
} else {
    Write-Host "✓ Configuration directory exists" -ForegroundColor Green
}

# Create data directory
$dataDir = "..\x987-data"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    Write-Host "✓ Data directory created" -ForegroundColor Green
} else {
    Write-Host "✓ Data directory exists" -ForegroundColor Green
}

# Run doctor check
if (-not $SkipDoctor) {
    Write-Host "Running system diagnostics..." -ForegroundColor Yellow
    python -m x987 doctor
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ System diagnostics passed" -ForegroundColor Green
    } else {
        Write-Host "⚠ System diagnostics had issues" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To use the application:" -ForegroundColor Cyan
Write-Host "1. Activate the virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Run the application: python -m x987" -ForegroundColor White
Write-Host "3. Or run specific commands: python -m x987 doctor" -ForegroundColor White
Write-Host ""
Write-Host "Configuration file: $configDir\config.toml" -ForegroundColor Cyan
Write-Host "Data output: $dataDir" -ForegroundColor Cyan
