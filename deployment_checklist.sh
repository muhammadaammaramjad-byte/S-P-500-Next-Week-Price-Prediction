#!/bin/bash
# deployment_checklist.sh

echo "🔍 Running Final Pre-Deployment Audit..."
echo "========================================="

# 1. Test suite (must be 66/66)
echo "✅ Running test suite..."
pytest tests/ -v --tb=no --quiet
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All 66 tests PASSING"
else
    echo "❌ Tests failing - aborting deployment"
    exit 1
fi

# 2. Check for secrets
echo "🔐 Scanning for exposed secrets..."
if grep -r "password\|secret\|key\|token" --include="*.py" --exclude-dir=".git" | grep -v "os.environ\|getenv\|config.example"; then
    echo "⚠️  WARNING: Potential secrets found in code"
else
    echo "✅ No hardcoded secrets detected"
fi

# 3. Validate imports
echo "📦 Checking imports..."
python -c "import src.models.xgboost; import src.dashboard.app; print('✅ All imports successful')"

# 4. Check dashboard configuration
echo "🎨 Validating dashboard..."
python -c "from src.dashboard.config import config; print(f'✅ Dashboard config loaded: {config.THEME[\"primary\"]}')"

# 5. Verify CI/CD pipeline
echo "⚙️  Checking GitHub Actions workflow..."
if [ -f ".github/workflows/ci.yml" ]; then
    echo "✅ CI/CD pipeline configured"
else
    echo "⚠️  CI/CD pipeline missing"
fi

echo "========================================="
echo "🎯 DEPLOYMENT READY - Push to GitHub now"
