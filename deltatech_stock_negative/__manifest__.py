# ©  2008-2021 Deltatech
# See README.rst file on addons root folder for license details

{
    "name": "No Negative Stock",
    "summary": "Negative stocks are not allowed",
    "version": "15.0.2.0.2",
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "category": "Generic Modules/Stock",
    "depends": ["stock"],
    #"depends": ['base', 'mrp', 'stock', 'sale', 'purchase', 'flsp-product', 'flspautomation'],
    "license": "LGPL-3",
    "data": ["views/res_config_view.xml", "views/stock_location_view.xml"],
    "images": ["static/description/main_screenshot.png"],
    "installable": True,
    "development_status": "Mature",
    "maintainers": ["dhongu"],
}
