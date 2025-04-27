"""Модуль простых операций с PDF-файлами на уровне страниц."""

import os
from tkinter import filedialog
import webbrowser

from PyPDF2 import (
    PdfMerger,
    PageObject,
    PdfReader,
    PdfWriter
)


def file_open():
    """Создаёт диалог открытия файла и отдаёт его полный путь."""

    file = filedialog.Open(
        filetypes=[('*.pdf files', '.pdf')],
    ).show()
    return file


def file_save(
    writer: PdfWriter,
    filename: str | None,
    name_modificator: str | None,
):
    """Сохраняет файл с помощью диалога."""

    file_path = filedialog.asksaveasfilename(
        filetypes=[('*.pdf files', '.pdf')],
        initialfile=f'{filename}_{name_modificator}',
    )
    if not file_path.endswith('.pdf'):
        file_path += '.pdf'
    with open(file_path, 'wb'):
        writer.write(file_path)


def select_pages(reader: PdfReader):
    """Создаёт список с выбранными пользователем номерами страниц файла."""

    nuber_of_pages = len(reader.pages)
    print(f'Число страниц в файле - {nuber_of_pages}')
    pages_string = input(
        'Введите номера обрабатываемых страниц через запятую '
        '(all - выбор всех страниц): '
    ).split(',')
    pages = []
    if pages_string == 'all':
        for page_num in range(nuber_of_pages):
            pages.append(page_num)
        print('Выбраны все страницы в файле.')
        return pages
    for page in pages_string:
        try:
            page_num = int(page)-1
            if page_num >= 0 and page_num < nuber_of_pages:
                pages.append(page_num)
        except Exception:
            continue
    if not pages:
        print('Внимание! Не выбрано ни одной страницы!')
    else:
        new_pages = ''
        for page in pages:
            new_pages += f'{page+1}, '
        print(
            'Выбраны следующие страницы:'
            f'{new_pages}'
        )
    return pages


def make_file(reader: PdfReader, pages: list):
    """Создаёт файл из списка страниц исходного файла."""

    writer = PdfWriter()
    for page_num in pages:
        page = reader.pages[page_num]
        writer.add_page(page)
    return writer


def rotate_pages(reader: PdfReader, pages: list):
    """Создаёт новый файл с поворотом страниц из списка."""

    writer = PdfWriter()
    try:
        angle = int(input('На сколько градусов повернуть (90, 180, 270)? - '))
        if angle not in ('90', '180', '270'):
            print('Ошибка при вводе угла поворота стрницы.')
            angle = 0
    except Exception as e:
        print(f'Ошибка при вводе угла поворота стрницы: {e}')
        angle = 0
    for page_num in range(len(reader.pages)):
        page: PageObject = reader.pages[page_num]
        if page_num in pages:
            page.rotate(angle)
        writer.add_page(page)
    return writer


def delete_pages(reader: PdfReader, pages: list):
    """
    Создаёт новый файл с исключением из исходного файла страниц из списка.
    """

    writer = PdfWriter()
    for page_num in range(len(reader.pages)):
        page: PageObject = reader.pages[page_num]
        if page_num in pages:
            continue
        writer.add_page(page)
    return writer


def merge_files(file_name: str):
    """Присоединяет выбираемые файлы к исходному файлу."""

    merger = PdfMerger()
    merger.append(file_name)
    choice = '1'
    files: list = []
    while choice != '0':
        if choice == '1':
            new_file: str = file_open()
            if not new_file:
                continue
            files.append(new_file)
            print(f'Добавлен файл: {new_file}')
        choice = input('Добавить файл для слияния? (1-да, 0-нет)')
    print(f'Выбраны файлы для добавления: {files}')
    for file in files:
        merger.append(file)
    return merger


def split_file(reader: PdfReader, file_name: str):
    base_name = os.path.splitext(file_name)[0]
    for page_num in range(len(reader.pages)):
        page: PageObject = reader.pages[page_num]
        writer = PdfWriter()
        writer.add_page(page)
        file_path = f'{base_name}_page_{page_num + 1}.pdf'
        with open(file_path, 'wb'):
            writer.write(file_path)
        writer.close()


def main():
    """Главная функция модуля."""

    file_name: str | None = None
    choice = '6'
    while choice != 0:
        if choice == '6':
            file_name = file_open()
            short_name = os.path.splitext(os.path.basename(file_name))[0]
            if not file_name:
                return
            if input('Открыть файл для просмотра? (1-да)') == '1':
                try:
                    webbrowser.open(file_name)
                except Exception as e:
                    print(f'Ошибка открытия файла на просмотр: {e}')
        with open(file_name, 'rb') as file:
            print(f'Открыт для работы файл: {file_name}.')
            reader = PdfReader(file)
            print(
                'Что сделать с файлом? \n'
                '1 - Выделить страницы и сшить в новый файл; \n'
                '2 - Выбрать страницы и повернуть; \n'
                '3 - Удалить выбранные страницы; \n'
                '4 - Присоединить файлы к текущему; \n'
                '5 - Разбить файл на страницы; \n'
                '6 - Выбрать новый файл; \n'
                '0 - Выйти.'
            )
            choice = input('Ваш выбор? - ')
            if choice == '1':
                pages = select_pages(reader)
                new_file: PdfWriter = make_file(
                    reader,
                    pages
                )
                file_save(new_file, short_name, 'selected')
                new_file.close()
            elif choice == '2':
                pages = select_pages(reader)
                new_file: PdfWriter = rotate_pages(
                    reader,
                    pages
                )
                file_save(new_file, short_name, 'rotated')
                new_file.close()
            elif choice == '3':
                pages = select_pages(reader)
                new_file: PdfWriter = delete_pages(
                    reader,
                    pages
                )
                file_save(new_file, short_name, 'cleared')
                new_file.close()
            elif choice == '4':
                new_file: PdfMerger = merge_files(file_name)
                file_save(new_file, short_name, 'merged')
                new_file.close()
            elif choice == '5':
                split_file(reader, file_name)
            elif choice == '6':
                continue
            elif choice == '0':
                return


if __name__ == '__main__':
    main()
