import re
from splits.splits_winorient import SplitsWinOrient
from functions import substraction_time



class RelayWinOrient(SplitsWinOrient):
    def init(self, html):
        """
        Полностью наследует методы
        - get_groups
        - get_persons_by_group
        - check_top_time
        """
        super().__init__(html)

    def get_persons_by_group(self, group_name): # +
        """Возвращает список имен участников группы"""
        persons = []
        group_html = self.groups[group_name]
        children = group_html.children
        for child in children:
            if child.name == 'b':
                continue
            child = [x.strip() for x in child.text.strip().split('  ') if x != '']
            for x in child:
                if re.search(r'\d*\s*[А-Я][а-я]+\s+[А-Я][а-я]', x):
                    if len(x.split()) == 2:
                        current_name = x
                    else:
                        current_name = ' '.join(x.split()[1:]).strip()
                    persons.append(current_name)

        return persons

    def get_person_splits(self, group_name, name):
        sportsman = {}
        group_html = self.groups[group_name]
        children = group_html.children
        for child in children:
            if child.text.strip() == '':
                continue
            if child.name == 'b':
                last_control = 'Start'
                current_name = None
                continue
            child = [x.strip() for x in child.text.strip().split('  ') if x != '']

            for x in child:
                if re.search(r'\d*\s*[А-Я][а-я]+\s+[А-Я][а-я]\s*[А-Я]*', x):
                    if len(x.split()) == 2:
                        current_name = x
                    else:
                        current_name = ' '.join(x.split()[1:]).strip()
                    if current_name == name:
                        sportsman[current_name] = {}
                if current_name != name:
                    continue
                if re.search(r'\d\d:\d\d:\d\d\(\s*\d+\)', x):
                    cur_splits = [y for y in x.split(') ')]
                    for split in cur_splits:
                        if '(' in split:
                            time = split[:8]
                            number = split.split('(')[1].strip()
                        else:
                            time = split
                            number = 'Finish'

                        leg = f"{last_control} -> {number}".strip()
                        sportsman[current_name][leg] = time
                        last_control = number

                elif re.search(r'\d:\d\d\(', x):
                    x = x.replace(')', '')
                    time, number = x.split('(')
                    leg = f"{last_control} -> {number.strip()}".strip()
                    last_control = number
                    if len(time) == 4:
                        time = "00:0" + time

                    sportsman[current_name][leg] = time


        return sportsman

    def get_group_splits(self, group_name):
        splits = []
        persons = self.get_persons_by_group(group_name)
        for person_name in persons:
            try:
                person_splits = self.get_person_splits(group_name, person_name)[person_name]
            except:
                continue
            for split in person_splits.keys():
                if split not in splits:
                    splits.append(split)

        return splits

    def get_legs(self):
        groups = self.groups
        splits = set()
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