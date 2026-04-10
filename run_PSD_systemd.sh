#!/bin/bash
source /home/soh/.bash_profile

time_current=$(TZ="UTC" date '+%Y-%m-%dT%H:%M:%S')
time_before=$(TZ="UTC" date -d '-2 hour' '+%Y-%m-%dT%H:%M:%S')
params_file=$1

source /home/soh/noise-toolkit/venv/bin/activate
echo "Run PSD started for $params_file at $time_current"
python3 bin/ntk_autoPSD.py $time_before $time_current $params_file >> LOGS/$(date "+%Y.%m.%d-%H.%M.%S")_${params_file}_run_psd.log 2>  >(tee -a LOGS/$(date "+%Y.%m.%d-%H.%M.%S")_${params_file}_run_psd.log >&2)
wait
time_ended=$(TZ="UTC" date '+%Y-%m-%dT%H:%M:%S')
echo "Run PSD ended for $params_file at $time_ended"
deactivate


