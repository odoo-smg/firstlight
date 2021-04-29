odoo.define('flsp.tour.customer.badge', function(require) {
"use strict";

var core = require('web.core');
var tour = require('web_tour.tour');

var _t = core._t;

tour.register('badge_create_success', {
    url: "/web",
}, [tour.STEPS.SHOW_APPS_MENU_ITEM, 
    {
    content: _t('Open Sales app'),
    trigger: '.o_app[data-menu-xmlid="sale.sale_menu_root"]',
    position: 'right',
    edition: 'community'
}, {
    content: _t('Open Sales app'),
    trigger: '.o_app[data-menu-xmlid="sale.sale_menu_root"]',
    position: 'bottom',
    edition: 'enterprise'
}, {
    content: _t("Click Menu 'Configuration'"),
    trigger: "li a[data-menu-xmlid='sale.menu_sale_config']",
}, {
    content: _t("Click 'Customer Badges'"),
    trigger: "li a[data-menu-xmlid='flsp-salesorder.customer_badge_menu']",
}, {
    content: _t("Create a new customer badge"),
    extra_trigger: ".o_customer_badge_tree",
    trigger: ".o_list_button_add",
    position: "bottom",
}, {
    content: _t("Write the name of the customer badge"),
    extra_trigger: ".o_customer_badge_form",
    trigger: ".o_field_widget[name='name']",
    position: "bottom",
    run: 'text DemoBadge'
},  {
    trigger: ".o_field_widget[name='reward_level']",
    run: function () {
        var $input = $(".o_field_widget[name='reward_level']");
        $input.find('option')[1].selected=true; 
        $input.trigger("change");
    }
}, {
    content: _t("Input the currency"),
    trigger: ".o_field_widget[name='currency_id'] input",
    run: 'text USD'
}, {
    trigger: ".ui-menu-item > a",
    auto: true,
    in_modal: false,
}, {
    content: _t("Write the Annual Program Spend"),
    trigger: ".o_field_widget[name='annual_program_amount'] input",
    run: 'text 10000'
}, {
    content: _t("Write the Rewards Pricing Discount"),
    trigger: ".o_field_widget[name='sale_discount']",
    run: 'text 5'
}, {
    content: _t("Write the Freight Discount 5-10"),
    trigger: ".o_field_widget[name='freight_units_5_to_10_discount']",
    run: 'text 10'
}, {
    content: _t("Write the Freight Discount >10"),
    trigger: ".o_field_widget[name='freight_units_over_10_discount']",
    run: 'text 15'
}, {
    content: _t("Save the customer badge"),
    trigger: ".o_form_button_save",
    position: "right"
}, {
    content: _t("Check the creation"),
    trigger: "li:contains('DemoBadge')",
}]);


tour.register('badge_create_no_rewardLevel', {
    url: "/web",
}, [tour.STEPS.SHOW_APPS_MENU_ITEM, 
    {
    content: _t('Open Sales app'),
    trigger: '.o_app[data-menu-xmlid="sale.sale_menu_root"]',
    position: 'right',
    edition: 'community'
}, {
    content: _t('Open Sales app'),
    trigger: '.o_app[data-menu-xmlid="sale.sale_menu_root"]',
    position: 'bottom',
    edition: 'enterprise'
}, {
    content: _t("Click Menu 'Configuration'"),
    trigger: "li a[data-menu-xmlid='sale.menu_sale_config']",
}, {
    content: _t("Click 'Customer Badges'"),
    trigger: "li a[data-menu-xmlid='flsp-salesorder.customer_badge_menu']",
}, {
    content: _t("Create a new customer badge"),
    extra_trigger: ".o_customer_badge_tree",
    trigger: ".o_list_button_add",
    position: "bottom",
}, {
    content: _t("Write the name of the customer badge"),
    extra_trigger: ".o_customer_badge_form",
    trigger: ".o_field_widget[name='name']",
    position: "bottom",
    run: 'text DemoBadge'
},  {
    trigger: ".o_field_widget[name='reward_level']",
    run: function () {
        var $input = $(".o_field_widget[name='reward_level']");
        $input.find('option')[1].selected=true; 
        // disable the trigger to fail the selection
        // $input.trigger("change");
    }
}, {
    content: _t("Input the currency"),
    trigger: ".o_field_widget[name='currency_id'] input",
    run: 'text USD'
}, {
    trigger: ".ui-menu-item > a",
    auto: true,
    in_modal: false,
}, {
    content: _t("Write the Annual Program Spend"),
    trigger: ".o_field_widget[name='annual_program_amount'] input",
    run: 'text 10000'
}, {
    content: _t("Write the Rewards Pricing Discount"),
    trigger: ".o_field_widget[name='sale_discount']",
    run: 'text 5'
}, {
    content: _t("Write the Freight Discount 5-10"),
    trigger: ".o_field_widget[name='freight_units_5_to_10_discount']",
    run: 'text 10'
}, {
    content: _t("Write the Freight Discount >10"),
    trigger: ".o_field_widget[name='freight_units_over_10_discount']",
    run: 'text 15'
}, {
    content: _t("Save the customer badge"),
    trigger: ".o_form_button_save",
    position: "right"
}, { 
    content: _t("Error notification exists"),
    trigger: "li:contains('Reward Level')",
}]);


tour.register('badge_manage_for_customer', {
    url: "/web",
}, [tour.STEPS.SHOW_APPS_MENU_ITEM, 
    {
    content: _t('Open Sales app'),
    trigger: '.o_app[data-menu-xmlid="sale.sale_menu_root"]',
    position: 'right',
    edition: 'community'
}, {
    content: _t('Open Sales app'),
    trigger: '.o_app[data-menu-xmlid="sale.sale_menu_root"]',
    position: 'bottom',
    edition: 'enterprise'
}, {
    content: _t("Click Menu 'Orders'"),
    trigger: "li a[data-menu-xmlid='sale.sale_order_menu']",
}, {
    content: _t("Click Menu 'Customers'"),
    trigger: "li a[data-menu-xmlid='sale.res_partner_menu']",
}, {
    content: _t("View customer list"),
    trigger: ".o_res_partner_kanban",
}, {
    content: _t("Select a customer"),
    extra_trigger: ".o_res_partner_kanban",
    trigger: "span:contains('smg')",
    run: 'click'
}, {
    content: _t("Click badge button for the customer to set a badge"),
    extra_trigger: "a:contains('Customers')",
    trigger: ".btn-primary[name='button_customer_badge']",
    position: "bottom",
    run: 'click'
}, {
    content: _t("Write a badge for the customer"),
    extra_trigger: "h4:contains('Manage Customer Badge')",
    trigger: ".o_field_many2one[name='flsp_cb_id'] input",
    position: "bottom",
    run: 'text Bronze'
}, {
    content: _t("Choose the badge"),
    trigger: ".ui-menu-item > a",
    auto: true,
    in_modal: false,
}, {
    content: _t("Set the badge"),
    trigger: ".btn-primary[name='button_set_customer_badge']",
    position: "bottom",
    run: 'click'
}, {
    content: _t("Click badge button for the customer to remove the badge"),
    trigger: ".btn-primary[name='button_customer_badge']",
    position: "bottom",
    run: 'click'
}, {
    content: _t("Delete the badge"),
    trigger: ".btn-primary[name='button_delete_customer_badge']",
    position: "bottom",
    run: 'click'
}, {
    content: _t("Check going back to the homepage of the customer"),
    extra_trigger: "a:contains('Customers')",
    trigger: ".btn-primary[name='button_customer_badge']",
}]);

});