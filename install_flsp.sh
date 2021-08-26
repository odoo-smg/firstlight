#!/bin/bash

set -e

echo "======================================================"
echo "Installing the database $1....."
./odoo-bin -c ./openerp-server.conf --stop-after-init -d $1 

function install_module()
{
    echo "======================================================"
    echo "Installing the module '$2' on the database '$1'....."
    echo "./odoo-bin -c ./openerp-server.conf -d $1 --stop-after-init -i $2"
    ./odoo-bin -c ./openerp-server.conf -d $1 --stop-after-init -i $2
}

module_list_1=('base' 'product' 'sale_management' 'sale' 'purchase' 'stock' 'mrp' 'base_automation' 'delivery' 'stock_dropshipping')
for m in ${module_list_1[@]}
do
  install_module $1 $m
done

module_list_2=('flsp-product')
for m in ${module_list_2[@]}
do
  install_module $1 $m
done

module_list_3=(
    'dhx_gantt' 'ks_binary_file_preview' 'smg' 'flspmfg' 'report_xlsx' 'inputmask_widget' 'flsp_specification' 'flspautomation'
    'flspticketsystem' 'flsptktmsg' 'flsp_tktboarding' 'flsp_tktversionctrl' 'flsp_tktonhold'
    'flsp_pdct_standard_location' 'flspproducttags' 'flsp_uom' 'flspserialnum'
    'flspacc' 'flspgst'
    'flsp-salesorder' 'flsp_sale_target' 'flsp_sales_report' 'flspsales_forecast' 'flspsaleapproval' 'flsp_sales_item_report'
    'flsppurchase' 'flsppurchase_status' 'flsp_pq' 'flsp_backorder' 'flsppurchase_warranty' 'flsp_backflush'
    'flspstock' 'deltatech_stock_negative' 'flspcustom_inventory' 'flsp_inventory_count' 'flspstockrequest' 'flsp_wip_transfer'
    'flsp-mrp' 'mrp_flattened_bom_xlsx' 'flsp_bom_availability' 'flspcomparebom' 'flsp_mrp_summarized_bom' 'mrp_bom_component_menu' 'flsp_mrp_structure' 'flsp_serial_mrp' 'flsp_mrp_simulation'
    'flsp_gantt_mrp' 'flsp_mrp_filter_sn' 'flsp_mrp_purchase' 'flsp_mrp_batch_produce' 'flsp_mrp_planning' 'flsp_mrp_mto' 'flsp_sale_delivery_check' 'flsp_mrp_sales_report' 'flsp_mrp_negative_inv_report' 'flsp_mrp_wip'
    'flsp-eco' 'flsp_eco_reject' 'flspmailecoapproval'
    'flspquality' 'flsp_maintenance' 'flspautoemails' 'flsp_dynamic_label' 'flsp_stock_report_transactions' 
    )
for m in ${module_list_3[@]}
do
  install_module $1 $m
done

echo "======================================================"
echo "Installation completes on database $1 !!!"
echo "======================================================"
