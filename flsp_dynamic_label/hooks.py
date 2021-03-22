def uninstall_hook(cr, registry):
    """
    Purpose: To remove all the actions created for the models
    """
    cr.execute("select ref_ir_act_report from flsp_dynamic_label")
    label_data = cr.fetchall()
    if label_data:
        value_list = [rec[0] for rec in label_data]
        cr.execute("delete from ir_act_window where id in %s", (tuple(value_list),))
        cr.execute("delete from ir_actions where id in %s", (tuple(value_list),))
