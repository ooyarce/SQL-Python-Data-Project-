# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
# Objects
from matplotlib          import pyplot as plt
from pathlib             import Path
from typing              import Optional
from scipy.signal        import savgol_filter  # Para suavizado
from pyseestko.errors    import PlottingError
from pyseestko.utilities import pwl
from adjustText          import adjust_text

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
    
    
    
    
    # ==================================================================================
    # INIT PARAMS
    # ==================================================================================
    def __init__(self, sim_type:int,  stories:int, magnitude:float, rupture:int, station:int):
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
        #self.save_path = Path(path) # old way of doing it
        self.save_path = Path('')
        
        
        self.file_name       = f'{self.sim_type}_{self.magnitude}_{self.rup_type}_s{self.station}'
        self.id              = f'{self.sim_type} |  {self.magnitude} | {self.rup_type} | Station {self.station}'
        self.drift_title     = f'Drift per story plot | {self.id}'
        self.spectrums_title = f'Story PSa plot | {self.id}'
        self.base_shear_ss_title = f'Base Shear Plot | {self.id}'
        #self.input_title         = f'Input Accelerations Response Spectra Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        #self.base_spectrum_title = f'Base Accelerations Spectrum Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'

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




    # ==================================================================================
    # PLOT METRICS FUNCTIONS
    # ==================================================================================
    def plotModelDrift(self, max_corner_x: list, max_center_x: list, max_corner_y: list, max_center_y:list, xlim_inf:float = 0.0, xlim_sup:float = 0.008 ):
        # Input params
        fig, ax, y = self.plotConfig(self.drift_title)
        ax.set_yticks(range(1, self.stories))
        ax.set_xlabel('Interstory Drift Ratio (Drift/Story Height)')
        ax.set_ylabel('Story')
        ax.set_xlim(xlim_inf, xlim_sup)

        # Plot corner drift
        y = [i for i in range(1, self.stories+1)]
        ax.set_yticks(y)
        ax.plot(max_corner_x, y, label='max_corner_x', color='blue')
        ax.plot(max_center_x, y, label='max_center_x',linestyle='--', color='red')

        # Plot center drift
        ax.plot(max_corner_y, y, label='max_corner_y', color='cyan')
        ax.plot(max_center_y, y, label='max_center_y',linestyle='--', color='magenta')

        # Plot NCH433 limits
        ax.axvline(x=0.002, color='black', linestyle='--', linewidth=2, alpha = 0.9, label='NCh433 Limit - 5.9.2 = 0.002')

        ax.legend()
        self.plotSave(fig)
        return ax

    def plotLocalStoriesSpectrums(self,
                            accel_df:pd.DataFrame, story_nodes_df:pd.DataFrame, direction:str, stories_lst:list[int],
                            plot:bool=True, ax:Optional[plt.Axes]=None, method:str='Fix Base', soften:bool=False):   #linestyle:str='--'
        # Init params
        self.file_name = f'{self.sim_type}_{self.magnitude}_{self.rup_type}_s{self.station}_{direction.upper()}'
        colors         = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'purple', 'brown']
        line_styles    = ['-', '--', '-.', ':']  # Diferentes estilos de línea
        texts          = []
        
        # Check input and raise errors
        if direction not in ['x', 'y', 'z']: raise PlottingError(f'Dir must be x, y or z! Current: {direction}')
        if len(stories_lst) > len(colors):   raise PlottingError(f'Not enough colors for the number of stories! Current: {len(stories_lst)}\n Try adding less stories.')
        
        # Plot config
        if ax is None: fig, ax, _ = self.plotConfig(self.spectrums_title)
        else:
            self.spectrums_title = f'{method} {self.spectrums_title}'
            fig = ax.figure
        ax.set_xlabel('T (s)')
        ax.set_ylabel(f'Acceleration in {direction.upper()} (m/s/s)')
        nu = 0.05
        T = np.linspace(0.003, 2, 1000)
        w  = 2 * np.pi / np.array(T)

        # Make plot spectrum
        for i, story in enumerate(stories_lst):
            # Setup color and linestyle
            color = colors[i % len(colors)]
            line_style = line_styles[i % len(line_styles)] 

            # Obtain the spectrum
            df = accel_df[story_nodes_df.loc[story].index].copy()
            df.loc[:,'Average'] = df.mean(axis=1)
            adir = df.xs(direction, level='Dir')['Average'][::16]
            Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [pwl(adir.values, wi, nu)]]
            Spe = np.array(Spe)
            
            # Soften the spectrum
            if soften and len(Spe) > 50: Spe = savgol_filter(Spe, 51, 3) 
            
            # Write the maximum values of the spectrum
            max_value = max(Spe)
            max_index = np.argmax(Spe)
            annotation = ax.annotate(f'{max_value:.2f}', xy=(T[max_index], max_value), textcoords="offset points", xytext=(0,10), ha='center')
            texts.append(annotation)
            ax.plot(T, Spe, label=f'{method}: Story {story}', linestyle=line_style, color=color)
            
        #adjust_text(texts, arrowprops=dict(arrowstyle='->', color='blue'), ax=ax)
        ax.legend()
        if plot:
            self.plotSave(fig)
        return ax
    
    def plotShearBaseOverTime(self, time:np.ndarray, time_shear_fma:list[float], Qmin:float, Qmax:float, dir_:str):
        # Input params
        if dir_ not in ['x','X','y','Y']: raise ValueError(f'dir must be x, y! Current: {dir}')
        self.file_name = f'{self.sim_type}_{self.magnitude}_{self.rup_type}_s{self.station}_{dir_.upper()}'
        
        fig, ax, _ = self.plotConfig(self.base_shear_ss_title)
        ax.axhline(y=Qmax,  color='red', linestyle='--', linewidth=2, alpha = 0.9, label='NCh433 Qmax - 6.3.7.1')
        ax.axhline(y=-Qmax, color='red', linestyle='--', linewidth=2, alpha = 0.9, label=None)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel(f'Shear in {dir_.upper()} direction (kN)')
        ax.plot(time, time_shear_fma, label='Method: F=ma')
        ax.legend()
        self.plotSave(fig)







    """
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
        Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [pwl(ae.values, wi, nu)]]
        Spn = [max(max(u_y), abs(min(u_y))) * wi**2 for wi in w for u_y, _ in [pwl(an.values, wi, nu)]]
        ax.plot(T, Spe, label='Dir X')
        ax.plot(T, Spn, label='Dir Y')

        # Plot z if desired
        if plot_z:
            az = df.xs('z', level='Dir')['Average'][::16]
            Spz = [max(max(u_z), abs(min(u_z))) * wi**2 for wi in w for u_z, _ in [pwl(az.values, wi, nu)]]
            ax.plot(T, Spz, label='Dir Z')

        # Plot the modes in vertical lines with squares or crosses
        for i, mode in enumerate(spectrum_modes):
            ax.axvline(x=mode, linestyle='--', label=f'Mode{i} = {mode}',color='red')

        ax.legend()
        self.plotSave(fig)
        return ax






    # ==================================================================================
    # AUXIALIARY FUNCTIONS
    # ==================================================================================   
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
    """