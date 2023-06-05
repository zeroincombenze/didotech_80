# -*- coding: utf-8 -*-
# © 2017 Didotech srl (http://www.didotech.com).
# © Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import math


class ProjectTaskWork(models.Model):
    _inherit = 'project.task.work'

    @api.multi
    def get_date(self):
        for work in self:
            return datetime.datetime.strptime(
                work.date, DEFAULT_SERVER_DATETIME_FORMAT).date().strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.multi
    def get_time(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return '{}:{:0>2d}'.format(factor * int(math.floor(val)), int(round((val % 1) * 60)))


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def get_time(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return '{}:{:0>2d}'.format(factor * int(math.floor(val)), int(round((val % 1) * 60)))
