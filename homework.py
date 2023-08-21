import argparse
import os
import time
from pathlib import Path

import requests
import threading
import multiprocessing
import asyncio

image_urls = []
with open('images.txt', 'r') as images:
    for image in images.readlines():
        image_urls.append(image.strip())


def download_image(url, image_path):
    start_time = time.time()
    response = requests.get(url, stream=True)
    filename = image_path.joinpath(os.path.basename(url))
    with open(filename, "wb") as f:
        for data in response.iter_content(1024):
            f.write(data)
    print(f"Загружено изображение {filename} за {time.time() - start_time:.2f} секунд.")


async def download_image_async(url, image_path):
    start_time = time.time()
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, {"stream": True})
    filename = image_path.joinpath(os.path.basename(url))
    with open(filename, "wb") as f:
        for data in response.iter_content(1024):
            f.write(data)
    print(f"Загружено изображение {filename} за {time.time() - start_time:.2f} секунд.")


def download_images_threading(urls, image_path):
    start_time = time.time()
    threads = []
    for url in urls:
        t = threading.Thread(target=download_image, args=(url, image_path))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"\nОбщее время загрузки через потоки: {time.time() - start_time:.2f} секунд.")


def download_images_multiprocessing(urls, image_path):
    start_time = time.time()
    processes = []
    for url in urls:
        p = multiprocessing.Process(target=download_image, args=(url, image_path))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print(f"\nОбщее время загрузки через процессы: {time.time() - start_time:.2f} секунд.")


async def download_images_asyncio(urls, image_path):
    start_time = time.time()
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(download_image_async(url, image_path))
        tasks.append(task)

    await asyncio.gather(*tasks)

    print(f"\nОбщее время загрузки через асинхронный метод: {time.time() - start_time:.2f} секунд.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Этот скрипт загружает все изображения с файла images.txt")
    parser.add_argument("-p", "--path", help="Каталог, в котором вы хотите хранить изображения.", default='images')
    args = parser.parse_args()
    path = args.path
    if not os.path.isdir(path):
        os.makedirs(path)
    image_path = Path(path)

    print(f"Загружаем {len(image_urls)} изображений, используя потоки.")
    time.sleep(2)
    download_images_threading(image_urls, image_path)

    print(f"\nЗагружаем {len(image_urls)} изображений, используя процессы.")
    time.sleep(2)
    download_images_multiprocessing(image_urls, image_path)

    print(f"\nЗагружаем {len(image_urls)} изображений, используя асинхронность.")
    time.sleep(2)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_images_asyncio(image_urls, image_path))
