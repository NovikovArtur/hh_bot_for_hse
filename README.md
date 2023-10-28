# Телеграм бот для для нахождения сотрудников в свои проекты
Реализован на Python / aiogram. Использует библиотеки sqlite3 и БД SQLite. В боте реализована система управления состояниями.

## Возможности
Бот даёт возможность пользователю варианты использования. Т.е. бот может быть полезным как для соискателей, так и для работодателей.
Для этого в боте реализованы функции работы с резюме, работы с проектами, а так же предусмотренна возможность добавления вакансий в проекты.

Функции работы с резюме:
1) Добавление резюме (можно >1)
2) Редактирование резюме: в случае наличия ошибки при вводе данных, пользователь всегда сможет исправить ошибки
3) Удаление резюме
4) Просмотр каждого резюме: пользователь может увидеть название, а так же текст каждого из своих резюме

Функции работы с проектами:
1) Добавление проектов (можно >1)
2) Редактирование проектов: как и в случае с резюме, пользователь имеет возможность исправить допущенные ошибки
3) Удаление проекта
4) Просмотр каждого проекта: пользователь имеет возможность посмотреть название и описание проекта

Функции работы с вакансиями:
Возможности работы с вакансиями изначально скрыты от пользователя. Доступ к ним открывается только после добавления хотя бы одного проекта к себе.
В данный момент в боте реализовано 3 основных функции работы с вакансиями, а именно:
1) Добавление вакансий к проекту (>1 к каждому проекту)
2) Удаление определенной вакансии из определенного проекта
3) Просмотр всех вакансий в каждом проекте

Дальнейшие планы по развитию бота:
1) Добавление возможности редактировать вакансии
2) Добавление поиска подходящих под конкретное резюме вакансий (Доступ к нему так, же как и с вакансиями, открывается не сразу, а только после добавления хотя бы 1 резюме)
3) Добавление отклика на вакансию (Будет реализовано как входящее уведомление автору проекта, с указанием тг ника, позиции на которую откликнулся соискатель, а так же его резюме)
4) Добавление умных рекомендаций для более качественного подбора подходящих проектов


## Структура БД

В боте реализована работа с базой данных hse_bot. 
Описание таблиц:

1) users
Таблица содержит уникальный номер пользователя, создаваемый автоматически (user_id) - первичный ключ; тг ник пользователя (tg); 2 столбца CV и project, которые являются индикаторами наличия резюме или проекта у данного пользователя и принимают только значения 0 или 1
2) CV
Таблица содержит уникальный номер резюме, создаваемый автоматически (CV_id) - первичный ключ; тг ник пользователя (tg); название резюме, совпадающее с профессией пользователя, по которой он хочет найти работу (name_CV); текст резюме (CV)
3) project
Таблица содержит уникальный номер проекта, создаваемый автоматически (project_id) - первичный ключ; тг ник пользователя (tg); название проекта (name_project); описание проекта (project); индикатор наличия в этом резюме вакансий (vacancy), который принимает значения только 0 или 1
4) vacancy
Таблица содержит уникальный номер вакансии, создаваемый автоматически (vacancy_id) - первичный ключ; номер проекта, в котором актуальна эта вакансия (project_id); название вакансии (профессии), на которую ведется поиск специалистов (vacancy_name); описание вакансии (vacancy)
5) response
Работа в боте с этой таблицей еще не реализована, но по предварительному анализу в этой таблице хватит следующих столбцов:
Уникальный номер отклика, создаваемый автоматически (ID) - первичный ключ; номер вакансии, на которую произошел отклик (vacancy_id); номер пользователя, который откликнулся на эту вакансию (user_id)

## Ввод данных
Ввод данных осуществляется или с помощью Inline кнопок, или с помощью клавиатуры. 
Резюме, проект и вакансию необходимо вводить следующим образом:
Программист
Люблю писать ботов


##Дополнительные возможности
В боте реализована возможность посмотреть информацию об авторе бота, есть ссылка на тг, чтобы пользователь, в случае возникновения проблемы с использованием бота или коммерческим предложением, мог обратиться к его создателю
