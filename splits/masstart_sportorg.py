import re

from bs4 import BeautifulSoup

from splits.splits_sportorg import SplitSportorg
from functions import substraction_time, find_first_control


class MasStartSportorg(SplitSportorg):
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'lxml')
        self.groups = self.get_groups()


    def get_groups(self):
        """Получает код-html каждой группы"""
        groups = {}
        group_names = [a['id'] for a in self.soup.select('div#results-tables h2') if a.text]
        group_html = self.soup.select('table.sportorg-table > tbody')
        for group_name, group in zip(group_names, group_html):
            groups[group_name] = group

        return groups


    def get_group_legs(self, group_name):
        group_legs = []
        group_html = self.groups[group_name]
        children = group_html.children
        for child in children:
            person_info = child.get_text(separator='  ').split('  ')
            name = person_info[1]
            print(name)
            first_control_index = find_first_control(person_info)
            for i in range(first_control_index, len(person_info), 3):
                print(person_info[i], person_info[i+1])

    def get_person_splits(self, group_name, person_name):
        sportsman = {}
        sportsman[person_name] = {}
        group_html = self.groups[group_name]
        children = group_html.children

        x = 1
        for child in children:
            last_control = 'Start'
            person_info = child.get_text(separator='  ').split('  ')
            if len(person_info) <= 1:
                x = 0
                continue
            if person_name == person_info[x]:
                first_control_index = find_first_control(person_info)
                if first_control_index:
                    for i in range(first_control_index, len(person_info), 3):
                        current_control = person_info[i][1:-1].strip()
                        time = person_info[i + 1]

                        leg = f"{last_control} -> {current_control}"
                        sportsman[person_name][leg] = time
                        last_control = current_control
                    break

        return sportsman

    def get_persons_by_group(self, group_name):
        persons = []
        group_html = self.groups[group_name]
        children = group_html.children
        x = 1
        for child in children:
            person_info = child.get_text(separator='  ').split('  ')
            if len(person_info) <= 1:
                x = 0
                continue

            persons.append(person_info[x])

        return persons

    def get_group_splits(self, group_name):
        splits = []
        persons = self.get_persons_by_group(group_name)
        for person_name in persons:
            person_splits = self.get_person_splits(group_name, person_name)[person_name]
            for split in person_splits.keys():
                if split not in splits:
                    splits.append(split)

        return splits

    def get_legs(self):
        splits = set()

        groups = self.groups
        for group_name in groups:
            splits = splits | set(self.get_group_splits(group_name))

        return sorted(list(splits))

    def make_best_split(self, group_name):
        group_splits = self.get_group_splits(group_name)
        best_split = {leg: "99:99:99" for leg in group_splits}

        persons = self.get_persons_by_group(group_name)
        for person in persons:
            person_splits = self.get_person_splits(group_name, person)
            for split in person_splits.values():
                for number, time in split.items():
                    try:
                        if time < best_split[number]:
                            best_split[number] = time
                    except KeyError:
                        if '\r' in number:
                            number = number.split('\r')[0].strip()
                            if time < best_split[number]:
                                best_split[number] = time
        return best_split

    def make_person_report(self, group_name, person_name):
        report = f"{person_name}\n"
        i = 1

        best_split = self.make_best_split(group_name)
        person_splits = self.get_person_splits(group_name, person_name)[person_name]

        for leg, time in person_splits.items():
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

