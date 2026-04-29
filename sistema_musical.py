from datetime import date


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

class Recomendador:
    """Clase prinicpal de sistema, que se encargará de centralizar la sesión del usuario.
    
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