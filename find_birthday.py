import hashlib
import asyncio

from dataclasses import dataclass, field
from typing import ClassVar
from datetime import date as dd

import aiohttp

URL = 'https://diploma.rsr-olymp.ru/files/rsosh-diplomas-static/compiled-storage-{}/by-person-released/{}/codes.js'


def sha256(s):
    hash_obj = hashlib.sha256(s.encode('utf-8'))
    hash_value = hash_obj.hexdigest()
    return hash_value


# field(validator=validators.matches_re(regex="[A-ZА-Я][A-Za-zА-Яа-я]+"))
@dataclass(slots=False)
class Initials:
    last_name: str
    first_name: str
    middle_name: str

    def __post_init__(self) -> None:
        # Finding every *_name field and validating their values
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                value = getattr(self, attr)

                if isinstance(value, str) and attr.endswith("_name"):
                    # Check if it contains only letters
                    if not value.isalpha():
                        raise ValueError('ФИО должно содержать только буквы')
                    # Convert to standard name convention
                    setattr(self, attr, value.title())

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    @classmethod
    def create_from_input(cls):
        fields = {
            'last': "Введите фамилию: ",
            'first': "Введите имя: ",
            'middle': "Введите отчество: ",
        }
        answers = {}

        while True:
            for name, descr in fields.items():
                answers[name] = str(input(descr)).title()
            try:
                initials = Initials(*answers.values())
                return initials
            except ValueError as e:
                print(e)


@dataclass(slots=False)
class Date:
    CURRENT_YEAR: ClassVar = dd.today().year
    DEFAULT: ClassVar = {
        'range_of_years': range(2000, CURRENT_YEAR + 1),
        'range_of_months': range(1, 12 + 1),
        'range_of_days': range(1, 31 + 1)
    }

    range_of_years: list[dd.year] = DEFAULT['range_of_years']
    range_of_months: list[dd.month] = DEFAULT['range_of_months']
    range_of_days: list[dd.day] = DEFAULT['range_of_days']

    tracked_diploma_years: list[dd.year] = field(init=False, default=range(2014, CURRENT_YEAR + 1))
    possible_birthday: set[str] = field(init=False, default_factory=set)

    def __post_init__(self):
        # Finding every range_of field and intersect them with allowed range
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                value = getattr(self, attr)

                if isinstance(value, list) and attr.startswith("range_"):
                    setattr(self, attr, [x for x in value if x in Date.DEFAULT[attr]])
                    if not getattr(self, attr):
                        setattr(self, attr, Date.DEFAULT[attr])

        min_dp_year = min(max(min(self.range_of_years) + 14, 2014), Date.CURRENT_YEAR)
        max_dp_year = min(max(self.range_of_years) + 19, Date.CURRENT_YEAR)
        self.tracked_diploma_years = list(range(min_dp_year, max_dp_year + 1))

    def generate_possible_dates(self):
        """
        Generate all possible dates, with assumption that year of receiving
        the diploma presumably lies in the period of 8-11 grade
        """
        for y in self.range_of_years:
            for dy in self.tracked_diploma_years:
                for m in self.range_of_months:
                    for d in self.range_of_days:
                        try:
                            yield dd(y, m, d), dy
                        except ValueError:
                            continue

    def add_suitable_date(self, date: dd):
        self.possible_birthday.add(date.isoformat())

    @staticmethod
    def process_diapason(s: str) -> [int]:
        numbers = []

        if len(s) == 0:
            return numbers

        for n in s.strip().split(','):
            if n.isdigit():
                numbers += [int(n)]
            elif '-' in n:
                l, r = n.split('-')
                if l.isdigit() and r.isdigit():
                    numbers += range(int(l), int(r) + 1)
                else:
                    raise ValueError('Диапазоны должны быть корректными')

            else:
                raise ValueError('В диапазонах должны быть числа')

        return numbers

    @classmethod
    def create_from_input(cls):
        fields = {
            'years': "Диапазон года рождения: ",
            'months': "Диапазон месяца рождения: ",
            'days': "Диапазон дня рождения:"
        }
        answers = {}

        print('Диапазон чисел вводится через \'-\', числа вводятся через запятую\n'
              'Пример 1: 2003-2004, 2006  Пример 2: 2002\n'
              'Для пропуска ввода нажмите ENTER \nРекомендуется ввести хотя бы диапазон лет, '
              'иначе поиск может затянуться')
        while True:
            try:
                for name, descr in fields.items():
                    answers[name] = Date.process_diapason(str(input(descr)))

                date = Date(*answers.values())
                return date
            except ValueError as e:
                print(e)


@dataclass(slots=False)
class Person:
    full_name: Initials
    probable_dates: Date

    def get_tasks(self, session: aiohttp.ClientSession) -> list:
        tasks = []

        for date, diploma_year in self.probable_dates.generate_possible_dates():
            name_string = str(self.full_name) + ' ' + date.isoformat()
            hash_string = sha256(name_string)

            tasks += [session.get(URL.format(diploma_year, hash_string))]

        return tasks

    async def bruteforce_birthday_date(self):
        async with aiohttp.ClientSession() as session:
            tasks = self.get_tasks(session)

            responses = await asyncio.gather(*tasks)
            for resp, date in zip(responses, self.probable_dates.generate_possible_dates()):
                if resp.ok:
                    self.probable_dates.add_suitable_date(date[0])

    def find_birthday(self) -> None:
        try:
            asyncio.run(self.bruteforce_birthday_date())

            bd = self.probable_dates.possible_birthday

            if len(bd) == 1:
                print(f"Возможная дата дня рождения: {bd}")
            elif len(bd) > 1:
                print(f"Возможные даты дня рождения: {bd}, нашлись полные тезки!")
            else:
                print("Ничего не нашлось :(")
        except aiohttp.ClientConnectorError:
            print('Ошибка сети. Проверьте подключение к интернету')


def main():
    initials = Initials.create_from_input()
    date = Date.create_from_input()

    p = Person(initials, date)
    p.find_birthday()


if __name__ == '__main__':
    main()
