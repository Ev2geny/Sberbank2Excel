# Sberbank2Excel

Утилита для конвертации выписки Свербанка по карте из формата PDF в формат Excel

Примеры уже сконвертированных файлов можно посмтреть [здесь](https://github.com/Ev2geny/Sberbank2Excel/tree/master/Examples). Например [этот](https://github.com/Ev2geny/Sberbank2Excel/raw/master/Examples/testovaya_vipiska_po_karte_dlinnaya_primer_konvertatsii.xlsx)

Автор: ev2geny собака gmail.com

Ссылка на утилиту в системе github https://github.com/Ev2geny/Sberbank2Excel

Ссылка для скачивания скомпилированного файла, готового к запуску на Windows https://github.com/Ev2geny/Sberbank2Excel/releases/latest

## Как пользоваться

Для использования утилиты сначала надо сконвертировать выписку PDF в текстовый формат используя foxit PDF reader  https://www.foxitsoftware.com/pdf-reader/

**!!! Важно:** программа не будет работать если для конвертации в текстовый режим использовать Adobe Acrobat Reader, т.к. он по-другому конвертирует pdf  в текстовый файл

### Подготовка
#### sberbankPDFtext2ExcelGUI

**Обязательные шаги**
1. Скачать последнюю версию  **sberbankPDFtext2ExcelGUI.zip** https://github.com/Ev2geny/Sberbank2Excel/releases/latest 
1. Разархивировать ZIP файл в отдельную директорию и найти `sberbankPDFtext2ExcelGUI.bat`

**Опциональные шаги (проверка программы на тестовом файле)**
1. Запустите `sberbankPDFtext2ExcelGUI.bat`
1. Выбирите тестовый файл `testovaya_vipiska_po_karte_dlinnaya.txt` из папки `Exaples`
1. Нажмите "Сконвертировать выбранные файлы"
1. Убедитесь, что программа создаст файл `testovaya_vipiska_po_karte_dlinnaya.xlsx` в тойже папке (`Examples`)


#### foxit PDF reader
1. Установить foxit PDF reader  https://www.foxitsoftware.com/pdf-reader/

### Конвертация 

**Шаг 1** Окройте выписку Сбербанка по карте в формате PDF используюя заранее установленный foxit PDF reader

**Шаг 2** Сохраните файл в текстовом формате (File ==> Save as ==> computer ==> (Выберете папку)). При сохранении выберете формат **TXT files (*.txt)**

**Шаг 3** Запустите `sberbankPDFtext2ExcelGUI.bat`

**Шаг 4** Выберите один или несколько сконвертированных текстовых файлов

**Шаг 5** Нажмите "Сконвертировать выбранные файлы"

**Результат:** утилита создаст файлы с расширением .xlsx 

## Что делать в случае, если программа не конвертирует файл в формат Excel и/или выдаёт сообщение об ошибке.

Начиная с релиза 1.3.1 в дистрибутив добавлена папка Examples. Проведите тестовую конвертацию текстовых файлов из этой папки в формат Excel, использую **sberbankPDFtext2ExcelGUI**. Сравните результат с файлами .xlsx, находящимися в той же папке. Если программа успешно конвертирует тестовые файлы, значит дело в формате вашего текстового файла.

Сообщите об ошибке разработчику. Желательно сделать это через инструментарий github: https://github.com/Ev2geny/Sberbank2Excel/issues. Либо сообщите об ошибке по электронной почте (ev2geny собака gmail.com)

При информировании об ошибке необходимо приложить входной текстовый файл, с которым произошла ошибка. Т.к. такой файл в изначальном виде будет содержать персональную информацию, то рекомендуется удалить эту информацию используя в качестве примера файл [primer_dlya_soobsheniya_ob_oshibkah.txt](https://github.com/Ev2geny/Sberbank2Excel/blob/master/Examples/primer_dlya_soobsheniya_ob_oshibkah.txt) из папки [Examples](https://github.com/Ev2geny/Sberbank2Excel/tree/master/Examples)
