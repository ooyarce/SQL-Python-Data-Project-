# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
# Objects
from matplotlib.ticker     import FuncFormatter
from matplotlib            import pyplot as plt
from pathlib               import Path
from typing                import Union, Tuple
from numpy.typing          import NDArray
from scipy.signal          import savgol_filter  # Para suavizado
from pyseestko.errors      import PlottingError
from pyseestko.utilities   import pwl
from typing                import List
from sklearn.preprocessing import PowerTransformer
from scipy.stats           import shapiro, fligner

# Packages
import statsmodels.api as sm
import scipy.stats     as stats
import seaborn         as sns 
import pandas          as pd
import numpy           as np
# ==================================================================================
# MAIN FUNCTIONS CLASS
# ==================================================================================
def plotConfig(title:str, x = 19.2, y = 10.8, dpi = 100):
    fig = plt.figure(num=1, figsize=(x, y), dpi=dpi)
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(True)
    ax.set_title(title)
    return fig, ax

def plotStatisticByReplicas(df:pd.DataFrame, statistic:str, title:str, ylabel:str,  x = 19.2, y = 10.8, dpi = 100):
    """
    This function plots the mean values of the replicas of the dataframe.
    It is supossed to use the getCummStatisticalDFs() functions to get the dataframes.
    So, df is supossed to have only a story as index, and the cummulative value of the drifts or spectra
    over the replicas as columns.
    As a example, the df could be like this:
    | Story | Replica 1 | Replica 2 | Replica 3 | ... | Replica 10 |
    |-------|-----------|-----------|-----------|-----|------------|
    | 1     | 0.001     | 0.002     | 0.003     | ... | 0.001      |
    | 2     | 0.002     | 0.003     | 0.004     | ... | 0.002      |
    | 3     | 0.003     | 0.004     | 0.005     | ... | 0.003      |
    | ...   | ...       | ...       | ...       | ... | ...        |
    | 10    | 0.010     | 0.011     | 0.012     | ... | 0.010      |
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with the mean values of the replicas.
    statistic : str
        Statistic to plot. The options are 'mean' and 'std'.
    title : str
        Title of the plot.  
    x : float, optional
        Width of the plot. The default is 19.2.
    y : float, optional
        Height of the plot. The default is 10.8.
    dpi : int, optional
        Dots per inch of the plot. The default is 100.
        
    Returns
    -------
    fig : plt.Figure
        Figure of the plot.
    ax : plt.Axes
        Axes of the plot.
    """
    # Check input
    if statistic not in ['mean', 'std']: raise ValueError(f'Statistic must be mean or std! Current: {statistic}')
    
    # Plot config
    fig, ax = plotConfig(title, x, y, dpi)
    
    # Plot the statistic value over the replicas for a given story
    for i in df.index:
        replicas  = [1,2,3,4,5,6,7,8,9,10]
        mean_vals = df.loc[i].values 
        plt.plot(replicas, mean_vals, label=f'Story {i}')
        
    # Set x values in [1,2,3,4,5,6,7,8,9,10]
    plt.xticks([1,2,3,4,5,6,7,8,9,10])
    plt.xlabel('Number of replicas')
    plt.ylabel(ylabel)
    
    # Write a vline segmented in red color in x=[3,5,10]
    plt.axvline(x=3, color ='black', linestyle=':')
    plt.axvline(x=5, color ='black', linestyle=':')
    plt.axvline(x=10, color='black', linestyle=':')
    
    # Set legend and grid
    plt.legend()
    plt.grid(True)
    plt.show()
    return fig, ax


# Función para verificar supuestos y generar gráficos de normalidad
def analyze_manova_assumptions(
    df:pd.DataFrame, 
    dependent_vars:List[str], 
    group_vars: List[str], 
    project_path:Path, 
    drift:bool=True, 
    xdir:bool=True):
    plt.rcParams.update({
        "text.usetex": True,
        "font.size": 13,
        "font.family": "serif",
        "text.latex.preamble": r'\usepackage{amsmath}'
    })
    
    # Filtrar solo las columnas de interés
    df = df[dependent_vars + group_vars]
    
    # Transformación de Box-Cox
    pt = PowerTransformer(method='box-cox', standardize=True)
    X_transformed = pt.fit_transform(df[dependent_vars])
    df_transformed = pd.DataFrame(X_transformed, columns=dependent_vars)
    for group_var in group_vars:
        df_transformed[group_var] = df[group_var].values
    
    # Verificación de normalidad individual con Shapiro-Wilk
    normality_results = {var: shapiro(X_transformed[:, i]).pvalue for i, var in enumerate(dependent_vars)}
    
    # Verificación de homogeneidad de varianzas con Fligner-Killeen
    df_transformed['combined_factors'] = df_transformed[group_vars].astype(str).agg('-'.join, axis=1)
    homogeneity_results = {}
    for var in dependent_vars:
        grouped_data = [group[var].values for name, group in df_transformed.groupby('combined_factors')]
        _, p_value = fligner(*grouped_data)
        homogeneity_results[var] = p_value
    
    # Generación de gráficos de normalidad en dos filas y cinco columnas
    fig, axes = plt.subplots(2, 5, figsize=(9, 5))
    
    # Etiquetas de estaciones
    station_labels = [f'Estación {i}' for i in [1, 5, 10, 15, 20]]
    
    for i, var in enumerate(dependent_vars):
        # Histograma en la primera fila
        sns.histplot(df_transformed[var], kde=True, ax=axes[0, i])
        axes[0, i].set_title(f'Histograma de normalidad\n{station_labels[i]}') if i == 2 else axes[0, i].set_title(station_labels[i])
        axes[0, i].set_xlabel('')
        axes[0, i].set_ylabel('') if i != 0 else axes[0, i].set_ylabel('Frecuencia')
        
        # Q-Q plot en la segunda fila
        sm.qqplot(df_transformed[var], line='s', ax=axes[1, i])
        #axes[0, i].set_title(station_labels[i])
        axes[1, i].set_title(f'Q-Q Plot de normalidad\n{station_labels[i]}') if i == 2 else axes[1, i].set_title(station_labels[i])
        axes[1, i].set_ylabel('') if i != 0 else axes[1, i].set_ylabel('Cuantiles de la muestra')
        axes[1, i].set_xlabel('Cuantiles teóricos') if i==2 else axes[1, i].set_xlabel('')
    
    file_name = 'drift' if drift else 'spectra'
    xdir = 'x' if xdir else 'y'
    fig_title = f'Métrica de {file_name.capitalize()} en dirección {xdir}'
    fig.suptitle(fig_title)
    fig.subplots_adjust(top=2)  # Ajustar el espacio superior para evitar superposición
    fig.tight_layout()
    fig.savefig(project_path / f'manova_supps_{file_name}_{xdir}.pdf', dpi=100)
    plt.show()
    plt.close(fig)
    # Resultados en un DataFrame
    results_df = pd.DataFrame({
        'Variable': dependent_vars,
        'Normalidad (p-valor)': list(normality_results.values()),
        'Homogeneidad (p-valor)': list(homogeneity_results.values())
    })
    
    return results_df

def analyze_anova_assumptions(
    df:pd.DataFrame, 
    analysis_columns:List[str], 
    project_path:Path):
    """
    Realiza un análisis de los supuestos para ANOVA en las columnas especificadas y guarda los resultados en archivos de imagen.

    Parameters:
    df (pd.DataFrame): DataFrame con las columnas 'Sim_Type', 'Nsubs', 'Station', 'Iteration' y columnas de análisis.
    analysis_columns (list): Lista de las columnas para las cuales se desea realizar el análisis.
    output_file_prefix (str): Prefijo del nombre del archivo para guardar las imágenes de los resultados.
    """
    plt.rcParams.update({
        "text.usetex": True,
        "font.size": 13,
        "font.family": "serif",
        "text.latex.preamble": r'\usepackage{amsmath}'
    })

    for col in analysis_columns:
        # Agrupar por Sim_Type, Nsubs y Station, y calcular la media de la columna especificada
        df_grouped = df.groupby(['Sim_Type', 'Nsubs', 'Station']).agg({col: 'mean'}).reset_index()
        
        # Aplicar la transformación Box-Cox
        df_grouped[f'{col}_boxcox'], fitted_lambda = stats.boxcox(df_grouped[col])

        # Verificar normalidad usando la prueba de Shapiro-Wilk
        shapiro_test = stats.shapiro(df_grouped[f'{col}_boxcox'])

        # Verificar homocedasticidad usando la prueba de Levene
        grouped_data = [df_grouped[df_grouped['Sim_Type'] == g][f'{col}_boxcox'].values for g in df_grouped['Sim_Type'].unique()]
        levene_test  = stats.levene(*grouped_data)

        # Crear la figura y los ejes
        fig, ax = plt.subplots(1, 2, figsize=(8, 5))

        # Histograma para los datos transformados con Box-Cox
        sns.histplot(df_grouped[f'{col}_boxcox'], kde=True, ax=ax[0])
        name = f'Corte Basal X' if col == 'MaxShearX' else f'Corte Basal Y'
        xdir = 'x' if col == 'MaxShearX' else 'y'
        file_name = f'anova_supps_bshear_{xdir}.pdf'
        ax[0].set_title(f'Histograma de {col}')

        # Gráfico Q-Q para verificar normalidad
        sm.qqplot(df_grouped[f'{col}_boxcox'], line='s', ax=ax[1])
        ax[1].set_title(f'Q-Q Plot de {col}')

        # Ajustar la disposición de la figura
        fig.tight_layout()
        fig.subplots_adjust(top=0.85)
        
        # Guardar la figura como imagen
        save_path = project_path / file_name
        save_path.parent.mkdir(parents=True, exist_ok=True)  # Crear directorio si no existe
        fig.suptitle(f'{name}')
        fig.savefig(save_path, dpi=100)
        plt.close(fig)

        # Mostrar resultados de las pruebas en consola
        print(f'fitted_lambda: {fitted_lambda:.3f}')
        print(f"Resultados de la Prueba de Shapiro-Wilk para {name} (Normalidad)")
        print(f"Estadístico: {shapiro_test.statistic:.3f}, Valor p: {shapiro_test.pvalue:.3f}\n")

        print(f"Resultados de la Prueba de Levene para {name} (Homocedasticidad)")
        print(f"Estadístico: {levene_test.statistic:.3f}, Valor p: {levene_test.pvalue:.3f}\n")


# ==================================================================================
# PLOTTING METRICS CLASS
# ==================================================================================
"""
This class is used to perform the seismic analysis of the structure.
It's used to analyse quiclky the structure and get the results of the analysis.
You use it in the main after the results are uploaded to the database.

Parameters
----------
sim_type : int
    Simulation type of the model.
stories : int
    Number of stories of the model.
nsubs : int
    Number of subterrains of the model.
magnitude : float
    Magnitude of the earthquake.
    An example of the magnitude is 6.7.
iteration : int
    Iteration of the simulation.
rupture : int
    Rupture type of the earthquake.
    An example of the rupture is 1 for 'bl'.
station : int
    Station of the earthquake.
    An example of the station is 0.
"""
class Plotting:

    # ==================================================================================
    # INIT PARAMS
    # ==================================================================================
    def __init__(
            self, sim_type:int,
            stories:int, nsubs:int,
            magnitude:float, iteration:int, rupture:int, station:int, 
            show_plots:bool = True, dpi:int = 100, grid:bool = False, file_type:str = 'png'
            ):
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
        # Main atributtes
        self.x_direction = None
        self.direction   = None
        self.dpi         = dpi
        self.file_type   = file_type
        self.sim_type    = sim_type_map.get(sim_type)
        self.stories     = stories
        self.magnitude   = magnitude
        self.iteration   = iteration
        self.rup_type    = rup_type_map.get(rupture)
        self.station     = station
        self.nsubs       = nsubs
        
        # Grey scale for the plots when grid is true
        self.gray_scale_1 = ['#111111', '#333333', '#555555', '#777777', '#999999']
        
        # Plot config
        if not show_plots:
            plt.switch_backend('agg')
        else:
            plt.switch_backend('module://matplotlib_inline.backend_inline')
        
        # Grid params
        self.grid     = grid
        self.grid_id  = None
        
        # Plot and files names
        self.save_path           = Path('')
        self.file_name           = None
        self.id                  = None
        self.drift_title         = None
        self.spectrums_title     = None
        self.base_shear_ss_title = None
    
    def setup_direction(self, x_direction:bool=True):
        self.x_direction = x_direction
        self.direction = 'X' if x_direction else 'Y'
        self.id        = f'{self.sim_type} - {self.stories} stories - {self.nsubs} subs - {self.direction}dir' if self.grid else f'{self.sim_type} -  {self.magnitude}Mw - Station {self.station} - {self.stories} stories - {self.nsubs} subs - {self.direction}dir'
        self.file_name = f'{self.sim_type}_20f{self.nsubs}_{self.direction}' if self.grid else f'{self.sim_type}_{self.magnitude}_{self.rup_type}{self.iteration}_s{self.station}_{self.direction}'
        self.drift_title     = f'Drift Plot - {self.id}'
        self.spectrums_title = f'Story PSa Plot - {self.id}'
        self.base_shear_ss_title = f'Base Shear Plot - {self.id}'
        
    def plotConfig(self, title:str, x = 19.2, y = 10.8):
        """
        This function is used to configure the plot eather for a single metric or for a 
        grid metrics plot. Bewware that if you turn grid in on the plot will be a 3x3 grid
        and the axes will be returned as a 3x3 numpy array. That implies that you will have 
        to add plots in a way of axes[0,0].plot() instead of ax.plot().
        """
        plt.rcParams.update({
            "text.usetex": True,  # Habilitar LaTeX
            "font.size": 13,      # Tamaño de fuente por defecto (puedes cambiar a 12 si lo prefieres)
            "font.family": "serif",  # Usar una fuente serif que es típica en documentos LaTeX
            "text.latex.preamble": r'\usepackage{amsmath}'  # Opcional: paquete extra de LaTeX para matemáticas
        })
        if self.grid:
            fig, axes = plt.subplots(3, 3, figsize=(x, y), dpi=self.dpi)
            for ax in axes.flatten():
                ax.grid(True)
            fig.suptitle(title)  # Título para la figura completa            
            return fig, axes
        else:
            fig = plt.figure(num=1, figsize=(x, y), dpi=self.dpi)
            ax = fig.add_subplot(1, 1, 1)
            ax.grid(True)
            ax.set_title(title)
            return fig, ax

    def plotSave(self, fig):
        self.save_path.mkdir(parents=True, exist_ok=True)
        full_save_path = self.save_path / f'{self.file_name}.{self.file_type}'
        fig.savefig(full_save_path, dpi=100)
        # Mostrar figura solo si el backend no es 'Agg'
        if plt.get_backend() != 'agg':
            plt.show()
        plt.close(fig)  # Asegúrate de cerrar la figura para liberar memoria

    # ==================================================================================
    # PLOT METRICS FUNCTIONS
    # ==================================================================================
    def to_per_mil(self, x, pos):
        return f'{x * 1000:.0f}'
    def to_empty(self, x, pos):
        return ''
    def to_equal(self, x, pos):
        return f'{x}'
    def to_int(self, x, pos):
        return f'{int(x)}'
    def to_dot_mil(self, x, pos):
        return f'{(int(x/1000))}'
    
    def plotModelDrift(self, max_corner_x: list, max_center_x: list, max_corner_y: list, max_center_y:list, xlim_inf:float = 0.0, xlim_sup:float = 0.002,
                       axes:plt.Axes|NDArray[plt.Axes]=None, save_fig:bool=True, legend:bool=True, fig_size: tuple[float, float]=(19.2, 10.8), line_color = None
                       )->plt.Axes|NDArray[plt.Axes]:
        # Plot config
        ax = axes
        if self.grid:
            color_1 = self.gray_scale_1[self.iteration-1]
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]
        fig, axes = self.plotConfig(self.drift_title, x=fig_size[0], y=fig_size[1]) if ax is None else (ax.figure, axes)
        ax = axes
        if self.grid:
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]
        
        # Setup X 
        formatter1 = FuncFormatter(self.to_per_mil) 
        formatter2 = FuncFormatter(self.to_empty)
        formatter3 = FuncFormatter(self.to_equal)
        ax.xaxis.set_major_formatter(formatter1) if self.station in [7,8,9] else ax.xaxis.set_major_formatter(formatter2)
        ax.set_xlabel('Interstory Drift Ratio (Drift/Story Height)‰') if self.station in [8] else ax.set_xlabel('')
        ax.set_xlim(xlim_inf, xlim_sup) if self.station == 1 and self.iteration == 1 else ax.set_xlim(xlim_inf, axes[0, 0].get_xlim()[1])

        # Setup Y axis
        ax.set_yticks([1,5,10,15,20]) #if self.station in [1,4,7] else ax.set_yticks([])
        ax.yaxis.set_major_formatter(formatter3) if self.station in [1,4,7] else ax.yaxis.set_major_formatter(formatter2)
        ax.set_ylabel('Story') if self.station in [4] else ax.set_ylabel('')
        ax.set_ylim(1, self.stories)
        
        # Set local title 
        ax.set_title(f'Station {self.station}')
        
        # Plot center drift
        y = [i for i in range(1, self.stories+1)]
        if self.x_direction:
            candidate = np.array(max_center_x).max() + 0.0005 if self.station == 1  else 0
            ax.set_xlim(xlim_inf, candidate) if candidate > axes[0,0].get_xlim()[1] else ax.set_xlim(xlim_inf, axes[0,0].get_xlim()[1])
            color = color_1 if self.grid and not line_color else 'red'
            linewidth = 0.5 if self.grid and not line_color else 0.6
            marker = 'v'    if line_color else None
            label = 'Iter.Drift' if not line_color else 'Mean Iter.Drift'
            ax.plot(max_center_x, y, label=label, marker=marker, color=color, linewidth=0.5, markersize=2)
        else:
            candidate = np.array(max_center_y).max() + 0.0005 if self.station == 1  else 0
            ax.set_xlim(xlim_inf, candidate) if candidate > axes[0,0].get_xlim()[1] else ax.set_xlim(xlim_inf, axes[0,0].get_xlim()[1])
            color = color_1 if self.grid and not line_color else 'blue'
            linewidth = 0.5 if self.grid and not line_color else 0.6
            marker = 'd'    if line_color else None
            label = 'Iter.Drift' if not line_color else 'Mean Iter.Drift'
            ax.plot(max_center_y, y, label=label, marker=marker, color=color, linewidth=linewidth, markersize=2)
        
        # Plot NCH433 limits
        color2 = 'blue' if self.x_direction else 'red'
        ax.axvline(x=0.002, color=color2, linestyle='--', linewidth=0.65, alpha = 0.9, label='NCh433 Limit=0.002') if line_color else None

        # Set legend and save fig if needed
        if legend:
            fig.subplots_adjust(top=0.85)  # Ajustar el espacio superior para evitar superposición
            handles, labels = axes[0, 0].get_legend_handles_labels()
            fig.legend([handles[-4], handles[-2], handles[-1]], [labels[-4], labels[-2], labels[-1]], 
                       loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=fig.transFigure, fontsize='xx-small')

        if save_fig:
            fig.tight_layout()
            self.plotSave(fig)
        return axes

    def plotLocalStoriesSpectrums(self,
                            accel_df:pd.DataFrame, story_nodes_df:pd.DataFrame, direction:str, stories_lst:list[int], 
                            save_fig:bool=True, axes:plt.Axes=None, fig_size:tuple[float, float]=(19.2, 10.8)
                            )->Tuple[plt.Axes, pd.DataFrame]:   #linestyle:str='--'
        # Init params
        colors         = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'purple', 'brown']
        line_styles    = ['-', '--', '-.', ':']  # Diferentes estilos de línea
        
        # Check input and raise errors
        if direction not in ['x', 'y', 'z']: raise PlottingError(f'Dir must be x, y or z! Current: {direction}')
        if len(stories_lst) > len(colors):   raise PlottingError(f'Not enough colors for the number of stories! Current: {len(stories_lst)}\n Try adding less stories.')

        # Plot config
        ax = axes
        if self.grid:
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]
        fig, axes = self.plotConfig(self.spectrums_title, x=fig_size[0], y=fig_size[1]) if ax is None else (ax.figure, axes)
        ax = axes
        if self.grid:
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]
        # Set local title 
        ax.set_title(f'Station {self.station}')
               
        # Setup axis
        formatter = FuncFormatter(self.to_empty)
        ax.set_xlabel('T (s)') if self.station in [7,8,9] else ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel(f'Acceleration in {direction.upper()} (m/s/s)') if self.station in [4] else ax.set_ylabel('')
        
        # Make plot spectrum
        nu = 0.05
        T = np.linspace(0.003, 2, 1000)
        w  = 2 * np.pi / np.array(T)
        spa_lst = []
        for i, story in enumerate(stories_lst):
            # Setup color and linestyle
            color = colors[i % len(colors)]
            line_style = line_styles[i % len(line_styles)]

            # Obtain the spectrum
            df = accel_df[story_nodes_df.loc[story].index].copy()
            df.loc[:,'Average'] = df.mean(axis=1) # We use the acceleration in the center of mass
            adir = df.xs(direction, level='Dir')['Average'][::16]
            Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [pwl(adir.values, wi, nu)]]
            Spe = np.array(Spe)
            spa_lst.append(Spe)

            # Write the maximum values of the spectrum
            ax.plot(T, Spe, label=f'Story {story}', alpha=0.1, linestyle=line_style, color=color, linewidth=0.5)

        # Compute df
        spa_df = pd.DataFrame({f'Story {story} {direction}': spa for story, spa in zip(stories_lst, spa_lst)}, index=T)

        if save_fig:
            self.plotSave(fig)
        return axes, spa_df
    
    def plotMeanStoriesSpectrums(self,
                            mean_spectras:pd.DataFrame, direction:str, stories_lst:list[int], 
                            save_fig:bool=True, axes:plt.Axes=None,
                            fig_size:tuple[float, float]=(19.2, 10.8)
                            )->Tuple[plt.Axes, pd.DataFrame]:   #linestyle:str='--'
        # Init params
        colors         = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'purple', 'brown']
        line_styles    = ['-', '--', '-.', ':']  # Diferentes estilos de línea
        
        # Check input and raise errors
        if direction not in ['x', 'y', 'z']: raise PlottingError(f'Dir must be x, y or z! Current: {direction}')
        if len(stories_lst) > len(colors):   raise PlottingError(f'Not enough colors for the number of stories! Current: {len(stories_lst)}\n Try adding less stories.')

        # Plot config
        ax = axes
        if self.grid:
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]
        fig, axes = self.plotConfig(self.spectrums_title, x=fig_size[0], y=fig_size[1]) if ax is None else (ax.figure, axes)
        ax = axes
        if self.grid:
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]

        # Set local title 
        ax.set_title(f'Station {self.station}')

        # Setup axis
        formatter1 = FuncFormatter(self.to_empty)
        formatter2 = FuncFormatter(self.to_int)
        ax.set_xlabel('T (s)') if self.station in [7,8,9] else ax.xaxis.set_major_formatter(formatter1)
        ax.set_ylabel(f'Acceleration in {direction.upper()} (m/s/s)') if self.station in [4] else ax.set_ylabel('')
        ax.yaxis.set_major_formatter(formatter2)
        
        # Make plot spectrum
        T = np.linspace(0.003, 2, 1000)
        spa_lst = []
        for i, story in enumerate(stories_lst):
            # Setup color and linestyle
            color = colors[i % len(colors)]
            line_style = line_styles[i % len(line_styles)]

            # Obtain the spectrum
            df = mean_spectras[f'Story {story} {direction}'].copy()
            df.loc[:,'Mean'] = df.mean(axis=1) # We use the acceleration in the center of mass
            Spe = np.array(df['Mean'])
            spa_lst.append(Spe)

            # Write the maximum values of the spectrum
            ax.plot(T, Spe, label=f'Story {story}', linestyle=line_style, color=color, linewidth=0.5)

        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles[-5:], labels[-5:], loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=fig.transFigure, fontsize='x-small')
        
        # plot a vertical line at the 3rd mode of vibration (T=0.82)
        ax.axvline(x=0.82, color='black', linestyle='--', linewidth=0.5, alpha = 0.9, label='Torsional Mode')
        if save_fig:
            self.plotSave(fig)
    
    def plotShearBaseOverTime(self, time:np.ndarray, time_shear_fma:list[float], Qmax:float, dir_:str, axes: plt.Axes=None,
                              save_fig:bool=True, fig_size:tuple[float, float]=(19.2, 10.8), mean=False, leyend=False,
                              ylim_inf=-100, ylim_sup=100)->plt.Axes|NDArray[plt.Axes]:
        # Input params
        if dir_ not in ['x','X','y','Y']: raise ValueError(f'dir must be x, y! Current: {dir}')

        # Plot config
        ax = axes
        if self.grid:
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]
        fig, axes = self.plotConfig(self.base_shear_ss_title, x=fig_size[0], y=fig_size[1]) if ax is None else (ax.figure, axes)
        ax = axes
        if self.grid:
            row = (self.station - 1) // 3
            col = (self.station - 1) % 3 
            ax  = axes[row, col]
        
        # Set local title 
        ax.set_title(f'Station {self.station}')
        
        # Plot
        alpha = 0.1 if not mean else 1
        ax.plot(time, time_shear_fma, label='Shear Base', color='blue', linewidth=0.5, alpha=alpha)
        ax.axhline(y=Qmax,  color='red', linestyle='--', linewidth=0.5, alpha = 0.9, label='NCh433 Qmax') 
        ax.axhline(y=-Qmax, color='red', linestyle='--', linewidth=0.5, alpha = 0.9, label=None) 
        
        # Setup axis
        formatter1 = FuncFormatter(self.to_empty)
        formatter2 = FuncFormatter(self.to_equal)
        formatter3 = FuncFormatter(self.to_dot_mil)
        ax.set_ylim(ylim_inf, ylim_sup) if self.station ==1 and self.iteration == 1 else ax.set_ylim(axes[0, 0].get_ylim())
        ax.set_xlabel('Time (s)') if self.station in [8] else ax.xaxis.set_major_formatter(formatter1)
        ax.set_ylabel(f'Shear in {dir_.upper()} direction (Mega Newtons)')  if self.station in [4] else ax.set_ylabel('')
        ax.xaxis.set_major_formatter(formatter2) if self.station in [7,8,9] else ax.xaxis.set_major_formatter(formatter1)
        ax.yaxis.set_major_formatter(formatter3) if self.station in [1,4,7] else ax.yaxis.set_major_formatter(formatter1)
    
        candidate_neg = np.array(time_shear_fma).min() - 1000 if self.station == 1 and mean else 0
        ax.set_ylim(candidate_neg, axes[0,0].get_ylim()[1]) if candidate_neg < axes[0,0].get_ylim()[0] else ax.set_ylim(axes[0,0].get_ylim()[0], axes[0,0].get_ylim()[1])
        candidate_pos = np.array(time_shear_fma).max() + 1000 if self.station == 1 and mean else 0
        ax.set_ylim(axes[0,0].get_ylim()[0], candidate_pos) if candidate_pos > axes[0,0].get_ylim()[1] else ax.set_ylim(axes[0,0].get_ylim()[0], axes[0,0].get_ylim()[1])
        
        if leyend:
            handles, labels = axes[0, 0].get_legend_handles_labels()
            fig.legend([handles[-3], handles[-2]], [labels[-3], labels[-2]], 
                       loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=fig.transFigure, fontsize='small')
            
        if save_fig:
            self.plotSave(fig)
        return axes

