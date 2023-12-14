# -*- coding: utf-8 -*-
from odoo import models, fields


class HrAttendance(models.Model):
    """ Override HrAttendance class in order to add new fields
        project_id, task_id, check_in_description, check_out_description
    """
    _inherit = "hr.attendance"

    project_id = fields.Many2one('project.project', string="Project")
    task_id = fields.Many2one('project.task', string="Task")
    check_in_description = fields.Char(string="Check In Description")
    check_out_description = fields.Char(string="Check Out Description")
