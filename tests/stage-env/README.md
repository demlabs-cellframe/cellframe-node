# Stage Environment - Cellframe Node Testing Infrastructure

**Autonomous E2E testing system for blockchain applications**

---

## 📖 Documentation / Документация

Choose your language / Выберите язык:

### 🇬🇧 English
- **[README](docs/en/README.md)** - Main documentation
- **[Tutorial](docs/en/scenarios/Tutorial.md)** - Step-by-step guide for QA engineers
- **[Cookbook](docs/en/scenarios/Cookbook.md)** - Ready recipes for common tasks
- **[Glossary](docs/en/scenarios/Glossary.md)** - Complete language reference

### 🇷🇺 Русский
- **[README](docs/ru/README.md)** - Основная документация
- **[Tutorial](docs/ru/scenarios/Tutorial.md)** - Пошаговое руководство для QA инженеров
- **[Cookbook](docs/ru/scenarios/Cookbook.md)** - Готовые рецепты для типовых задач
- **[Glossary](docs/ru/scenarios/Glossary.md)** - Полный справочник языка

---

## 🚀 Quick Start

```bash
# Start test network
cd tests
./stage-env/stage-env start

# Run tests
./stage-env/stage-env run-tests scenarios/

# Stop
./stage-env/stage-env stop
```

## 🎯 Features

- ✅ YAML-based test scenarios (no programming required)
- ✅ Docker-isolated test environment
- ✅ Flexible network topologies
- ✅ Automatic artifacts collection & PDF reports
- ✅ Rich CLI with colored output

## 📦 What's Inside

```
stage-env/
├── docs/
│   ├── en/          # English documentation
│   └── ru/          # Russian documentation
├── scenarios/       # Test scenarios
│   ├── common/      # Reusable templates
│   └── features/    # Feature tests
├── src/             # Python source code
└── config/          # Configuration files
```

## 🔗 Links

- [Cellframe Node](https://github.com/demlabs-cellframe/cellframe-node)
- [DAP SDK](https://github.com/demlabs-cellframe/dap-sdk)
- [Python Cellframe](https://github.com/demlabs-cellframe/python-cellframe)

---

**Choose your language above to read full documentation**
