#!/bin/bash

# 🚀 Скрипт быстрого развертывания на GitHub

echo "🚀 YouTube Comment Analyzer - Quick Deploy Script"
echo "=================================================="

# Проверяем, что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the backend directory."
    exit 1
fi

# Проверяем наличие .env.local (с реальными ключами)
if [ ! -f ".env.local" ]; then
    echo "❌ Error: .env.local not found. Please create it with your API keys."
    exit 1
fi

# Проверяем, что .env.local не будет загружен в Git
if ! grep -q ".env.local" .gitignore; then
    echo "❌ Error: .env.local is not in .gitignore. This is unsafe!"
    exit 1
fi

echo "✅ Safety checks passed"

# Инициализируем Git если нужно
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git branch -M main
fi

# Добавляем все файлы (кроме исключенных в .gitignore)
echo "📦 Adding files to Git..."
git add .

# Проверяем, что .env.local не добавлен
if git status --porcelain | grep -q ".env.local"; then
    echo "❌ DANGER: .env.local is being added to Git! Aborting."
    git reset
    exit 1
fi

echo "✅ .env.local is safely excluded from Git"

# Коммитим изменения
echo "💾 Committing changes..."
git commit -m "🚀 Ready for deployment: YouTube Comment Analyzer

✅ API keys secured (not in repository)
✅ Environment variables configured for Render
✅ All dependencies listed in requirements.txt
✅ Health checks and monitoring endpoints ready
✅ Documentation updated

Deploy instructions: See DEPLOY_COMPLETE_GUIDE.md"

echo ""
echo "🎯 NEXT STEPS:"
echo "1. Create GitHub repository: https://github.com/new"
echo "2. Add remote: git remote add origin https://github.com/YOUR_USERNAME/youtube-comment-analyzer.git"
echo "3. Push code: git push -u origin main"
echo "4. Deploy on Render: https://render.com/"
echo "5. Add environment variables in Render dashboard"
echo ""
echo "📖 Full instructions: See DEPLOY_COMPLETE_GUIDE.md"
echo ""
echo "✅ Your project is ready for safe deployment!"
