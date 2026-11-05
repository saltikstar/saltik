# Interdent Clinic — перенос изображений и иконок в Tilda

Изображения на текущем сайте уже сжаты: WebP для фотографий, JPG для скриншотов отзывов. Не конвертируйте отзывы в WebP с низким качеством — текст может стать нечитаемым.

## Иконки

Иконки встроены непосредственно в HTML как SVG с собственными path, stroke, viewBox и размерами. Они не зависят от SVG-спрайта, шрифтов или внешних библиотек. Отдельные файлы для загрузки в Tilda: папка `tilda/icons/`. Для стандартного изображения в Zero Block добавляйте SVG-файл, для HTML-блока оставляйте встроенный SVG.

## Фотографии и документы

Все используемые локальные изображения доступны в `assets/`. При переносе на Tilda загрузите их в Tilda и замените относительные пути `assets/...` на адреса файлов Tilda. Не ссылайтесь на GitHub как на постоянный CDN. Важны размеры и адаптивное кадрирование: `object-fit: cover` только для фотографий, для скриншотов отзывов и документов — `contain`.

**Внешняя фотография модели челюсти** используется с Wikimedia Commons и требует отдельной загрузки в Tilda и сохранения авторской атрибуции; в репозитории эта фотография пока не хранится.

| Файл | Размер |
|---|---:|
| `assets/mark-transparent.webp` | 16 КБ |
| `assets/team-hero.webp` | 72 КБ |
| `assets/service-implant-v5.webp` | 137 КБ |
| `assets/service-orthodont-v5.webp` | 113 КБ |
| `assets/microscope-scene.webp` | 43 КБ |
| `assets/service-prosthetics-v4.webp` | 14 КБ |
| `assets/service-surgery-v7.webp` | 84 КБ |
| `assets/service-hygiene-v7.webp` | 57 КБ |
| `assets/service-diagnostic-v4.webp` | 34 КБ |
| `assets/team-clinic.webp` | 65 КБ |
| `assets/surgery-open-implants.webp` | 143 КБ |
| `assets/surgery-closed-implants.webp` | 168 КБ |
| `assets/surgery-open.webp` | 238 КБ |
| `assets/diagnostic-scene.webp` | 27 КБ |
| `assets/abu.webp` | 9 КБ |
| `assets/maksat.webp` | 10 КБ |
| `assets/gaziza.webp` | 11 КБ |
| `assets/aliya.webp` | 12 КБ |
| `assets/akmaral.webp` | 12 КБ |
| `assets/review-01.webp` | 68 КБ |
| `assets/review-02.webp` | 21 КБ |
| `assets/review-03.webp` | 51 КБ |
| `assets/review-04.webp` | 18 КБ |
| `assets/review-05.webp` | 15 КБ |
| `assets/review-06.webp` | 33 КБ |
| `assets/review-07.webp` | 58 КБ |
| `assets/review-08.webp` | 53 КБ |
| `assets/review-6846.jpg` | 154 КБ |
| `assets/review-6847.jpg` | 113 КБ |
| `assets/review-6844.jpg` | 106 КБ |
| `assets/review-6839.jpg` | 191 КБ |
| `assets/review-6843.jpg` | 88 КБ |
| `assets/review-6841.jpg` | 189 КБ |
| `assets/review-6842.jpg` | 86 КБ |
| `assets/review-6840.jpg` | 89 КБ |
| `assets/license-thumb.webp` | 48 КБ |
| `assets/registration-thumb.webp` | 23 КБ |

## Подключение

В Tilda HTML-блоке вставьте HTML секции, CSS подключите через «Дополнительный CSS» страницы или отдельный блок T123, JS — перед закрывающим `</body>` в настройках страницы. Сохраните порядок стилей и проверьте pop-up окон врачей, слайдер отзывов, 2ГИС и кнопки WhatsApp. Шрифты Manrope и Cormorant Garamond должны быть подключены отдельно.

Не копируйте теги `<html>`, `<head>` и `<body>` прямо внутрь HTML-блока. Все изображения клиники и отзывы должны открываться по адресам Tilda перед публикацией.

Скриншоты отзывов сохранены без обрезки. Для первого экрана используется `fetchpriority="high"`, для изображений ниже первого экрана — `loading="lazy"`, для всех фотографий — `decoding="async"`.
