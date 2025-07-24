import re
from splits.splits_winorient import SplitsWinOrient
from functions import substraction_time


class MasStartWinOrient(SplitsWinOrient):
    def init(self, html):
        """
        Полностью наследует методы
        - get_groups
        - get_persons_by_group
        - check_top_time
        """
        super().__init__(html)

    def get_legs(self):
        groups = self.groups
        splits = set()
        for group_name in groups:
            splits = splits | set(self.get_group_splits(group_name))

        return sorted(list(splits))

    def get_person_splits(self, group_name, name):
        sportsman = {}
        group_html = self.groups[group_name]
        children = group_html.children
        for child in children:
            if child == '\n':
                continue
            if child.name == 'u':
                last_control = 'Start'
                current_name = None
                continue
            child = [x.strip() for x in child.text.strip().split('   ') if x != '']

            for x in child:
                if re.search(r'\d+\s+[А-Я][а-я]+\s+[А-Я][а-я]\s*[А-Я]*', x):
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

                        leg = f"{last_control} -> {number}"
                        sportsman[current_name][leg] = time
                        last_control = number
        return sportsman

    def get_group_splits(self, group_name):
        persons = self.get_persons_by_group(group_name)
        legs = []
        for person in persons:
            last_control = 'Start'
            values = self.get_person_splits(group_name, person).values()
            for splits in values:
                for split in splits:
                    number = split.split()[-1]
                    leg = f"{last_control} -> {number}"
                    if leg not in legs:
                        legs.append(leg)

                    last_control = number

        return legs

    def make_best_split(self, group_name):
        group_html = self.groups[group_name]
        group_splits = self.get_group_splits(group_name)
        best_split = {leg: "99:99:99" for leg in group_splits}

        children = group_html.children
        for child in children:
            if child.name == 'u':
                last_control = 'Start'
                continue

            splits = [x.strip() for x in child.text.strip().split('   ') if x != '']
            if splits:
                splits = splits[-1].split(') ')
                for split in splits:
                    if '(' in split:
                        time = split[:8]
                        number = split.split('(')[1].strip()
                    else:
                        time = split
                        number = 'Finish'

                    leg = f"{last_control} -> {number}"
                    try:
                        if time < best_split[leg]:
                            best_split[leg] = time
                        last_control = number
                    except KeyError:
                        continue

        return best_split


    def make_person_report(self, group_name, person_name):
        report = ""
        i = 1
        flag = True
        group_html = self.groups[group_name]

        best_split = self.make_best_split(group_name)
        person_splits = self.get_person_splits(group_name, person_name)[person_name]

        children = group_html.children
        for child in children:
            if not flag:
                break
            if child.name == 'u':
                last_control = 'Start'
                continue
            child = [x.strip() for x in child.text.strip().split('   ') if x != '']
            for x in child:
                if re.search(r'\d+\s+[А-Я][а-я]+\s+[А-Я][а-я]', x):
                    current_name = ' '.join(x.split()[1:]).strip()
                    if flag:
                        info = ' '.join(child[:5])
                if current_name == person_name:
                    info = ' '.join(child[:-1])
                    flag = False
                    break

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

        report += info
        return report
