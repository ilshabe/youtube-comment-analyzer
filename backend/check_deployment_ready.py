#!/usr/bin/env python3
"""
🔍 Скрипт проверки готовности к развертыванию
Проверяет все необходимые файлы и конфигурации
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Проверяет существование файла"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - НЕ НАЙДЕН")
        return False

def check_env_safety():
    """Проверяет безопасность переменных окружения"""
    print("\n🔐 ПРОВЕРКА БЕЗОПАСНОСТИ:")
    
    # Проверяем .gitignore
    gitignore_path = ".gitignore"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
            
        if ".env.local" in gitignore_content:
            print("✅ .env.local исключен из Git")
        else:
            print("❌ .env.local НЕ исключен из Git - ОПАСНО!")
            return False
    
    # Проверяем наличие .env.local с реальными ключами
    if os.path.exists(".env.local"):
        print("✅ .env.local найден (содержит реальные ключи)")
    else:
        print("⚠️  .env.local не найден - создайте его с вашими API ключами")
    
    return True

def check_dependencies():
    """Проверяет зависимости"""
    print("\n📦 ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
    
    required_files = [
        ("requirements.txt", "Список зависимостей Python"),
        ("main.py", "Главный файл приложения"),
        ("sentiment_analyzer.py", "Модуль анализа тональности"),
        ("keyword_extractor.py", "Модуль извлечения ключевых слов"),
        ("youtube_service.py", "Сервис YouTube API"),
        ("gemini_service.py", "Сервис Gemini AI")
    ]
    
    all_good = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def check_deployment_files():
    """Проверяет файлы для развертывания"""
    print("\n🚀 ПРОВЕРКА ФАЙЛОВ РАЗВЕРТЫВАНИЯ:")
    
    deployment_files = [
        ("Procfile", "Файл конфигурации Render"),
        ("render.yaml", "Конфигурация сервиса Render"),
        (".env.example", "Пример переменных окружения"),
        ("DEPLOY_COMPLETE_GUIDE.md", "Руководство по развертыванию"),
        ("start.sh", "Скрипт запуска продакшена")
    ]
    
    all_good = True
    for filepath, description in deployment_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def main():
    """Основная функция проверки"""
    print("🔍 ПРОВЕРКА ГОТОВНОСТИ К РАЗВЕРТЫВАНИЮ")
    print("=" * 50)
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists("main.py"):
        print("❌ Запустите скрипт из директории backend/")
        sys.exit(1)
    
    all_checks_passed = True
    
    # Выполняем все проверки
    all_checks_passed &= check_dependencies()
    all_checks_passed &= check_deployment_files()
    all_checks_passed &= check_env_safety()
    
    print("\n" + "=" * 50)
    
    if all_checks_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("✅ Проект готов к безопасному развертыванию")
        print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Создайте репозиторий на GitHub")
        print("2. Выполните: git init && git add . && git commit -m 'Initial commit'")
        print("3. Загрузите код: git push origin main")
        print("4. Разверните на Render согласно DEPLOY_COMPLETE_GUIDE.md")
        print("5. Добавьте переменные окружения в панели Render")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ!")
        print("🔧 Исправьте указанные выше ошибки перед развертыванием")
        sys.exit(1)

if __name__ == "__main__":
    main()
