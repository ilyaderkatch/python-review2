# python-review2
Реализация бота, выдающий шутки. Ссылка - @Pupa_Joke_Bot.

ОСНОВНАЯ ЦЕЛЬ
Создание бота, котрый будет собирать шутки с сайта anekdot.ru

ФУНКЦИОНАЛ
1. Генерация новой шутки, неповторяющейся со старой
2. Оценивание предыдущей шутки
3. Запрос средней оценки по конкретному анекдоту
(в принципе все это прописано в самом боте:) )

НЕКОТОРЫЙ КОММЕНТАРИЙ ПО ПРОГРАММЕ:
все написанное делится на несколько типов:
1. Функции парсинга (находятся в самом начале, один класс для обхода блокировки паука и сама функция, генерирующий лист шуток)
2. Функции БД(и сама бд) (находятся в конце, их много)
3. Класс, отображающий состояние бота (де-факто - грамотно обрабатывает результаты парсинга)
4. Функции связи с ботом (находится после класса, перед бд)

