import sqlite3
import tkinter as tk
from tkinter import messagebox

class LibraryGUI:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

        self.root = tk.Tk()
        self.genre = None
        self.root.title("Библиотека")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.title_label = tk.Label(self.root, text="Название:")
        self.title_label.pack()
        self.title_entry = tk.Entry(self.root)
        self.title_entry.pack()

        self.author_label = tk.Label(self.root, text="Автор:")
        self.author_label.pack()
        self.author_entry = tk.Entry(self.root)
        self.author_entry.pack()

        self.description_label = tk.Label(self.root, text="Описание:")
        self.description_label.pack()
        self.description_entry = tk.Entry(self.root)
        self.description_entry.pack()

        self.genre_var = tk.StringVar(self.root)
        self.genre_var.set("Выберите жанр")  # Значение по умолчанию
        genre_options = self.get_genres()
        self.genre_menu = tk.OptionMenu(self.root, self.genre_var, *genre_options, command=self.on_select)
        self.genre_menu.pack()

        self.genre_label = tk.Label(self.root, text="Указать свой:")
        self.genre_label.pack()
        self.genre_entry = tk.Entry(self.root)
        self.genre_entry.pack()

        self.add_button = tk.Button(self.root, text="Добавить книгу", command=self.add_book)
        self.add_button.pack()

        self.remove_label = tk.Label(self.root, text="Удалить книгу по названию:")
        self.remove_label.pack()
        self.remove_entry = tk.Entry(self.root)
        self.remove_entry.pack()
        self.remove_button = tk.Button(self.root, text="Удалить книгу", command=self.remove_book)
        self.remove_button.pack()

        self.search_label = tk.Label(self.root, text="Поиск по ключевому слову:")
        self.search_label.pack()
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack()
        self.search_button = tk.Button(self.root, text="Поиск", command=self.search_books)
        self.search_button.pack()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            description TEXT,
            genre_id INTEGER REFERENCES genres (id) ON DELETE CASCADE ON UPDATE CASCADE)''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )''')
        self.conn.commit()

    def on_select(self, value):
        self.genre = self.cursor.execute("SELECT id FROM genres WHERE name = ?", (value,)).fetchone()[0]

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        description = self.description_entry.get()
        if not self.genre:
            genre_name = self.genre_entry.get()
            if not genre_name:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите или напишите жанр")
                return
            genre = self.add_genre(self.genre_entry.get())
        else:
            genre = self.genre
        
        if title and author and description and genre:
            self.cursor.execute("INSERT INTO books (title, author, description, genre_id) VALUES (?, ?, ?, ?)",
                                (title, author, description, genre))
            self.conn.commit()
            messagebox.showinfo("Успех", "Книга добавлена")
            self.title_entry.delete(0, 'end')
            self.author_entry.delete(0, 'end')
            self.description_entry.delete(0, 'end')
            self.genre = None
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")

    def add_genre(self, ganre_name):
        self.cursor.execute("INSERT INTO genres (name) VALUES (?)",
                            (ganre_name,))
        genre_id = self.cursor.execute("SELECT id from genres ORDER BY id DESC").fetchone()[0]
        return genre_id

    def get_genres(self):
        genres_data = self.cursor.execute("SELECT name FROM genres").fetchall()
        genres = [genre[0] for genre in genres_data]
        if not genres:
            genres = ["Поэма", "Проза", "Автобиография", "Роман"]
            query = "INSERT INTO genres (name) VALUES "
            for genre in genres:
                query += f"('{genre}'),"
            self.cursor.execute(query[:-1])
            self.conn.commit()
        return genres

    def remove_book(self):
        title = self.remove_entry.get()
        
        if title:
            self.cursor.execute("DELETE FROM books WHERE title=?", (title,))
            self.conn.commit()
            messagebox.showinfo("Успех", "Книга удалена")
            self.remove_entry.delete(0, 'end')
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, введите название книги")

    def search_books(self):
        keyword = self.search_entry.get()
        
        if keyword:
            search_results = self.cursor.execute("SELECT books.title, books.author, books.description, genres.name FROM books LEFT JOIN genres ON books.genre_id = genres.id WHERE books.title LIKE ? OR books.author LIKE ? OR genres.name LIKE ?", ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%')).fetchall()
            if search_results:
                result_str = ""
                for book in search_results:
                    result_str += f"{book[1]} - {book[2]}\n"
                messagebox.showinfo("Результаты поиска", result_str)
            else:
                messagebox.showinfo("Результаты поиска", "Книги не найдены")
            self.search_entry.delete(0, 'end')
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ключевое слово для поиска")

    def run(self):
        self.root.mainloop()


library_gui = LibraryGUI('library.db')
library_gui.run()
