import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
# Valores de las variables
sobrelendig = [4, 4, 4, 5, 5, 6, 7, 8, 9, 9, 9]
mercado_inmobiliario = [6, 6, 7, 8, 8, 7, 6, 5, 4, 4, 5]
credito_hipotecario = [7, 7, 6, 5, 5, 6, 7, 8, 9, 9, 8]
derivados_financieros = [4, 4, 4, 5, 6, 7, 8, 9, 10, 10, 9]
regulacion = [5, 5, 5, 5, 6, 7, 8, 8, 8, 9, 9]
riesgo_crediticio = [4, 4, 4, 5, 6, 8, 9, 9, 7, 6, 5]
securitizacion = [5, 5, 6, 7, 8, 9, 8, 7, 6, 5, 4]
cdos = [7, 7, 8, 9, 9, 10, 10, 9, 8, 8, 9]
interes_bajo = [1, 1, 1, 1, 1, 1, 1, 1, 1, 5.5, 6.5]
crisis_financiera = [0, 0, 0, 0, 1, 1, 1, 2, 3, 4, 1]

# Tiempo
time = np.arange(2001, 2012)

# Gráfico
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
plt.subplots_adjust(hspace=0.5)


# Variable Sobrelendig
spl = make_interp_spline(time, sobrelendig)
x_new = np.linspace(time.min(), time.max(), 100)
y_new = spl(x_new)
spl2 = make_interp_spline(time,regulacion)
spl3 = make_interp_spline(time,riesgo_crediticio)
spl4 = make_interp_spline(time,securitizacion)
y2 = spl2(x_new)
y3 = spl3(x_new)
y4 = spl4(x_new)
ax1.plot(x_new, y2, label="Regulación")
ax1.plot(x_new, y3, label="Riesgo Crediticio")
ax1.plot(x_new, y4, label="Securitización")
ax1.plot(x_new, y_new, label="Sobrelendig")
ax1.set_ylabel("Monto del préstamo (en miles de dólares)")
ax1.set_title("Variables financieras durante la crisis del 2008")
ax1.legend()

# Variables de mercado inmobiliario
spl = make_interp_spline(time, mercado_inmobiliario)
spl2 = make_interp_spline(time, credito_hipotecario)
y1 = spl(x_new)
y2 = spl2(x_new)
ax2.plot(x_new, y1, label="Mercado Inmobiliario")
ax2.plot(x_new, y2, label="Crédito Hipotecario")
ax2.set_ylabel("Monto (en miles de dólares)")
ax2.legend()

# Variables de riesgo y regulación
spl1 = make_interp_spline(time,derivados_financieros)

spl5 = make_interp_spline(time,cdos)
spl6 = make_interp_spline(time,interes_bajo)
spl7 = make_interp_spline(time,crisis_financiera)
y1 = spl1(x_new)

y5 = spl5(x_new)
y6 = spl6(x_new)
y7 = spl7(x_new)
ax3.plot(x_new, y1, label="Derivados Financieros")

ax3.plot(x_new, y5, label="CDOs")
ax3.plot(x_new, y6, label="Interés Bajo")
ax3.plot(x_new, y7, label="Crisis Financiera")
ax3.set_ylabel('Magnitud')
ax3.set_xlabel("Año")
ax3.legend(loc='upper right', bbox_to_anchor=(1, 1))

plt.show()
