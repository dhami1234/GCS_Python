python ../gui.py -rd -soho C2 -stereo COR2 "2013-03-15 07:24" STA SOHO
python ../gui.py -rd -soho C2 -stereo COR2 "2013-03-15 07:39" STA SOHO
python ../gui.py -rd -soho C3 -stereo COR2 "2013-03-15 07:54" STA SOHO
python ../gui.py -rd -soho C3 -stereo COR2 "2013-03-15 09:24" STA SOHO

python ../analyse_gcs_results.py CME_05_A_science.bat
