#!/bin/bash

python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2012-06-14 14:24" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2012-06-14 14:39" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2012-06-14 14:54" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C3' -stereo 'COR2beacon' "2012-06-14 15:09" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C3' -stereo 'COR2beacon' "2012-06-14 15:24" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C3' -stereo 'COR2beacon' "2012-06-14 15:39" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C3' -stereo 'COR2beacon' "2012-06-14 15:54" 'STA' 'SOHO' 'STB'

python ../analyse_gcs_results.py 'CME_34_beacon.sh'