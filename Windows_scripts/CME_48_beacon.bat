python ../gui.py -rd -soho C2 -stereo COR2beacon "2013-03-15 07:24" STA SOHO STB
python ../gui.py -rd -soho C2 -stereo COR2beacon "2013-03-15 07:39" STA SOHO STB
python ../gui.py -rd -soho C3 -stereo COR2beacon "2013-03-15 07:54" STA SOHO STB
python ../gui.py -rd -soho C3 -stereo COR2beacon "2013-03-15 09:24" STA SOHO STB

python ../analyse_gcs_results.py CME_48_beacon.bat
