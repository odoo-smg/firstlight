:: How to use the script:
:: 1) Before running, update "openerp-server.conf" ahead with necessary odoo info, like below:
::      db_user = odoo
::      db_password = odoo
::      xml_rpc_port = 8069
::      bin_path = C:/Program Files/wkhtmltopdf/bin
::      addons_path = C:\odoo-13.0\addons, C:\odoo-13.0\firstlight
::      logfile = C:\odoo-13.0\install.flsp.log
:: 2) Copy the file "Install-FLSP.bat" from \firstlight\ to Odoo dev root directory(with "openerp-server.conf" inside), like "C:\odoo-13.0".
:: 3) Command to run in Windows CMD promote or PowerShell(preferred):
::      Install-FLSP.bat -db "your-db-name"
:: 4) Just for module installation, NOT for module upgrade;
:: 5) Just for local dev env, NOT for module installation in Odoo production env
:: 6) If a new module is created for FLSP, append its module name in "FLSP_MODULE_LIST";
:: 7) (Optional AFTER installation) If you want to change default password for user "admin", you can use pgAdmin to update it before login the installed FLSP server;

@ECHO OFF

IF NOT "%1"=="-db" (
    echo Please rerun the script in format: Install-FLSP.bat -db "your-db-name"
    echo For example: Install-FLSP.bat -db db1
    EXIT 0
) 
IF "%2"=="" (
    echo Please rerun the script in format: Install-FLSP.bat -db "your-db-name"
    echo For example: Install-FLSP.bat -db db1
    EXIT 0
) 
set DB_NAME=%2

echo ======================================================
echo Time to install: %date% %time%
echo Creating database '%DB_NAME%' .....
%cd%\venv\Scripts\python.exe %cd%\odoo-bin -c %cd%\openerp-server.conf -d %DB_NAME% --stop-after-init
if %ERRORLEVEL% GEQ 1 (
    echo Error when to create the database!
    pause
    EXIT 1
) else (
    echo The database is created successfully.
)

set ODOO_MODULE_LIST=base product sale_management sale purchase stock mrp mrp_plm base_automation delivery stock_dropshipping utm hr maintenance
for %%a in (%ODOO_MODULE_LIST%) do ( 
    call :installModuleFunc %DB_NAME% %%a
)

set FLSP_FUNDAMENTAL_MODULE=flsp-product
call :installModuleFunc %DB_NAME% %FLSP_FUNDAMENTAL_MODULE%

set FLSP_MODULE_LIST=dhx_gantt ks_binary_file_preview smg flspmfg report_xlsx inputmask_widget flsp_specification flspautomation^
 flspticketsystem flsptktmsg flsp_tktboarding flsp_tktversionctrl flsp_tktonhold^
 flsp_pdct_standard_location flspproducttags flsp_uom flspserialnum^
 flspacc flspgst^
 flsp-salesorder flsp_sale_target flsp_sales_report flspsales_forecast flspsaleapproval flsp_sales_item_report^
 flsppurchase flsppurchase_status flsp_pq flsp_backorder flsppurchase_warranty flsp_backflush^
 flspstock deltatech_stock_negative flspcustom_inventory flsp_inventory_count flspstockrequest flsp_stock_report_transactions flsp_wip_transfer^
 flsp-mrp mrp_flattened_bom_xlsx flsp_bom_availability flspcomparebom flsp_mrp_summarized_bom mrp_bom_component_menu flsp_mrp_structure flsp_serial_mrp flsp_mrp_simulation^
 flsp_gantt_mrp flsp_mrp_filter_sn flsp_mrp_purchase flsp_mrp_batch_produce flsp_mrp_planning flsp_mrp_mto flsp_sale_delivery_check flsp_mrp_sales_report flsp_mrp_negative_inv_report flsp_mrp_wip^
 flsp-eco flsp_eco_reject flspmailecoapproval^
 flspquality flsp_maintenance flspautoemails flsp_dynamic_label
for %%a in (%FLSP_MODULE_LIST%) do ( 
    call :installModuleFunc %DB_NAME% %%a
)

echo ======================================================
echo Installation completes on database %DB_NAME% !!!
echo Time to complete: %date% %time%
echo ======================================================
EXIT /B %ERRORLEVEL%

:installModuleFunc
echo ======================================================
echo Module: '%~2'
echo Installing the module on the database .....
%cd%\venv\Scripts\python.exe %cd%\odoo-bin -c %cd%\openerp-server.conf -d %~1 -i %~2 --stop-after-init
if %ERRORLEVEL% neq 0 (
        echo Error when to install the module!
        pause
        EXIT 1
) else (
        echo The module is installed successfully.
)
EXIT /B %ERRORLEVEL%

