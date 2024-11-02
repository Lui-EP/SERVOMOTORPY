import tkinter as tk
from tkinter import messagebox
import serial
import time
import threading
import mysql.connector

arduino_port = "COM3"
baud_rate = 9600
arduino = None

db_config = {
    'host': 'localhost',
    'database': 'programacionavanzada',
    'user': 'root',
    'password': 'pERSONAL04'
}

def conectar():
    global arduino
    try:
        arduino = serial.Serial(arduino_port, baud_rate)
        time.sleep(2)
        IbConection.config(text="Estado: Conectado", fg="green")
        messagebox.showinfo("Conexión", "Conexión establecida.")
        start_reading()
    except serial.SerialException:
        messagebox.showerror("Error", "No se pudo conectar al Arduino. Verifique el puerto.")

def desconectar():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        IbConection.config(text="Estado: Desconectado", fg="red")
        messagebox.showwarning("Conexión", "Conexión terminada.")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión activa.")

def enviar_limite():
    global arduino
    if arduino and arduino.is_open:
        try:
            limite = tbLimTemp.get()
            if limite.isdigit():
                arduino.write(f"{limite}\n".encode())
                messagebox.showinfo("Enviado", f"Límite de temperatura enviado: {limite}°C")
            else:
                messagebox.showerror("Error", "Ingrese un valor numérico para el límite")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el límite: {e}")
    else:
        messagebox.showwarning("Advertencia", "Conéctese al Arduino antes de enviar el límite.")

def read_from_arduino():
    global arduino
    while arduino and arduino.is_open:
        try:
            data = arduino.readline().decode().strip()
            if "Temperatura" in data:
                temp_value = data.split(":")[1].strip().split(" ")[0]
                IbTemp.config(text=f"Temperatura: {temp_value} °C")
                insertar_datos_en_bd(temp_value)
            time.sleep(1)
        except Exception as e:
            print(f"Error leyendo datos: {e}")
            break

def insertar_datos_en_bd(temperatura):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        insert_query = "INSERT INTO dattemp (temperatura) VALUES (%s)"
        cursor.execute(insert_query, (temperatura,))
        connection.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Error en la base de datos", f"Error al insertar datos: {err}")
    finally:
        cursor.close()
        connection.close()

def start_reading():
    threading.Thread(target=read_from_arduino, daemon=True).start()

root = tk.Tk()
root.title("Control de Arduino")

IbConection = tk.Label(root, text="Estado: Desconectado", fg="red")
IbConection.pack(pady=10)

IbTemp = tk.Label(root, text="Temperatura: --- °C")
IbTemp.pack(pady=10)

tbLimTemp = tk.Entry(root)
tbLimTemp.pack(pady=10)
tbLimTemp.insert(0, "Ingrese límite de temperatura")

btnConectar = tk.Button(root, text="Conectar", command=conectar)
btnConectar.pack(pady=5)

btnDesconectar = tk.Button(root, text="Desconectar", command=desconectar)
btnDesconectar.pack(pady=5)

btnEnviar = tk.Button(root, text="Enviar límite", command=enviar_limite)
btnEnviar.pack(pady=5)

root.mainloop()
