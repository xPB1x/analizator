from bs4 import BeautifulSoup
from functions import substraction_time, find_first_control
from splits.splits_sportorg import SplitSportorg


class SplitsSportorgDirection(SplitSportorg):
    def __init__(self, html):
        super().__init__(html)

    def get_groups(self):
        """Получает код-html каждой группы"""
        groups = {}
        group_names = [a['id'] for a in self.soup.select('div#results-tables h2') if a.text]
        group_html = self.soup.select('table.sportorg-table > tbody')
        for group_name, group in zip(group_names, group_html):
            groups[group_name] = group

        return groups

    def get_group_splits(self, group_name):
        pass

    def get_person_splits(self, group_name, person_name):
        sportsman = {}
        sportsman[person_name] = {}
        group_html = self.groups[group_name]
        children = group_html.children
        legs = self.get_group_splits(group_name)

        x = 1
        for child in children:
            last_control = 'Start'
            person_info = child.get_text(separator='  ').split('  ')
            if len(person_info) <= 1:
                x = 0
                continue
            if person_info[x] == person_name:
                first_control_index = find_first_control(person_info)
                if first_control_index:
                    i = 0
                    for i in range(first_control_index, len(person_info), 2):
                        time = person_info[i][:8]
                        leg = legs[i]
                        sportsman[person_name][leg] = time
                        i += 1
                    break
        return sportsman