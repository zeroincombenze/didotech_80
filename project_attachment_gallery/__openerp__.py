# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Project Gallery',
    'version': '0.1',
    'category': 'Project/Tools',
    'sequence': 2,
    'summary': 'Project Attachment Gallery',
    'description': """
The module provide the gallery view of project images and documents and also same for task and issues
""",
    'author': 'Denero Team',
    'website': 'http://www.deneroteam.com',
    'depends': [
        'project',
        'project_issue',
        'document',
        'web_fancybox',
    ],
    'data': [
        'project_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
