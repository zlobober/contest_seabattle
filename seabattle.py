#!/usr/bin/python2
# -*- coding: utf8 -*-

import pcms

class Game:
    def __init__(self, config):
        self.config = config
        self.fields = [
            self.config.get("team1", "field").strip().split(),
            self.config.get("team2", "field").strip().split(),
        ]
        self.problems = pcms.parse_xml(self.config.get("settings", "xml_url"))["problems"] 
 
    def _build_head(self):
        head = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta http-equiv="content-language" content="ru-ru">
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <p class="header">
            Морской бой. {contest_name}
        </p>
""".format(contest_name=self.config.get("settings", "contest_name"))
        return head 

    def _build_field(self, team, enemy_team, section, enemy_section, reveal):
        field = """
        <div class="results">
            <p class="team_header {self}">{name}</p>
            <table>
                <tr><td class="problem"></td>""".format(name=self.config.get(section, "name"), self="self" if reveal else "")
        for problem in self.problems:
            field += '<td title="{title}" class="problem">{alias}</td>'.format(**problem)
        field += "</tr>\n"

        current_state = pcms.parse_xml(self.config.get("settings", "xml_url"))
        matrix = current_state["matrix"]
        names = current_state["names"]
        for i, contestant_alias in enumerate(self.config.get(enemy_section, "contestant_aliases").split()):
            field += """<tr><td class="name" title="{title}">{alias}</td>""".format(alias=contestant_alias, 
                                                                                    title=names.get(contestant_alias, "Некто без единой посылки"))
            for j, problem in enumerate(self.problems):
                state = matrix.get(contestant_alias, {}).get(problem["alias"], "n/a")
                if reveal and self.fields[team][i][j] == 'X':
                    cls = "ship" if state == "n/a" else "ship_unsuccess" if state == "miss" else "broken"
                else:
                    cls = "unknown" if state == "n/a" else "unsuccess" if state == "miss" else "broken" if self.fields[team][i][j] == 'X' else "empty"
                field += """<td class="map_cell {cls}"></td>""".format(cls=cls)
            field += """</tr>
"""                
        
        unsuccessful_submits = current_state["unsuccessful_submits"]
        total_successful_shot = 0
        total_successful_miss = 0
        total_unsuccessful = 0
        for i, contestant_alias in enumerate(self.config.get(section, "contestant_aliases").split()):
            total_unsuccessful += unsuccessful_submits.get(contestant_alias, 0)
            for j, problem in enumerate(self.problems):
                state = matrix.get(contestant_alias, {}).get(problem["alias"], "n/a")
                if state == "shot":
                    if self.fields[enemy_team][i][j] == 'X':
                        total_successful_shot += 1
                    else:
                        total_successful_miss += 1

        field += """
            </table>
            <ul>
                <li>Успешные попытки: {total_successful}</li>
                <ul>
                    <li>из них в цель: {total_successful_shot}</li>
                    <li>из них мимо: {total_successful_miss}</li>
                </ul>
                <li>Безуспешные попытки: {total_unsuccessful}</li>
            </ul>
        </div>
""".format(total_successful = total_successful_miss + total_successful_shot, total_successful_shot = total_successful_shot,
           total_successful_miss = total_successful_miss, total_unsuccessful = total_unsuccessful)

        return field

    def _build_legend(self):
        return """
        <div class="results">
            <p class="team_header">Легенда</p>
            <table>
                <tr><td class="map_cell unknown"></td><td>Клетка, по которой не стреляли</td></tr>
                <tr><td class="map_cell ship"></td><td>Клетка корабля</td></tr>
                <tr><td class="map_cell unsuccess"></td><td>Клетка, по которой безуспешно пытались стрелять</td></tr>
                <tr><td class="map_cell ship_unsuccess"></td><td>Клетка корабля, по которой неуспешно пытались стрелять</td></tr>
                <tr><td class="map_cell empty"></td><td>&quot;Мимо&quot;</td></tr>
                <tr><td class="map_cell broken"></td><td>&quot;Ранен/убит&quot;</td></tr>
            </table>
        </div>
"""
    
    def _build_body(self, secret):
        reveal = None
        if secret == self.config.get("settings", "secret"):
            reveal = [True, True]
        elif secret == self.config.get("team1", "secret"):
            reveal = [True, False]
        elif secret == self.config.get("team2", "secret"):
            reveal = [False, True]
        else:
            return '<p class="alert">GET-параметр secret не указан или указан неправильно.</p>'
         
        body = ""
        for team in range(2):
            body += self._build_field(team, 1 - team, "team" + str(team + 1), "team" + str(2 - team), reveal[team])
        return body
        

    def _build_tail(self):
        tail = """
    </body>
</html>
"""
        return tail

    def build_html(self, secret):        
        head = self._build_head()
        body = self._build_body(secret)
        legend = self._build_legend()
        tail = self._build_tail()
        return head + body + legend + tail 

