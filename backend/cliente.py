from tkinter import *
from tkinter import messagebox
import requests

SERVER_URL = "http://localhost:5000/insertar"

def insertar_valores():
    try:
        n = int(entry_n.get())
        num_terminos = int(entry_terminos.get())
        tipo_serie = serie_var.get()
        
        data = {"n": n, "num_terminos": num_terminos, "tipo_serie": tipo_serie}
        response = requests.post(SERVER_URL, json=data)
        
        if response.status_code == 200:
            messagebox.showinfo("Éxito", f"Datos enviados al servidor correctamente.\nSerie: {tipo_serie}\nPuntos: {n}\nTérminos: {num_terminos}")
        else:
            messagebox.showerror("Error", "No se pudo enviar los datos al servidor.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = Tk()
root.title("Cliente - Series Matemáticas")
root.geometry("400x250")

Label(root, text="Número de puntos (n):").grid(row=0, column=0, padx=10, pady=10)
entry_n = Entry(root)
entry_n.grid(row=0, column=1, padx=10, pady=10)

Label(root, text="Número de términos:").grid(row=1, column=0, padx=10, pady=10)
entry_terminos = Entry(root)
entry_terminos.grid(row=1, column=1, padx=10, pady=10)

Label(root, text="Tipo de serie:").grid(row=2, column=0, padx=10, pady=10)
serie_var = StringVar(value="coseno")
opciones = ["coseno", "exp", "onda_cuadrada", "fibonacci_coseno"]
OptionMenu(root, serie_var, *opciones).grid(row=2, column=1, padx=10, pady=10)

btn_enviar = Button(root, text="Enviar Datos", command=insertar_valores)
btn_enviar.grid(row=3, column=0, columnspan=2, pady=20)

root.mainloop()