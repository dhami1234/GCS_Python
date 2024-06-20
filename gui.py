import argparse
import datetime as dt
import json
import os
import sys
from typing import List

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QComboBox
from astropy import units
from astropy.coordinates import concatenate
from matplotlib import colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from sunpy import log
from sunpy.coordinates import get_horizons_coord
from sunpy.map import Map

from geometry import gcs_mesh_sunpy, apex_radius
from utils.helioviewer import get_helioviewer_client
from utils.widgets import SliderAndTextbox

import wget
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os.path
from pathlib import Path
import shutil

"""
year=2012
month=5
day=3
hour=10
minute=50
second=0
"""



matplotlib.use('Qt5Agg')

hv = get_helioviewer_client()

straight_vertices, front_vertices, circle_vertices = 10, 10, 20
draw_modes = ['off', 'point cloud', 'grid']

# disable sunpy warnings
log.setLevel('ERROR')

# Some extra function
def download_HI(date, observatory):

    user_datetime = date
    print("Observatory", observatory)

    # Some Functions
    def yyyymmdd(dt) : return f"{dt.year:04d}{dt.month:02d}{dt.day:02d}"

    def hhMMss(dt) : return f"{dt.hour:02d}{dt.minute:02d}{dt.second:02d}"

    def gettotsec(hh,mm,ss) : return hh*3600+mm*60+ss

    def getnearbyfilename(fnames,userdt):
        sz = len(fnames)
        dif_totsec = [0]*sz
        hh = [0]*sz
        mm = [0]*sz
        ss = [0]*sz
        usr_totsec = gettotsec(user_datetime.hour,user_datetime.minute,user_datetime.second)
        # print("usr_totsec",usr_totsec)
        for i in range(sz):
            items   = fnames[i].split('_')
            hh[i]     = int(items[1][0:2])
            mm[i]     = int(items[1][2:4])
            ss[i]     = int(items[1][4:6])
            dif_totsec[i] = abs(usr_totsec -gettotsec(hh[i],mm[i],ss[i]))
        min_value = min(dif_totsec)
        min_index= dif_totsec.index(min_value)
        return fnames[min_index],min_index

    if observatory == 'STEREO_A':
        url = f'https://stereo-ssc.nascom.nasa.gov/data/ins_data/secchi/secchi_hi/L2_11_25/a/img/hi_1/{yyyymmdd(user_datetime)}'
    else:
        url = f'https://stereo-ssc.nascom.nasa.gov/data/ins_data/secchi/secchi_hi/L2_11_25/b/img/hi_1/{yyyymmdd(user_datetime)}'

    print("Url",url)
    ext = 'fts'

    def listFD(url, ext=''):

        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        return [node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    
    avail_filenames = listFD(url, ext)

    
    HI_filename, HI_fileindex = getnearbyfilename(avail_filenames,user_datetime)
    print("HI_filename, HI_fileindex",HI_filename, HI_fileindex)

    HIbase_filename = avail_filenames[HI_fileindex-1]
    print("HI_filename",HI_filename)
    print("HI base filename",HIbase_filename)

    # Define the directory and ensure it exists
    fits_data_dir = '../fits_data'
    os.makedirs(fits_data_dir, exist_ok=True)

    # Construct the full paths for the files in the fits_data directory
    HI_file_path = os.path.join(fits_data_dir, HI_filename)
    HIbase_file_path = os.path.join(fits_data_dir, HIbase_filename)

    # Check if HI file is already downloaded. If so, skip download. If not, download in local directory.
    if os.path.isfile(HI_file_path):
        print(f"HI File already exists in fits_data directory - [{HI_file_path}]")
        HIfile = HI_file_path
    else:
        print("HI File doesn't exist. Downloading ...")
        HIfile = wget.download(f'{url}/{HI_filename}', out=HI_file_path)
        print("HI File downloaded")

    # Check if HI base file is already downloaded. If so, skip download. If not, download in local directory.
    if os.path.isfile(HIbase_file_path):
        print(f"HI Base File already exists in fits_data directory - [{HIbase_file_path}]")
        HIbasefile = HIbase_file_path
    else:
        print("HI Base File doesn't exist. Downloading ...")
        HIbasefile = wget.download(f'{url}/{HIbase_filename}', out=HIbase_file_path)
        print("HI Base File downloaded")

    return HIfile,HIbasefile

def download_Cor2_beacon(date, observatory):

    user_datetime = date
    print("Observatory", observatory)

    # Some Functions
    def yyyymmdd(dt) : return f"{dt.year:04d}{dt.month:02d}{dt.day:02d}"

    def hhMMss(dt) : return f"{dt.hour:02d}{dt.minute:02d}{dt.second:02d}"

    def gettotsec(hh,mm,ss) : return hh*3600+mm*60+ss

    def getnearbyfilename(fnames,userdt,base=False):
        sz = len(fnames)
        dif_totsec = [0]*sz
        hh = [0]*sz
        mm = [0]*sz
        ss = [0]*sz
        usr_totsec = gettotsec(userdt.hour,userdt.minute,userdt.second)
        # print("usr_totsec",usr_totsec)
        for i in range(sz):
            items   = fnames[i].split('_')
            hh[i]     = int(items[1][0:2])
            mm[i]     = int(items[1][2:4])
            ss[i]     = int(items[1][4:6])
            dif_totsec[i] = abs(usr_totsec -gettotsec(hh[i],mm[i],ss[i]))
        min_value = min(dif_totsec)
        min_index= dif_totsec.index(min_value)

        # Check if the minimum time difference is more than 10 minutes (600 seconds)
        if min_value > 600 and not base:
            sys.exit(f"Error: Closest filename couldn't be found within 10 minutes of {userdt}.")

        return fnames[min_index],min_index

    if observatory == 'STEREO_A':
        url = f'https://stereo-ssc.nascom.nasa.gov/data/beacon/ahead/secchi/img/cor2/{yyyymmdd(user_datetime)}'
    else:
        url = f'https://stereo-ssc.nascom.nasa.gov/data/beacon/behind/secchi/img/cor2/{yyyymmdd(user_datetime)}'

    print("Url",url)
    ext = 'fts'

    def listFD(url, ext=''):

        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        return [node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    
    avail_filenames = listFD(url, ext)

    
    Cor2beacon_filename, Cor2beacon_fileindex = getnearbyfilename(avail_filenames,user_datetime)
    # print("Cor2beacon_filename, Cor2beacon_fileindex",Cor2beacon_filename, Cor2beacon_fileindex)

    base_time = user_datetime - dt.timedelta(hours=1)
    print("Time",user_datetime)
    print("Base time",base_time)
    Cor2beaconbase_filename, Cor2beaconbase_fileindex = getnearbyfilename(avail_filenames,base_time, True)

    # Cor2beaconbase_filename = avail_filenames[Cor2beacon_fileindex-2]
    print("Cor2beacon_filename",Cor2beacon_filename)
    print("Cor2beacon base filename",Cor2beaconbase_filename)

    # Define the directory and ensure it exists
    fits_data_dir = '../fits_data'
    os.makedirs(fits_data_dir, exist_ok=True)

    # Construct the full paths for the files in the fits_data directory
    Cor2beacon_file_path = os.path.join(fits_data_dir, Cor2beacon_filename)
    Cor2beaconbase_file_path = os.path.join(fits_data_dir, Cor2beaconbase_filename)

    # Check if Cor2beacon file is already downloaded. If so, skip download. If not, download in local directory.
    if os.path.isfile(Cor2beacon_file_path):
        print(f"Cor2beacon File already exists in fits_data directory - [{Cor2beacon_file_path}]")
        Cor2beaconfile = Cor2beacon_file_path
    else:
        print("Cor2beacon File doesn't exist. Downloading ...")
        Cor2beaconfile = wget.download(f'{url}/{Cor2beacon_filename}', out=Cor2beacon_file_path)
        print("Cor2beacon File downloaded")

    # Check if Cor2beacon base file is already downloaded. If so, skip download. If not, download in local directory.
    if os.path.isfile(Cor2beaconbase_file_path):
        print(f"Cor2beacon Base File already exists in fits_data directory - [{Cor2beaconbase_file_path}]")
        Cor2beaconbasefile = Cor2beaconbase_file_path
    else:
        print("Cor2beacon Base File doesn't exist. Downloading ...")
        Cor2beaconbasefile = wget.download(f'{url}/{Cor2beaconbase_filename}', out=Cor2beaconbase_file_path)
        print("Cor2beacon Base File downloaded")

    return Cor2beaconfile,Cor2beaconbasefile


import os
import sys
from datetime import datetime

def find_local_Cor2_files(date, observatory, fits_data_dir='../fits_data'):
    user_datetime = date
    print("Observatory", observatory)

    # Helper Functions
    def yyyymmdd(dt): return f"{dt.year:04d}{dt.month:02d}{dt.day:02d}"

    def hhMMss(dt): return f"{dt.hour:02d}{dt.minute:02d}{dt.second:02d}"

    def gettotsec(hh, mm, ss): return hh*3600 + mm*60 + ss

    def getnearbyfilename(fnames, userdt, base=False):
        sz = len(fnames)
        dif_totsec = [0] * sz
        hh = [0] * sz
        mm = [0] * sz
        ss = [0] * sz
        usr_totsec = gettotsec(userdt.hour, userdt.minute, userdt.second)
        # print("usr_totsec", usr_totsec)
        for i in range(sz):
            items = fnames[i].split('_')
            date_part = items[0]
            time_part = items[1]
            file_date = datetime.strptime(date_part, "%Y%m%d")
            if file_date.date() == userdt.date():
                hh[i] = int(time_part[0:2])
                mm[i] = int(time_part[2:4])
                ss[i] = int(time_part[4:6])
                dif_totsec[i] = abs(usr_totsec - gettotsec(hh[i], mm[i], ss[i]))
            else:
                dif_totsec[i] = float('inf')
        min_value = min(dif_totsec)
        min_index = dif_totsec.index(min_value)

        # Check if the minimum time difference is more than 10 minutes (600 seconds)
        if min_value > 600 and not base:
            sys.exit(f"Error: Closest filename couldn't be found within 10 minutes of {userdt}.")

        return fnames[min_index], min_index

    if not os.path.exists(fits_data_dir):
        sys.exit(f"Error: Directory {fits_data_dir} does not exist.")

    # List all .fts files in the directory for the given observatory
    avail_filenames = [f for f in os.listdir(fits_data_dir) if f.endswith('.fts') and f'd7c2{observatory[-1]}' in f]

    # Sort the filenames
    avail_filenames.sort()

    if observatory not in ['STEREO_A', 'STEREO_B']:
        sys.exit("Error: Observatory must be 'STEREO_A' or 'STEREO_B'.")

    Cor2beacon_filename, Cor2beacon_fileindex = getnearbyfilename(avail_filenames, user_datetime)
    # print("Cor2beacon_filename, Cor2beacon_fileindex", Cor2beacon_filename, Cor2beacon_fileindex)

    # Cor2beaconbase_filename = avail_filenames[Cor2beacon_fileindex - 1]
    
    base_time = user_datetime - dt.timedelta(hours=1)
    print("Time", user_datetime)
    print("Base time", base_time)
    Cor2beaconbase_filename, Cor2beaconbase_fileindex = getnearbyfilename(avail_filenames, base_time, True)

    print("Cor2beacon_filename", Cor2beacon_filename)
    print("Cor2beacon base filename", Cor2beaconbase_filename)

    # Construct the full paths for the files in the fits_data directory
    Cor2beacon_file_path = os.path.join(fits_data_dir, Cor2beacon_filename)
    Cor2beaconbase_file_path = os.path.join(fits_data_dir, Cor2beaconbase_filename)

    # Check if Cor2beacon file exists
    if not os.path.isfile(Cor2beacon_file_path):
        sys.exit(f"Error: Cor2beacon file does not exist in fits_data directory - [{Cor2beacon_file_path}]")

    # Check if Cor2beacon base file exists
    if not os.path.isfile(Cor2beaconbase_file_path):
        sys.exit(f"Error: Cor2beacon base file does not exist in fits_data directory - [{Cor2beaconbase_file_path}]")

    return Cor2beacon_file_path, Cor2beaconbase_file_path


def running_difference(a, b):
    a_data = (a.data - np.mean(a.data)) / np.std(a.data)
    b_data = (b.data - np.mean(b.data)) / np.std(b.data) 
    diff = ((b_data) - (a_data))
    return Map(diff, b.meta)

def running_difference_COR2beacon(a, b):
    a_data = (a.data - np.mean(a.data)) / np.std(a.data)
    b_data = (b.data - np.mean(b.data)) / np.std(b.data) 
    diff = ((b_data) - (a_data))
    return Map(diff, b.meta)

def running_difference_HI(a, b):
    return Map(np.log(b.data * 1.0 - a.data * 1.0), b.meta)


def load_image(spacecraft: str, detector: str, date: dt.datetime, runndiff: bool):
    if spacecraft == 'STA':
        observatory = 'STEREO_A'
        instrument = 'SECCHI'
        if detector not in ['COR1', 'COR2', 'COR2beacon']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.')
    elif spacecraft == 'STB':
        observatory = 'STEREO_B'
        instrument = 'SECCHI'
        if detector not in ['COR1', 'COR2', 'COR2beacon']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.')
    elif spacecraft == 'SOHO':
        observatory = 'SOHO'
        instrument = 'LASCO'
        if detector not in ['C2', 'C3']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.')
    elif spacecraft == 'HISTA':
        observatory = 'STEREO_A'
        instrument = 'SECCHI'
        if detector not in ['HI']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.') 
    elif spacecraft == 'HISTB':
        observatory = 'STEREO_B'
        instrument = 'SECCHI'
        if detector not in ['HI']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.')
    else:
        raise ValueError(f'unknown spacecraft: {spacecraft}')
        
    # Code added to download HI data    
    if detector == 'HI':
        f1 = download_HI(date, observatory) #it downloads both file and base file as list
        if runndiff:
            return running_difference_HI(Map(f1[1]),Map(f1[0])) 
        else:
            return Map(f1[1])   
    elif detector == 'COR2beacon':
        # f1 = download_Cor2_beacon(date, observatory)
        f1 = find_local_Cor2_files(date, observatory)
        if runndiff:
            return running_difference_COR2beacon(Map(f1[1]),Map(f1[0])) 
        else:
            return Map(f1[1])	 
    else:	
        f = download_helioviewer(date, observatory, instrument, detector)
    if runndiff:
        f2 = download_helioviewer(date - dt.timedelta(hours=1), observatory, instrument, detector)
        return running_difference(f2, f)
    else:
        return f


def download_helioviewer(date, observatory, instrument, detector):
    file = hv.download_jp2(date, observatory=observatory, instrument=instrument, detector=detector)
    f = Map(file)

    if observatory == 'SOHO':
       # add observer location information:
       soho = get_horizons_coord('SOHO', f.date)
       f.meta['HGLN_OBS'] = soho.lon.to('deg').value
       f.meta['HGLT_OBS'] = soho.lat.to('deg').value
       f.meta['DSUN_OBS'] = soho.radius.to('m').value

    return f


def save_params(params,date):
    # Create the directory if it does not exist
    Path('../Outputs').mkdir(parents=True, exist_ok=True)
    # Define the filenames using pathlib
    # In date string, replace the : with -
    date_out = date.strftime('%Y-%m-%d %H-%M')
    filename1 = Path(f'../Outputs/gcs_params{date_out}.json')
    filename2 = Path('../Outputs/gcs_params.json')
    with open(filename1, 'w') as file:
        json.dump(params, file)
    with open(filename2, 'w') as file:
        json.dump(params, file)


def load_params(date):
    date_out = date.strftime('%Y-%m-%d %H-%M')
    filename1 = Path(f'../Outputs/gcs_params{date_out}.json')
    filename = Path('../Outputs/gcs_params.json')
    if os.path.exists(filename1):
        with open(filename1) as file:
            return json.load(file)
    elif os.path.exists(filename):
        with open(filename) as file:
            return json.load(file)
            
    else:
        # start with default values
        return {
            'half_angle': 25,
            'height': 10,
            'kappa': 0.25,
            'lat': 0,
            'lon': 0,
            'tilt': 0
        }


class GCSGui(QtWidgets.QMainWindow):
    def __init__(self, date: dt.datetime, spacecraft: List[str], runndiff: bool = False,
            detector_stereo: str = 'COR2', detector_soho='C2', detector_histereo ='HI'):
        super().__init__()
        self._spacecraft = spacecraft
        self._date = date
        self._runndiff = runndiff
        self._detector_stereo = detector_stereo
        self._detector_soho = detector_soho
        # We added this
        self._detector_histereo = detector_histereo

        self._root = QtWidgets.QWidget()
        self.setCentralWidget(self._root)
        self._mainlayout = QtWidgets.QHBoxLayout(self._root)

        self._figure = Figure(figsize=(5 * len(spacecraft), 5))
        canvas = FigureCanvas(self._figure)
        self._mainlayout.addWidget(canvas, stretch=5)
        self.addToolBar(NavigationToolbar(canvas, self))
        self._current_draw_mode = None

        self.create_widgets(date)

        self.make_plot()
        self.show()

    def create_widgets(self,date: dt.datetime):
        self._date = date
        print('Date=',date)
        params = load_params(date)
        self._s_half_angle = SliderAndTextbox('Half angle, \u03B1 [°]', 0, 90, params['half_angle'])
        self._s_height = SliderAndTextbox('Apex Height, R\u2090\u209A\u2091\u2093 [Rs]', 0, 70, params['height'])
        self._s_kappa = SliderAndTextbox('Aspect Ratio, \u03BA', 0, 1, params['kappa'])
        self._s_lat = SliderAndTextbox('Heliographic Latitude, \u03B8 [°]', -90, 90, params['lat'])
        self._s_lon = SliderAndTextbox('Stonyhurst Longitude, \u03C6 [°]', 0, 360, params['lon'])
        self._s_tilt = SliderAndTextbox('Tilt angle, \u03B3 [°]', -90, 90, params['tilt'])
        sliders = self._s_half_angle, self._s_height, self._s_kappa, self._s_lat, self._s_lon, self._s_tilt

        layout = QtWidgets.QVBoxLayout()
        for slider in sliders:
            layout.addWidget(slider)
            slider.valueChanged.connect(self.plot_mesh)

        # add checkbox to enable or disable plot
        cb_mode_label = QLabel()
        cb_mode_label.setText('Display mode')
        layout.addWidget(cb_mode_label)
        self._cb_mode = QComboBox()
        for mode in draw_modes:
            self._cb_mode.addItem(mode)
        self._cb_mode.setCurrentIndex(2)
        layout.addWidget(self._cb_mode)
        self._cb_mode.currentIndexChanged.connect(self.plot_mesh)

        # add labels for useful quantities
        self._l_radius = QLabel()
        layout.addWidget(self._l_radius)

        b_save = QtWidgets.QPushButton('Save')
        b_save.clicked.connect(self.save)
        layout.addWidget(b_save)
        layout.addStretch(1)

        self._mainlayout.addLayout(layout, stretch=1)
        self.showMaximized()

    def make_plot(self):
        fig = self._figure
        spacecraft = self._spacecraft
        date = self._date
        runndiff = self._runndiff
        cols_max = 3
        rows_max = len(spacecraft) // cols_max + 1
        if (len(spacecraft) % cols_max) == 0:
            rows_max = rows_max - 1
        spec = GridSpec(ncols=cols_max, nrows=rows_max, figure=fig)

        axes = []
        images = []
        self._mesh_plots = []
        for i, sc in enumerate(spacecraft):
            if sc in ['STA', 'STB']:
                detector = self._detector_stereo
            elif sc == 'SOHO':
                detector = self._detector_soho            	
            else:
                detector = self._detector_histereo    
            image = load_image(sc, detector, date, runndiff)
            images.append(image)
            #find remainder of i divided by 3
            col_here = i % cols_max
            #find quotient of i divided by 3
            row_here = i // cols_max
            ax = fig.add_subplot(spec[row_here, col_here], projection=image)
            ax.tick_params(axis='x',left = False, right = False , labelleft = False ,
                labelbottom = False, bottom = False)
            ax.tick_params(axis='y',left = False, right = False , labelleft = False ,
                labelbottom = False, bottom = False)

            axes.append(ax)
            if detector == 'HI':
                image.plot(axes=ax,annotate=False, cmap='Greys_r', norm=colors.Normalize(vmin=-0.5, vmax=0.5) if runndiff else None)
            elif detector == 'COR2beacon' and sc == 'STA':
                image.plot(axes=ax,annotate=False, cmap='Greys_r', norm=colors.Normalize(vmin=np.mean(image)-2*np.std(image), vmax=np.mean(image)+2*np.std(image)) if runndiff else None)
            elif detector == 'COR2beacon' and sc == 'STB':
                image.plot(axes=ax,annotate=False, cmap='Greys_r', norm=colors.Normalize(vmin=np.mean(image)-2*np.std(image), vmax=np.mean(image)+2*np.std(image)) if runndiff else None)
            else:
            	image.plot(axes=ax,annotate=False, cmap='Greys_r', norm=colors.Normalize(vmin=np.mean(image)-4*np.std(image), vmax=np.mean(image)+4*np.std(image)) if runndiff else None)
            
        self._bg = fig.canvas.copy_from_bbox(fig.bbox)
        self._images = images
        self._axes = axes

        self.plot_mesh()

        fig.canvas.draw()
        fig.tight_layout()

    def plot_mesh(self):
        fig = self._figure
        half_angle = np.radians(self._s_half_angle.val)
        height = self._s_height.val
        kappa = self._s_kappa.val
        lat = np.radians(self._s_lat.val)
        lon = np.radians(self._s_lon.val)
        tilt = np.radians(self._s_tilt.val)

        # calculate and show quantities
        ra = apex_radius(half_angle, height, kappa)
        self._l_radius.setText('Apex cross-section radius: {:.2f} Rs'.format(ra))

        # check if plot should be shown
        draw_mode = draw_modes[self._cb_mode.currentIndex()]
        if draw_mode != self._current_draw_mode:
            for plot in self._mesh_plots:
                plot.remove()
            self._mesh_plots = []
            fig.canvas.draw()
            self._current_draw_mode = draw_mode
            if draw_mode == 'off':
                return

        # create GCS mesh
        mesh = gcs_mesh_sunpy(self._date, half_angle, height, straight_vertices, front_vertices, circle_vertices,
                              kappa, lat, lon, tilt)
        if draw_mode == 'grid':
            mesh2 = mesh.reshape((front_vertices + straight_vertices) * 2 - 3, circle_vertices).T.flatten()
            mesh = concatenate([mesh, mesh2])

        for i, (image, ax) in enumerate(zip(self._images, self._axes)):
            if len(self._mesh_plots) <= i:
                # new plot
                style = {
                    'grid': '-',
                    'point cloud': '.'
                }[draw_mode]
                params = {
                    'grid': dict(lw=0.5),
                    'point cloud': dict(ms=2)
                }[draw_mode]
                p = ax.plot_coord(mesh, style, color='blue', scalex=False, scaley=False, **params)[0]
                self._mesh_plots.append(p)
            else:
                # update plot
                p = self._mesh_plots[i]

                frame0 = mesh.frame.transform_to(image.coordinate_frame)
                xdata = frame0.spherical.lon.to_value(units.deg)
                ydata = frame0.spherical.lat.to_value(units.deg)
                p.set_xdata(xdata)
                p.set_ydata(ydata)
                ax.draw_artist(p)

        
        fig.canvas.draw()
    def get_d(self):
        return self._date

    def get_params_dict(self):
        return {
            'half_angle': self._s_half_angle.val,
            'height': self._s_height.val,
            'kappa': self._s_kappa.val,
            'lat': self._s_lat.val,
            'lon': self._s_lon.val,
            'tilt': self._s_tilt.val
        }
    
    def save(self):
        save_params(self.get_params_dict(),self.get_d())
        # Create the directory if it does not exist
        Path('../Outputs').mkdir(parents=True, exist_ok=True)
        # Define the filenames using pathlib
        date_out = self.get_d().strftime('%Y-%m-%d %H-%M')
        filename1 = Path(f'../Outputs/{date_out}.png')
        self._figure.savefig(filename1)
        self.close()


def main():
    parser = argparse.ArgumentParser(description='Run the GCS GUI', prog='gcs_gui')
    parser.add_argument('date', type=lambda d: dt.datetime.strptime(d, '%Y-%m-%d %H:%M'),
                        help='Date and time for the coronagraph images. Format: "yyyy-mm-dd HH:MM" (with quotes). '
                             'The closest available image will be loaded for each spacecraft.')
    parser.add_argument('spacecraft', type=str, nargs='+', choices=['STA', 'STB', 'SOHO', 'HISTA', 'HISTB'],
                        help='List of spacecraft to use.')
    parser.add_argument('-rd', '--running-difference', action='store_true',
                        help='Whether to use running difference images')
    parser.add_argument('-soho', type=str, default='C2', choices=['C2', 'C3'],
                        help='Which coronagraph to use at SOHO/LASCO.')
    parser.add_argument('-stereo', type=str, default='COR2', choices=['COR1', 'COR2', 'COR2beacon'],
                        help='Which coronagraph to use at STEREO.')
    parser.add_argument('-histereo', type=str, default='HI', choices=['HI'],
                        help='Which coronagraph to use at HISTEREO.')                     
    args = parser.parse_args()
    qapp = QtWidgets.QApplication(sys.argv)
    app = GCSGui(args.date, args.spacecraft, args.running_difference, detector_stereo=args.stereo,
                 detector_soho=args.soho,detector_histereo=args.histereo)
    app.show()
    
    qapp.exec_()

    #Delete the fits_data directory if it exists
    # if os.path.exists('fits_data'):
    #     shutil.rmtree('fits_data')



if __name__ == '__main__':
    main()

