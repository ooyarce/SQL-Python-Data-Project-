import matplotlib.pyplot as plt
import numpy as np

# Valores de las variables
sobrelendig = [100, 110, 120, 135, 155, 180, 210, 245, 290, 350]
mercado_inmobiliario = [500, 550, 600, 700, 800, 1000, 1200, 1400, 1600, 1800]
credito_hipotecario = [200, 220, 240, 270, 300, 350, 400, 450, 500, 550]
derivados_financieros = [50, 70, 90, 120, 150, 200, 250, 300, 350, 400]
regulacion = [60, 65, 70, 75, 80, 85, 90, 95, 100, 110]
riesgo_crediticio = [20, 25, 30, 35, 40, 50, 60, 70, 80, 90]
securitizacion = [30, 35, 40, 50, 60, 80, 100, 120, 140, 160]
cdos = [10, 15, 20, 25, 30, 40, 50, 60, 70, 80]
interes_bajo = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
crisis_financiera = [0, 0, 0, 0, 10, 50, 100, 150, 200, 300]

# Tiempo
time = np.arange(2001, 2011)

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
ax3.semilogy(time, derivados_financieros, label="Derivados Financieros")
ax3.semilogy(time, regulacion, label="Regulación")
ax3.semilogy(time, riesgo_crediticio, label="Riesgo Crediticio")
ax3.set_ylabel("Monto (logarítmico)")
ax3.set_xlabel("Año")
ax3.legend()

plt.show()
