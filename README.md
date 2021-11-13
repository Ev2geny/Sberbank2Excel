# Sberbank2Excel

Расширяемая утилита для конвертации выписки Сбербанка по карте из формата PDF в формат Excel. (С возможностями расширения для выписок других банков). 

![Sberbank2Excel.PNG](misc/Sberbank2Excel.PNG "Sberbank2Excel")


**Разработчик:** ev2geny собака gmail.com

## Функционал
- Конвертация одного или многих файлов PDF - выписки за один раз

- Поддерживает несколько форматов выписки. См. [Приложение А](#Приложение-А.-Список-поддерживаемых-форматов) 

- Легко расширяется для поддержки дополнительных форматов (см. [CONTRIBUTING.md](CONTRIBUTING.md))

- Автоматическое определение формата выписки

- Верификация баланса по трансакциям и по шапке. Утилита вычисляет баланс по всем найденным трансакциям и сравнивает это число с балансом, вычисленным по информации в шапке выписки (к примеру баланс_по_шапке = СУММА ПОПОЛНЕНИЙ - СУММА СПИСАНИЙ - СУММА СПИСАНИЙ БАНКА). Если эти два числа не совпадают, то выписка по умолчанию не создаётся. Это даёт высокую вероятность того, что если Excel файл был создан, то конвертация прошла без ошибок.

## Как пользоваться

### Подготовка
1. Скачать последнюю версию программы https://github.com/Ev2geny/Sberbank2Excel/releases/latest 
1. Разархивировать ZIP файл в отдельную директорию и найти `sberbankPDF2ExcelGUI.bat`

### Конвертация 

**Шаг 1** Запустите `sberbankPDF2ExcelGUI.bat`

**Шаг 2** Выберите один или несколько файлов выписки Сбербанка по карте в формате PDF

**Шаг 3** Нажмите "Сконвертировать выбранные файлы"

**Результат:** утилита создаст файлы с расширением .xlsx 

**Примечание:** опции **Не удалять промежуточный текстовый файл** и **Игнорировать результаты сверки баланса по транзакциям и в шапке выписки** используются в основном для отладки, сообщениях о проблемах или для тестирования. 

## Обратная связь
Для сообщения об ошибках или пожеланиях по улучшению лучше всего воспользоваться [функционалом системы github](https://github.com/Ev2geny/Sberbank2Excel/issues)

На общие темы начните дискуссию [здесь](https://github.com/Ev2geny/Sberbank2Excel/discussions)

Либо напишите письмо разработчику: ev2geny собака gmail.com

## Приложения
### Приложение А. Список поддерживаемых форматов
#### Сбербанк
**SBER_DEBIT_2005**  - Выписка по счёту дебетовой карты Сбербанка образца мая 2020 года. Протестирована на карте MasterCard .  
??? Поддержка VISA неизвестна.

**SBER_DEBIT_2107** - Выписка по счёту дебетовой карты Сбербанка образца июля 2021 года. Протестирована на карте MasterCard .  
??? Поддержка VISA неизвестна.

**SBER_CREDIT_2110** - Выписка по счёту кредитной карты Сбербанка образца октября 2021 года. Протестирована на карте VISA.  
??? Поддержка MasterCard неизвестна.


### Приложение Б. Как безопасно пересылать проблемный файл
В случае если происходит ошибка в конвертации выписки, либо есть потребность добавить новй формат, разработчику потребуется доступ к проблемной/новой выписке для исправления программы. 
Если из соображений конфиденциальности нет возможности переслать разработчику изначальную выписку, можно переслать анонимизированный промежуточный текстовый файл. Для этого надо сделать следующее:
- При ошибке конвертации конвертер создаст промежуточный текстовый файл с расширением .txt. Этот файл содержит текстовую информацию из pdf-выписки, которая в дальнейшем должна была быть использована для создания Excel - файла. Однако не вся текстовая информация используется для создания Excel файла. Задача состоит в том чтобы удалить неиспользуемую конфиденциальную информацию либо заменить используемую конфиденциальную информацию, но сделать это таким образом чтобы конвертер всё еще распознавал бы структуру файла и смог бы выполнить проверку вычисления сумм транзакций. 
[Инструкция](misc/Anonymisation%20instructions.png) показывает что можно удалять, что можно заменять, а что нужно оставить без изменений.
-  Используйте текстовый редактор и [инструкцию](misc/Anonymisation%20instructions.png) чтобы удалить конфиденциальную информацию из промежуточного текстового файла (номер карты, фамилию, имя и т.д.). 
Т.к. для конвертер различает символ табуляции и пробелы, то рекомендуется использовать текстовый редактор, который показывает символы табуляции чтобы случайно не удалить их. Рекомендуемый текстовый редактор для этих целей: [Notepad++](https://notepad-plus-plus.org/)   
-  **Старайтесь удалять или менять как можно меньше информации**. 
На выходе должно получиться что-то типа этого: [пример анонимизированного промежуточного текстового файла](misc/_SBER_DEBIT_2107_anonymized_reduced.txt)

- Попытайтесь сконвертировать теперь уже анонимизированный текстовый файл используя всё тот же sberbankPDF2ExcelGUI (для этого на **Шаге 2** при выборе файлов надо разрешить выбор любых файлов, а не только .pdf)
- Убедитесь, что при попытке конвертации анонимизированного текстового файла конвертер выдаёт такое же сообщение об ошибке, как и при попытке конвертации PDF файла.
- Перешлите анонимизированный текстовый файл разработчику (ev2geny собака gmail.com) вместе с информацией об ошибке.
