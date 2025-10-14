# Allure TestOps Integration для Cellframe Node QA

**Дата создания**: 2025-01-27  
**Версия**: 1.0  
**Назначение**: Интеграция allurectl с существующей QA системой Cellframe Node

## 📋 Обзор интеграции

Эта интеграция добавляет возможность отправки результатов тестов в Allure TestOps через allurectl, расширяя существующую QA инфраструктуру Cellframe Node.

## 🎯 Что добавлено

### Новые файлы:
1. **allurectl** - CLI приложение для работы с TestOps
2. **allurectl.env** - конфигурация TestOps
3. **run-tests-with-allurectl.sh** - скрипт интеграции
4. **Dockerfile.qa-allurectl** - Docker контейнер с allurectl
5. **.gitlab-ci-allurectl.yml** - пример GitLab CI интеграции
6. **ALLURECTL_INTEGRATION.md** - эта документация

### Расширенные возможности:
- ✅ Отправка результатов в Allure TestOps
- ✅ Интеграция с CI/CD pipeline
- ✅ Централизованная отчетность
- ✅ Аналитика и метрики
- ✅ Командная работа с результатами

## 🚀 Быстрый старт

### 1. Настройка TestOps

#### Создание проекта в TestOps:
1. Зайдите в Allure TestOps
2. Создайте новый проект "Cellframe Node QA"
3. Получите Project ID
4. Создайте API токен в меню пользователя

#### Настройка конфигурации:
```bash
cd qa-tests
cp allurectl.env allurectl.env.local
# Отредактируйте allurectl.env.local с вашими настройками
```

Пример `allurectl.env.local`:
```bash
export ALLURE_ENDPOINT=https://your-testops-instance.com
export ALLURE_TOKEN=your-actual-api-token
export ALLURE_PROJECT_ID=your-project-id
export ALLURE_LAUNCH_NAME="Cellframe Node QA - $(date +%Y-%m-%d_%H-%M)"
export ALLURE_LAUNCH_TAGS="cellframe,node,qa,automated"
```

### 2. Запуск тестов с интеграцией

#### Локальный запуск:
```bash
cd qa-tests
source allurectl.env.local
./run-tests-with-allurectl.sh
```

#### Docker запуск:
```bash
cd qa-tests
docker build -f Dockerfile.qa-allurectl -t cellframe-node-qa-allurectl .
docker run --rm --privileged \
  -e ALLURE_ENDPOINT=https://your-testops-instance.com \
  -e ALLURE_TOKEN=your-token \
  -e ALLURE_PROJECT_ID=your-project-id \
  cellframe-node-qa-allurectl
```

## 🔧 Детальная настройка

### Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `ALLURE_ENDPOINT` | URL вашего TestOps инстанса | ✅ |
| `ALLURE_TOKEN` | API токен для аутентификации | ✅ |
| `ALLURE_PROJECT_ID` | ID проекта в TestOps | ✅ |
| `ALLURE_LAUNCH_NAME` | Название запуска | ❌ |
| `ALLURE_LAUNCH_TAGS` | Теги запуска | ❌ |
| `ALLURE_LAUNCH_DESCRIPTION` | Описание запуска | ❌ |
| `ALLURE_ENVIRONMENT` | Окружение (dev, test, prod) | ❌ |
| `ALLURE_BUILD_NAME` | Название билда | ❌ |

### Типы тестов

#### 1. Pytest тесты (с Allure интеграцией)
```bash
# Запуск только pytest тестов
pytest test_cellframe_qa.py --alluredir=allure-results -v
allurectl upload allure-results
```

#### 2. Функциональные тесты (bash)
```bash
# Запуск функциональных тестов
./test-suite-functional.sh
# Результаты автоматически конвертируются в Allure формат
```

#### 3. Комбинированный запуск
```bash
# Запуск всех тестов
./run-tests-with-allurectl.sh
# Выберите опцию 3 для запуска всех типов тестов
```

## 🐳 Docker интеграция

### Базовый контейнер с allurectl:
```dockerfile
FROM debian:bullseye
# ... установка зависимостей ...
# Установка allurectl
RUN wget -q https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_linux_amd64 -O /usr/local/bin/allurectl && \
    chmod +x /usr/local/bin/allurectl
```

### Запуск с переменными окружения:
```bash
docker run --rm --privileged \
  -e ALLURE_ENDPOINT=https://testops.example.com \
  -e ALLURE_TOKEN=your-token \
  -e ALLURE_PROJECT_ID=100 \
  -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
  cellframe-node-qa-allurectl
```

## 🔄 CI/CD интеграция

### GitLab CI

#### Настройка переменных в GitLab:
1. Перейдите в Settings → CI/CD → Variables
2. Добавьте переменные:
   - `ALLURE_ENDPOINT` (Protected, Masked)
   - `ALLURE_TOKEN` (Protected, Masked)
   - `ALLURE_PROJECT_ID` (Protected)

#### Использование в .gitlab-ci.yml:
```yaml
qa-tests-allurectl:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  variables:
    ALLURE_LAUNCH_NAME: "Cellframe Node QA - $CI_COMMIT_SHORT_SHA"
    ALLURE_LAUNCH_TAGS: "cellframe,node,qa,ci,gitlab"
  script:
    - cd qa-tests
    - docker build -f Dockerfile.qa-allurectl -t cellframe-node-qa-allurectl .
    - docker run --rm --privileged 
        -e ALLURE_ENDPOINT=$ALLURE_ENDPOINT
        -e ALLURE_TOKEN=$ALLURE_TOKEN
        -e ALLURE_PROJECT_ID=$ALLURE_PROJECT_ID
        -e ALLURE_LAUNCH_NAME="$ALLURE_LAUNCH_NAME"
        -e ALLURE_LAUNCH_TAGS="$ALLURE_LAUNCH_TAGS"
        cellframe-node-qa-allurectl
```

### GitHub Actions

```yaml
name: QA Tests with Allure TestOps
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build test container
        run: |
          cd qa-tests
          docker build -f Dockerfile.qa-allurectl -t cellframe-node-qa-allurectl .
      - name: Run tests and upload to TestOps
        env:
          ALLURE_ENDPOINT: ${{ secrets.ALLURE_ENDPOINT }}
          ALLURE_TOKEN: ${{ secrets.ALLURE_TOKEN }}
          ALLURE_PROJECT_ID: ${{ secrets.ALLURE_PROJECT_ID }}
        run: |
          docker run --rm --privileged 
            -e ALLURE_ENDPOINT=$ALLURE_ENDPOINT
            -e ALLURE_TOKEN=$ALLURE_TOKEN
            -e ALLURE_PROJECT_ID=$ALLURE_PROJECT_ID
            -e ALLURE_LAUNCH_NAME="Cellframe Node QA - ${{ github.sha }}"
            -e ALLURE_LAUNCH_TAGS="cellframe,node,qa,github"
            cellframe-node-qa-allurectl
```

## 📊 Результаты и отчеты

### В TestOps вы увидите:

#### 1. Запуски тестов:
- Название запуска с временной меткой
- Статус выполнения (passed/failed)
- Время выполнения
- Теги и описание

#### 2. Детальные результаты:
- Список всех тестов
- Статус каждого теста
- Время выполнения
- Логи и ошибки
- Прикрепленные файлы

#### 3. Аналитика:
- Тренды по времени
- Статистика успешности
- Анализ ошибок
- Покрытие тестами

### Локальные отчеты:
```bash
# Генерация локального отчета
allure generate allure-results -o allure-report --clean

# Просмотр отчета
allure serve allure-results
```

## 🛠️ Troubleshooting

### Частые проблемы:

#### 1. "allurectl: command not found"
```bash
# Убедитесь что allurectl загружен и исполняемый
ls -la allurectl
chmod +x allurectl
```

#### 2. "Authentication failed"
```bash
# Проверьте токен и endpoint
echo $ALLURE_TOKEN
echo $ALLURE_ENDPOINT
```

#### 3. "Project not found"
```bash
# Проверьте Project ID
echo $ALLURE_PROJECT_ID
```

#### 4. "No test results found"
```bash
# Убедитесь что директория allure-results существует и содержит файлы
ls -la allure-results/
```

### Отладка:
```bash
# Запуск с подробным выводом
./allurectl upload allure-results --verbose

# Проверка конфигурации
./allurectl config
```

## 📈 Метрики и KPI

### Ключевые показатели в TestOps:

1. **Стабильность тестов**: % успешных запусков
2. **Скорость выполнения**: время выполнения тестов
3. **Покрытие**: % функциональности покрытой тестами
4. **Время исправления**: от обнаружения до исправления бага

### Дашборды:
- Обзор качества релизов
- Тренды по времени выполнения
- Статистика по типам ошибок
- Покрытие тестами по модулям

## 🔮 Дальнейшее развитие

### Краткосрочные улучшения:
1. Автоматическое создание тест-кейсов
2. Интеграция с системой управления требованиями
3. Настройка уведомлений и алертов

### Долгосрочные планы:
1. Интеграция с системой релизов
2. Автоматическое назначение ответственных
3. Связывание с системой мониторинга

## 📚 Дополнительные ресурсы

### Документация:
- [Allure TestOps Documentation](https://docs.qatools.ru/)
- [allurectl GitHub](https://github.com/allure-framework/allurectl)
- [Allure Framework](https://allurereport.org/)

### Примеры интеграции:
- [GitLab CI Integration](https://docs.qatools.ru/integrations/ci-systems/gitlab)
- [Jenkins Integration](https://docs.qatools.ru/integrations/ci-systems/jenkins)
- [GitHub Actions Integration](https://docs.qatools.ru/integrations/ci-systems/github)

## ✅ Чеклист внедрения

### Подготовка:
- [ ] Создан проект в TestOps
- [ ] Получен API токен
- [ ] Настроен файл allurectl.env
- [ ] Установлен allurectl

### Тестирование:
- [ ] Локальный запуск прошел успешно
- [ ] Результаты появились в TestOps
- [ ] Docker контейнер работает
- [ ] CI/CD интеграция настроена

### Production:
- [ ] Настроены переменные в CI/CD
- [ ] Команда обучена работе с TestOps
- [ ] Настроены дашборды и алерты
- [ ] Документация обновлена

## 📞 Поддержка

### Если что-то не работает:

1. **Проверьте конфигурацию**:
   ```bash
   source allurectl.env
   echo $ALLURE_ENDPOINT
   echo $ALLURE_TOKEN
   echo $ALLURE_PROJECT_ID
   ```

2. **Проверьте логи**:
   ```bash
   ./allurectl upload allure-results --verbose
   ```

3. **Изучите документацию**:
   - [Allure TestOps Docs](https://docs.qatools.ru/)
   - [allurectl GitHub](https://github.com/allure-framework/allurectl)

4. **Свяжитесь с командой**:
   - GitLab Issues
   - Telegram: t.me/cellframe_dev_en

---

**Создано**: 2025-01-27  
**Версия**: 1.0  
**Статус**: ✅ Ready for use

**Интеграция готова к использованию!** 🚀




