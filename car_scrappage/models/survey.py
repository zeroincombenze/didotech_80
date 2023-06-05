# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, tools, SUPERUSER_ID


class Survey(models.Model):
    _inherit = 'survey.survey'

    def action_start_survey(self, cr, uid, ids, context=None):
        ''' Open the website page with the survey form '''
        trail = ""
        context = dict(context or {}, relative_url=True)
        if 'survey_token' in context:
            trail = "/" + context['survey_token']
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'new',
            'url': self.read(cr, uid, ids, ['public_url'], context=context)[0]['public_url'] + trail
        }

    def action_print_survey(self, cr, uid, ids, context=None):
        ''' Open the website page with the survey printable view '''
        trail = ""
        context = dict(context or {}, relative_url=True)
        if 'survey_token' in context:
            trail = "/" + context['survey_token']
        return {
            'type': 'ir.actions.act_url',
            'name': "Print Survey",
            'target': 'new',
            'url': self.read(cr, uid, ids, ['print_url'], context=context)[0]['print_url'] + trail
        }
