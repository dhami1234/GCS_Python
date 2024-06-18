#!/bin/bash

python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2010-05-23 18:54" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2010-05-23 19:24" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2010-05-23 19:54" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2010-05-23 20:24" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C2' -stereo 'COR2beacon' "2010-05-23 21:54" 'STA' 'SOHO' 'STB'
python ../gui.py -rd -soho 'C3' -stereo 'COR2beacon' "2010-05-23 22:24" 'STA' 'SOHO' 'STB'

python ../analyse_gcs_results.py 'CME_02_AB_beacon.sh'