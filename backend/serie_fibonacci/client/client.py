import mysql.connector
import math
from tkinter import *
from tkinter import messagebox
from datetime import datetime

def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",  # Ajusta según tu configuración
            password="tu_contraseña",
            database="fibonacci_trigonometric"
        )
        print("Conexión a la base de datos exitosa desde el cliente")
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos desde el cliente: {e}")
        raise

def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def insertar_valores():
    try:
        n = int(entry_n.get())
        usuario_id = int(entry_usuario.get())
        print(f"Generando {n} términos de Fibonacci para usuario {usuario_id}")
        conexion = conectar()
        cursor = conexion.cursor()

        for i in range(n):
            fib = float(fibonacci(i))
            cos_fib = math.cos(fib)
            error = abs(fib / (fib + 1) - cos_fib) if fib != 0 else 0
            iteraciones = i + 1
            fecha = datetime.now()
            sql = """
                INSERT INTO fibonacci_cos (usuario_id, tipo_serie, resultado, cos_fib, error, iteraciones, fecha)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            valores = (usuario_id, "Fibonacci", fib, cos_fib, error, iteraciones, fecha)
            cursor.execute(sql, valores)
            print(f"Insertado: resultado={fib}, cos_fib={cos_fib}, error={error}")
            conexion.commit()

        messagebox.showinfo("Éxito", f"{n} valores generados e insertados correctamente.")
        cursor.close()
        conexion.close()

    except Exception as e:
        messagebox.showerror("Error", f"Error al insertar valores: {str(e)}")
        print(f"Error en insertar_valores: {e}")

root = Tk()
root.title("Cliente - Serie de Fibonacci")
root.geometry("400x200")

Label(root, text="Número de términos de Fibonacci").grid(row=0, column=0, padx=10, pady=10)
entry_n = Entry(root)
entry_n.grid(row=0, column=1, padx=10, pady=10)

Label(root, text="ID del usuario").grid(row=1, column=0, padx=10, pady=10)
entry_usuario = Entry(root)
entry_usuario.grid(row=1, column=1, padx=10, pady=10)

btn_insertar = Button(root, text="Generar y Enviar Datos", command=insertar_valores)
btn_insertar.grid(row=2, column=0, columnspan=2, pady=20)

root.mainloop()