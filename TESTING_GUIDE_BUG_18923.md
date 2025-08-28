# 🧪 Инструкция для тестирования исправления бага #18923

## 📋 Описание бага
**Проблема:** На macOS при отключении сетей путем добавления `.dis` к названию конфига появлялись дублирующие файлы (`raiden.cfg` И `raiden.cfg.dis`), из-за чего сеть продолжала работать вместо отключения.

**Исправление:** Добавлена защита от дублирования в процессе установки и улучшена логика обработки конфигов.

---

## 🎯 Цель тестирования
Убедиться, что после установки исправленной версии:
1. ✅ Ручное отключение сетей работает корректно
2. ✅ Не создаются дублирующие конфигурационные файлы
3. ✅ Пользовательские настройки сохраняются при обновлении

---

## 🔧 Подготовка к тестированию

### Системные требования
- **ОС:** macOS 10.15+ (Catalina или новее)
- **Права:** Администратор системы
- **Место на диске:** ~500 MB свободного места

### Инструменты для тестирования
```bash
# Откройте Terminal.app и подготовьте команды:
ls -la "/Library/Application Support/CellframeNode/etc/network/"
/Applications/CellframeNode.app/Contents/MacOS/cellframe-node-cli
```

---

## 📦 Получение исправленной версии

### Вариант 1: Сборка из исходников (для разработчиков)
```bash
# Клонировать репозиторий
git clone https://gitlab.demlabs.net/cellframe/cellframe-node.git
cd cellframe-node

# Переключиться на ветку с исправлением
git checkout bugfix-18923

# Следовать стандартной процедуре сборки для macOS
```

### Вариант 2: Получить готовую сборку
- Запросить у команды разработки тестовую сборку с ветки `bugfix-18923`
- Скачать установочный пакет `.pkg` для macOS

---

## 🔄 Сценарии тестирования

## **ТЕСТ 1: Чистая установка**

### Шаг 1: Подготовка
```bash
# Полностью удалить существующую установку (если есть)
sudo launchctl unload /Library/LaunchDaemons/com.demlabs.cellframe-node.plist 2>/dev/null || true
sudo rm -rf /Applications/CellframeNode.app
sudo rm -rf "/Library/Application Support/CellframeNode"
sudo rm -f /Library/LaunchDaemons/com.demlabs.cellframe-node.plist
sudo rm -f /Library/LaunchDaemons/com.demlabs.cellframe-diagtool.plist
```

### Шаг 2: Установка исправленной версии
1. Запустить установочный пакет `.pkg`
2. Следовать инструкциям установщика
3. Дождаться завершения установки

### Шаг 3: Проверка начального состояния
```bash
# Проверить какие сети включены по умолчанию
ls -la "/Library/Application Support/CellframeNode/etc/network/"
```

**Ожидаемый результат:**
```
Backbone.cfg        <- включена
KelVPN.cfg          <- включена  
raiden.cfg.dis      <- отключена
riemann.cfg.dis     <- отключена
subzero.cfg.dis     <- отключена
```

### Шаг 4: Проверка запуска ноды
```bash
# Проверить что нода запущена
ps aux | grep cellframe-node

# Подключиться к CLI и проверить активные сети
/Applications/CellframeNode.app/Contents/MacOS/cellframe-node-cli
```

В CLI выполнить:
```
net list
```

**Ожидаемый результат:** Должны отображаться только `Backbone` и `KelVPN`

### ✅ **ТЕСТ 1 ПРОШЕЛ:** Только включенные сети работают, отключенные не загружаются

---

## **ТЕСТ 2: Ручное отключение сети**

### Шаг 1: Отключить включенную сеть
```bash
cd "/Library/Application Support/CellframeNode/etc/network/"

# Отключить KelVPN добавлением .dis
mv KelVPN.cfg KelVPN.cfg.dis

# Проверить что получилось
ls -la
```

**Ожидаемый результат:**
```
Backbone.cfg        <- включена
KelVPN.cfg.dis      <- отключена ✓
raiden.cfg.dis      <- отключена
riemann.cfg.dis     <- отключена
subzero.cfg.dis     <- отключена
```

### Шаг 2: Перезапустить ноду
```bash
# Перезапустить службу
sudo launchctl unload /Library/LaunchDaemons/com.demlabs.cellframe-node.plist
sudo launchctl load /Library/LaunchDaemons/com.demlabs.cellframe-node.plist

# Подождать 5 секунд для запуска
sleep 5
```

### Шаг 3: Проверить результат
```bash
# Подключиться к CLI
/Applications/CellframeNode.app/Contents/MacOS/cellframe-node-cli
```

В CLI выполнить:
```
net list
```

**Ожидаемый результат:** Должна отображаться только сеть `Backbone` (KelVPN должна исчезнуть)

### ✅ **ТЕСТ 2 ПРОШЕЛ:** Ручное отключение сети работает корректно

---

## **ТЕСТ 3: Ручное включение сети**

### Шаг 1: Включить отключенную сеть
```bash
cd "/Library/Application Support/CellframeNode/etc/network/"

# Включить raiden убиранием .dis
mv raiden.cfg.dis raiden.cfg

# Проверить что получилось
ls -la
```

**Ожидаемый результат:**
```
Backbone.cfg        <- включена
KelVPN.cfg.dis      <- отключена
raiden.cfg          <- включена ✓
riemann.cfg.dis     <- отключена
subzero.cfg.dis     <- отключена
```

### Шаг 2: Перезапустить ноду
```bash
# Перезапустить службу
sudo launchctl unload /Library/LaunchDaemons/com.demlabs.cellframe-node.plist
sudo launchctl load /Library/LaunchDaemons/com.demlabs.cellframe-node.plist

# Подождать 5 секунд для запуска
sleep 5
```

### Шаг 3: Проверить результат
```bash
# Подключиться к CLI
/Applications/CellframeNode.app/Contents/MacOS/cellframe-node-cli
```

В CLI выполнить:
```
net list
```

**Ожидаемый результат:** Должны отображаться сети `Backbone` и `raiden`

### ✅ **ТЕСТ 3 ПРОШЕЛ:** Ручное включение сети работает корректно

---

## **ТЕСТ 4: Проверка отсутствия дублирования (основной тест бага)**

### Шаг 1: Создать проблемную ситуацию
```bash
cd "/Library/Application Support/CellframeNode/etc/network/"

# Убедиться что raiden включена
ls -la raiden.*

# Если raiden.cfg не существует, создать:
if [ ! -f "raiden.cfg" ]; then
    cp raiden.cfg.dis raiden.cfg 2>/dev/null || echo "Файл raiden.cfg.dis не найден"
fi
```

### Шаг 2: Имитировать переустановку (критический момент)
```bash
# Остановить ноду
sudo launchctl unload /Library/LaunchDaemons/com.demlabs.cellframe-node.plist

# Запустить конфигурационный инструмент (имитация postinstall)
/Applications/CellframeNode.app/Contents/MacOS/cellframe-node-config -i "/Library/Application Support/CellframeNode/share/default.setup" -v
```

### Шаг 3: Проверить отсутствие дублей
```bash
# Проверить файлы raiden
ls -la "/Library/Application Support/CellframeNode/etc/network/"raiden.*
```

**Ожидаемый результат (ИСПРАВЛЕНО):**
```
raiden.cfg          <- ТОЛЬКО ОДИН файл, пользовательская настройка сохранена
```

**НЕ должно быть:**
```
raiden.cfg          <- ❌ дубль
raiden.cfg.dis      <- ❌ дубль  
```

### Шаг 4: Проверить функциональность
```bash
# Запустить ноду
sudo launchctl load /Library/LaunchDaemons/com.demlabs.cellframe-node.plist
sleep 5

# Проверить что raiden работает
/Applications/CellframeNode.app/Contents/MacOS/cellframe-node-cli
```

В CLI:
```
net list
```

**Ожидаемый результат:** raiden должна быть в списке активных сетей

### ✅ **ТЕСТ 4 ПРОШЕЛ:** Дублирование файлов устранено, пользовательские настройки сохранены

---

## **ТЕСТ 5: Проверка обновления с сохранением пользовательских настроек**

### Шаг 1: Настроить пользовательскую конфигурацию
```bash
cd "/Library/Application Support/CellframeNode/etc/network/"

# Включить riemann, отключить Backbone
mv riemann.cfg.dis riemann.cfg
mv Backbone.cfg Backbone.cfg.dis

# Проверить текущее состояние
ls -la *.cfg*
```

### Шаг 2: Сохранить эталонное состояние
```bash
# Запомнить какие сети включены
find "/Library/Application Support/CellframeNode/etc/network/" -name "*.cfg" ! -name "*.dis" -exec basename {} .cfg \;
```

### Шаг 3: Имитировать обновление системы
```bash
# Остановить ноду
sudo launchctl unload /Library/LaunchDaemons/com.demlabs.cellframe-node.plist

# Запустить процедуру "обновления" (postinstall script логика)
/Applications/CellframeNode.app/Contents/MacOS/cellframe-node-config -i "/Library/Application Support/CellframeNode/share/default.setup" -v
```

### Шаг 4: Проверить сохранение настроек
```bash
# Проверить что пользовательские настройки сохранились
ls -la "/Library/Application Support/CellframeNode/etc/network/"*.cfg*

# Проверить отсутствие дублей
for net in Backbone KelVPN raiden riemann subzero; do
    echo "=== $net ==="
    ls -la "/Library/Application Support/CellframeNode/etc/network/"$net.* 2>/dev/null || echo "Файлы не найдены"
done
```

**Ожидаемый результат:**
- ✅ Пользовательские настройки (riemann.cfg, Backbone.cfg.dis) сохранены
- ✅ Нет дублирующих файлов
- ✅ Логика по умолчанию не перезаписала пользовательские изменения

### ✅ **ТЕСТ 5 ПРОШЕЛ:** Обновление корректно сохраняет пользовательские настройки

---

## 📊 Отчет о тестировании

### Заполните после каждого теста:

| Тест | Статус | Комментарии |
|------|--------|-------------|
| **ТЕСТ 1:** Чистая установка | ☐ ПРОШЕЛ / ☐ ПРОВАЛЕН | |
| **ТЕСТ 2:** Ручное отключение | ☐ ПРОШЕЛ / ☐ ПРОВАЛЕН | |
| **ТЕСТ 3:** Ручное включение | ☐ ПРОШЕЛ / ☐ ПРОВАЛЕН | |
| **ТЕСТ 4:** Отсутствие дублей | ☐ ПРОШЕЛ / ☐ ПРОВАЛЕН | |
| **ТЕСТ 5:** Сохранение настроек | ☐ ПРОШЕЛ / ☐ ПРОВАЛЕН | |

### 🎯 **Критерии успешного тестирования:**
- ✅ Все 5 тестов пройдены
- ✅ Отсутствуют дублирующие файлы `.cfg` и `.cfg.dis`
- ✅ Ручное управление сетями работает как ожидается
- ✅ Пользовательские настройки сохраняются при обновлении

---

## 🆘 Что делать при обнаружении проблем

### Если тест провалился:
1. **Сделать скриншот** ошибки
2. **Сохранить логи:**
   ```bash
   # Системные логи
   tail -100 /var/log/system.log > ~/cellframe_system.log
   
   # Состояние файлов
   ls -la "/Library/Application Support/CellframeNode/etc/network/" > ~/cellframe_files.log
   ```
3. **Описать шаги** которые привели к проблеме
4. **Отправить отчет** команде разработки с указанием:
   - Номер теста
   - Версия macOS
   - Полученный результат vs ожидаемый
   - Приложенные логи и скриншоты

### Контакты для отчетов:
- **GitLab Issue:** https://gitlab.demlabs.net/cellframe/cellframe-node/-/issues/18923
- **Ветка с исправлением:** `bugfix-18923`

---

## 🎉 Заключение

Если все тесты пройдены успешно, это означает, что:
- ✅ **Баг #18923 исправлен**
- ✅ **Ручная корректировка сетей работает корректно**
- ✅ **Дублирование конфигов устранено**
- ✅ **Система готова к production развертыванию**

**Версия:** bug fix для issue #18923  
**Дата:** $(date)  
**Тестировщик:** _[Укажите ваше имя]_
