import os
from tkinter import filedialog
import webbrowser

from PyPDF2 import (
    # PdfMerger,
    PageObject,
    PdfReader,
    PdfWriter
)


def file_open():
    file = filedialog.Open(
        None,
        filetypes=[('*.pdf files', '.pdf')]
    ).show()
    return file


def file_save(
    writer: PdfWriter,
    filename: str | None,
    name_modificator: str | None,
):
    file_path = filedialog.asksaveasfilename(
        filetypes=[('*.pdf files', '.pdf')],
        initialfile=f'{filename}_{name_modificator}',
    )
    if not file_path.endswith('.pdf'):
        file_path += '.pdf'
    with open(file_path, 'wb'):
        writer.write(file_path)


def select_pages(reader: PdfReader):
    nuber_of_pages = len(reader.pages)
    print(f'Число страниц в файле - {nuber_of_pages}')
    pages_string = input(
        'введите номера обрабатываемых страниц через запятую: '
    ).split(',')
    pages = []
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
    writer = PdfWriter()
    for page_num in pages:
        page = reader.pages[page_num]
        writer.add_page(page)
    return writer


def rotate_pages(reader: PdfReader, pages: list):
    writer = PdfWriter()
    try:
        angle = int(input('На сколько градусов повернуть (90, 180, 270)? - '))
    except Exception as e:
        print(f'Ошибка при вводе угла поворота стрницы: {e}')
        angle = 0
    for page_num in range(len(reader.pages)):
        page: PageObject = reader.pages[page_num]
        if page_num in pages:
            page.rotate(angle)
        writer.add_page(page)
    return writer


def main():
    file_name = file_open()
    short_name = os.path.splitext(os.path.basename(file_name))[0]
    if not file_name:
        return
    webbrowser.open(file_name)
    with open(file_name, 'rb') as file:
        reader = PdfReader(file)
        pages = select_pages(reader)
        print(
            'Что сделать с выделенными страницами? \n'
            '1 - Сшить в новый файл; \n'
            '2 - Повернуть выбранные страницы \n'
            '0 - Выйти'
        )
        choice = input('Ваш выбор? - ')
        if choice == '1':
            new_file = make_file(
                reader,
                pages
            )
            file_save(new_file, short_name, 'selected')
        elif choice == '2':
            new_file = rotate_pages(
                reader,
                pages
            )
            file_save(new_file, short_name, 'rotated')
        elif choice == '0':
            return


if __name__ == '__main__':
    main()
