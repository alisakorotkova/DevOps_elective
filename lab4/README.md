# Лабораторная работа 4 (базовый-трек)

## Ход выполнения

### Часть 1

**Bad CI/CD**

1. Setup
2. Lint
3. Test
4. Build
5. Deploy



**Good CI/CD**

1. Validate
2. Lint
3. Test
4. Build
5. Deploy



#### БЭД practice 1 - secrets

```yaml
env:
  API_KEY: "hardcoded-secret-key-12345"
  SERVER_PASSWORD: "prod_password"
```

**Почему плохо:**
- секретные ключи и пароли хранятся прямо в CI/CD файле
- любой, кто имеет доступ к репозиторию, может их увидеть
- при изменении секрета нужно менять код в репозитории
- это небезопасно

**ГУД файл:**

```yaml
env:
  API_KEY: ${{ secrets.DEPLOY_API_KEY }}
  SERVER_PASSWORD: ${{ secrets.SERVER_PASSWORD }}
```

**Влияние:**
- секреты хранятся в настройках GitHub и не записаны напрямую в репозитории
- секреты доступны только во время выполнения pipeline
- можно изменить секреты без изменения кода
- повышается безопасность


#### БЭД practice 2 - floating versions

```yaml
runs-on: ubuntu-latest

with:
  python-version: "3.x"
```

**Почему плохо:**
- `ubuntu-latest` может со временем начать указывать на другую версию Ubuntu
- `python-version: "3.x"` может выбрать новую версию Python
- pipeline может неожиданно сломаться после обновления окружения
- результат сборки становится менее предсказуемым

**ГУД файл:**

```yaml
runs-on: ubuntu-24.04

with:
  python-version: "3.12"
```

**Влияние:**
- используется конкретная версия Ubuntu и Python
- pipeline становится стабильнее
- результат выполнения легче повторить


#### БЭД practice 3 - unpinned dependencies

```bash
pip install pytest flake8
```

**Почему плохо:**
- устанавливаются последние доступные версии библиотек
- новая версия библиотеки может сломать pipeline
- сложно понять, с какими версиями проект точно работал

**ГУД файл:**

```bash
python -m pip install -r requirements.txt
```

Файл `requirements.txt`:

```text
pytest==8.3.4
flake8==7.1.1
```

**Влияние:**
- зависимости зафиксированы
- pipeline становится более предсказуемым
- проще воспроизвести сборку локально и на GitHub
- меньше риск случайной поломки из-за обновления библиотек


#### БЭД practice 4 - ignoring errors

```yaml
continue-on-error: true
```

```bash
flake8 app.py tests || true
pytest || true
```

**Почему плохо:**
- pipeline может быть зеленым, даже если есть ошибки
- ошибки линтера игнорируются
- ошибки тестов игнорируются
- можно случайно отправить нерабочий код дальше в build или deploy

**ГУД файл:**

```bash
flake8 app.py tests
pytest
```

**Влияние:**
- если линтер находит ошибку, pipeline падает
- если тесты не проходят, pipeline падает
- некачественный код не проходит дальше


#### БЭД practice 5 - deploy from any branch or pull request

```yaml
on:
  push:
  pull_request:
```

```yaml
deploy:
  name: 5. Deploy
  runs-on: ubuntu-latest
  needs: build
```

**Почему плохо:**
- deploy запускается после push в любую ветку
- deploy запускается даже для pull request
- можно случайно выполнить deploy из тестовой ветки
- нет контроля, откуда разрешен deploy

**ГУД файл:**

```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
```

```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**Влияние:**
- deploy запускается только при push в ветку `main`
- pull request может пройти проверки, но не запускает deploy
- снижается риск случайного deploy
- процесс становится безопаснее и контролируемее

