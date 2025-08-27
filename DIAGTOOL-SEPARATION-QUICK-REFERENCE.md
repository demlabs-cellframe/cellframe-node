# Quick Reference: Diagtool Separation (Feature 16121)

## 🎯 What Was Done / Что было сделано

**BEFORE:** diagtool was part of cellframe-node package  
**NOW:** diagtool is a separate independent package

## 📦 Package Structure / Структура пакетов

### cellframe-node (Main Package)
```
/opt/cellframe-node/bin/cellframe-node
/opt/cellframe-node/bin/cellframe-node-cli  
/opt/cellframe-node/bin/cellframe-node-tool
```

### cellframe-diagtool (New Separate Package)
```  
/opt/cellframe-tools/bin/cellframe-diagtool
/opt/cellframe-tools/share/cellframe-diagtool.service
/opt/cellframe-tools/share/cellframe-tray.service
/opt/cellframe-tools/bin/install.sh
```

## 🚀 How to Build / Как собрать

### Main Node (without diagtool)
```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

### Diagtool (standalone)
```bash
cd diagtool
./build-diagtool.sh release
./pack-diagtool.sh release
# Result: build_diagtool_linux_release/cellframe-diagtool-1.0-0-amd64.deb
```

## 🔄 How to Rollback / Как откатить
```bash
git checkout develop
git submodule update --init --recursive
# OR revert commits: dd8776b2, 16c1e307, etc.
```

## 🌳 Branches / Ветки
- **Main repo:** `feature-16121` 
- **diagtool submodule:** `feature-16121-port`
- **prod_build submodule:** `feature-16121`

## ✅ Status / Статус
**Ready for merge to develop** - All tests passed, all platforms supported

## 📋 Key Changes / Основные изменения
- ❌ Removed diagtool from CMakeLists.txt
- ➕ Added standalone build system for diagtool  
- 🔧 Updated CI/CD with separate diagtool jobs
- 📦 Modified all platform installers (Linux/macOS/Windows)
- 🔀 Moved service files to diagtool package

See `FEATURE-16121-DIAGTOOL-SEPARATION.md` for complete documentation.
