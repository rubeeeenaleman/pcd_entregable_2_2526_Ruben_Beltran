from datetime import date
from abc import ABC, abstractmethod
from datetime import datetime


class Cancion:
    def __init__(self, titulo : str, fecha_creacion : date, atributos_sonoros : dict, atributos_sentimentales : dict):
        self.titulo = titulo
        self.fecha = fecha_creacion
        self.atributos_sonoros = atributos_sonoros
        self.atributos_sentimentales = atributos_sentimentales

class Cantante:
    def __init__(self, nombre : str, fecha_nacimiento : str, canciones : list):
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento

    def calcular_atrb_sonoros():
        pass
    
    def calcular_atrb_sentimentales():
        pass

class Playlist:
    def __init__(self, nombre : str, fecha_creacion : str, canciones : list):
        self.nombre = nombre
        self.fecha_creacion = fecha_creacion
    
    def calcular_atrb_sonoros():
        pass
    
    def calcular_atrb_sentimentales():
        pass

class Catalogo:
    """Almacena todas las canciones, cantantes y playlists del sistema."""
    def __init__(self):
        self.canciones: list[Cancion] = []
        self.cantantes: list[Cantante] = []
        self.playlists: list[Playlist] = []


    
class ObservadorUsuario(ABC):
    '''
    Definimos al subscriptor, cualquier clase que quiera observar al Publicador, deberá de tener implementado este método.
    
    Como el publicador es el Usuario, los subcriptores lo que harán serán actualizar la sesion, cuando el sujeto observador, publique que ha escuchado una canción.
    
    NOTA: PREGUNTARLE AL PRFOESOR SI EN ESTE CASO ESTAMOS NUEVAMENTE DANDO MUCHA IMPORTANCIÁ AL USUARIO, IMPORTANCIA QUE DEBERIAMOS DE DARSELA AL SISTEMA MUSCIAL
    '''
    @abstractmethod
    def actualizar_sesion(self, id_cancion: str, fechahora: datetime):
        pass    


class Usuario:
    '''
    Clase que representa el usuario (tambíen es el sujeto observado)
    '''
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.subscriptores: list[ObservadorUsuario] = []
        
    def alta(self, subscriptor: ObservadorUsuario):
        """Añade un nuevo observador a la lista."""
        if subscriptor not in self.subscriptores:
            self.subscriptores.append(subscriptor)

    def baja(self, subscriptor: ObservadorUsuario):
        """Elimina un observador de la lista."""
        if subscriptor in self.subscriptores:
            self.subscriptores.remove(subscriptor)

    def notificar_escucha(self, id_cancion: str, fechahora: datetime):
        """Avisa a todos los suscriptores de que se ha escuchado una canción."""
        for subscriptor in self.subscriptores:
            subscriptor.actualizar_sesion(id_cancion, fechahora)

    def escuchar_cancion(self, id_cancion: str, fechahora: datetime):
        """Simula la acción real de reproducir música."""
        print(f"[{fechahora.strftime('%H:%M:%S')}] {self.nombre} está escuchando la canción ID: {id_cancion}")
        
        # en el momento que un usuario reaiza la escucha de una canción, el patrón observer manda una notificación a los subscriptores
        self.notificar_escucha(id_cancion, fechahora)
        
class Recomendador(ObservadorUsuario):
    """Clase prinicpal de sistema, que se encargará de centralizar la sesión del usuario.
    
    Tambíen actua como suscriptor del observer, siendo notificado cuando el cliente o usuario realiza la acción de escuchar una canción.
    
    Debemos de definir una sesión de escucha, para ello vamos a usar las últimas 10 canciones usadas por el usuario, lo que genera la necesidad de tener un límite de escuchapor sesión.
    
    """
    _unicaInstancia = None
    
    def __init__(self):
        self.catalogo = Catalogo()
        

        self.historial_sesion = []
        self.limite_sesion = 10
        
        # blqoue de los resultados obtenidos por cada patron: 
        self.cadena_estadisticos = None      # Chain of Responsibility
        self.estrategia = None               # Strategy
        self.generador_recomendacion = None  # Decorator
        
    
    # como particularidad de ser un Singleton, debe de tener su porpio método obtener instancia    
    @classmethod # especificamos que este método es de la clase no de un objeto
    def obtener_instancia(cls):
        """Método de clase estático para obtener la instancia única."""
        if not cls._unicaInstancia:
            # Si no existe, creamos la única instancia y la guardamos
            cls._unicaInstancia = cls()
        return cls._unicaInstancia
    
    
    # por el método observer
    def actualizar_sesion(self, id_cancion: str, fechahora: datetime):
        """
        Reacciona cuando el usuario notifica una escucha.
        
        Como hemos mencionado que la manera de definir el hisotrial de escucha será amntener las últimas 10 canciones, debemos de seguir una estrucutra de fifo, es decir una cola, el primero en entrar es el primero en salir
        """
        
       # añadimos la tupla cancion,fechahora a nuestro historial
        self.historial_sesion.append((id_cancion, fechahora))
        
        
        # si la sesión fuera de 10 cacniones, la canción 11, sería introducida por la canción 1 (cola)
        if len(self.historial_sesion) > self.limite_sesion:
            self.historial_sesion.pop(0)
            