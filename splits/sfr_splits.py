from bs4 import BeautifulSoup
from functions import substraction_time, find_first_control


class SFRSplits:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.groups = self.get_groups()

    def get_groups(self):
        groups = {}
        headers = self.soup.select('h2')
        groups_html = self.soup.select('table.rezult')
        for header, html in zip(headers, groups_html):
            groups[header.text] = html

        return groups

    def get_persons_by_group(self, group_name):
        persons = []
        group_html = self.groups[group_name]
        children = group_html.children
        flag = True
        for child in children:
            person_info = [x for x in child.get_text(separator=';').split(';') if x != '\n']
            if person_info:
                if flag:
                    flag = False
                    continue
                persons.append(person_info[2])

        return persons

    def get_person_splits(self, group_name, person_name):
        sportsman = {}
        sportsman[person_name] = {}
        group_html = self.groups[group_name]
        children = group_html.children

        times = []
        legs = []

        flag = True
        for child in children:
            last_control = 'Start'
            person_info = [x for x in child.get_text(separator=';').split(';') if x != '\n']
            if person_info:
                if flag:
                    flag = False
                    first_control = find_first_control(person_info)
                    for i in range(first_control, len(person_info)):
                        current_control = person_info[i].split('(')[-1].strip()[:-1]
                        if current_control == '240':
                            current_control = 'Finish'
                        leg = f"{last_control} -> {current_control}"
                        legs.append(leg)
                        last_control = current_control
                else:
                    if person_info[2] == person_name:
                        first_control = find_first_control(person_info)
                        for i in range(first_control, len(person_info), 2):
                            time = person_info[i].split('(')[0]
                            if len(time) == 4:
                                time = "00:0" + time
                            elif len(time) == 5:
                                time = "00:" + time
                            times.append(time)

        for time, leg in zip(times, legs):
            sportsman[person_name][leg] = time

        return sportsman

    def get_group_splits(self, group_name):
        group_html = self.groups[group_name]
        children = group_html.children

        legs = []

        flag = True
        for child in children:
            last_control = 'Start'
            person_info = [x for x in child.get_text(separator=';').split(';') if x != '\n']
            if person_info:
                if flag:
                    flag = False
                    first_control = find_first_control(person_info)
                    for i in range(first_control, len(person_info)):
                        current_control = person_info[i].split('(')[-1].strip()[:-1]
                        if current_control == '240':
                            current_control = 'Finish'
                        leg = f"{last_control} -> {current_control}"
                        legs.append(leg)
                        last_control = current_control
                break
        return legs

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
