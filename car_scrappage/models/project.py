# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>)
#
#                       All Rights Reserved
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
# #############################################################################

from openerp import models, fields, api, tools, SUPERUSER_ID
from openerp.tools.translate import _


class ProjectProjectType(models.Model):
    _name = 'project.project.type'
    _description = 'Stage of Scrappage'
    _order = 'sequence'

    name = fields.Char(_('Identification Number'), size=128)
    description = fields.Char(_('Description'))
    close = fields.Boolean(_('Close Project'))
    sequence = fields.Integer('Sequence')
    fold = fields.Boolean(_('Folded in Kanban View'))


class ProjectProject(models.Model):
    _inherit = 'project.project'

    dossier_number = fields.Char(_('Dossier number'), size=64)
    car_color = fields.Char(_('Car color'), size=32)
    stage_id = fields.Many2one('project.project.type', 'Stage', track_visibility='onchange', select=True, copy=False)
    doc_number = fields.Char(_('Document Number'))
    car_type_id = fields.Many2one('product.category', 'Car Category')
    engine_type = fields.Char(_('Engine Type'))
    survey = fields.Many2one('survey.survey', 'Interview Form', help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job")
    response_id = fields.Many2one('survey.user_input', "Response", ondelete='set null', oldname="response")
    image = fields.Binary(
        "Image",
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    image_medium = fields.Binary(
        compute="_get_image",
        # fnct_inv=_set_image,
        string="Medium-sized image",
        # multi="_get_image",
        # store={
        #     'project.project': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        # },
        help="""Medium-sized image of the product. It is automatically
             resized as a 128x128px image, with aspect ratio preserved,
             only when the image exceeds one of those sizes. Use this field in form views or some kanban views."""
    )
    image_small = fields.Binary(
        compute="_get_image",
        # fnct_inv=_set_image,
        string="Small-sized image",
        # multi="_get_image",
        # store={
        #     'project.project': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        # },
        help="""Small-sized image of the product. It is automatically
             resized as a 64x64px image, with aspect ratio preserved.
             Use this field anywhere a small image is required."""
    )
    has_image = fields.Boolean(compute='_has_image')
    plate = fields.Char(_('Plate'))
    date_registration = fields.Date(_('First Registration date'))
    date_action = fields.Date(_('Action date'))

    @api.one
    def _get_image(self):
        # image = self.pool.get('project.project').browse(self._cr, self._uid, self.id).image
        image_dict = tools.image_get_resized_images(self.image, avoid_resize_medium=True)

        self.image_medium = image_dict['image_medium']
        self.image_small = image_dict['image_small']

    @api.one
    def _has_image(self):
        if self.image:
            self.has_image = True
        else:
            self.has_image = False

    # def _set_image(self, cr, uid, id, name, value, args, context=None):
    #     return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    @api.multi
    def action_start_survey(self):
        applicant = self[0]
        survey_obj = self.pool['survey.survey']
        response_obj = self.env['survey.user_input']
        # create a response and link it to this applicant
        if not applicant.response_id:
            response_id = response_obj.create({'survey_id': applicant.survey.id, 'partner_id': applicant.partner_id.id})
            self.write({'response_id': response_id.id})
        else:
            response_id = applicant.response_id

        # grab the token of the response and start surveying
        response = response_obj.browse(response_id.id)

        context = {'survey_token': response.token}
        return survey_obj.action_start_survey(self._cr, self._uid, [applicant.survey.id], context=context)

    @api.multi
    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        applicant = self[0]
        survey_obj = self.pool['survey.survey']
        if not applicant.response_id:
            return survey_obj.action_print_survey(self._cr, self._uid, [applicant.survey.id])
        else:
            response = applicant.response_id
            context = {'survey_token': response.token}
        return survey_obj.action_print_survey(self._cr, self._uid, [applicant.survey.id], context=context)

    @api.multi
    def action_dummy(self):
        return True

    @api.onchange(
        'stage_id'
    )
    def onchange_stage_id(self):
        if self.stage_id.close:
            self.set_done()

    def default_get(self, cr, uid, fields, context=None):
        result = super(ProjectProject, self).default_get(cr, uid, fields, context=context)
        project_project_type_ids = self.pool['project.project.type'].search(cr, uid, [], context=context)
        if project_project_type_ids:
            result['stage_id'] = project_project_type_ids[0]
        result['use_tasks'] = False
        result['use_issues'] = False
        return result
