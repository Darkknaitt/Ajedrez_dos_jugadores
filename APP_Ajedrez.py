from tkinter import Tk, Canvas, Label, Button
from PIL import Image, ImageTk
import socket
import pickle
import threading


class TableroAjedrez:

    def __init__(self, ventanita):
        # -------------------------------------------------
        self.ventana2 = ventanita
        self.ventana2.resizable(width=False, height=False)
        self.ventana2.title("Menu de inicio")
        self.ventana2.geometry("640x640")
        self.ventana2.iconbitmap("Imagenes/icono.ico")

        # Crear un Canvas para colocar la imagen de fondo
        self.canvas = Canvas(self.ventana2, width=640, height=640)
        self.canvas.pack()

        # Cargar la imagen de fondo y redimensionarla al tamaño del canvas
        imagen_original = Image.open("Imagenes/Fondo.jpg")
        imagen_redimensionada = imagen_original.resize((640, 640))
        self.imagen_fondo_tk = ImageTk.PhotoImage(imagen_redimensionada)

        # Establecer la imagen de fondo en el canvas
        self.canvas.create_image(0, 0, image=self.imagen_fondo_tk, anchor='nw')

        self.etiqueta2 = Label(self.canvas, text="\tProyecto Programacion - Maestria en T.A. UPIITA\t",
                               font=("Arial", 20))
        self.etiqueta2.pack(pady=50)

        self.etiqueta = Label(self.canvas, text="\tDe clic a iniciar y se le\t \n \temparejará una partida al azar \t",
                              font=("Arial", 13))
        self.etiqueta.pack(pady=50)

        self.boton_facil = Button(self.canvas, text="Iniciar juego",
                                  command=lambda: self.abrir_tablero_ajedrez('Iniciar'),
                                  width=20, height=3, font=("Arial", 14))
        self.boton_facil.pack(pady=100)

        self.label_programador = Label(self.canvas, text="Programado por Abraham Pablo", width=50, height=3,
                                       font=("Arial", 8))
        self.label_programador.pack(pady=10)
        self.dificultad = 'None'
        self.SERVER_IP = 'localhost'
        self.SERVER_PORT = 12345
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.SERVER_IP, self.SERVER_PORT))
        self.coordenadas = []  # Lugar donde se guardan las coordenadas de los clics
        self.conteo = 0  # Conteo de clics para dar inicio a eventos
        self.turno_blancas = True  # Variable para conocer de quien es turno
        self.Elimina_Enroque_Blanco = False
        self.Elimina_Enroque_Negro = False
        self.Eliminar_Enroque_Largo_Blancas = True
        self.Eliminar_Enroque_Largo_Negras = True
        self.Posicion_Pieza_Negra_Al_Paso = [(0, 0)]
        self.Posicion_Pieza_Blanca_Al_Paso = [(0, 0)]
        self.Al_paso_Para_Blancas = False  # Variable para guardar las coordenadas de un peon que se movio dos casillas
        self.Al_paso_Para_Negras = False  # Variable para guardar las coordenadas de un peon que se movio dos casillas
        self.Validacion = False
        self.circulos = []
        self.board = [['TN', 'CN', 'AN1', 'DN', 'RN', 'AN1', 'CN', 'TN'],
                      ['PN', 'PN', 'PN', 'PN', 'PN', 'PN', 'PN', 'PN'],
                      ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                      ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                      ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                      ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                      ['PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PB'],
                      ['TB', 'CB', 'AB1', 'DB', 'RB', 'AB1', 'CB', 'TB']]
        self.Amenazas_Blancas2 = \
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]
        self.Amenazas_Negras2 = \
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]

        self.tablero_ficticio = self.board

        # Columnas de arriba hacia abajo, segun el orden son:
        # [0][i] los elementos en la fila superior (piezas negras)
        # [7][j] los elementos de la primera fila con piezas blancas

        self.rectangulos = []  # Lista para almacenar las referencias a los rectángulos creados
        self.Pieza_Seleccionada = {'P1': [], 'P2': []}  # Función para reconocer la pieza en todo momento
        self.validacion_baja = 0
        self.images = []  # Lista para almacenar las referencias a las imágenes
        self.Tablero_Existe = False
        self.Color_Socket = False
        self.hilo_respuestas = threading.Thread(target=self.recibir_respuestas)
        self.hilo_respuestas.start()
        self.Jaque = False

    def recibir_respuestas(self):
        validacion1 = 0
        self.validacion_baja = 0
        while True:
            # Recibir datos del cliente
            respuesta = self.client_socket.recv(4096)
            respuesta_deserializada = pickle.loads(respuesta)
            if not respuesta:
                break
            else:
                if respuesta_deserializada[-1] == 'Negras' or respuesta_deserializada[-1] == 'Blancas':
                    self.dificultad = respuesta_deserializada[0]
                    self.Tablero_Existe = False
                    self.Color_Socket = True
                    self.llega_de_socket = True
                else:
                    self.coordenadas.append(respuesta_deserializada[-2])
                    self.coordenadas.append(respuesta_deserializada[-1])
                    validacion1 = validacion1 + 1
                    if validacion1 == 1:
                        self.conteo = 2
                        self.validacion_baja = 1
                        self.ventana.after(0, self.comprobar_movimiento, 0)
                        validacion1 = 0

    def on_keypress(self, event):
        if event.keysym == "Escape":
            # Eliminar todos los rectángulos de la lista y del lienzo
            for rectangulo in self.rectangulos:
                self.User_Interface.delete(rectangulo)
            for circulo in self.circulos:
                self.User_Interface.delete(circulo)
            self.rectangulos = []  # Vaciar la lista de rectángulos
            self.conteo = 0
            self.coordenadas = []

    def dibujar_tablero(self):
        self.analisis_jaque()
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    color = 'white'
                else:
                    color = '#896B49'
                self.User_Interface.create_rectangle(j * 80, i * 80, (j + 1) * 80, (i + 1) * 80, fill=color)

        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece != '  ':
                    image = Image.open(f"Imagenes/{piece}.png")
                    image = image.resize((60, 60))
                    photo = ImageTk.PhotoImage(image)
                    self.User_Interface.create_image(j * 80 + 40, i * 80 + 40, image=photo)
                    self.images.append(photo)  # Agregar la referencia a la lista
        self.tablero_ficticio = self.board
    def clics(self, event):
        col, row = event.x // 80, event.y // 80
        self.coordenadas.append([row, col, self.board[row][col]])
        rectangulo = self.User_Interface.create_rectangle(col * 80, row * 80, (col + 1) * 80, (row + 1) * 80,
                                                          outline='red', width=3)
        self.Validacion = True
        self.Circulos()
        self.Validacion = False
        self.rectangulos.append(rectangulo)
        if len(self.rectangulos) == 3:
            # Eliminar el primer rectángulo de la lista y del tablero de juego
            self.User_Interface.delete(self.rectangulos.pop(0))
            self.comprobar_movimiento(self.coordenadas[-1])
            self.Validacion = False
        else:
            if (len(self.rectangulos) == 1 and self.board[row][col] != '  ') or (len(self.rectangulos) == 2):
                self.Validacion = False
                self.comprobar_movimiento(self.coordenadas[-1])


    def comprobar_movimiento(self, coordenada):
        self.conteo = self.conteo + 1
        if self.conteo == 2 or self.validacion_baja == 1:
            match self.coordenadas[-2][-1][0]:
                case 'P':
                    self.comprobacion_peon(0, 0, 0, 0)
                case 'T':
                    self.comprobacion_torre(0, 0, 0, 0)
                case 'R':
                    self.comprobacion_rey(0, 0, 0, 0)
                case 'A':
                    self.comprobacion_alfil(0, 0, 0, 0)
                case 'D':
                    self.comprobacion_dama(0, 0, 0, 0)
                case 'C':
                    self.comprobacion_caballo(0, 0, 0, 0)
                case _:
                    pass
        else:
            pass

    def comprobacion_caballo(self, fila1, columna1, fila2, columna2):
        if self.Validacion or self.Jaque:
            row1, col1 = fila1, columna1
            row2, col2 = fila2, columna2
        else:
            row1, col1 = self.coordenadas[-2][-3:-1]
            row2, col2 = self.coordenadas[-1][-3:-1]
        # MOVIMIENTO DE BLANCAS
        if (self.turno_blancas or self.Analisis_Jaque == 'Blancas') and \
                (self.dificultad == 'Blancas' or self.validacion_baja == 1 or self.Analisis_Jaque == 'Blancas'):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                pass
            # Si trata de mover hacia adelante una casilla
            elif ((abs(row1 - row2) == 2 and abs(col1 - col2) == 1) or
                  (abs(row1 - row2) == 1 and abs(col1 - col2) == 2)) and self.board[row2][col2][1] != 'B' \
                    and self.board[row1][col1][1] == 'B':
                self.mover_pieza(row1, col1, row2, col2)
            else:
                pass
        # MOVIMIENTO DE NEGRAS
        if (self.turno_blancas == False or self.Analisis_Jaque == 'Negras') and \
                (self.dificultad == 'Negras' or self.validacion_baja == 1 or self.Analisis_Jaque == 'Negras'):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                pass
            # Si trata de mover hacia adelante una casilla
            elif ((abs(row1 - row2) == 2 and abs(col1 - col2) == 1) or
                  (abs(row1 - row2) == 1 and abs(col1 - col2) == 2)) and self.board[row2][col2][1] != 'N' \
                    and self.board[row1][col1][1] == 'N':
                self.mover_pieza(row1, col1, row2, col2)
            else:
                pass

    def comprobacion_rey(self, fila1, columna1, fila2, columna2):
        if self.Validacion or self.Jaque:
            row1, col1 = fila1, columna1
            row2, col2 = fila2, columna2
        else:
            row1, col1 = self.coordenadas[-2][-3:-1]
            row2, col2 = self.coordenadas[-1][-3:-1]
        auxiliar = 0
        pieza1 = self.board[row1][col1]
        pieza2 = self.board[row2][col2]

        # MOVIMIENTO DEL REY BLANCOOOOO ---------------------------------------------
        if (self.turno_blancas or self.Analisis_Jaque == 'Blancas')and self.board[row1][col1] == 'RB' and (
                self.dificultad == 'Blancas' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                pass
            # Si trata de mover hacia al frente una casilla
            elif (abs(row2 - row1) <= 1 and abs(col2 - col1) <= 1) and self.board[row2][col2][1] != 'B':
                if self.Validacion == False and self.Jaque==False:
                    self.Elimina_Enroque_Blanco = True
                    self.mover_pieza(0, 0, 0, 0)
                else:
                    self.mover_pieza(row1, col1, row2, col2)
            # Enroque
            elif pieza1 == 'RB' and pieza2 == 'TB' and (
                    self.Elimina_Enroque_Blanco == False or self.Eliminar_Enroque_Largo_Blancas == False):
                if col2 > col1 and self.Elimina_Enroque_Blanco == False:
                    for i in range(abs(col2 - col1)):
                        if self.board[row1][col1 + i + 1][1] != '  ' and self.Elimina_Enroque_Blanco == False:
                            auxiliar += 1
                            if abs(col2 - col1) == auxiliar:
                                if self.Validacion == False and self.Jaque==False:
                                    self.Elimina_Enroque_Blanco = False
                                    self.mover_enroque(True)
                                else:
                                    self.mover_pieza(row1, col1, row2, col2)
                                break
                        else:
                            pass
                            break

                elif col2 < col1 and self.Eliminar_Enroque_Largo_Blancas == False:
                    for i in range(abs(col2 - col1)):
                        if self.board[row1][col1 - i - 1][1] != '  ':
                            auxiliar += 1
                            if abs(col2 - col1) == auxiliar:
                                if self.Validacion == False and self.Jaque == False:
                                    self.Eliminar_Enroque_Largo_Blancas = False
                                    self.mover_pieza(0, 0, 0, 0)
                                else:
                                    self.mover_pieza(row1, col1, row2, col2)
                                break
                        else:
                            break
            else:
                pass
        # MOVIMIENTO DEL REY NEGROOOO ---------------------------------------------
        elif (self.turno_blancas == False or self.Analisis_Jaque == 'Negras') and self.board[row1][col1][1] == 'N' and (
                self.dificultad == 'Negras' or self.validacion_baja == 1):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                pass
            # Si trata de mover hacia al frente una casilla
            elif (abs(row2 - row1) <= 1 and abs(col2 - col1) <= 1) and self.board[row2][col2][1] != 'N' \
                    and self.board[row1][col1][1] == 'N':
                if self.Validacion == False and self.Jaque==False:
                    self.Elimina_Enroque_Blanco = True
                    self.mover_pieza(0, 0, 0, 0)
                else:
                    self.mover_pieza(row1, col1, row2, col2)
            # Enroque
            elif pieza1 == 'RN' and pieza2 == 'TN' and (
                    self.Elimina_Enroque_Negro == False or self.Eliminar_Enroque_Largo_Negras == False):
                if col2 > col1 and self.Elimina_Enroque_Negro == False:
                    for i in range(abs(col2 - col1)):
                        if self.board[row1][col1 + i + 1][1] != '  ':
                            auxiliar += 1
                            if abs(col2 - col1) == auxiliar:
                                if self.Validacion == False and self.Jaque==False:
                                    self.Elimina_Enroque_Blanco = False
                                    self.mover_enroque(True)
                                else:
                                    self.mover_pieza(row1, col1, row2, col2)
                                break
                        else:
                            break
                elif col2 < col1 and self.Eliminar_Enroque_Largo_Negras == False:
                    for i in range(abs(col2 - col1)):
                        if self.board[row1][col1 - i - 1][1] != '  ':
                            auxiliar += 1
                            if abs(col2 - col1) == auxiliar:
                                if self.Validacion == False and self.Jaque==False:
                                    self.Elimina_Enroque_Negro = False
                                    self.mover_enroque(True)
                                else:
                                    self.mover_pieza(row1, col1, row2, col2)
                                    break
                        else:
                            break
            else:
                pass

    def comprobacion_torre(self, fila1, columna1, fila2, columna2):
        if self.Validacion == True or self.Jaque:
            row1, col1 = fila1, columna1
            row2, col2 = fila2, columna2
        else:
            row1, col1 = self.coordenadas[-2][-3:-1]
            row2, col2 = self.coordenadas[-1][-3:-1]
        Condicional = (abs(row2 - row1), abs(col2 - col1))
        auxiliar = 0  # Variable para hacer conteos en los bucles
        if ((self.turno_blancas or self.Analisis_Jaque == 'Blancas') and self.board[row1][col1][1] == 'B') and (
                self.dificultad == 'Blancas' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de moverse en la misma casila
            if (row1 == row2) and (col1 == col2):
                pass
            # Movimiento de torre sobre fila
            elif Condicional[0] == 0 and self.board[row2][col2][1] != 'B':
                # Movimiento de torre sobre fila al lado positivo
                if col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                # Movimiento de torre sobre fila al lado negativo
                else:
                    for i in range(abs(col2 - col1)):
                        if self.board[row1][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1:
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] == 'N'
                                                                 or self.board[row2][col2][1] != 'B'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
            # Movimiento de torre sobre columna ------------------------------------------
            elif Condicional[1] == 0 and self.board[row2][col2][1] != 'B':
                # Movimiento de torre sobre columna al lado positivo
                if row2 > row1:
                    for i in range(abs(row2 - row1)):
                        if self.board[row1 + 1 + i][col1] == '  ' or abs(row2 - row1) == i + 1:
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] == 'N'
                                                                 or self.board[row2][col2][1] != 'B'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                # Movimiento de torre sobre columna al lado negativo
                else:
                    for i in range(abs(row2 - row1)):
                        if self.board[row1 - 1 - i][col1] == '  ' or abs(row2 - row1) == i + 1:
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] == 'N'
                                                                 or self.board[row2][col2][1] != 'B'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
        # movimiento de negras de torre ------------------------
        elif (self.turno_blancas == False or self.Analisis_Jaque == 'Negras') and self.board[row1][col1][1] == 'N' and (
                self.dificultad == 'Negras' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de moverse en la misma casila
            if (row1 == row2) and (col1 == col2):
                pass
            # Movimiento de torre sobre fila
            elif Condicional[0] == 0 and self.board[row2][col2][1] != 'N':
                # Movimiento de torre sobre fila al lado positivo
                if col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if self.board[row1][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1:
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] == 'B'
                                                                 or self.board[row2][col2][1] != 'N'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                # Movimiento de torre sobre fila al lado negativo
                else:
                    for i in range(abs(col2 - col1)):
                        if self.board[row1][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1:
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] == 'B'
                                                                 or self.board[row2][col2][1] != 'N'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
            # Movimiento de torre sobre columna ------------------------------------------
            elif Condicional[1] == 0 and self.board[row2][col2][1] != 'N':
                # Movimiento de torre sobre columna al lado positivo
                if row2 > row1:
                    for i in range(abs(row2 - row1)):
                        if self.board[row1 + 1 + i][col1] == '  ' or abs(row2 - row1) == i + 1:
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] == 'B'
                                                                 or self.board[row2][col2][1] != 'N'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                # Movimiento de torre sobre columna al lado negativo
                else:
                    for i in range(abs(row2 - row1)):
                        if self.board[row1 - 1 - i][col1] == '  ' or abs(row2 - row1) == i + 1:
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] == 'B'
                                                                 or self.board[row2][col2][1] != 'N'):
                                self.Mover_Torre(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
        # SECCION DE MOVIMIENTOS

    def comprobacion_alfil(self, fila1, columna1, fila2, columna2):
        if self.Validacion or self.Jaque:
            row1, col1 = fila1, columna1
            row2, col2 = fila2, columna2
        else:
            row1, col1 = self.coordenadas[-2][-3:-1]
            row2, col2 = self.coordenadas[-1][-3:-1]
        auxiliar = 0
        if (self.turno_blancas or self.Analisis_Jaque == 'Blancas') and self.board[row1][col1][1] == 'B' and (
                self.dificultad == 'Blancas' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                pass
                # Si trata de mover hacia adelante una casilla
            elif (abs(row2 - row1) == abs(col2 - col1)):
                if row2 > row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 > row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                else:
                    pass
        elif (self.turno_blancas == False or self.Analisis_Jaque == 'Negras') and self.board[row1][col1][1] == 'N' and (
                self.dificultad == 'Negras' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                pass
                # Si trata de mover hacia adelante una casilla
            elif (abs(row2 - row1) == abs(col2 - col1)):
                if row2 > row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 > row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                else:
                    pass

    def comprobacion_peon(self, fila1, columna1, fila2, columna2):
        if self.Validacion == True or self.Jaque:
            row1, col1 = fila1, columna1
            row2, col2 = fila2, columna2
        else:
            row1, col1 = self.coordenadas[-2][-3:-1]
            row2, col2 = self.coordenadas[-1][-3:-1]
        if (self.turno_blancas or self.Analisis_Jaque == 'Blancas') and self.board[row1][col1][1] == 'B' and (
                self.dificultad == 'Blancas' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de mover en el mismo sitio
            pass
            if (row1 == row2) and (col1 == col2):
                self.conteo = 0
                pass
            # Si trata de mover hacia al frente una casilla
            elif (row1 - 1 == row2) and (col1 == col2) and self.board[row2][col2] == '  ':
                if self.Validacion or self.Jaque:
                    self.mover_pieza(row1, col1, row2, col2)
                else:
                    self.Al_paso_Para_Negras = False
                    self.mover_pieza(0, 0, 0, 0)
            # Captura de peon normal
            elif self.board[row2][col2][1] == 'N' and (row1 - 1 == row2) and (abs(col1 - col2) == 1):
                if self.Validacion or self.Jaque:
                    self.mover_pieza(row1, col1, row2, col2)
                else:
                    self.Al_paso_Para_Negras = False
                    self.mover_pieza(0, 0, 0, 0)
            # Mover dos casillas el peon y activa la posibilidad de comer al paso
            elif row1 == 6 and (self.board[row1 - 1][col1] == '  ') and (self.board[row2][col2] == '  '):
                # cambio en esta otra linea
                if (self.Validacion or self.Jaque) and abs(row2 - row1) == 2 and col2 == col1:
                    self.mover_pieza(row1, col1, row2, col2)
                # cambio en esta linea
                elif (self.Validacion == False or self.Jaque == False) and abs(row2 - row1) == 2 and col2 == col1:
                    self.Al_paso_Para_Negras = True
                    self.Posicion_Pieza_Blanca_Al_Paso = [(row2, col2)]
                    self.mover_pieza(0, 0, 0, 0)
            # Capturar al paso
            elif self.board[row2][col2] == '  ' and row1 - 1 == row2 and abs(
                    col2 - col1) == 1 and self.Al_paso_Para_Blancas == True \
                    and row1 == self.Posicion_Pieza_Negra_Al_Paso[0][0] and (
                    col2 == self.Posicion_Pieza_Negra_Al_Paso[0][1]):
                # AQUI ME QUEDE EN LOS CAMBIOSSSSSSS  1 -----------
                if self.Validacion or self.Jaque:
                    self.mover_pieza(row1, col1, row2, col2)
                else:
                    self.mover_peon_al_paso(row1, col2, self.Posicion_Pieza_Negra_Al_Paso[0][0],
                                            self.Posicion_Pieza_Negra_Al_Paso[0][1])
            else:
                pass
        # PEON NEGRO

        elif self.board[row1][col1] == 'PN' and (self.turno_blancas == False or self.Analisis_Jaque == 'Negras') and (
                self.dificultad == 'Negras' or self.validacion_baja or self.Jaque):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                self.conteo = 0
                pass
            # Si trata de mover hacia al frente una casilla
            elif (row1 + 1 == row2) and (col1 == col2) and self.board[row2][col2] == '  ':
                if self.Validacion or self.Jaque:
                    self.mover_pieza(row1, col1, row2, col2)
                else:
                    self.Al_paso_Para_Blancas = False
                    self.mover_pieza(0, 0, 0, 0)
            # Captura de peon normal
            elif self.board[row2][col2][1] == 'B' and (row1 + 1 == row2) and (abs(col1 - col2) == 1):
                if self.Validacion or self.Jaque:
                    self.mover_pieza(row1, col1, row2, col2)
                else:
                    self.Al_paso_Para_Blancas = False
                    self.mover_pieza(0, 0, 0, 0)
            # Mover dos casillas el peon y activa la posibilidad de comer al paso
            elif row1 == 1 and (self.board[row1 + 1][col1] == '  ') and (self.board[row2][col2] == '  '):
                if (self.Validacion or self.Jaque) and abs(row2 - row1) == 2 and col2 == col1:
                    self.mover_pieza(row1, col1, row2, col2)
                elif (self.Validacion == False or self.Jaque == False) and abs(row2 - row1) == 2 and col2 == col1:
                    self.Al_paso_Para_Blancas = True
                    self.Posicion_Pieza_Negra_Al_Paso = [(row2, col2)]
                    self.mover_pieza(0, 0, 0, 0)
            # Capturar al paso
            elif self.board[row2][col2] == '  ' and row1 + 1 == row2 and abs(
                    col2 - col1) == 1 and self.Al_paso_Para_Negras == True \
                    and row1 == self.Posicion_Pieza_Blanca_Al_Paso[0][0] and (
                    col2 == self.Posicion_Pieza_Blanca_Al_Paso[0][1]):
                if self.Validacion or self.Jaque:
                    self.mover_pieza(row1, col1, row2, col2)
                else:
                    self.mover_peon_al_paso(row1, col1, self.Posicion_Pieza_Blanca_Al_Paso[0][0],
                                            self.Posicion_Pieza_Blanca_Al_Paso[0][1])
            else:
                pass

    def comprobacion_dama(self, fila1, columna1, fila2, columna2):
        if self.Validacion == True or self.Jaque:
            row1, col1 = fila1, columna1
            row2, col2 = fila2, columna2
        else:
            row1, col1 = self.coordenadas[-2][-3:-1]
            row2, col2 = self.coordenadas[-1][-3:-1]
        auxiliar = 0
        if (self.turno_blancas or self.Analisis_Jaque == 'Blancas') and self.board[row1][col1][1] == 'B' and (
                self.dificultad == 'Blancas' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de mover en el mismo sitio
            pass
            if (row1 == row2) and (col1 == col2):
                pass
                # Si trata de mover hacia adelante una casilla
            elif (abs(row2 - row1) == abs(col2 - col1)) or ((row2 - row1) == 0) or (col1 - col2 == 0):
                if row2 > row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 > row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 == row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 == row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 < row1 and col2 == col1:
                    for i in range(abs(row2 - row1)):
                        if (self.board[row1 - i - 1][col1] == '  ' or abs(row2 - row1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 > row1 and col2 == col1:
                    for i in range(abs(row2 - row1)):
                        if (self.board[row1 + i + 1][col1] == '  ' or abs(row2 - row1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] != 'B'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                else:
                    pass



        # MOVIMIENTO DE LA DAMA NEGRA
        elif (self.turno_blancas == False or self.Analisis_Jaque == 'Negras') and self.board[row1][col1][1] == 'N' and (
                self.dificultad == 'Negras' or self.validacion_baja == 1 or self.Jaque):
            # Si trata de mover en el mismo sitio
            if (row1 == row2) and (col1 == col2):
                pass
                # Si trata de mover hacia adelante una casilla
            elif (abs(row2 - row1) == abs(col2 - col1)) or ((row2 - row1) == 0) or (col1 - col2 == 0):
                if row2 > row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 > row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 + 1 + i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                elif row2 < row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1 - 1 - i][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 == row1 and col2 > col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1][col1 + 1 + i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 == row1 and col2 < col1:
                    for i in range(abs(col2 - col1)):
                        if (self.board[row1][col1 - 1 - i] == '  ' or abs(col2 - col1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(col2 - col1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 < row1 and col2 == col1:
                    for i in range(abs(row2 - row1)):
                        if (self.board[row1 - i - 1][col1] == '  ' or abs(row2 - row1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break
                elif row2 > row1 and col2 == col1:
                    for i in range(abs(row2 - row1)):
                        if (self.board[row1 + i + 1][col1] == '  ' or abs(row2 - row1) == i + 1):
                            auxiliar = auxiliar + 1
                            if auxiliar == abs(row2 - row1) and (self.board[row2][col2][1] != 'N'):
                                self.mover_pieza(row1, col1, row2, col2)
                            else:
                                pass
                        else:
                            break

                else:
                    pass

        else:
            pass

    # SECCION DE MOVIMIENTOS DE PIEZAS
    def mover_pieza(self, valrow1, valcol1, valrow2, valcol2):
        self.tablero_ficticio = self.board
        if self.Validacion:
            self.dibujar_circulos(valrow1, valcol1, valrow2, valcol2)
        elif self.Jaque:
            if self.Analisis_Jaque == 'Negras':
                self.Amenazas_Negras[valrow2][valcol2] = self.Amenazas_Negras[valrow2][valcol2] + 1
                self.Amenazas_Negras2[valrow2][valcol2] = self.Amenazas_Negras2[valrow2][valcol2] + 1
            else:
                self.Amenazas_Blancas[valrow2][valcol2] = self.Amenazas_Blancas[valrow2][valcol2] + 1
                self.Amenazas_Blancas2[valrow2][valcol2] = self.Amenazas_Blancas2[valrow2][valcol2] + 1
        else:

            # AQUI DEBE ESTAR EL ERRORRRR
            self.tablero_ficticio[self.coordenadas[-1][-3]][self.coordenadas[-1][-2]] = self.coordenadas[-2][-1]
            self.tablero_ficticio[self.coordenadas[-2][-3]][self.coordenadas[-2][-2]] = '  '
            self.conteo = 0
            if self.sale_de_jaque(self.turno_blancas):
                if self.turno_blancas:
                    self.Al_paso_Para_Blancas = False
                else:
                    self.Al_paso_Para_Negras = False
                if self.validacion_baja == 1:
                    pass
                else:
                    lista_enviar = []
                    lista_enviar.append(self.coordenadas[-2])
                    lista_enviar.append(self.coordenadas[-1])

                    lista_serializada = pickle.dumps(lista_enviar)

                    # Enviar la lista serializada al servidor
                    self.client_socket.sendall(lista_serializada)

                self.tablero_ficticio = self.board
                self.turno_blancas = not self.turno_blancas
                self.Pieza_Seleccionada = []

                self.board[self.coordenadas[-1][-3]][self.coordenadas[-1][-2]] = self.coordenadas[-2][-1]
                self.board[self.coordenadas[-2][-3]][self.coordenadas[-2][-2]] = '  '
                self.conteo = 0
                # Se agrega condicional para eliminar enroque en caso de que se mueva la torre
                self.dibujar_tablero()
                self.validacion_baja = 0
                self.validacion1 = 0
            else:
                pass

    def mover_enroque(self, Enroque):
        row1 = self.coordenadas[-2][-3]
        col1 = self.coordenadas[-2][-2]
        row2 = self.coordenadas[-1][-3]
        col2 = self.coordenadas[-1][-2]
        if self.validacion_baja == 0 and self.Jaque==False and self.Validacion==False:
            lista_enviar = []
            lista_enviar.append(self.coordenadas[-2])
            lista_enviar.append(self.coordenadas[-1])
            lista_serializada = pickle.dumps(lista_enviar)
            # Enviar la lista serializada al servidor
            self.client_socket.sendall(lista_serializada)
        else:
            pass
        # enroque -------------------------------------------
        if (self.Elimina_Enroque_Blanco == False or self.Eliminar_Enroque_Largo_Blancas == False) and Enroque == True \
                and self.turno_blancas and self.Jaque == False:
            self.conteo = 0
            Se_Puede = self.sale_de_jaque(self.turno_blancas)
            if col2 < col1 and self.Elimina_Enroque_Blanco == False and Se_Puede == True:
                self.tablero_ficticio = self.board
                self.board[row1][col2 + 2] = self.board[row2][col2]
                self.board[row2][col2] = '  '
                self.board[row1][col2 - 1] = self.board[row1][col1]
                self.board[row1][col1] = '  '
                self.conteo = 0
                self.Elimina_Enroque_Blanco = True
                self.turno_blancas = False
                self.dibujar_tablero()
                self.validacion_baja = 0
                self.validacion1 = 0
            elif Se_Puede == True and col1< col2:
                self.tablero_ficticio = self.board
                self.board[row1][col2 - 2] = self.board[row2][col2]
                self.board[row2][col2] = '  '
                self.board[row1][col1 + 2] = self.board[row1][col1]
                self.board[row1][col1] = '  '
                self.conteo = 0
                self.Eliminar_Enroque_Largo_Blancas = True
                self.turno_blancas = False
                self.dibujar_tablero()
                self.validacion_baja = 0
                self.validacion1 = 0

        elif (
                self.Elimina_Enroque_Negro == False or self.Eliminar_Enroque_Largo_Negras == False) and Enroque == True and \
                self.turno_blancas == False and self.Jaque == False:
            self.conteo = 0
            Se_Puede = self.sale_de_jaque(self.turno_blancas)
            if col2 < col1 and self.Elimina_Enroque_Negro == False and Se_Puede == True:
                self.tablero_ficticio = self.board
                self.board[row1][col2 + 2] = self.board[row2][col2]
                self.board[row2][col2] = '  '
                self.board[row1][col2 - 1] = self.board[row1][col1]
                self.board[row1][col1] = '  '
                self.conteo = 0
                self.Elimina_Enroque_Negro = True
                self.turno_blancas = True
                self.dibujar_tablero()
                self.validacion_baja = 0
                self.validacion1 = 0
            elif Se_Puede == True and col2>col1:
                self.tablero_ficticio = self.board
                self.board[row1][col2 - 2] = self.board[row2][col2]
                self.board[row2][col2] = '  '
                self.board[row1][col1 + 2] = self.board[row1][col1]
                self.board[row1][col1] = '  '
                self.conteo = 0
                self.Eliminar_Enroque_Largo_Negras = True
                self.turno_blancas = True
                self.dibujar_tablero()
                self.validacion_baja = 0
                self.validacion1 = 0
        else:
            pass

    def Mover_Torre(self, valrow1, valcol1, valrow2, valcol2):
        if self.Validacion == True or self.Jaque == True:
            if self.Jaque == True:
                if self.Analisis_Jaque == 'Negras':
                    self.Amenazas_Negras[valrow2][valcol2] = self.Amenazas_Negras[valrow2][valcol2] + 1
                    self.Amenazas_Negras2[valrow2][valcol2] = self.Amenazas_Negras2[valrow2][valcol2] + 1
                else:
                    self.Amenazas_Blancas[valrow2][valcol2] = self.Amenazas_Blancas[valrow2][valcol2] + 1
                    self.Amenazas_Blancas2[valrow2][valcol2] = self.Amenazas_Blancas2[valrow2][valcol2] + 1

            elif self.Validacion:
                self.dibujar_circulos(valrow1, valcol1, valrow2, valcol2)
            else:
                pass
        else:
            self.conteo = 0
            if self.sale_de_jaque(self.turno_blancas):
                row1 = self.coordenadas[-2][-3]
                col1 = self.coordenadas[-2][-2]
                if self.validacion_baja == 0:
                    lista_enviar = []
                    lista_enviar.append(self.coordenadas[-2])
                    lista_enviar.append(self.coordenadas[-1])
                    lista_serializada = pickle.dumps(lista_enviar)
                    # Enviar la lista serializada al servidor
                    self.client_socket.sendall(lista_serializada)
                else:
                    pass
                if self.board[row1][col1] == 'TN':
                    if col1 == 7:
                        self.Eliminar_Enroque_Largo_Negras = True
                        self.mover_pieza(0, 0, 0, 0)
                    else:
                        self.Elimina_Enroque_Negro = True
                        self.mover_pieza(0, 0, 0, 0)
                elif self.board[row1][col1] == 'TB':
                    if col1 == 7:
                        self.Eliminar_Enroque_Largo_Blancas = True
                        self.mover_pieza(0, 0, 0, 0)
                    else:
                        self.Elimina_Enroque_Blanco = True
                        self.mover_pieza(0, 0, 0, 0)
            else:
                pass

    def mover_peon_al_paso(self, row1, col1, row2, col2):
        if self.Jaque == True:
            if self.Analisis_Jaque == 'Negras':
                self.Amenazas_Negras[row2][col2] = self.Amenazas_Negras[row2][col2] + 1
                self.Amenazas_Negras2[row2][col2] = self.Amenazas_Negras2[row2][col2] + 1
            else:
                self.Amenazas_Blancas[row2][col2] = self.Amenazas_Blancas[row2][col2] + 1
                self.Amenazas_Blancas2[row2][col2] = self.Amenazas_Blancas2[row2][col2] + 1
        elif (self.validacion_baja == 0) and (self.Al_paso_Para_Blancas or self.Al_paso_Para_Blancas):
            self.conteo = 0
            if self.sale_de_jaque(self.turno_blancas):
                lista_enviar = []
                lista_enviar.append(self.coordenadas[-2])
                lista_enviar.append(self.coordenadas[-1])

                lista_serializada = pickle.dumps(lista_enviar)

                # Enviar la lista serializada al servidor
                self.client_socket.sendall(lista_serializada)

                self.turno_blancas = not self.turno_blancas
                self.Pieza_Seleccionada = []
                self.board[self.coordenadas[-2][-3]][self.coordenadas[-2][-2]] = '  '
                self.board[self.coordenadas[-1][-3]][self.coordenadas[-1][-2]] = self.coordenadas[-2][-1]
                self.board[row2][col2] = '  '
                self.conteo = 0
                self.Al_paso_Para_Blancas = False
                self.Al_paso_Para_Negras = False
                self.validacion_baja = 0
                self.validacion1 = 0
                self.dibujar_tablero()
        elif self.validacion_baja == 1:
            self.conteo = 0
            if self.analisis_jaque():
                self.turno_blancas = not self.turno_blancas
                self.Pieza_Seleccionada = []
                self.board[self.coordenadas[-2][-3]][self.coordenadas[-2][-2]] = '  '
                self.board[self.coordenadas[-1][-3]][self.coordenadas[-1][-2]] = self.coordenadas[-2][-1]
                self.board[row2][col2] = '  '
                self.conteo = 0
                self.Al_paso_Para_Blancas = False
                self.Al_paso_Para_Negras = False
                self.dibujar_tablero()
                self.validacion_baja = 0
                self.validacion1 = 0

        elif self.Validacion and self.validacion_baja == 0:
            self.dibujar_circulos(row1, col1, self.coordenadas[-1][-3], self.coordenadas[-1][-2])

    def Circulos(self):
        row2, col2 = self.coordenadas[-1][-3:-1]
        for i in range(8):
            for j in range(8):
                match self.board[row2][col2][0]:
                    case 'P':
                        self.comprobacion_peon(row2, col2, i, j)
                    case 'T':
                        self.comprobacion_torre(row2, col2, i, j)
                    case 'R':
                        self.comprobacion_rey(row2, col2, i, j)
                    case 'A':
                        self.comprobacion_alfil(row2, col2, i, j)
                    case 'D':
                        self.comprobacion_dama(row2, col2, i, j)
                    case 'C':
                        self.comprobacion_caballo(row2, col2, i, j)
                    case _:
                        pass

    def dibujar_circulos(self, valrow1, valcol1, valrow2, valcol2):
        color = 'Blue'
        x1 = valcol2 * 80 + 10  # Coordenada x del punto superior izquierdo del círculo
        y1 = valrow2 * 80 + 10  # Coordenada y del punto superior izquierdo del círculo
        x2 = (valcol2 + 1) * 80 - 10  # Coordenada x del punto inferior derecho del círculo
        y2 = (valrow2 + 1) * 80 - 10  # Coordenada y del punto inferior derecho del círculo
        circulo = self.User_Interface.create_oval(x1, y1, x2, y2, fill='', outline=color, width=3)
        self.circulos.append(circulo)

    # -----------------------------------------------------------------------------------

    def abrir_tablero_ajedrez(self, mensaje_x):
        dificultad = list(mensaje_x)
        if self.Tablero_Existe == False and self.Color_Socket == False:
            lista_serializada = pickle.dumps(dificultad)
            # Enviar la lista serializada al servidor
            self.client_socket.sendall(lista_serializada)
        else:
            pass

        self.ventana2.destroy()
        ventanita = Tk()
        self.ventana = ventanita
        self.User_Interface = Canvas(ventanita, width=640, height=640)
        self.ventana.title("Ajedrez para dos jugadores")
        self.ventana.iconbitmap("C:/Users/jesus/PycharmProjects/pythonProject3/Imagenes/icono.ico")
        self.User_Interface.pack()
        ventanita.resizable(width=False, height=False)
        self.User_Interface.bind("<Button-1>", self.clics)  # Función para el clic
        ventanita.bind("<KeyPress>", self.on_keypress)  # Registrar el evento KeyPress
        self.User_Interface.bind("<Button-1>", self.clics)  # Función para el clic
        self.Tablero_Existe = True
        self.dibujar_tablero()  # Función que dibuja el tablero
        self.ventana.mainloop()

    def analisis_jaque(self):
        self.Jaque = True
        self.Amenazas_Blancas = \
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]
        self.Amenazas_Negras = \
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]

        self.Analisis_Jaque = 'Negras'
        for k in range(8):

            for l in range(8):
                row2, col2 = k, l
                for i in range(8):
                    for j in range(8):
                        match self.board[row2][col2]:
                            case 'PN':
                                self.comprobacion_peon(row2, col2, i, j)
                            case 'TN':
                                self.comprobacion_torre(row2, col2, i, j)
                            case 'RN':
                                self.comprobacion_rey(row2, col2, i, j)
                            case 'AN1':
                                self.comprobacion_alfil(row2, col2, i, j)
                            case 'DN':
                                self.comprobacion_dama(row2, col2, i, j)
                            case 'CN':
                                self.comprobacion_caballo(row2, col2, i, j)

        self.Analisis_Jaque = 'Blancas'

        for m in range(8):
            for n in range(8):
                row2, col2 = m, n
                for o in range(8):
                    for p in range(8):
                        match self.board[row2][col2]:
                            case 'PB':
                                self.comprobacion_peon(row2, col2, o, p)
                            case 'TB':
                                self.comprobacion_torre(row2, col2, o, p)
                            case 'RB':
                                self.comprobacion_rey(row2, col2, o, p)
                            case 'AB1':
                                self.comprobacion_alfil(row2, col2, o, p)
                            case 'DB':
                                self.comprobacion_dama(row2, col2, o, p)
                            case 'CB':
                                self.comprobacion_caballo(row2, col2, o, p)

        self.Jaque = False
        self.Analisis_Jaque = '  '
        self.tablero_ficticio = self.board

    def sale_de_jaque(self, color):
        # BUSCAR REY BLANCO EN EL TABLERO
        self.tablero_ficticio = self.board
        movimiento = True
        row_blanco = 0
        col_blanco = 0
        row_negro = 0
        col_negro = 0
        for i in range(8):
            for j in range(8):
                if self.tablero_ficticio[i][j] == 'RB':
                    row_blanco = i
                    col_blanco = j
                elif self.tablero_ficticio[i][j] == 'RN':
                    row_negro = i
                    col_negro = j
        # BUSCAR REY NEGRO EN EL TABLERO
        self.Jaque = True
        self.Amenazas_Blancas2 = \
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]
        self.Amenazas_Negras2 = \
            [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]

        self.Analisis_Jaque = 'Negras'
        for i in range(8):
            for j in range(8):
                match self.board[i][j]:
                    case 'PN':
                        self.comprobacion_peon(i, j, row_blanco, col_blanco)
                    case 'TN':
                        self.comprobacion_torre(i, j, row_blanco, col_blanco)
                    case 'RN':
                        self.comprobacion_rey(i, j, row_blanco, col_blanco)
                    case 'AN1':
                        self.comprobacion_alfil(i, j, row_blanco, col_blanco)
                    case 'DN':
                        self.comprobacion_dama(i, j, row_blanco, col_blanco)
                    case 'CN':
                        self.comprobacion_caballo(i, j, row_blanco, col_blanco)

        self.Analisis_Jaque = 'Blancas'

        for i in range(8):
            for j in range(8):
                match self.board[i][j]:
                    case 'PB':
                        self.comprobacion_peon(i, j, row_negro, col_negro)
                    case 'TB':
                        self.comprobacion_torre(i, j, row_negro, col_negro)
                    case 'RB':
                        self.comprobacion_rey(i, j, row_negro, col_negro)
                    case 'AB1':
                        self.comprobacion_alfil(i, j, row_negro, col_negro)
                    case 'DB':
                        self.comprobacion_dama(i, j, row_negro, col_negro)
                    case 'CB':
                        self.comprobacion_caballo(i, j, row_negro, col_negro)

        self.Jaque = False
        self.Analisis_Jaque = '  '
        if self.Amenazas_Negras2[row_blanco][col_blanco] > 0 and color:
            movimiento = False
        elif self.Amenazas_Blancas2[row_negro][col_negro] >0 and color == False:
            movimiento = False
        self.tablero_ficticio = self.board
        return movimiento

ventana = Tk()
Tablero = TableroAjedrez(ventana)
ventana.mainloop()
