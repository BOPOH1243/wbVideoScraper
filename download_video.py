#!/usr/bin/env python3
import argparse
import sys
import os
import time
import requests
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By

def wait_for_element(driver, selector, timeout=30, scroll_step=500, poll_frequency=1):
    """
    Прокручиваем страницу вниз, пока не найдём элемент с заданным селектором
    или не истечёт таймаут.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            return elements[0]
        # Прокручиваем страницу вниз
        driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_step)
        time.sleep(poll_frequency)
    return None

def main():
    parser = argparse.ArgumentParser(description="Скачивание видео из отзыва Wildberries")
    parser.add_argument("url", help="Ссылка на товар с wildberries.ru")
    parser.add_argument("--output", default="output_video.mp4",
                        help="Путь и имя выходного видеофайла (по умолчанию: output_video.mp4)")
    args = parser.parse_args()

    url = args.url
    output_mp4 = args.output

    # Проверка, что URL относится к Wildberries
    if "wildberries.ru" not in url:
        print("Error: Provided URL does not belong to wildberries.ru")
        sys.exit(1)

    # Настройки Selenium для headless режима с разрешением 1920x1080
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") почему-то сайт не работает с headless :(
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")  # Установка разрешения окна

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        
        # Прокручиваем страницу до появления элемента отзывов
        print("Ожидание появления элемента 'section.user-photos'...")
        element = wait_for_element(driver, "section.user-photos", timeout=30)
        if not element:
            print("Элемент section.user-photos не найден после прокрутки.")
            sys.exit(1)
        
        # Извлекаем ссылки на превью отзывов с видео
        image_elements = driver.find_elements(By.CSS_SELECTOR, ".swiper-wrapper > .swiper-slide > img")
        video_preview_urls = []
        for el in image_elements:
            src = el.get_attribute("src")
            if src and "preview.webp" in src:
                video_preview_urls.append(src)
        
        if not video_preview_urls:
            print("Нет отзывов с видео (не найдено ссылок с 'preview.webp').")
            sys.exit(1)
        
        # Берем первую ссылку и заменяем /preview.webp на /index.m3u8
        first_preview_url = video_preview_urls[0]
        m3u8_url = first_preview_url.replace("preview.webp", "index.m3u8")
        print("Получаем плейлист:", m3u8_url)
        
        # Запрос плейлиста
        response = requests.get(m3u8_url)
        if response.status_code != 200:
            print("Ошибка при получении плейлиста, статус-код:", response.status_code)
            sys.exit(1)
        
        # Обработка данных: фильтруем строки, не начинающиеся на '#'
        lines = response.text.split('\n')
        segment_files = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        
        if not segment_files:
            print("Не удалось найти сегменты видео в плейлисте.")
            sys.exit(1)
        
        print("Найдено сегментов:", segment_files)
        
        # Базовый URL для сегментов (убираем "index.m3u8")
        base_url = m3u8_url.rsplit('/', 1)[0] + '/'
        
        # Имя временного файла для объединённого видео (.ts)
        temp_ts = "temp_video.ts"
        
        # Скачиваем и объединяем сегменты
        with open(temp_ts, "wb") as f:
            for seg in segment_files:
                segment_url = base_url + seg
                print("Скачиваем сегмент:", segment_url)
                seg_response = requests.get(segment_url)
                if seg_response.status_code == 200:
                    f.write(seg_response.content)
                else:
                    print("Ошибка при скачивании сегмента:", segment_url)
        
        print("Видео TS сохранено во временном файле:", temp_ts)
        
        # Конвертация .ts в формат mp4 с помощью ffmpeg
        ffmpeg_command = ["ffmpeg", "-y", "-i", temp_ts, "-c", "copy", output_mp4]
        print("Конвертируем TS в MP4...")
        result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("Видео успешно конвертировано в:", output_mp4)
            # Удаляем временный файл
            os.remove(temp_ts)
        else:
            print("Ошибка при конвертации видео:", result.stderr.decode())
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
