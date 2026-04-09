#!/bin/bash
# startup.sh - Quick start script for the project

echo "🚀 RetailCRM Orders Integration System - Startup"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env not found!${NC}"
    echo "Creating from example..."
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}📝 Please edit backend/.env with your credentials${NC}"
    echo ""
fi

# Check if frontend .env exists (optional)
if [ ! -f "frontend/.env" ]; then
    echo "Creating frontend/.env from example..."
    cp frontend/.env.example frontend/.env
fi

echo -e "${GREEN}✓ Configuration files ready${NC}"
echo ""

echo "📦 Next steps:"
echo ""
echo "1. Edit backend/.env with your credentials:"
echo "   vim backend/.env"
echo ""
echo "2. Terminal 1 - Start Backend:"
echo "   cd backend"
echo "   pip install -r requirements.txt"
echo "   python app.py"
echo ""
echo "3. Terminal 2 - Start Frontend:"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "4. Open browser:"
echo "   http://localhost:3000"
echo ""
echo -e "${GREEN}Good luck! 🎉${NC}"
