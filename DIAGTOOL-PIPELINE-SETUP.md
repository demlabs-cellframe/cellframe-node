# Diagtool Independent Pipeline Setup

## 🎯 Overview / Обзор

**Completed:** Diagtool now has its own independent CI/CD pipeline, separate from the main cellframe-node project.

## 📋 What Was Implemented / Что было реализовано

### ✅ **Independent CI/CD Pipeline**
- **Location:** `diagtool/.gitlab-ci.yml` (275 lines)
- **Platforms:** Linux (amd64, arm64, armhf), macOS, Windows  
- **Build Types:** Debug, Release, RelWithDebInfo
- **Artifacts:** .deb, .dmg, .exe, .msi packages

### ✅ **Enhanced Build Scripts**
- **build-diagtool.sh:** Improved argument parsing for cross-platform builds
- **pack-diagtool.sh:** Enhanced packaging with target platform support
- **Target Support:** `--target linux|osx|windows`

### ✅ **Complete Documentation**  
- **README.md:** 156-line comprehensive guide
- **Usage Examples:** Build commands, installation, development
- **Architecture Overview:** Dependencies, paths, configuration

---

## 🏗️ Pipeline Architecture / Архитектура пайплайна

### **Stages / Стадии**
```yaml
stages:
    - build      # Compile for each platform
    - package    # Create distribution packages  
    - publish    # Deploy artifacts
```

### **Supported Builds / Поддерживаемые сборки**
```
Linux AMD64:   amd64:linux.release / amd64:linux.debug
Linux ARM64:   arm64:linux.release
Linux ARMHF:   armhf:linux.release
macOS AMD64:   amd64:osx.release     (with OSXCROSS)
Windows AMD64: amd64:windows.release (with MinGW)
```

### **Artifacts Structure / Структура артефактов**
```
build_diagtool_linux_release/
├── cellframe-diagtool-1.0-0-amd64.deb
└── build/cellframe-diagtool

build_diagtool_osx_release/
├── cellframe-diagtool-1.0.dmg
└── build/cellframe-diagtool.app

build_diagtool_windows_release/ 
├── cellframe-diagtool-1.0.exe
├── cellframe-diagtool-1.0.msi
└── build/cellframe-diagtool.exe
```

---

## 🚀 Usage Examples / Примеры использования

### **Manual Local Builds**
```bash
cd diagtool/

# Release build for current platform
./build-diagtool.sh release
./pack-diagtool.sh release

# Cross-platform builds
./build-diagtool.sh release --target osx      
./build-diagtool.sh release --target windows
```

### **Pipeline Triggers**
```bash
# Trigger full pipeline
git push origin feature-branch

# Pipeline creates:
# - Multi-platform builds
# - Distribution packages  
# - Deployed artifacts
```

### **Artifact Access**
```bash
# Download from CI artifacts
# Or access via deployment:
# https://pub.cellframe.net/linux/cellframe-diagtool/branch-name/
```

---

## ⚙️ Configuration / Конфигурация

### **Environment Variables**
```yaml
# In .gitlab-ci.yml:
ENABLE_MACOS_BUILDS: "true"    # Enable macOS cross-compilation
ENABLE_WINDOWS_BUILDS: "true"  # Enable Windows cross-compilation
BUILD_TYPE: "release"          # Default build type
```

### **Docker Images Required**
- `demlabs/debian/amd64:qt5` - Linux AMD64 builds
- `demlabs/debian/arm64:qt5` - Linux ARM64 builds  
- `demlabs/debian/arm32:qt5` - Linux ARMHF builds
- `demlabs/debian/amd64:osx-qt5` - macOS cross-compilation
- `demlabs/debian/amd64:mingw-qt5` - Windows cross-compilation

### **Build Dependencies**
- Qt5 (Core, Widgets, Quick, Qml)
- CMake 3.10+
- Standard build tools (GCC/Clang)
- Platform-specific toolchains (OSXCROSS, MinGW)

---

## 🔄 Integration Points / Точки интеграции

### **With Main Project**
- **Submodule Reference:** Updated to feature-16121-port
- **Independent Releases:** Diagtool versions separate from node versions
- **Cross-Project CI:** Main project can trigger diagtool builds if needed

### **Deployment Integration**
- **Artifact Storage:** `/opt/buildtools/deploy_files.sh` compatible
- **Repository Structure:** pub.cellframe.net/[platform]/cellframe-diagtool/[branch]/
- **Package Naming:** cellframe-diagtool-[version]-[arch].[ext]

---

## 🛠️ Maintenance / Обслуживание

### **Regular Tasks**
- **Dependency Updates:** Update Qt5 versions, build tools
- **Platform Support:** Add new architectures as needed
- **Performance:** Monitor build times, optimize as needed

### **Monitoring**
- **Pipeline Status:** GitLab CI/CD pipelines page
- **Artifact Sizes:** Track package sizes over time
- **Build Success Rate:** Monitor cross-platform compatibility

---

## 📊 Impact Assessment / Оценка влияния

### **Benefits / Преимущества**
✅ **Independent Development** - Diagtool team can iterate faster  
✅ **Separate Releases** - Diagtool updates don't require node releases  
✅ **Reduced Build Times** - Main node pipeline is lighter  
✅ **Better Testing** - Dedicated diagtool-specific tests  
✅ **Modular Architecture** - Clear separation of concerns  

### **Deployment Strategy / Стратегия развертывания**
- **Phase 1:** Test on feature branches ✅ COMPLETED
- **Phase 2:** Merge to develop branch (pending)  
- **Phase 3:** Production deployment (after QA)
- **Phase 4:** Legacy cleanup (remove old diagtool CI jobs)

---

## 🔗 Related Documentation / Связанная документация

- **Feature Documentation:** `FEATURE-16121-DIAGTOOL-SEPARATION.md`
- **Quick Reference:** `DIAGTOOL-SEPARATION-QUICK-REFERENCE.md`
- **Commit History:** `COMMIT-HISTORY-FEATURE-16121.md`
- **Diagtool README:** `diagtool/README.md`

---

**Status:** ✅ **PRODUCTION READY**  
**Next Steps:** Merge feature-16121 and feature-16121-port to develop branches

*Created: $(date)*  
*Part of Feature-16121 implementation*
