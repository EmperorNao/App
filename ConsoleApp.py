import pandas as pd
import os
from DB import Database


class ConsoleApplication:

    def __init__(self, db: Database, tables=[], additional_queries={}):

        self.active_keys = [str(i) for i in range(0, 10)] + [chr(ch) for ch in range(ord('a'), ord('z') + 1)]

        if len(tables) + len(additional_queries.keys()) > len(self.active_keys):
            raise ValueError("Too much values in tables and queries")

        self.entities = tables
        self.active_keys = [str(i) for i in range(0, 10)] + [chr(ch) for ch in range(ord('a'), ord('z') + 1)]
        self.additional_queries = additional_queries

        self.keys = {self.active_keys[i]: self.entities[i] for i in range(0, len(self.entities))}
        self.keys.update({self.active_keys[len(self.entities) + i]: q
                                     for i, q in enumerate(self.additional_queries.keys())})

        self.quit_char = "*"
        self.use_clear_mode = 0
        self.db = db

    @staticmethod
    def clear_console():
        command = 'clear'
        if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
            command = 'cls'
        os.system(command)

    def generate_text(self):

        out = ["Нажмите соответствующую клавишу для просмотра содержимого таблицы"]
        for k, v in self.keys.items():
            out.append(k + ": " + v)
        out.append(self.quit_char + ": " + "Выход")
        return "\n".join(out)

    def run(self):

        print("Использовать clear-mode? Во время этого режима "
              "консоль будет очищаться после каждого запроса (Y/N)")

        clear_mode = input().lower()[0]
        if clear_mode == "y":
            print("Clear-mode включен")
            self.use_clear_mode = 1
        else:
            print("Clear-mode выключен")

        key = ""
        while True:

            text = self.generate_text()
            print(text)

            key = input()

            if self.use_clear_mode:
                ConsoleApplication.clear_console()

            if key:
                key = key[0]

            if key == self.quit_char:
                break

            if key in self.keys.keys():

                result = {}
                request = self.keys[key]

                if request in self.entities:
                    result = self.db.select_all(request)
                elif request in self.additional_queries.keys():
                    result = self.db.execute(self.additional_queries[request])

                df = pd.DataFrame(result)
                print(df)
                print("Введите Enter для продолжения")
                input()

            else:
                print("Не распознал клавишу, введите ещё раз")
