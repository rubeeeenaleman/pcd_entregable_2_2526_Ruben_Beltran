from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod
import statistics
import random
from typing import List, Tuple, Dict
import asyncio

# --- Excepciones ---

class SesionVaciaError(Exception):
    """Se lanza cuando se intenta generar recomendaciones sin historial."""

class AtributosInvalidosError(ValueError):
    """Se lanza cuando los atributos de una canción son inválidos."""

class CancionNoExisteError(Exception):
    """Se lanza cuando se intenta reproducir una canción que no está en el catálogo."""


    
    
class Cancion:
    '''
    Representa una canción del catálogo musical.
    '''
    
    def __init__(self, titulo: str, fecha_creacion: date, atributos_sonoros: dict, atributos_sentimentales: dict):
        self.titulo = titulo
        self.fecha = fecha_creacion
        self.atributos_sonoros = atributos_sonoros
        self.atributos_sentimentales = atributos_sentimentales
     
        if not isinstance(atributos_sonoros, dict) or not atributos_sonoros:
            raise AtributosInvalidosError(
                "atrb_sonoros debe ser un diccionario no vacío."
            )
        if not isinstance(atributos_sentimentales, dict) or not atributos_sentimentales:
            raise AtributosInvalidosError(
                "atrb_sentimentales debe ser un diccionario no vacío."
            )   
        
        
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
    def __init__(self, nombre: str, fecha_creacion: str, canciones: list):
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
        self.cantantes.append(cantante)
        
    def agregar_playlist(self, playlist: Playlist):
        self.playlists.append(playlist)


# Patrón Chain of Responsibility 

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
        """ 
        Función que extraiga las claves numéricas del diccionario de las canciones, agrupe los valores y calcule los estadísticos.
        """
        valores = {} # historial_sesion guarda tuplas (Cancion, datetime)

        # bucle para recorrer las canciones y extraer los atributos sonoros
        for cancion, _ in historial_sesion:
            for clave, valor in cancion.atributos_sonoros.items():
                if isinstance(valor, (int, float)): # comprueba que el valor que cogemos es un número 
                    if clave not in valores:  # comprobamos si la clave existe en el diccionario vacío creado, de no ser así lo que hace es guardarla junto con una lista que es donde se almacenarán los valores de esa clave.
                        valores[clave] = []
                    valores[clave].append(valor)
        
        # una vez que tenemos el diccionario valores con los estadísticos que nos interesan, calculamos
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
    """ Mismo funcionamiento que la función calcular estadísticos pero esta vez con atributos sentimentales.""" 
    def calcular_estadisticos(self, historial_sesion: list, estadisticos_actuales: dict):
        valores = {}

        for cancion, _ in historial_sesion:
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
    def buscar(self, catalogo: Catalogo, estadisticos: dict) -> dict:
        pass
    
    #implementamos en la clase padre para aprobechar la herencia
    def _hace_match(self, atributos_sonoros: dict, atributos_sentimentales: dict, estadisticos: dict) -> bool:
        '''esta función la voy a hacer porque es necesario para comprobar si los valores de los estadísticos de los atributos sonoros y sentimentales están dentro de un 
        rango que definiremos, para por así decir, que haga match el primer elemento que coincida con las características sonoras y sentimental3s de la sesión de escucha actual.'''
        margen = 35

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
             if self._hace_match(playlist.calcular_atributos(tipo = 'sonoro'), playlist.calcular_atributos(tipo = 'sentimentales'), estadisticos):
                primera_playlist = playlist
                break
        
        primer_cantante = None
        for cantante in cantantes_ordenados:
             if self._hace_match(cantante.calcular_atributos(tipo = 'sonoro'), cantante.calcular_atributos(tipo = 'sentimentales'), estadisticos):
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
            if self._hace_match(playlist.calcular_atributos(tipo = 'sonoro'), playlist.calcular_atributos(tipo = 'sentimentales'), estadisticos):
                primera_playlist = playlist
                break
        
        primer_cantante = None
        for cantante in cantantes_aleatorios:
            if self._hace_match(cantante.calcular_atributos(tipo = 'sonoro'), cantante.calcular_atributos(tipo = 'sentimentales'), estadisticos):
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
    def generar(self, catalogo: Catalogo, estadisticos: dict, estrategia: EstrategiaBusqueda) -> list:
        pass
    
class GeneradorCanciones(GeneradorRecomendacion):
    '''Establecemos la recomendación por defecto, recomendaciones de canciciones'''
    def generar(self, catalogo: Catalogo, estadisticos: dict, estrategia: EstrategiaBusqueda) -> list:
        recomendacion = estrategia.buscar(catalogo, estadisticos)
        # Extraemos solo la canción para la base
        return [{'cancion': recomendacion['cancion']}] if recomendacion and recomendacion.get('cancion') else [] # comporbamos que exista la estrategia nos devuelva algo, y que exista la canción

class DecoradorRecomendacion(GeneradorRecomendacion):
    def __init__(self, componente: GeneradorRecomendacion):
        self.componente = componente

    @abstractmethod
    def generar(self, catalogo: Catalogo, estadisticos: dict, estrategia: EstrategiaBusqueda) -> list:
        pass



class GeneradorArtistas(DecoradorRecomendacion):
    def generar(self, catalogo: Catalogo, estadisticos: dict, estrategia: EstrategiaBusqueda) -> list:
        # primero llamamos al método padre, y generamos la recomendación de canciones
        recomendaciones = self.componente.generar(catalogo, estadisticos, estrategia)
        
        # segundo vamos a la segunda capa, obteniendo aparte de las canciones los artistas, para ello usamos el patron strategy
        recomendacion_artista = estrategia.buscar(catalogo, estadisticos)

        if recomendacion_artista and recomendacion_artista.get('cantante'):
            recomendaciones.append({'cantante': recomendacion_artista['cantante']})
            
        return recomendaciones


class GeneradorPlaylists(DecoradorRecomendacion):
    def generar(self, catalogo: Catalogo, estadisticos: dict, estrategia: EstrategiaBusqueda) -> list:
        # primero llamamos al método padre, y generamos la recomendación de canciones
        recomendaciones = self.componente.generar(catalogo, estadisticos, estrategia)
        
        # segundo vamos a la segunda capa, obteniendo aparte de las canciones las playlist, para ello usamos el patron strategy 
        recomendacion_playlist = estrategia.buscar(catalogo, estadisticos)
        if recomendacion_playlist and recomendacion_playlist.get('playlist'):
            recomendaciones.append({'playlist': recomendacion_playlist['playlist']})
            
        return recomendaciones

class Recomendador:
    """Clase prinicpal de sistema, que se encargará de centralizar la sesión del usuario.
    
    
    Debemos de definir una sesión de escucha, para ello vamos a usar las últimas 10 canciones usadas por el usuario, lo que genera la necesidad de tener un límite de escuchapor sesión.
    
    """
    _unicaInstancia = None
    
    def __init__(self, catalogo: Catalogo):
        self.catalogo :Catalogo = catalogo
        
        self.estadisticos_sesion: Dict[str, dict] = {}
        self.historial_sesion: List[Tuple[Cancion, datetime]] = []
        self.limite_sesion = 10
        
        # blqoue de los resultados obtenidos por cada patron: 
        self.analizador_sesion: ManejadorEstadisticos = None    # Chain of Responsibility
        self._estrategia: EstrategiaBusqueda = None             # Strategy
        self._generador: GeneradorRecomendacion = None          # Decorator
        
    
    # como particularidad de ser un Singleton, debe de tener su porpio método obtener instancia    
    @classmethod # especificamos que este método es de la clase no de un objeto
    def obtener_instancia(cls, catalogo=None):
        """Método de clase estático para obtener la instancia única."""
        if not cls._unicaInstancia:
            # Si no existe, creamos la única instancia y la guardamos
            cls._unicaInstancia = cls(catalogo)
        return cls._unicaInstancia
    
    
    def reproducir_cancion(self, cancion: Cancion, fecha_hora: datetime):
        """
        Simula que el usuario escucha una canción. 
        Actualiza la sesión y lanza el cálculo de estadísticos.
        """
        print(f"Reproduciendo canción: {cancion.titulo} a las {fecha_hora.strftime('%H:%M:%S')}")
        self.__actualizar_sesion(cancion, fecha_hora)  # internamente actualizamos la sesion de escucha
    
    def __actualizar_sesion(self, cancion: Cancion, fechahora: datetime):
        """
        Reacciona cuando el usuario notifica una escucha.
        
        Como hemos mencionado que la manera de definir el hisotrial de escucha será amntener las últimas 10 canciones, debemos de seguir una estrucutra de fifo, es decir una cola, el primero en entrar es el primero en salir
        """
        
       # añadimos la tupla cancion,fechahora a nuestro historial
        self.historial_sesion.append((cancion, fechahora))
        
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
        if not self.estadisticos_sesion:
            raise SesionVaciaError("La sesión está vacía. Escucha al menos una canción primero.")
        return self._generador.generar(self.catalogo, self.estadisticos_sesion, self._estrategia)
    
    # para una mayor felxibilidad debemos de tener configuración en tiempo de ejecución
    def set_estrategia(self, estrategia: EstrategiaBusqueda) -> None:
        """Cambia la estrategia de búsqueda """
        self._estrategia = estrategia

    def activar_recomendacion_artistas(self) -> None:
        """Envuelve el generador actual con el Decorador de artistas """
        self._generador = GeneradorArtistas(self._generador)

    def activar_recomendacion_playlists(self) -> None:
        """Envuelve el generador actual con el Decorador de playlists """
        self._generador = GeneradorPlaylists(self._generador)

class Usuario:
    '''
    Clase que representa el usuario.
    Cada usuario posee exactamente una instancia de Recomendador (Singleton)
    '''
    def __init__(self, id: str, nombre: str, catalogo: Catalogo):
        self.id = id
        self.nombre = nombre
        self.catalogo = catalogo
        self._recomendador: Recomendador = Recomendador.obtener_instancia(catalogo)
    
    def reproducir_cancion(self, titulo_cancion: str):
        # Buscamos el objeto canción por título para pasárselo al recomendador
        cancion_obj = next((c for c in self.catalogo.canciones if c.titulo == titulo_cancion), None) # comporbamos si la canción coincide con el título buscado, con next solo nos quedamos con la primera aparición
        if cancion_obj:
            self._recomendador.reproducir_cancion(cancion_obj, datetime.now())
        else:
            raise CancionNoExisteError('Canción no encontrada en el catálogo.')

        
    def solicitar_recomendacion(self):
        """El usuario solicita recomendaciones basadas en su sesión actual."""
        return self._recomendador.generar_recomendacion()

    def cambiar_estrategia(self, estrategia: EstrategiaBusqueda):
        self._recomendador.set_estrategia(estrategia)

    def activar_artistas(self):
        self._recomendador.activar_recomendacion_artistas()

    def activar_playlists(self):
        self._recomendador.activar_recomendacion_playlists()


async def simular_escucha_concurrente(usuario: Usuario, canciones_a_escuchar: list): # creamos una subrutina asicrona
    """
    Simula de forma asíncrona al usuario escuchando varias canciones.
    """
    print("\n[INICIANDO SESIÓN DE ESCUCHA]")
    for titulo_cancion in canciones_a_escuchar:
        await asyncio.sleep(0.5)
        usuario.reproducir_cancion(titulo_cancion)
        
def imprimir_recomendaciones(recomendaciones):
    """Función auxiliar para imprimir las recomendaciones de forma limpia."""
    if not recomendaciones:
        print("  Ningún elemento cumplió con el margen establecido.")
        return
        
    for i, rec_dict in enumerate(recomendaciones):
        print(f"\n  Resultados de la capa {i+1}:")
        if rec_dict.get('cancion'): print(f"    Canción recomendada: {rec_dict['cancion'].titulo}")
        if rec_dict.get('cantante'): print(f"    Cantante recomendado: {rec_dict['cantante'].nombre}")
        if rec_dict.get('playlist'): print(f"    Playlist recomendada: {rec_dict['playlist'].nombre}")

async def main(): # comenzamos con el sistema musical
    try:
        # CREACIÓN DEL CATÁLOGO Y DATOS ALEATORIOS
        catalogo = Catalogo()
        
        # Generamos 50 canciones aleatorias para tener más variedad
        for i in range(1, 51):
            c = Cancion(
                titulo=f"Hit Musical {i:02d}", # Formato 01, 02 para que la búsqueda alfabética se vea mejor
                fecha_creacion=date.today() - timedelta(days=random.randint(1, 1000)),
                atributos_sonoros={"ritmo": random.uniform(10.0, 90.0), "tono": random.uniform(10.0, 90.0)},
                atributos_sentimentales={"felicidad": random.uniform(10.0, 90.0), "energia": random.uniform(10.0, 90.0)}
            )
            catalogo.agregar_cancion(c)

        # Generamos varios Cantantes y Playlists con varias canciones del catálogo 
        cantante1 = Cantante("Rosalía", "1992-09-25", catalogo.canciones[0:15])
        cantante2 = Cantante("C. Tangana", "1990-07-16", catalogo.canciones[15:30])
        cantante3 = Cantante("Dua Lipa", "1995-08-22", catalogo.canciones[30:50])
        catalogo.agregar_cantante(cantante1)
        catalogo.agregar_cantante(cantante2)
        catalogo.agregar_cantante(cantante3)

        # Hacemos lo mismo con las Playlists, incluso cruzando canciones de distintos cantantes
        playlist1 = Playlist("Top Hits Verano", "2026-06-01", catalogo.canciones[5:25])
        playlist2 = Playlist("Chill Out Domingo", "2025-11-15", catalogo.canciones[20:45])
        canciones_workout = catalogo.canciones[0:10] + catalogo.canciones[40:50]
        playlist3 = Playlist("Workout Extremo", "2026-01-10", canciones_workout)
        
        catalogo.agregar_playlist(playlist1)
        catalogo.agregar_playlist(playlist2)
        catalogo.agregar_playlist(playlist3)

        # CREACIÓN DEL USUARIO 
        usuario = Usuario(id="U_001", nombre="Rubén", catalogo=catalogo)
        
        # iniciamos los patrones
        recomendador = usuario._recomendador
        
        # Chain of Responsibility
        manejador_sonoro = ManejadorSonoros()
        manejador_sentimental = ManejadorSentimentales()
        manejador_sonoro.establecer_siguiente(manejador_sentimental)
        recomendador.analizador_sesion = manejador_sonoro
        
        # Decorator (Base)
        recomendador._generador = GeneradorCanciones()
        
        # Estrategia Inicial
        usuario.cambiar_estrategia(BusquedaAleatoria())
        
        # Añadimos Decoradores usando métodos de Usuario
        print("Añadiendo preferencias del usuario: Artistas y Playlists...")
        usuario.activar_artistas()
        usuario.activar_playlists()

        # SIMULACIÓN ASÍNCRONA DE REPRODUCCIÓN
        canciones_random = random.sample(catalogo.canciones, 8)
        titulos_random = [c.titulo for c in canciones_random]
        await simular_escucha_concurrente(usuario, titulos_random)
        
        print("\n[ESTADÍSTICOS CALCULADOS]")
        for tipo, datos in recomendador.estadisticos_sesion.items():
            print(f"  {tipo.upper()}:")
            for metrica, valores in datos.items():
                print(f"    - {metrica}: Media {valores['media']:.2f} | Desviación {valores['dev_tipica']:.2f}")

        # SOLICITUD DE RECOMENDACIONES: ESTRATEGIA ALEATORIA
        print("\n[OBTENIENDO RECOMENDACIONES - ESTRATEGIA ALEATORIA]")
        recomendaciones = usuario.solicitar_recomendacion()
        imprimir_recomendaciones(recomendaciones)

        # PRUEBA DE CAMBIO DE ESTRATEGIA: ALFABÉTICA
        print("\n[CAMBIANDO ESTRATEGIA: Búsqueda Alfabética...]")
        usuario.cambiar_estrategia(BusquedaAlfabetica())
        recomendaciones_alf = usuario.solicitar_recomendacion()
        imprimir_recomendaciones(recomendaciones_alf)

        # PRUEBA DE CAMBIO DE ESTRATEGIA: TEMPORAL
        print("\n[CAMBIANDO ESTRATEGIA: Búsqueda Temporal...]")
        usuario.cambiar_estrategia(BusquedaTemporal())
        recomendaciones_temp = usuario.solicitar_recomendacion()
        imprimir_recomendaciones(recomendaciones_temp)

        # PRUEBA DE MANEJO DE ERRORES ESPERADOS
        print("\n[PRUEBA DE ERROR: Intentando reproducir canción inexistente]")
        try:
            usuario.reproducir_cancion("Canción Fantasma 3000")
        except Exception as error_esperado:
            print(f"  -> ¡Excepción capturada correctamente!: {type(error_esperado).__name__} - {error_esperado}")

    except Exception as e:
        print(f"\n[ERROR DURANTE LA EJECUCIÓN DEL SISTEMA]: {e}")

if __name__ == "__main__":
    asyncio.run(main())