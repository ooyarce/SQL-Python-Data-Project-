import numpy as np
import matplotlib.pyplot as plt

# Definir los parámetros para la zona 2 y tipo de suelo D
a = 0.4
T1 = 0.1
T2 = 0.5
T3 = 2.0
T4 = 10.0
pga = 0.25

# Definir los valores de período y aceleración
T = np.logspace(-2, 1, 100)
S = np.zeros_like(T)

# Calcular el espectro de respuesta sísmica
for i, t in enumerate(T):
    if t <= T1:
        S[i] = a * (0.4 + (0.6 * t / T1))
    elif T1 < t <= T2:
        S[i] = a
    elif T2 < t <= T3:
        S[i] = a * (T2 / t)
    elif T3 < t <= T4:
        S[i] = (0.4 - (0.1 * np.log10(t / T3))) * pga
    else:
        S[i] = (0.4 - (0.1 * np.log10(T4 / T3))) * pga * (T4 / t) ** 2

# Graficar el espectro de respuesta sísmica
plt.loglog(T, S)
plt.xlabel('Período (s)')
plt.ylabel('Aceleración (g)')
plt.title('Espectro de respuesta sísmica para zona 2, tipo de suelo D')
plt.grid(True, which="both")
plt.show()
