import matplotlib.pyplot as plt

# Valores de cada variable a lo largo del tiempo
sobrelendig = [120, 125, 130, 135, 140, 145, 150, 155, 160]
mercado_inmobiliario = [100, 110, 120, 130, 140, 150, 160, 150, 140, 130]
credito_hipotecario = [80, 85, 90, 92, 94, 95, 93, 90, 85, 80]
derivados_financieros = [200, 225, 250, 275, 300, 325, 350, 300, 250, 200]
regulacion = [0, 0, 0, 0, 0, 10, 50, 100, 150, 200]
riesgo_crediticio = [1, 2, 3, 4, 5, 6, 8, 10, 12, 10]
securitizacion = [50, 60, 70, 80, 90, 100, 80, 60, 40, 20]
cdos = [100, 125, 150, 175, 200, 225, 250, 200, 150, 100]
interes_bajo = [1.25, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.25]
crisis_financiera = [1200, 1250, 1300, 1350, 1400, 1350, 1300, 1250, 1200, 1250]

# Intervalo de tiempo
anios = [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010]

# Crear figura y subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

# Gráfico 1 - Unidades en cantidades
ax1.plot(anios, sobrelendig, label='Sobrelendig')
ax1.plot(anios, mercado_inmobiliario, label='Mercado inmobiliario')
ax1.plot(anios, credito_hipotecario, label='Crédito hipotecario')
ax1.plot(anios, derivados_financieros, label='Derivados financieros')
ax1.set_xlabel('Años')
ax1.set_ylabel('Unidades')
ax1.set_title('Variables relacionadas con la crisis financiera del 2008 - Unidades en cantidades')

# Gráfico 2 - Unidades en dólares
ax2.plot(anios, regulacion, label='Regulación')
ax2.plot(anios, riesgo_crediticio, label='Riesgo crediticio')
ax2.plot(anios, securitizacion, label='Securitización')
ax2.set_xlabel('Años')
ax2.set_ylabel('Unidades')
ax2.set_title('Variables relacionadas con la crisis financiera del 2008 - Unidades en dólares')

# Gráfico 3 - Unidades en miles de millones de dólares
ax3.plot(anios, cdo, label='CDOs')
ax3.set_xlabel('Años')
ax3.set_ylabel('Unidades')
ax3.set_title('Variables relacionadas con la crisis financiera del 2008 - Unidades en miles de millones de dólares')

# Ajustar leyenda y mostrar gráfico
ax1.legend()
ax2.legend()
ax3.legend()
plt.tight_layout()
plt.show()
