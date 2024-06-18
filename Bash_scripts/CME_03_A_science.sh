#!/bin/bash

python ../gui.py -rd -soho 'C2' -stereo 'COR2' "2012-06-14 14:24" 'STA' 'SOHO' 
python ../gui.py -rd -soho 'C2' -stereo 'COR2' "2012-06-14 14:39" 'STA' 'SOHO' 
python ../gui.py -rd -soho 'C2' -stereo 'COR2' "2012-06-14 14:54" 'STA' 'SOHO' 
python ../gui.py -rd -soho 'C3' -stereo 'COR2' "2012-06-14 15:24" 'STA' 'SOHO' 

python ../analyse_gcs_results.py 'CME_03_A_science.sh'