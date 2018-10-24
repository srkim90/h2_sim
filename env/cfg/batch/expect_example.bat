:: File : 0.ALL.bat

:: batch start from_file /sim/cfg/batch/1.authentication_data.bat

:: -- start of batch file --
disable log
enable expect

set reset_stat
show echo delete_all_data
set sleep 250
send request eps_am_data {ueId} DELETE active_apn_data {ActiveApnData:apnContextId}
set sleep 250
send request ims_am_data {ueId} DELETE as_notify_data ALL
set sleep 250
send request ims_am_data {ueId} DELETE cscf_restore_data
set sleep 250

show echo 1._start_test_authentication_data
show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request authentication_data {ueId} GET ALL
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request authentication_data {ueId} PATCH eps
set sleep 400
send request authentication_data {ueId} GET eps
set sleep 400


show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request authentication_data {ueId} PATCH ims
set sleep 400
send request authentication_data {ueId} GET ims
set sleep 400


show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request authentication_data {ueId} PATCH wifi
set sleep 400
send request authentication_data {ueId} GET wifi
set sleep 400

echo 2._start_test_eps_am_data
show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 404 IGNORE_JSON GET GET
send request eps_am_data {ueId} GET active_apn_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 201 COMPARE_JSON POST GET
send request eps_am_data {ueId} POST active_apn_data {ActiveApnData:apnContextId}
set sleep 400
send request eps_am_data {ueId} GET ALL
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PUT GET
send request eps_am_data {ueId} PUT active_apn_data {ActiveApnData:apnContextId}
set sleep 400
send request eps_am_data {ueId} GET active_apn_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 IGNORE_JSON DELETE GET
send request eps_am_data {ueId} DELETE active_apn_data {ActiveApnData:apnContextId}
set sleep 400
send request eps_am_data {ueId} GET active_apn_data
set sleep 400

echo 3._start_test_ims_am_data
show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request ims_am_data {ueId} GET ALL
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 404 IGNORE_JSON GET GET
send request ims_am_data {ueId} GET cscf_restore_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 404 IGNORE_JSON GET GET
send request ims_am_data {ueId} GET as_notify_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 201 COMPARE_JSON POST GET
send request ims_am_data {ueId} POST cscf_restore_data {ImsSubsData:imsPrivateUserId}
set sleep 400
send request ims_am_data {ueId} GET cscf_restore_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 201 COMPARE_JSON POST GET
send request ims_am_data {ueId} POST as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}
set sleep 400
send request ims_am_data {ueId} GET as_notify_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PUT GET
send request ims_am_data {ueId} PUT cscf_restore_data {ImsSubsData:imsPrivateUserId}
set sleep 400
send request ims_am_data {ueId} GET cscf_restore_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PUT GET
send request ims_am_data {ueId} PUT as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}
set sleep 400
send request ims_am_data {ueId} GET as_notify_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request ims_am_data {ueId} GET cscf_restore_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request ims_am_data {ueId} GET as_notify_data
set sleep 400


show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 IGNORE_JSON DELETE GET
send request ims_am_data {ueId} DELETE cscf_restore_data
set sleep 400
send request ims_am_data {ueId} GET cscf_restore_data
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 IGNORE_JSON DELETE GET
send request ims_am_data {ueId} DELETE as_notify_data SELECT {AsNotifyData:asGroupId} {dataReferenceId}
set sleep 400
send request ims_am_data {ueId} GET as_notify_data
set sleep 400


echo 4_start_test_location_data
show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request location_data {ueId} GET  ALL
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request location_data {ueId} GET SELECT CsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request location_data {ueId} GET SELECT PsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request location_data {ueId} GET SELECT EpsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request location_data {ueId} GET SELECT ImsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request location_data {ueId} GET SELECT AsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request location_data {ueId} PATCH SELECT CommLocationData
set sleep 400
send request location_data {ueId} GET SELECT CsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request location_data {ueId} PATCH SELECT CsLocationData
set sleep 400
send request location_data {ueId} GET SELECT CsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request location_data {ueId} PATCH SELECT PsLocationData
set sleep 400
send request location_data {ueId} GET SELECT PsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request location_data {ueId} PATCH SELECT EpsLocationData
set sleep 400
send request location_data {ueId} GET SELECT EpsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request location_data {ueId} PATCH SELECT ImsLocationData
set sleep 400
send request location_data {ueId} GET SELECT ImsLocationData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request location_data {ueId} PATCH SELECT AsLocationData
set sleep 400
send request location_data {ueId} GET SELECT AsLocationData
set sleep 400


show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request location_data {ueId} PATCH SELECT AsLocationData
set sleep 400
send request location_data {ueId} GET SELECT AsLocationData
set sleep 400


echo 5_start_test_supplement_service_data
show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request supplement_service_data {ueId} GET ALL
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request supplement_service_data {ueId} GET SELECT BasicServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request supplement_service_data {ueId} GET SELECT CFServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request supplement_service_data {ueId} GET SELECT SNDServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request supplement_service_data {ueId} GET SELECT ImsServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request supplement_service_data {ueId} GET SELECT InServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 200 IGNORE_JSON GET GET
send request supplement_service_data {ueId} GET SELECT VirtualServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request supplement_service_data {ueId} PATCH CFServiceData
set sleep 400
send request supplement_service_data {ueId} GET SELECT CFServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request supplement_service_data {ueId} PATCH SNDServiceData
set sleep 400
send request supplement_service_data {ueId} GET SELECT SNDServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request supplement_service_data {ueId} PATCH ImsServiceData
set sleep 400
send request supplement_service_data {ueId} GET SELECT ImsServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request supplement_service_data {ueId} PATCH InServiceData
set sleep 400
send request supplement_service_data {ueId} GET SELECT InServiceData
set sleep 400

show echo --------------------------------------------------------------------------------------------------------------------------------------------------------------
set expect 204 COMPARE_JSON PATCH GET
send request supplement_service_data {ueId} PATCH VirtualServiceData
set sleep 400
send request supplement_service_data {ueId} GET SELECT VirtualServiceData
set sleep 400



set reset_data_file
show stat_once
disable expect
enable log
:: -- end of batch file --
