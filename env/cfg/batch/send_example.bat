:: File : 0.ALL.bat

:: batch start from_file /sim/cfg/batch/send_all.bat

:: -- start of batch file --

set sleep 2500
send request authentication_data {ueId} GET ALL
set sleep 2500
send request authentication_data {ueId} GET eps
set sleep 2500
send request authentication_data {ueId} GET ims
set sleep 2500
send request authentication_data {ueId} GET wifi
set sleep 2500
send request authentication_data {ueId} PATCH
set sleep 2500
send request eps_am_data {ueId} GET ALL
set sleep 2500
send request eps_am_data {ueId} GET active_apn_data
set sleep 2500
send request eps_am_data {ueId} POST active_apn_data {ActiveApnData:apnContextId}
set sleep 2500
send request eps_am_data {ueId} PUT active_apn_data {ActiveApnData:apnContextId}
set sleep 2500
send request eps_am_data {ueId} DELETE ALL
set sleep 2500
send request eps_am_data {ueId} DELETE active_apn_data {ActiveApnData:apnContextId}
set sleep 2500
send request ims_am_data {ueId} GET ALL
set sleep 2500
send request ims_am_data {ueId} GET cscf_restore_data
set sleep 2500
send request ims_am_data {ueId} GET as_notify_data
set sleep 2500
send request ims_am_data {ueId} POST cscf_restore_data {ImsSubsData:imsPrivateUserId}
set sleep 2500
send request ims_am_data {ueId} POST as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}
set sleep 2500
send request ims_am_data {ueId} PUT cscf_restore_data {ImsSubsData:imsPrivateUserId}
set sleep 2500
send request ims_am_data {ueId} PUT as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}
set sleep 2500
send request ims_am_data {ueId} DELETE cscf_restore_dat
set sleep 2500
send request ims_am_data {ueId} DELETE as_notify_data ALL
set sleep 2500
send request ims_am_data {ueId} DELETE as_notify_data SELECT {AsNotifyData:asGroupId} {dataReferenceId} 
set sleep 2500
send request location_data {ueId} GET  ALL
set sleep 2500
send request location_data {ueId} GET SELECT CsLocationData
set sleep 2500
send request location_data {ueId} GET SELECT PsLocationData
set sleep 2500
send request location_data {ueId} GET SELECT EpsLocationData
set sleep 2500
send request location_data {ueId} GET SELECT ImsLocationData
set sleep 2500
send request location_data {ueId} GET SELECT AsLocationData
set sleep 2500
send request location_data {ueId} GET BITMASK 1234
set sleep 2500
send request location_data {ueId} PATCH ALL
set sleep 2500
send request location_data {ueId} PATCH SELECT CommLocationData
set sleep 2500
send request location_data {ueId} PATCH SELECT CsLocationData
set sleep 2500
send request location_data {ueId} PATCH SELECT PsLocationData
set sleep 2500
send request location_data {ueId} PATCH SELECT EpsLocationData
set sleep 2500
send request location_data {ueId} PATCH SELECT ImsLocationData
set sleep 2500
send request location_data {ueId} PATCH SELECT AsLocationData
set sleep 2500
send request location_data {ueId} PATCH SELECT BSGServiceData
set sleep 2500
send request location_data {ueId} PATCH BITMASK 0123456
set sleep 2500
send request supplement_service_data {ueId} GET ALL
set sleep 2500
send request supplement_service_data {ueId} GET SELECT BasicServiceData
set sleep 2500
send request supplement_service_data {ueId} GET SELECT CFServiceData
set sleep 2500
send request supplement_service_data {ueId} GET SELECT SNDServiceData
set sleep 2500
send request supplement_service_data {ueId} GET SELECT ImsServiceData
set sleep 2500
send request supplement_service_data {ueId} GET SELECT InServiceData
set sleep 2500
send request supplement_service_data {ueId} GET SELECT VirtualServiceData
set sleep 2500
send request supplement_service_data {ueId} GET BITMASK 123456
set sleep 2500
send request supplement_service_data {ueId} PATCH BasicServiceData
set sleep 2500
send request supplement_service_data {ueId} PATCH CFServiceData
set sleep 2500
send request supplement_service_data {ueId} PATCH SNDServiceData
set sleep 2500
send request supplement_service_data {ueId} PATCH ImsServiceData
set sleep 2500
send request supplement_service_data {ueId} PATCH InServiceData
set sleep 2500
send request supplement_service_data {ueId} PATCH VirtualServiceData
set sleep 2500
send request tas_data {ueId} GET fields ALL
set sleep 2500
send request tas_data {ueId} GET tas_context_data
set sleep 2500
send request tas_data {ueId} GET tas_ndub_data ALL
set sleep 2500
send request tas_data {ueId} GET tas_ndub_data targetId {targetId}
set sleep 2500
send request tas_data {ueId} POST tas_ndub_data targetId {targetId}
set sleep 2500
send request tas_data {ueId} PATCH tas_context_data
set sleep 2500
send request tas_data {ueId} PATCH tas_ndub_data targetId {targetId}
set sleep 2500
send request tas_data {ueId} DELETE tas_ndub_data ALL
set sleep 2500
send request tas_data {ueId} DELETE tas_ndub_data targetId {targetId}
set sleep 2500



