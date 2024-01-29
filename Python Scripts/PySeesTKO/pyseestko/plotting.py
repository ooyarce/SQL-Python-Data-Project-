# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
# Objects
from matplotlib   import pyplot as plt
from pathlib      import Path
from typing       import Optional
from pyseestko.db_functions import ModelSimulation      

# Packages
import pandas as pd
import numpy  as np

# ==================================================================================
# SECONDARY CLASSES
# ==================================================================================
class Plotting:
    """
    This class is used to perform the seismic analysis of the structure.
    It's used to analyse quiclky the structure and get the results of the analysis.
    You use it in the main after the results are uploaded to the database.
    """
    def __init__(self, sim_type:int,  stories:int, magnitude:float, rupture:int, station:int, path:str):
        sim_type_map = {
            1: 'FB',
            2: 'AB',
            3: 'DRM',
        }
        rup_type_map = {
            1: 'BL',
            2: 'NS',
            3: 'SN'
        }
        self.sim_type  = sim_type_map.get(sim_type)
        self.stories   = stories
        self.magnitude = magnitude
        self.rup_type  = rup_type_map.get(rupture)
        self.station   = station
        self.save_path = Path(path)
        
        self.file_name   = f'{self.sim_type}_{self.magnitude}_{self.rup_type}_s{self.station}'
        self.drift_title = f'Drift per story plot | {self.sim_type} |  {self.magnitude} | {self.rup_type} | Station {self.station}'
        #self.input_title         = f'Input Accelerations Response Spectra Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        #self.sprectums_title     = f'Story PSa Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        #self.base_spectrum_title = f'Base Accelerations Spectrum Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        #self.base_shear_ss_title = f'Base Shear Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'

    def plotConfig(self, title:str, x = 19.2, y = 10.8, dpi = 100):
        fig = plt.figure(num=1, figsize=(x, y), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1)
        y = None
        ax.grid(True)
        ax.set_title(title)
        return fig, ax, y

    def plotSave(self, fig, file_type = 'png'):
        self.save_path.mkdir(parents=True, exist_ok=True)
        full_save_path = self.save_path / f'{self.file_name}.{file_type}'
        fig.savefig(full_save_path, dpi=100)
        plt.show()

    def plotModelDrift(self, max_corner_x: list, max_center_x: list, max_corner_y: list, max_center_y:list, xlim_inf:float = 0.0, xlim_sup:float = 0.008 ):
        # Input params
        fig, ax, y = self.plotConfig(self.drift_title)
        ax.set_yticks(range(1, self.stories))
        ax.set_xlabel('Interstory Drift Ratio (Drift/Story Height)')
        ax.set_ylabel('Story')
        ax.set_xlim(xlim_inf, xlim_sup)

        # Plot corner drift
        y = [i for i in range(1, self.stories)]
        ax.plot(max_corner_x, y, label='max_corner_x')
        ax.plot(max_center_x, y, label='max_center_x',linestyle='--')

        # Plot center drift
        ax.plot(max_corner_y, y, label='max_corner_y')
        ax.plot(max_center_y, y, label='max_center_y',linestyle='--')

        # Plot NCH433 limits
        ax.axvline(x=0.002, color='r', linestyle='--', label='NCh433 - 5.9.2 = 0.002')
        #ax.axvline(x=0.002+(0.001), color='r', linestyle='--', label=f'NCh433 - 5.9.3 = {0.002+(0.001)}')
        ax.legend()
        self.plotSave(fig)
        return ax

    def plotModelSpectrum(self, spectrum_x:list[float], spectrum_y:list[float], spectrum_z:list[float], plotNCh433:bool = True):
        # Input params
        fig, ax, y = self.plotConfig(self.input_title)
        ax.set_xlabel('T (s)')
        ax.set_ylabel('Acceleration (m/s/s)')

        # Plot Spectrums
        if plotNCh433:
            ax = self.NCh433Spectrum(ax)
        x = np.linspace(0.003, 2, 1000)
        ax.plot(x, spectrum_x, label='Spectrum X')
        ax.plot(x, spectrum_y, label='Spectrum Y')
        ax.plot(x, spectrum_z, label='Spectrum Z')
        ax.legend()
        self.plotSave(fig)
        return ax

    @staticmethod
    def NCh433Spectrum(ax, S = 1, To = 0.3, p = 1.5, Ao = 0.3 *9.81 , Io = 1.2, R = 5):
        # Input params
        T = np.linspace(0,2.,1000)
        Sah = np.zeros(1000)
        Sav = np.zeros(1000)

        # Compute spectrum
        for i in range(1000):
            tn = T[i]
            alpha = (1 + 4.5*(tn/To)**p)/(1 +(tn/To)**3)
            Sah[i] = S*Ao*alpha/(R/Io)
            Sav[i] = 2/3 * S*Ao*alpha/(R/Io)

        # Plot spectrum
        ax.plot(T, Sah, linestyle='--', label='NCh433 Horizontal')
        ax.plot(T, Sav, linestyle='--', label='NCh433 Vertical')
        return ax

    def plotLocalStoriesSpectrums(self, ModelSimulation: ModelSimulation, dir_:str, accel_df:pd.DataFrame, stories_df:pd.DataFrame,
                             stories_lst:list[int], T:np.ndarray, plot:bool=True, ax:Optional[plt.Axes]=None,
                             method:str='Fix Base', linestyle:str='--'):
        # Input params
        self.file_name = f'{self.sim_type}_{self.mag}_{self.rup_type}_s{self.station}_{dir_.upper()}'
        assert dir_ in ['x', 'y', 'z'], f'dir must be x, y or z! Current: {dir}'
        if ax is None:
            fig, ax, _ = self.plotConfig(self.sprectums_title)
        else:
            self.sprectums_title = f'{method} {self.sprectums_title}'
            fig = ax.figure
        ax.set_xlabel('T (s)')
        ax.set_ylabel(f'Acceleration in {dir_.upper()} (m/s/s)')
        nu = 0.05
        w  = 2 * np.pi / np.array(T)

        # Plot Spectrum
        for i in stories_lst:
            df = accel_df[stories_df.loc[i].index].copy()
            df.loc[:,'Average'] = df.mean(axis=1)
            adir = df.xs(dir_, level='Dir')['Average'][::16]
            Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [ModelSimulation.pwl(adir.values, wi, nu)]]
            ax.plot(T, Spe, label=f'{method}: Story {i}', linestyle=linestyle)
        ax.legend()
        if plot:
            self.plotSave(fig)
        return ax

    def plotLocalBaseSpectrum(self, ModelSimulation: ModelSimulation, accel_df:pd.DataFrame, stories_df:pd.DataFrame,
                         T:np.ndarray, spectrum_modes:list[float], plot_z:bool=True):
        # Input params
        fig, ax, _ = self.plotConfig(self.base_spectrum_title)
        ax.set_xlabel('T (s)')
        ax.set_ylabel('Acceleration (m/s/s)')
        nu = 0.05
        w  = 2 * np.pi / np.array(T)
        df = accel_df[stories_df.loc[0].index].copy()
        df.loc[:,'Average'] = df.mean(axis=1)

        # Compute and plot spectrum
        ae = df.xs('x', level='Dir')['Average'][::16]
        an = df.xs('y', level='Dir')['Average'][::16]
        Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [ModelSimulation.pwl(ae.values, wi, nu)]]
        Spn = [max(max(u_y), abs(min(u_y))) * wi**2 for wi in w for u_y, _ in [ModelSimulation.pwl(an.values, wi, nu)]]
        ax.plot(T, Spe, label='Dir X')
        ax.plot(T, Spn, label='Dir Y')

        # Plot z if desired
        if plot_z:
            az = df.xs('z', level='Dir')['Average'][::16]
            Spz = [max(max(u_z), abs(min(u_z))) * wi**2 for wi in w for u_z, _ in [ModelSimulation.pwl(az.values, wi, nu)]]
            ax.plot(T, Spz, label='Dir Z')

        # Plot the modes in vertical lines with squares or crosses
        for i, mode in enumerate(spectrum_modes):
            ax.axvline(x=mode, linestyle='--', label=f'Mode{i} = {mode}',color='red')

        ax.legend()
        self.plotSave(fig)
        return ax

    def plotLocalShearBaseOverTime(self, time:np.ndarray, time_shear_fma:list[float], time_shear_react:pd.Series, dir_:str):
        # Input params
        self.file_name = f'{self.sim_type}_{self.mag}_{self.rup_type}_s{self.station}_{dir_.upper()}'
        if dir_ not in ['x','X','y','Y','e','E','n','N']:
            raise ValueError(f'dir must be x, y, e or n! Current: {dir}')
        fig, ax, _ = self.plotConfig(self.base_shear_ss_title)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel(f'Shear in {dir_.upper()} direction (kN)')
        ax.plot(time, time_shear_fma, label='Method: F=ma')
        ax.plot(time, time_shear_react,linestyle='--', label='Method: Node reactions')
        ax.legend()
        self.plotSave(fig)


