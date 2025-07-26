from bs4 import BeautifulSoup
from functions import substraction_time, find_first_control2
from splits.sfr_splits import SFRSplits


class SFRMasStart(SFRSplits):
    def init(self, html):
        super().__init__(html)

    def get_person_splits(self, group_name, person_name):
        sportsman = {}
        sportsman[person_name] = {}
        group_html = self.groups[group_name]
        children = group_html.children

        for child in children:
            first = True
            last_control = 'Start'
            person_info = [x for x in child.get_text(separator=';').split(';') if x != '\n']
            if person_info and person_info[2] == person_name:
                first_control_index = find_first_control2(person_info)
                if first_control_index:
                    for i in range(first_control_index, len(person_info), 2):
                        if first:
                            time, current_number = person_info[i].split('[')
                            current_control = current_number[:-1].strip()
                            first = False
                        else:
                            time = person_info[i].strip()
                            current_control = person_info[i-1].split('[')[-1][:-1].strip()
                            if ':' in current_control:
                                current_control = 'Finish'
                        if len(time) == 4:
                            time = "00:0" + time
                        elif len(time) == 5:
                            time = "00:" + time
                        else:
                            last_control = current_control
                            continue
                        leg = f"{last_control} -> {current_control}"
                        last_control = current_control

                        sportsman[person_name][leg] = time

        return sportsman

    def get_group_splits(self, group_name):
        splits = []
        persons = self.get_persons_by_group(group_name)
        for person_name in persons:
            person_splits = self.get_person_splits(group_name, person_name)[person_name]
            for split in person_splits.keys():
                if split not in splits:
                    splits.append(split)

        return splits

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