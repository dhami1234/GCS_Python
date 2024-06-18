python ../gui.py -rd -soho C2 -stereo COR2beacon "2010-04-03 10:24" STA SOHO
python ../gui.py -rd -soho C2 -stereo COR2beacon "2010-04-03 10:39" STA SOHO 
python ../gui.py -rd -soho C2 -stereo COR2beacon "2010-04-03 10:54" STA SOHO 
python ../gui.py -rd -soho C2 -stereo COR2beacon "2010-04-03 11:24" STA SOHO 
python ../gui.py -rd -soho C2 -stereo COR2beacon "2010-04-03 11:39" STA SOHO 
python ../gui.py -rd -soho C3 -stereo COR2beacon "2010-04-03 11:54" STA SOHO 

python ../analyse_gcs_results.py CME_07_A_beacon.bat
