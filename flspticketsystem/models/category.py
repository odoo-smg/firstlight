# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Category(models.Model):
    """
        class_name:Category
        model_name: flspticketsystem.category
        Purpose: To help in creating the category model for the ticketing system
        Date: Sept/4th/2020/Fridays
        Author: Sami Byaruhanga
    """

    _name = 'flspticketsystem.category'
    _description = "Category"

    name = fields.Char(string="Category", required=True)
    description = fields.Text()
