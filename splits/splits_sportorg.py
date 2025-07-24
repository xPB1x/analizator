from bs4 import BeautifulSoup
from functions import substraction_time


class SplitSportorg:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'lxml')
        self.groups = self.get_groups() #  Список html-кодов каждой группы

    def get_groups(self):
        """Получает код-html каждой группы"""
        groups = {}
        group_names = [a['id'] for a in self.soup.select('div#results-tables h2') if a.text]
        group_html = self.soup.select('table.sportorg-table')
        for group_name, group in zip(group_names, group_html):
            groups[group_name] = group

        return groups

    def get_persons_by_group(self, group_name):
        """Создаёт словарь спортсменов с их html строкой"""
        group = self.groups[group_name]
        person_names = [td.text for td in group.select('table.sportorg-table td:nth-child(2)')]

        return person_names

    def get_legs(self):
        groups = self.groups
        splits = set()
        for group_name in groups.keys():
            splits = splits | set(self.get_group_splits(group_name))

    def get_group_splits(self, group_name):
        """Ищет порядок прохождения дистанции по названию группы"""
        group = self.groups[group_name]
        thead = group.select('thead th')

        return self.get_number_controls(thead)

    @staticmethod
    def get_number_controls(controls):
        """2)Собирает список номеров правильного прохождения дистанции"""
        control_list = []
        last_control = 'Start'

        for control in controls:
            if control.text.isdigit() or control.text.strip() == 'F':
                leg = f"{last_control} -> {control.text}"
                control_list.append(leg)
                last_control = control.text

        return control_list


    def get_person_splits(self, group_name, person_name):
        sportsman = {}
        sportsman[person_name] = {}
        group_html = self.groups[group_name]
        group_legs = self.get_group_splits(group_name)
        persons = group_html.select('table.sportorg-table > tbody > tr')
        for person in persons:
            if person.select_one('tr > td:nth-child(2)').text.strip() == person_name:
                splits = person.select('table.table-split tr:nth-child(1)')
                for split, leg in zip(splits, group_legs):
                    sportsman[person_name][leg] = split.text.strip()

        return sportsman


    def make_best_split(self, group_name):
        """Создаёт лучший сплит в группе"""
        group_splits = self.get_group_splits(group_name)
        best_split = {leg: "99:99:99" for leg in group_splits}
        persons = self.get_persons_by_group(group_name)

        for person in persons:
            person_splits = self.get_person_splits(group_name, person)
            for split in person_splits.values():
                for number, time in split.items():
                    try:
                        time, place = time.split()
                        place = int(place[1:-1].strip())
                    except ValueError:
                        place = 2

                    if place == 1:
                        try:
                            if time < best_split[number]:
                                best_split[number] = time
                        except KeyError:
                            if '\r' in number:
                                number = number.split('\r')[0].strip()
                                if time < best_split[number]:
                                    best_split[number] = time


                    elif 'F' in number:
                        if time < best_split[number]:
                            best_split[number] = time

        return best_split

    def make_person_report(self, group_name, person_name):
        report = f"{person_name}\n"
        i = 1

        best_split = self.make_best_split(group_name)
        person_splits = self.get_person_splits(group_name, person_name)[person_name]

        for leg, time in person_splits.items():
            time = time[:8]
            try:
                diff = substraction_time(time, best_split[leg])
            except KeyError:
                continue

            h, m, s = [int(x) for x in diff.split(':')]
            if h == 0:
                if m == 0:
                    if s == 0:
                        report += f'{i} перегон {leg}: Вы лидер\n'
                    else:
                        report += f'{i} перегон {leg}: +{s}sec\n'
                else:
                    report += f'{i} перегон {leg}: +{m}min {s}sec\n'
            else:
                report += f'{i} перегон {leg}: +{h}h {m}min {s}sec\n'
            i += 1

        return report


    def get_top10_on_each_leg_group(self, group_name):
        report = ""
        controls = self.get_group_splits(group_name)
        for control in controls:
            report += self.get_top10_on_leg_in_group(group_name, control)
            report += '***\n'

        return report

    def get_top10_on_leg_in_group(self, group_name, search_leg):
        report = ""
        top10 = [{f"99:99:0{i}": []} for i in range(10)]
        persons = self.get_persons_by_group(group_name)
        for person in persons:
            person_splits = self.get_person_splits(group_name, person)[person]
            for leg, time in person_splits.items():
                if len(time.strip()) > 8:
                    time, place = time.split()
                    place = int(place[1:-1].strip())
                else:
                    place = 0

                if leg == search_leg and place <= 10:
                    top10 = self.check_top_time(top10, time, person)
                    break

        report += f"{search_leg}\n"

        for i, inf in enumerate(top10):
            if inf == 0:
                continue
            time = [x for x in inf.keys()][0]
            if time[0] == '9':
                continue
            names = '\n                     '.join([name for name in inf[time]])
            report += f"{i + 1} {time} {names}\n"

        return report


    def get_top10_on_leg(self, search_leg):
        report = ""
        top10 = [{f'99:99:0{i}': []} for i in range(10)]
        groups = self.find_groups_by_leg(search_leg)
        for group_name in groups:
            persons = self.get_persons_by_group(group_name)
            for person in persons:
                person_splits = self.get_person_splits(group_name, person)[person]
                for leg, time in person_splits.items():
                    if len(time.strip()) > 8:
                        time, place = time.split()
                        place = int(place[1:-1].strip())
                    else:
                        place = 0
                    if leg == search_leg and place <= 10:
                        top10 = self.check_top_time(top10, time, person)
                        break

        report += f"{search_leg}\n"

        for i, inf in enumerate(top10):
            if inf == 0:
                continue
            time = [x for x in inf.keys()][0]
            if time[0] == '9':
                continue
            names = '\n                     '.join([name for name in inf[time]])
            report += f"{i + 1} {time} {names}\n"

        return report

    def find_groups_by_leg(self, leg):
        groups = []
        for group_name, group_html in self.groups.items():
            splits = self.get_group_splits(group_name)
            if leg in splits:
                groups.append(group_name)

        return groups

    @staticmethod
    def check_top_time(top, time, name):
        last = -1
        while True:
            if top[last] != 0:
                break
            last -= 1

        if time > [x for x in top[last].keys()][-1]:
            return top

        for i, place in enumerate(top):
            if place == 0:
                continue
            time_top = [x for x in place.keys()][0]

            if time == time_top:
                place[time_top].append(name)
                index = 9
                while index > i:
                    top[index] = top[index-1]
                    index -= 1
                if i < 9:
                    top[i+1] = 0
                break

            elif time < time_top:
                top[-1] = 0
                index = 9
                while index > i:
                    top[index] = top[index-1]
                    index -= 1
                top[i] = {time: [name]}
                break

        return top



