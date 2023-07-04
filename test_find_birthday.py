import unittest

import find_birthday as fb

last = 'Иванов'
first = 'Иван'
middle = 'Иванович'


class TestInitials(unittest.TestCase):
    def test_Initials_correct_creation(self):
        p = fb.Initials(last_name=last, first_name=first, middle_name=middle)
        self.assertEqual(p.last_name, last, "Last name does not match")
        self.assertEqual(p.first_name, first, "First name does not match")
        self.assertEqual(p.middle_name, middle, "Middle name does not match")

    def test_Initials_lowercase_creation(self):
        p = fb.Initials(last_name=last.lower(), first_name=first.lower(), middle_name=middle.lower())
        self.assertEqual(p.last_name, last, "Last name does not match")
        self.assertEqual(p.first_name, first, "First name does not match")
        self.assertEqual(p.middle_name, middle, "Middle name does not match")

    def test_Initials_CAPS_creation(self):
        p = fb.Initials(last_name=last.upper(), first_name=first.upper(), middle_name=middle.upper())
        self.assertEqual(p.last_name, last, "Last name does not match")
        self.assertEqual(p.first_name, first, "First name does not match")
        self.assertEqual(p.middle_name, middle, "Middle name does not match")

    def test_Initials_wrong_input(self):
        self.assertRaises(ValueError, fb.Initials, last_name=last+'123', first_name=first, middle_name=middle)
        self.assertRaises(ValueError, fb.Initials, last_name=last, first_name=first+'&', middle_name=middle)
        self.assertRaises(ValueError, fb.Initials, last_name=last, first_name=first, middle_name='')

    def test_Initials_str_method(self):
        p = fb.Initials(last_name=last, first_name=first, middle_name=middle)
        self.assertEqual(str(p), f"{last} {first} {middle}")

    def test_Initials_buffer_overflow(self):
        self.assertRaises(ValueError, fb.Initials, last_name=last*100 + '123', first_name=first, middle_name=middle)

    def test_Initials_correct_from_input(self):
        ...


years = [2004]
months = [1, 2, 3]
days = [1, 2, 3, 4, 5]


class TestDate(unittest.TestCase):
    def test_Date_correct_creation(self):
        d = fb.Date(range_of_years=years, range_of_months=months, range_of_days=days)
        self.assertEqual(d.range_of_years, years, "Wrong intersection between suitable and default ranges of years")
        self.assertEqual(d.range_of_months, months, "Wrong intersection between suitable and default ranges of months")
        self.assertEqual(d.range_of_days, days, "Wrong intersection between suitable and default ranges of days")

    def test_Date_inf_ranges(self):
        d = fb.Date(range_of_years=[1984, 1988], range_of_months=months, range_of_days=days)
        self.assertEqual(d.range_of_years, fb.Date.DEFAULT['range_of_years'])

        d = fb.Date(range_of_years=years, range_of_months=[0], range_of_days=days)
        self.assertEqual(d.range_of_months, fb.Date.DEFAULT['range_of_months'])

        d = fb.Date(range_of_years=years, range_of_months=months, range_of_days=list(range(-15, -2)))
        self.assertEqual(d.range_of_days, fb.Date.DEFAULT['range_of_days'])

    def test_Date_sup_ranges(self):
        d = fb.Date(range_of_years=[fb.Date.CURRENT_YEAR+3], range_of_months=months, range_of_days=days)
        self.assertEqual(d.range_of_years, fb.Date.DEFAULT['range_of_years'])

        d = fb.Date(range_of_years=years, range_of_months=[14, 15], range_of_days=days)
        self.assertEqual(d.range_of_months, fb.Date.DEFAULT['range_of_months'])

        d = fb.Date(range_of_years=years, range_of_months=months, range_of_days=list(range(33, 88)))
        self.assertEqual(d.range_of_days, fb.Date.DEFAULT['range_of_days'])

    def test_Date_generating_function(self):
        def gen(yr, mnh, dy):
            for x in range(yr + 14, yr + 19 + 1):
                yield fb.dd(yr, mnh, dy), x

        d = fb.Date(range_of_years=[2003], range_of_months=[9], range_of_days=[22])
        expected = [x for x in d.generate_possible_dates()]
        real = [x for x in gen(2003, 9, 22)]
        self.assertEqual(expected, real)

    def test_Date_correct_diapason(self):
        a, b, c1, c2 = 123, 234, 200, 210
        s = f"{a},{b},{c1}-{c2}"
        self.assertEqual(fb.Date.process_diapason(s), [a, b, *[x for x in range(c1, c2+1)]])

    def test_Date_incorrect_diapason(self):
        data = ['123#', 'abc', '20o0', '-', '-2000-1000', '-1,2']
        for s in data:
            self.assertRaises(ValueError, fb.Date.process_diapason, s)

    def test_Date_correct_from_input(self):
        ...


if __name__ == '__main__':
    unittest.main()
