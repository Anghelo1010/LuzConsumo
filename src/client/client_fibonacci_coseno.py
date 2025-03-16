import requests
import json
from tkinter import *
from tkinter import messagebox
import math
import time

# Configuración del servidor (ajusta la URL si el servidor está en otro dispositivo)
SERVER_URL = "http://localhost:5000"  # Cambia a la IP del servidor si es necesario
TOKEN = None  # Almacenará el token JWT tras el login

# Función para calcular Fibonacci exacto
def fibonacci_exacto(n):
    phi = (1 + math.sqrt(5)) / 2
    psi = (1 - math.sqrt(5)) / 2
    return round((math.pow(phi, n) - math.pow(psi, n)) / math.sqrt(5))

# Función para aproximar Fibonacci usando coseno
def fibonacci_coseno(n, theta):
    phi = (1 + math.sqrt(5)) / 2
    return (math.cos(n * theta) / math.sqrt(5)) * math.pow(phi, n)

# Función para iniciar sesión y obtener el token
def login():
    global TOKEN
    try:
        email = entry_email.get()
        clave = entry_clave.get()
        payload = {"email": email, "clave": clave}
        response = requests.post(f"{SERVER_URL}/login", json=payload)
        response.raise_for_status()
        TOKEN = response.json()["token"]
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso.")
        login_frame.pack_forget()  # Ocultar login
        main_frame.pack()  # Mostrar interfaz principal
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"No se pudo conectar al servidor: {e}")
    except KeyError:
        messagebox.showerror("Error", "Credenciales inválidas.")

# Función para enviar datos al servidor
def enviar_datos():
    if not TOKEN:
        messagebox.showerror("Error", "Por favor, inicia sesión primero.")
        return

    try:
        n = int(entry_n.get())
        theta = float(entry_theta.get())
        iteraciones = 1  # Fijo para este ejemplo
        precision = 0.0001  # Fijo para este ejemplo

        # Calcular Fibonacci exacto y aproximado
        start_time = time.time()
        fib_exacto = fibonacci_exacto(n)
        fib_coseno = fibonacci_coseno(n, theta)
        error = abs(fib_exacto - fib_coseno)
        tiempo_calculo = time.time() - start_time

        # Preparar datos para enviar al servidor
        payload = {
            "n": n,
            "theta": theta,
            "iteraciones": iteraciones,
            "precision": precision,
            "resultado": fib_coseno,
            "error": error,
            "tiempo_calculo": tiempo_calculo,
            "dispositivo": "Cliente Remoto"
        }

        # Enviar solicitud POST al servidor
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = requests.post(f"{SERVER_URL}/enviar_fibonacci_coseno", json=payload, headers=headers)
        response.raise_for_status()

        messagebox.showinfo("Éxito", "Datos enviados al servidor correctamente.")
    except ValueError as e:
        messagebox.showerror("Error", f"Entrada inválida: {e}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error al enviar datos: {e}")

# Crear la ventana principal con Tkinter
root = Tk()
root.title("Cliente - Fibonacci con Coseno")
root.geometry("400x300")

# Frame para el login
login_frame = Frame(root)
login_frame.pack(pady=20)

Label(login_frame, text="Email").grid(row=0, column=0, padx=10, pady=10)
entry_email = Entry(login_frame)
entry_email.grid(row=0, column=1, padx=10, pady=10)

Label(login_frame, text="Clave").grid(row=1, column=0, padx=10, pady=10)
entry_clave = Entry(login_frame, show="*")
entry_clave.grid(row=1, column=1, padx=10, pady=10)

btn_login = Button(login_frame, text="Iniciar Sesión", command=login)
btn_login.grid(row=2, column=0, columnspan=2, pady=20)

# Frame para la interfaz principal (oculta inicialmente)
main_frame = Frame(root)

Label(main_frame, text="Número de término (n)").grid(row=0, column=0, padx=10, pady=10)
entry_n = Entry(main_frame)
entry_n.grid(row=0, column=1, padx=10, pady=10)

Label(main_frame, text="Ángulo theta (radianes)").grid(row=1, column=0, padx=10, pady=10)
entry_theta = Entry(main_frame)
entry_theta.insert(0, "0.5")  # Valor por defecto
entry_theta.grid(row=1, column=1, padx=10, pady=10)

btn_enviar = Button(main_frame, text="Generar y Enviar Datos", command=enviar_datos)
btn_enviar.grid(row=2, column=0, columnspan=2, pady=20)

# Ejecutar la aplicación
root.mainloop()