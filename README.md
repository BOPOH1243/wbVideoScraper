# Wildberries Video Downloader

Простой скрипт на Python для скачивания видео из отзывов Wildberries.

## Зависимости

### APT пакеты (для Linux)
Установите следующие пакеты:
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver ffmpeg
```

### Python зависимости
Все необходимые библиотеки указаны в файле `requirements.txt`. Установить их можно так:
```bash
pip install -r requirements.txt
```

## Использование

Запустите скрипт, передав URL товара и, опционально, путь к выходному видеофайлу:
```bash
python download_video.py "https://www.wildberries.ru/catalog/192186031/detail.aspx" --output "/путь/к/выходному/файлу.mp4"
```

Для просмотра доступных опций запустите:
```bash
python download_video.py --help
```

## Описание

Скрипт открывает страницу товара Wildberries в headless браузере с разрешением 1920x1080, прокручивает страницу до появления блока с отзывами, извлекает ссылку на плейлист видео из первого отзыва, скачивает видео-сегменты, объединяет их в один `.ts` файл и конвертирует в формат MP4 с помощью ffmpeg.