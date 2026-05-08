from datetime import date
from abc import ABC, abstractmethod
from datetime import datetime
import statistics
import random
from datetime import datetime
from typing import List, Tuple, Dict

class Cancion:
    '''
    Representa una canción del catálogo musical.
    '''
    
    def __init__(self, titulo : str, fecha_creacion : date, atributos_sonoros : dict, atributos_sentimentales : dict):
        self.titulo = titulo
        self.fecha = fecha_creacion
        self.atributos_sonoros = atributos_sonoros
        self.atributos_sentimentales = atributos_sentimentales
        
class EntidadMusical(ABC):
    """
    Clase abstracta base para entidades que agrupan canciones (Cantante, Playlist).
    Los atributos sonoros y sentimentales se obtienen como la media de los atributos de sus canciones.
    """
    def __init__(self, canciones: list[Cancion]):
        # El padre guarda las canciones que le pasen sus hijos
        self.canciones: list[Cancion] = canciones
        
def calcular_atributos(self, tipo: str) :
    '''
    Para el cáclulo de los atributos debemos de suponer que cada una de las canciones comparten atributos.
    '''
    
    if not self.canciones:
        return {}
    # obtenemos cada uno de los diccionarios por cada canción
    lista_diccionarios = list(map(lambda c: c.atributos_sonoros if tipo == 'sonoro' else c.atributos_sentimentales, self.canciones))

    # realizamos la suma
    dict_suma = {}
    for diccionario in lista_diccionarios:
        for clave, valor in diccionario.items():
            if clave in dict_suma:
                dict_suma[clave] += valor
            else:
                dict_suma[clave] = valor
    
    # obtenemos las medias
    num_canciones = len(lista_diccionarios)
    dict_sol = {clave: (valor / num_canciones) for clave, valor in dict_suma.items()}
        
    return dict_sol
        
class Cantante(EntidadMusical):
    '''
    Artista musical con nombre y fecha de nacimiento.
    
    Al ser heredados de EntitdadMusical, ya tiene la fucnión de calcular atributo
    '''
    
    def __init__(self, nombre : str, fecha_nacimiento : str, canciones: list):
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        super().__init__(canciones) # pasando la lista de canciones al padre, ya podremos calcular los atributos tanto sonoros como sentimentales
    
class Playlist(EntidadMusical):
    '''
    Lista de reproducción con título y fecha de creación.
    
    Al ser heredados de EntitdadMusical, ya tiene la fucnión de calcular atributo
    '''
    def __init__(self, nombre : str, fecha_creacion : str, canciones):
        self.nombre = nombre
        self.fecha_creacion = fecha_creacion
        super().__init__(canciones)
        # pasando la lista de canciones al padre, ya podremos calcular los atributos tanto sonoros como sentimentales
        
class Catalogo:
    """Almacena todas las canciones, cantantes y playlists del sistema."""
    def __init__(self):
        self.canciones: list[Cancion] = []
        self.cantantes: list[Cantante] = []
        self.playlists: list[Playlist] = []
        
    def agregar_cancion(self, cancion: Cancion):
        self.canciones.append(cancion)
        
    def agregar_cantante(self, cantante: Cantante):
        self.cantante.append(cantante)
        
    def agregar_playlist(self, playlist: Playlist):
        self.playlist.append(playlist)

    
class ManejadorEstadisticos(ABC):
    """Clase abstracta base para los eslabones de la cadena"""
    def __init__(self):
        self.manejador_siguiente = None
    
    def establecer_siguiente(self, manejador):
        self.manejador_siguiente = manejador
        return manejador
    
    @abstractmethod
    def calcular_estadisticos(self, historial_sesion: list, estadisticos_actuales: dict):
        if self.manejador_siguiente is not None:
            return self.manejador_siguiente.calcular_estadisticos(historial_sesion, estadisticos_actuales)
        return estadisticos_actuales

class ManejadorSonoros(ManejadorEstadisticos):

    def calcular_estadisticos(self, historial_sesion: list, estadisticos_actuales: dict):
        """queremos crear una función que extraiga las claves numéricas del diccionario de las canciones, agrupe los valores y calcule los estadísticos."""
        valores = {} # diccionario donde agruparemos por clave el nombre del estadístico y valor una lista de los distitnos valores obtenidos

        # bucle para recorrer las canciones y extraer los atributos sonoros
        for cancion in historial_sesion:
            for clave, valor in cancion.atributos_sonoros.items():
                if isinstance(valor, (int, float)): # comprueba que el valor que cogemos es un número ya que los atributos que necesitamos para calcular estadísticos como la media o desviación típica deben de ser esencialmente números.
                    if clave not in valores:  # comprobamos si la clave existe en el diccionario vacío creado, de no ser así lo que hace es guardarla junto con una lista que es donde se almacenarán los valores de esa clave.
                        valores[clave] = []
                    valores[clave].append(valor)
        
        # una vez que tenemos el diccionario valores con los estadísticos que nos interesan realmente podemos pasar al cáclculo, nos ayudamos del módulo statistics
        estadisticos_sonoros = {} 
        for clave, lista_valores in valores.items():
            media = statistics.mean(lista_valores)
            desviacion_tipica = statistics.stdev(lista_valores) if len(lista_valores) > 1 else 0.0 # importante saber que para calcular la desviación es necesario al menos 2 valores, RECORDAMOS también que lista_valores es una lista.

            estadisticos_sonoros[clave] = {
                "media": media,
                "dev_tipica": desviacion_tipica
            }

        estadisticos_actuales['sonoros'] = estadisticos_sonoros
        
        return super().calcular_estadisticos(historial_sesion, estadisticos_actuales)
    
class ManejadorSentimentales(ManejadorEstadisticos):
    """Mismo funcionamiento que la función calcular estadísticos pero esta vez con atributos sentimentales."""
    def calcular_estadisticos(self, historial_sesion: list, estadisticos_actuales: dict):
        valores = {}

        for cancion in historial_sesion:
            for clave, valor in cancion.atributos_sentimentales.items():
                if isinstance(valor, (int, float)):
                    if clave not in valores:
                        valores[clave] = []
                    valores[clave].append(valor)

        estadisticos_sentimentales = {}
        for clave, lista_valores in valores.items():
                media = statistics.mean(lista_valores)
                desviacion_tipica = statistics.stdev(lista_valores) if len(lista_valores) > 1 else 0.0

                estadisticos_sentimentales[clave] = {
                    "media": media,
                    "dev_tipica": desviacion_tipica
                }
            
        estadisticos_actuales['sentimentales'] = estadisticos_sentimentales
            
        return super().calcular_estadisticos(historial_sesion, estadisticos_actuales)
        
#Patrón de estrategia de búsqueda:"""

class EstrategiaBusqueda(ABC):
    """Lo definimos como una clase abstracta donde las clases hijas que serán las distintas estrategias que vamos a implementar para que puedan usarse
    heredarán un método que será buscar, este método en la clase EstrategiaBusqueda no hace nada, sino que hay que implementarla en cada una de las clases hijas 
    según las necesidades."""

    @abstractmethod
    def buscar(self, catalogo, estadisticos: dict):
        pass
    
    #modificación, como esta función nos sirve para las tres estrategias de búsqueda distintas, mejor implementarla en la clase padre y que las hijas las hereden, asi ahorramos en líneas de código
    def _hace_match(self, atributos_sonoros: dict, atributos_sentimentales: dict, estadisticos: dict):
        '''esta función la voy a hacer porque es necesario para comprobar si los valores de los estadísticos de los atributos sonoros y sentimentales están dentro de un 
        rango que definiremos, para por así decir, que haga match el primer elemento que coincida con las características sonoras y sentimental3s de la sesión de escucha actual.'''
        margen = 15

        if 'sonoros' in estadisticos:
            for clave, calculos in estadisticos['sonoros'].items():
                if clave in atributos_sonoros:
                    valor_cancion = atributos_sonoros[clave]
                    media_sesion = calculos['media']

                    if not (media_sesion - margen <= valor_cancion <= media_sesion + margen):
                        return False

        if 'sentimentales' in estadisticos:
            for clave, calculos in estadisticos['sentimentales'].items():
                if clave in atributos_sentimentales:
                    valor_cancion = atributos_sentimentales[clave]
                    media_sesion = calculos['media']

                    if not (media_sesion - margen <= valor_cancion <= media_sesion + margen):
                        return False
        
        return True
    
    
#A continuación, tendremos las estrategias concretas, en este caso tenemos 3 tipos de búsquedas según dice el enunciado, estas son: alfabética, temporal y aleatoria.
class BusquedaAlfabetica(EstrategiaBusqueda):
    def buscar(self, catalogo : Catalogo, estadisticos: dict):
        """
        Ordena los ítems alfabéticamente por título/nombre 
        y devuelve el primero que coincida con la sesión.
        """
        
        # lo primero que vamos a hacer es ordenar las canciones, los cantantes y las playlists
        canciones_ordenadas = sorted(catalogo.canciones, key=lambda c: c.titulo.lower())
        cantantes_ordenados = sorted(catalogo.cantantes, key=lambda c: c.nombre.lower())
        playlist_ordenadas = sorted(catalogo.playlists, key=lambda p: p.nombre.lower())

        # con la función auxiliar creada, buscamos el primer match para canciones
        primera_cancion = None
        for cancion in canciones_ordenadas:
            if self._hace_match(cancion.atributos_sonoros, cancion.atributos_sentimentales, estadisticos):
                primera_cancion = cancion
                break
        
        # ahora se hace lo mismo para la playlist y para el cantante (DOY POR ECHO QUE VAN A TENER UNOS MÉTODOS QUE DIGAN SUS ATRIBUTOS SENTIMENTALES Y SONOROS.)
        primera_playlist = None
        for playlist in playlist_ordenadas:
             if self._hace_match(playlist.calcular_atributos(tipo = 'sonoro'), playlist.calcular_atributos(tipo = 'sentimentales'), estadisticos):
                primera_playlist = playlist
                break
        
        primer_cantante = None
        for cantante in cantantes_ordenados:
             if self._hace_match(cantante.calcular_atributos(tipo = 'sonoro'), cantante.calcular_atributos(tipo = 'sentimentales'), estadisticos):
                primer_cantante = cantante
                break
        
        # Devolvemos un diccionario con los resultados encontrados
        return {
            "cancion": primera_cancion,
            "playlist": primera_playlist,
            "cantante": primer_cantante
        }
        
class BusquedaTemporal(EstrategiaBusqueda): # esta estrategia de búsqueda es igual que la alfabética, lo único que nos cambia es la forma en la que ordenamos los datos.
    def buscar(self, catalogo, estadisticos: dict):
        # tenemos que ir del más nuevo al más antiguo!!, para ello hay que poner en el método sorted(): reverse = True
        canciones_ordenadas = sorted(catalogo.canciones, key=lambda c: c.fecha, reverse=True)
        cantantes_ordenados = sorted(catalogo.cantantes, key=lambda c: c.fecha_nacimiento, reverse=True)
        playlist_ordenadas = sorted(catalogo.playlists, key=lambda p: p.fecha_creacion, reverse=True)

        primera_cancion = None
        for cancion in canciones_ordenadas:
            if self._hace_match(cancion.atributos_sonoros, cancion.atributos_sentimentales, estadisticos):
                primera_cancion = cancion
                break
        
        primera_playlist = None
        for playlist in playlist_ordenadas:
             if self._hace_match(playlist.atributos_sonoros, playlist.atributos_sentimentales, estadisticos):
                primera_playlist = playlist
                break
        
        primer_cantante = None
        for cantante in cantantes_ordenados:
             if self._hace_match(cantante.atributos_sonoros, cantante.atributos_sentimentales, estadisticos):
                primer_cantante = cantante
                break
        
        return {
            "cancion": primera_cancion,
            "playlist": primera_playlist,
            "cantante": primer_cantante
        }


class BusquedaAleatoria(EstrategiaBusqueda):
    def buscar(self, catalogo, estadisticos: dict):
        canciones_aleatorias = list(catalogo.canciones)
        random.shuffle(canciones_aleatorias)

        cantantes_aleatorios = list(catalogo.cantantes)
        random.shuffle(cantantes_aleatorios)

        playlists_aleatorias = list(catalogo.playlists)
        random.shuffle(playlists_aleatorias)

        primera_cancion = None
        for cancion in canciones_aleatorias:
            if self._hace_match(cancion.atributos_sonoros, cancion.atributos_sentimentales, estadisticos):
                primera_cancion = cancion
                break
        
        primera_playlist = None
        for playlist in playlists_aleatorias:
            if self._hace_match(playlist.atributos_sonoros, playlist.atributos_sentimentales, estadisticos):
                primera_playlist = playlist
                break
        
        primer_cantante = None
        for cantante in cantantes_aleatorios:
            if self._hace_match(cantante.atributos_sonoros, cantante.atributos_sentimentales, estadisticos):
                primer_cantante = cantante
                break

        return {
            "cancion": primera_cancion,
            "playlist": primera_playlist,
            "cantante": primer_cantante
        }
    
    
class GeneradorRecomendacion(ABC):
    """
    Clase base del patrón Decorator.
    Actua como la interfaz para todos los generadores
    """
    @abstractmethod
    def generar(self, catalogo: Catalogo, estadisticos: dict, estrategia) -> list:
        pass
    
class GeneradorCanciones(GeneradorRecomendacion):
    '''Establecemos la recomendación por defecto, recoemndaciones de canciciones'''
    def generar(self, catalogo, estadisticos: dict, estrategia) :
        # usamos la estrategia
        recomendacion = estrategia.buscar(self.catalogo, estadisticos, 'canciones')
        
        return [recomendacion] if recomendacion else []

class DecoradorRecomendacion(GeneradorRecomendacion):
    # decorador para definir las otras subclases para generar recomendaciones
    def __init__(self, componente: GeneradorRecomendacion):
        super().__init__(componente.catalogo)
        self.componente = componente

    @abstractmethod
    def generar(self, catalogo, estadisticos: dict, estrategia):
        pass


class GeneradorArtistas(DecoradorRecomendacion):
    def generar(self, catalogo, estadisticos: dict, estrategia) -> list:
        # primero llamamos al método padre, y generamos la recomendación de canciones
        recomendaciones = self.componente.generar(catalogo, estadisticos, estrategia)
        
        # segundo vamos a la segunda capa, obteniendo aparte de las canciones los artistas, para ello usamos el patron strategy
        recomendacion_artista = estrategia.buscar(self.catalogo, estadisticos, 'cantante')

        if recomendacion_artista:
            recomendaciones.append(recomendacion_artista)
            
        return recomendaciones


class GeneradorPlaylists(DecoradorRecomendacion):
    def generar(self, catalogo, estadisticos: dict, estrategia) -> list:
        # primero llamamos al método padre, y generamos la recomendación de canciones
        recomendaciones = self.componente.generar(estadisticos, estrategia)
        
        # segundo vamos a la segunda capa, obteniendo aparte de las canciones las playlist, para ello usamos el patron strategy 
        recomendacion_playlist = estrategia.buscar(self.catalogo, estadisticos, 'playlist')
        if recomendacion_playlist:
            recomendaciones.append(recomendacion_playlist)
            
        return recomendaciones

class Recomendador:
    """Clase prinicpal de sistema, que se encargará de centralizar la sesión del usuario.
    
    
    Debemos de definir una sesión de escucha, para ello vamos a usar las últimas 10 canciones usadas por el usuario, lo que genera la necesidad de tener un límite de escuchapor sesión.
    
    """
    _unicaInstancia = None
    
    def __init__(self, catalogo) :
        self.catalogo :Catalogo = catalogo
        
        self.estadisticos_sesion : Dict[str, float] = {}
        self.historial_sesion : List[Tuple[str, datetime]] = []
        self.limite_sesion = 10
        
        # blqoue de los resultados obtenidos por cada patron: 
        self.analizador_sesion = None      # Chain of Responsibility
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
    
    
    def reproducir_cancion(self, id_cancion: str, fecha_hora: datetime):
        """
        Simula que el usuario escucha una canción. 
        Actualiza la sesión y lanza el cálculo de estadísticos.
        """
        print(f"Reproduciendo canción ID: {id_cancion} a las {fecha_hora}")
        self.__actualizar_sesion(id_cancion, fecha_hora) # internamente actualizamos la sesion de escucha
    
    def __actualizar_sesion(self, id_cancion: str, fechahora: datetime):
        """
        Reacciona cuando el usuario notifica una escucha.
        
        Como hemos mencionado que la manera de definir el hisotrial de escucha será amntener las últimas 10 canciones, debemos de seguir una estrucutra de fifo, es decir una cola, el primero en entrar es el primero en salir
        """
        
       # añadimos la tupla cancion,fechahora a nuestro historial
        self.historial_sesion.append((id_cancion, fechahora))
        
        
        # si la sesión fuera de 10 cacniones, la canción 11, sería introducida por la canción 1 (cola)
        if len(self.historial_sesion) > self.limite_sesion:
            self.historial_sesion.pop(0)
            
        # Si el analizador está configurado, calculamos los estadísticos
        if self.analizador_sesion:
            self.analizador_sesion.calcular_estadisticos(self.historial_sesion, self.estadisticos_sesion)
            
            
    def generar_recomendacion(self):
        """
        Delega la generación de la recomendación al Decorator usando el Strategy.
        """
        if not self._estadisticos_sesion:
            raise SesionVaciaError(
                "La sesión está vacía. Escucha al menos una canción primero."
            )
        return self.generador_recomendaciones.generar(self.estadisticos_sesion, self.estrategia)
    
    # para una mayor felxibilidad debemos de tener configuración en tiempo de ejecución
    def set_estrategia(self, estrategia: EstrategiaBusqueda) -> None:
        """Cambia la estrategia de búsqueda ."""
        self._estrategia = estrategia

    def activar_recomendacion_artistas(self) -> None:
        """Envuelve el generador actual con el Decorador de artistas ."""
        self._generador = GeneradorArtistas(self._generador)

    def activar_recomendacion_playlists(self) -> None:
        """Envuelve el generador actual con el Decorador de playlists (R3)."""
        self._generador = GeneradorPlaylists(self._generador)

class Usuario:
    '''
    Clase que representa el usuario (tambíen es el sujeto observado)
    '''
    def __init__(self, id, str, nombre: str, recomendador : Recomendador):
        self.id = id
        self.nombre = nombre
    
    def reproducir_cancion(self):
        '''
        LLamamos al recomendador
        '''
        pass
    
    def solicitar_recomendacion(self):
        '''
        LLamamos al recomendadior
        '''
        pass
        

    