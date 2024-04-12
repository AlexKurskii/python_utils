Репозиторий для хранения утилитных скриптов. Каждая директория предполагает отдельный скрипт.

1. [git_util](#git_util)

## git_util

Скрипт **git_util/git.py** массово во всех репозиториях указанной директории делает переход на ветку master и обновляет из репозитория, выполняя команду `git pull`.
В случае, если есть незакомиченные изменения, то такой репозиторий пропускается (выводится только список изменений с помощью `git status -s`).
По каждому обновлённому репозиторию в логи выводится запись о выполненных командах и указанием старой ветки, если она отличалась от master.

### Параметры скрипта

Скрипт имеет следующие параметры:

|Имя параметра|Описание|
|---|---|
|-p или --path|Обязательный параметр с указанием пути до директории, в которой расположены репозитории|
|-i или --ignore|Имена директорий, которые не требуется обрабатывать (параметр допустимо повторять)|
|-o или --offline|Параметр без значения для выполнения только checkout без pull|
|-b или --branch|Параметр для указания ветки, на которую нужно перейти в конкретном репозитории (параметр допустимо повторять. Ожидается значение по шаблону: "directory_name=branch_name")|
|--branch_default|Параметр для указания ветки, на которую нужно перейти (без указания этого параметра будет переход на master)|

### Запуск скрипта

Передполагается, что уже установлен git.
Ожидается, что все репозитории были скачаны по ssh или добавлены настройки для автоматической авторизации.

Для скрипта используются библиотеки, которые требуется установить с помощью команд:

```bash
pip install colored
```

Пример команды:

```bash
./git.py -p ../.. -i my-repo-utils
```
