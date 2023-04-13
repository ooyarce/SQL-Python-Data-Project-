import matplotlib.pyplot as plt
import numpy as np

# Valores de las variables
sobrelendig = [4, 4, 4, 5, 5, 6, 7, 8, 9, 9, 9]
mercado_inmobiliario = [6, 6, 7, 8, 8, 7, 6, 5, 4, 4, 5]
credito_hipotecario = [8, 8, 7, 6, 6, 7, 8, 9, 10, 10, 9]
derivados_financieros = [4, 4, 4, 5, 6, 7, 8, 9, 10, 10, 9]
regulacion = [5, 5, 5, 5, 6, 7, 8, 8, 8, 9, 9]
riesgo_crediticio = [8, 8, 8, 9, 9, 10, 10, 10, 9, 8, 8]
securitizacion = [6, 6, 7, 8, 8, 7, 6, 5, 4, 4, 5]
cdos = [7, 7, 8, 9, 9, 10, 10, 9, 8, 8, 9]
interes_bajo = [1, 1, 1, 1, 1, 1, 1, 1, 1, 5.5, 5.5]
crisis_financiera = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

# Tiempo
time = np.arange(2001, 2012)

# Gráfico
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
plt.subplots_adjust(hspace=0.5)

# Variable Sobrelendig
ax1.plot(time, sobrelendig, label="Sobrelendig")
ax1.set_ylabel("Monto del préstamo (en miles de dólares)")
ax1.set_title("Variables financieras durante la crisis del 2008")
ax1.legend()

# Variables de mercado inmobiliario
ax2.plot(time, mercado_inmobiliario, label="Mercado Inmobiliario")
ax2.plot(time, credito_hipotecario, label="Crédito Hipotecario")
ax2.set_ylabel("Monto (en miles de dólares)")
ax2.legend()

# Variables de riesgo y regulación
ax3.plot(time, derivados_financieros, label="Derivados Financieros")
ax3.plot(time, regulacion, label="Regulación")
ax3.plot(time, riesgo_crediticio, label="Riesgo Crediticio")
ax3.plot(time, securitizacion, label="Securitización")
ax3.plot(time, cdos, label="CDOs")
ax3.plot(time, interes_bajo, label="Interés Bajo")
ax3.plot(time, crisis_financiera, label="Crisis Financiera")
ax3.set_ylabel("Monto (logarítmico)")
ax3.set_xlabel("Año")
ax3.legend(loc='upper right', bbox_to_anchor=(1, 1))

plt.show()
