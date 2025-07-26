import re
from bs4 import BeautifulSoup
from functions import sum_time, substraction_time


class SplitsWinOrient:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.groups = self.get_groups()

    def get_groups(self): # +
        """Получает код-html каждой группы"""
        groups = {}
        group_names = [h2.text.split(',')[0] for h2 in self.soup.findAll('h2')]
        group_data = self.soup.select('body > pre')
        for group_name, group in zip(group_names, group_data[:-1]):
            groups[group_name] = group

        return groups

    def get_legs(self):
        groups = self.groups
        splits = set()
        for group_name in groups:
            splits = splits | set(self.get_group_splits(group_name))

        return sorted(list(splits))

    def get_persons_by_group(self, group_name): # +
        """Возвращает список имен участников группы"""
        persons = []
        group_html = self.groups[group_name]
        children = group_html.children
        for child in children:
            if child.name == 'u':
                continue
            child = [x.strip() for x in child.text.strip().split('   ') if x != '']
            for x in child:
                if re.search(r'\d+\s+[А-Я][а-я]+\s+[А-Я][а-я]', x):
                    current_name = ' '.join(x.split()[1:]).strip()
                    persons.append(current_name)

        return persons

    def get_person_splits(self, group_name, name): # +
        """Создает словарь, с информацией о спортсмене и его отметках"""
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
                if re.search(r'\d+\s+[А-Я][а-я]+\s+[А-Я][а-я]', x):
                    current_name = ' '.join(x.split()[1:]).strip()
                    if current_name == name:
                        sportsman[current_name] = {}
                if current_name != name:
                    continue
                if re.search(r'\(\s*\d+\)\(\s*\d+\)', x):
                    cur_splits = [y.split() for y in x.split(')  ')]
                    for split in cur_splits:
                        if len(split) == 3:
                            time = split[0][:-1]
                            number = split[1][:-2]
                        elif len(split) == 2:
                            split = split[0].replace(')', '').replace('(', ' ').strip()
                            try:
                                time, number = split.split()
                            except ValueError:
                                continue
                        else:
                            time = split[0]
                            number = 'Finish'
                        leg = f"{last_control} -> {number}"
                        last_control = number
                        time = time.replace('(', '')
                        if len(time) == 4:
                            time = "00:0" + time

                        sportsman[current_name][leg] = time

                elif re.search(r'\d:\d\d', x):
                    if len(x) == 4:
                        time = x
                        number = 'Finish'
                        leg = f"{last_control} -> {number}"
                        last_control = number
                        time = time.replace('(', '')
                        if len(time) == 4:
                            time = "00:0" + time

                        sportsman[current_name][leg] = time
                    else:
                        continue


        return sportsman

    def get_group_splits(self, group_name): # +
        """Ищет порядок прохождения дистанции по названию группы"""
        group = self.groups[group_name]
        head = group.select_one('u > b').text
        return self.get_number_controls(head.split('('))

    @staticmethod
    def get_number_controls(controls): # +
        """Список для вывода перегонов пользователю формат 'КП1 -> КП2'"""

        control_list = []
        last_control = None

        for control in controls:
            if control[:3].strip().isdigit():
                control = control[:3].strip()
                if last_control is None:
                    control_list.append(f"Start -> {control}")
                    last_control = control
                else:
                    control_list.append(f"{last_control} -> {control}")
                    last_control = control

        control_list.append(f"{last_control} -> Finish")
        return control_list

    def make_best_split(self, group_name): # +
        group = self.groups[group_name]
        group_splits = self.get_group_splits(group_name)
        best_split = {number: "99:99:99" for number in group_splits}

        children = group.children
        for child in children:
            if child.name == 'u':
                last_control = 'Start'
                continue

            child = [x.strip() for x in child.text.strip().split('   ') if x != '']
            for x in child:
                if re.search(r'\(\s*\d+\)\(\s*\d+\)', x):
                    cur_splits = [y.split() for y in x.split(')(')]
                    for split in cur_splits:
                        if len(split) == 3 and split[-1].isdigit():
                            time = split[1][:8]
                            number = split[2]
                        elif len(split) == 2:
                            if split[-1].isdigit():
                                time = split[0][:8]
                                number = split[1]
                            elif '(' in split[1]:
                                time = split[1][:8]
                                number = split[1].split('(')[1]
                            else:
                                time = split[1]
                                number = 'Finish'
                        elif len(split) == 1 and len(split[0]) > 7:
                            if len(split[0]) == 8:
                                time = split[0]
                                number = 'Finish'
                            else:
                                time = split[0][:8]
                                number = split[0].split('(')[1]
                        else:
                            continue

                        time = time.replace('(', '')
                        if len(time) == 4:
                            time = "00:0" + time

                        leg = f"{last_control} -> {number}"
                        try:
                            if time < best_split[leg]:
                                best_split[leg] = time
                            last_control = number
                        except KeyError:
                            continue

        return best_split


    def make_person_report(self, group_name, person_name): # +
        """Создает отчет о прохождение спортсменом дистанции с проигрышем на каждом КП"""
        report = ""
        group = self.groups[group_name]
        i = 1
        flag = True
        current_name = None
        best_split = self.make_best_split(group_name)
        children = group.children
        for child in children:
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
                    flag = False
                    if re.search(r'\(\s*\d+\)\(\s*\d+\)', x):
                        cur_splits = [y.split() for y in x.split(')(')]
                        for split in cur_splits:
                            if len(split) == 3 and split[-1].isdigit():
                                time = split[1][:8]
                                number = split[2]
                            elif len(split) == 2:
                                if split[-1].isdigit():
                                    time = split[0][:8]
                                    number = split[1]
                                elif '(' in split[1]:
                                    time = split[1][:8]
                                    number = split[1].split('(')[1]
                                else:
                                    time = split[1]
                                    number = 'Finish'
                            elif len(split) == 1 and len(split[0]) > 7:
                                if len(split[0]) == 8:
                                    time = split[0]
                                    number = 'Finish'
                                else:
                                    time = split[0][:8]
                                    number = split[0].split('(')[1]
                            else:
                                continue

                            time = time.replace('(', '')
                            leg = f"{last_control} -> {number}"
                            last_control = number
                            if len(time) == 4:
                                time = '00:0' + time

                            try:
                                diff = substraction_time(time, best_split[leg])
                            except KeyError:
                                continue


                            h, m, s = [int(x) for x in diff.split(':')]
                            if h == 0:
                                if m == 0:
                                    if s == 0:
                                        report += f'{i}КП №{number}: Вы лидер\n'
                                    else:
                                        report += f'{i}КП №{number}: +{s}sec\n'
                                else:
                                    report += f'{i}КП №{number}: +{m}min {s}sec\n'
                            else:
                                report += f'{i}КП №{number}: +{h}h {m}min {s}sec\n'
                            i += 1

        report += info
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
                if leg == search_leg:
                    top10 = self.check_top_time(top10, time, person)

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


    def get_top10_on_leg(self, search_leg):
        report = ""
        top10 = [{f'99:99:0{i}': []} for i in range(10)]
        groups = self.find_groups_by_leg(search_leg)
        for group_name in groups:
            persons = self.get_persons_by_group(group_name)
            for person in persons:
                person_splits = self.get_person_splits(group_name, person)[person]
                for leg, time in person_splits.items():
                    if leg == search_leg:
                        top10 = self.check_top_time(top10, time, person)

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

    def check_top_time(self, top, time, name): # +
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
                    top[index] = top[index - 1]
                    index -= 1
                if i < 9:
                    top[i + 1] = 0
                break

            elif time < time_top:
                top[-1] = 0
                index = 9
                while index > i:
                    top[index] = top[index - 1]
                    index -= 1
                top[i] = {time: [name]}
                break

        return top
