# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Matmoz d.o.o. (<http://www.matmoz.si>)
#
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Operations Management Board',
    'version': '2.0.6',
    'category': 'Board/Projects & Services',
    'description': """
        Central operations dashboard with all main menus
        collected at the same place, a complete view of
        all running tasks, issues, projects, leads,
        helpdesk claims and leads/opportunities on the
        same dash. A way to see what's going on in the
        company.

        The menu is placed under the messaging menu.
    """,
    'author': 'Matmoz d.o.o. (Didotech Group)',
    'website': 'http://www.matmoz.si',
    'license': 'AGPL-3',
    'depends': [
            'crm',
            'board',
            'mail',
            'project',
            'project_issue',
            'hr_timesheet',
            'analytic',
            'web_dashboard_open_action'
    ],
    'data': ['board_ceo_view.xml'],
    'demo': [],
    'test': [],
    'qweb': [],
    'installable': False,
    'auto_install': False,
    'application': False,
}
