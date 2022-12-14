<h1 align="center"> ♬👻 ToDo бᴏᴛ дᴧя ᴦᴩуᴨᴨᴏʙᴏᴦᴏ CHATa 😳♩</h1>

<p align="center">
<a href="#skills">⊂ກ০⊂০bዘ০⊂τu |</a>
<a href="#tokens">τ০kℯዘӸ u ID |</a>
<a href="#starts">∂ℯກᏁ০ú u ℨᏘກɣ⊂k</a>
</p>

<p align="center">
<img src="https://github.com/exp-ext/GitProjects/blob/main/pre.png" width="700">
</p>

<section id="skills">
    <h2> Οϰ γϻεετ </h2>
</section>

- оповещать о разовых напоминаниях, удаляя их после исполнения
- ежегодно оповещать о днях рождения
- рассказывать анекдоты
- показывать картинки с котиками
- выдавать прогноз погоды
- показывать список мероприятий в ближайшем мегаполисе на сегодняшний день
- сбрасывать ваше местоположение в общий чат

### Разовые напоминания ToDo

Разовые напоминания обязательно должны содержать дату в формате *##.##.##*. Если не прописать время в тексте напоминания, то оно по умолчанию будет 7:15. Если в тексте будет написано конкретное время, то бот оповестит вас за 4 часа до его наступления.

Пример: 20.12.2022 в 17:50 встреча в кафе с Васей.

### Ежегодные напоминания

О ежегодных напоминаниях бот оповещает в 7:15 на дату оповещения. Если в тексте был Емоджи 🎁, то дополнительно будет оповещение за 7 дней до даты. Это на случай если нужно купить подарок. В формате даты у ежегодного оповещения не должно быть года, только день и месяц *##.##*

Пример: 20.12 ДР у Васи Васиной 🎁

***

#### Анекдоты, картинки, список мероприятий, погоду и т.п. можно отобразить нажав на соответствующие кнопки

#### P.S. Прогноз погоды и всё что связано с геолокацией, можно получить только в личном чате с ботом.

***
<section id="tokens">
    <h2> Пσɠρσδϰεε σ ρεӷμϲτραҵμяχ </h2>
</section>

ТОКЕНЫ, ID и прочее: 

- **TOKEN = ' '** - токен Вашего бота, получаем его в Телеграмм https://t.me/BotFather.
После создания бота через [@BotFather](https://t.me/BotFather) и получения токена, тут же входим в настройки инлайн режима командой '/setinline' и включаем его.

Для создания кнопки с быстрыми командами, вводим '/setcommands' и передаём список самих команд:

    help - вывести список доступных команд
    help_location - показать кнопку с запросом погоды

- **CHAT_ID = ' '** - ID чата вашей группу, где будут отображаться напоминания. Получить его можно при помощи бота https://t.me/getmyid_bot. Для этого просто добавьте его в группу. Отрицательный номер это ID группы, второй ваш. Не забываем удалить этого бота из группы и добавить своего.

- **OW_API_ID = ' '** - токен для прогноза погоды. Доступен после регистрации по адресу https://home.openweathermap.org/api_keys

- **YANDEX_GEO_API = ' '** - токен Геокодера Яндекса. Получить можно по адресу  https://yandex.ru/dev/maps/geocoder/

- **ID_CHILDREN = ' '** - ID члена/ов общей группы, кому противопоказаны взрослые анекдоты. Т.е. лица моложе 18 лет. ID можно перечислять через пробел. Необязательный параметр.

- **ID_ADMIN = ' '** - ID пользователя, которому будут высылаться служебные сообщения о работе программы.

- **DOMEN = ' '** - домен на котором будет размещён ваш бот. К примеру для [HEROKU](https://heroku.com): *https:// имя app.herokuapp.com*

- **DATABASE_URL = ' '** - URL с данными подключения к базе PostgreSQL

- **PRACTICUM_TOKEN = ' '** необязательный параметр

<section id="starts">
    <h2> Пσɠρσδϰεε σ ӡαηγϲӄε δστα </h2>
</section>

Я использовал сервис [HEROKU](https://heroku.com) и поэтому буду описывать размещение бота на нём.

Дня начала нужно зарегистрироваться. В России, в условиях санкций, это возможно сделать только через прокси.

После регистрации создаём приложение, имя на ваше усмотрение.

В правом верхнем углу, нажав на кнопку из 9-ти точек, выбираем **Data**. Создаём Heroku Postgres базу данных, инсталлируя её с бесплатным планом. В строке *App to provision to* необходимо ввести название приложения, созданного ранее, и выбрать его из выпадающего списка.

В личном кабинете HEROKU переходим на вкладку **Settings**. Жмём на кнопочку *Reveals Config Vars* и вводим полученные токены:

<img src="https://github.com/exp-ext/GitProjects/blob/main/Снимок экрана от 2022-10-17 13-03-53.png" width="700">

Для дальнейших действий необходимо сделать [Fork репозитория](https://github.com/exp-ext/webhook_bot) к себе в **GitHub**. Только после этого, в личном кабинете **HEROKU** Вам будет доступно подключение этого бота через свой **GitHub**.

Итак, после форка, в личном кабинете **HEROKU** остаётся в разделе **Deploy** выбрать *Connect to GitHub*. В поле *Search for a repository to connect to* ввести имя ветки *webhook_bot*. Приконектится к ней и нажать на кнопку **Deploy Branch**.

Всё, бот  работе.

Для того чтоб он не засыпал через каждые 30 минут бездействия, необходимо извне делать к нему запросы. Для этого подойдёт любой сторонний сервис, к примеру [этот >>>](https://uptimerobot.com/). Регистрируемся, создаём новый монитор с параметром опроса по HTTPS, вводим URL *https:// имя app.herokuapp.com/test* и выставляем интервал мониторинга в 10 минут. Как приятный бонус, имеем оповещение на email от сервиса в случае отказа бота.

## License

[MIT © Andrey Borokin](https://github.com/exp-ext/webhook_bot/blob/main/LICENSE.txt)

[![Join Telegram](https://img.shields.io/badge/My%20Telegram-Join-blue)](https://t.me/Borokin)
