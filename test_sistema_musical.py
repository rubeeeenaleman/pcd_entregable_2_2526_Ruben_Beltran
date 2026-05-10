import pytest
from datetime import date, datetime, timedelta
from sistema_musical import (
    Cancion, Cantante, Playlist, Catalogo, Recomendador, Usuario,
    ManejadorSonoros, ManejadorSentimentales, 
    BusquedaAlfabetica, BusquedaTemporal, BusquedaAleatoria,
    GeneradorCanciones, GeneradorArtistas, GeneradorPlaylists,
    AtributosInvalidosError, CancionNoExisteError, SesionVaciaError
)

#DEFINIMOS DATOS DE PRUEBA QUE USAREMOS PARA CADA UNO DE LOS TESTS

@pytest.fixture
def canciones_prueba():
    c1 = Cancion("A Canción", date(2023, 1, 1), {"ritmo": 50.0}, {"energia": 60.0})
    c2 = Cancion("Z Canción", date(2024, 1, 1), {"ritmo": 50.0}, {"energia": 60.0})
    c3 = Cancion("B Canción", date(2022, 1, 1), {"ritmo": 10.0}, {"energia": 10.0})
    return [c1, c2, c3]
@pytest.fixture
def catalogo_lleno(canciones_prueba):
    # usamos una fucnión de rellenado de catálogo
    cat = Catalogo()
    for c in canciones_prueba:
        cat.agregar_cancion(c)
    
    cantante = Cantante("Artista Test", "1999-01-01", canciones_prueba[:2])
    cat.agregar_cantante(cantante)
    
    playlist = Playlist("Playlist Test", "2024-01-01", canciones_prueba[:2])
    cat.agregar_playlist(playlist)
    
    return cat

@pytest.fixture
def historial_mock(canciones_prueba):
    # Simulamos un historial con 2 canciones iguales para ver si calcula bien la media
    return [
        (canciones_prueba[0], datetime.now()),
        (canciones_prueba[1], datetime.now())
    ]


# TESTS UNITARIOS 

# --- ENTIDADES Y CATÁLOGO ---

def test_cancion():
    """Prueba principal de la clase Cancion: validación de atributos."""
    c = Cancion("Test", date.today(), {"ritmo": 20}, {"felicidad": 80})
    assert c.titulo == "Test"
    
    # Comprobamos que lanza el error esperado si los dicts están vacíos
    with pytest.raises(AtributosInvalidosError):
        Cancion("Error", date.today(), {}, {"felicidad": 80})

def test_cantante(canciones_prueba):
    """Prueba principal de Cantante (y EntidadMusical): cálculo de medias de atributos."""
    # c1 tiene ritmo 50, c2 tiene ritmo 50 -> La media debe ser 50
    cantante = Cantante("Paco", "1980-01-01", canciones_prueba[:2])
    atributos_calc = cantante.calcular_atributos('sonoro')
    assert atributos_calc['ritmo'] == 50.0

def test_playlist(canciones_prueba):
    """Prueba principal de Playlist: agrupa canciones y hereda calcular_atributos."""
    # c1 energía 60, c2 energía 60 -> La media debe ser 60
    playlist = Playlist("Mix", "2025-01-01", canciones_prueba[:2])
    atributos_calc = playlist.calcular_atributos('sentimentales')
    assert atributos_calc['energia'] == 60.0

def test_catalogo(canciones_prueba):
    """Prueba principal de Catalogo: inserción de elementos."""
    cat = Catalogo()
    cat.agregar_cancion(canciones_prueba[0])
    assert len(cat.canciones) == 1
    assert cat.canciones[0].titulo == "A Canción"
    
    
# --- CHAIN OF RESPONSIBILITY ---

def test_manejador_sonoros(historial_mock):
    """Prueba principal de ManejadorSonoros: cálculo de medias y desv. típica sonoras."""
    manejador = ManejadorSonoros()
    estadisticos = {}
    resultado = manejador.calcular_estadisticos(historial_mock, estadisticos)
    
    assert 'sonoros' in resultado
    assert resultado['sonoros']['ritmo']['media'] == 50.0

def test_manejador_sentimentales(historial_mock):
    """Prueba principal de ManejadorSentimentales"""
    manejador = ManejadorSentimentales()
    estadisticos = {}
    resultado = manejador.calcular_estadisticos(historial_mock, estadisticos)
    
    assert 'sentimentales' in resultado
    assert resultado['sentimentales']['energia']['media'] == 60.0



# --- STRATEGY ---

def test_busqueda_alfabetica(catalogo_lleno):
    """Prueba principal de BusquedaAlfabetica: ordena de la A a la Z."""
    busqueda = BusquedaAlfabetica()
    estadisticos = {
        'sonoros': {'ritmo': {'media': 50.0}},
        'sentimentales': {'energia': {'media': 60.0}}
    }
    # Entre "A Canción" y "Z Canción" que hacen match, debe devolver "A Canción" primero
    resultado = busqueda.buscar(catalogo_lleno, estadisticos)
    assert resultado['cancion'].titulo == "A Canción"

def test_busqueda_temporal(catalogo_lleno):
    """Prueba principal de BusquedaTemporal: ordena del más nuevo al más antiguo."""
    busqueda = BusquedaTemporal()
    estadisticos = {
        'sonoros': {'ritmo': {'media': 50.0}},
        'sentimentales': {'energia': {'media': 60.0}}
    }
    # Z Canción (2024) es más nueva que A Canción (2023)
    resultado = busqueda.buscar(catalogo_lleno, estadisticos)
    assert resultado['cancion'].titulo == "Z Canción"

def test_busqueda_aleatoria(catalogo_lleno):
    """Prueba principal de BusquedaAleatoria: devuelve un elemento válido aleatorio."""
    busqueda = BusquedaAleatoria()
    estadisticos = {
        'sonoros': {'ritmo': {'media': 50.0}},
        'sentimentales': {'energia': {'media': 60.0}}
    }
    resultado = busqueda.buscar(catalogo_lleno, estadisticos)
    # Solo comprobamos que devuelve algo que no sea None si hay match
    assert resultado['cancion'] is not None

# --- DECORATOR ---

def test_generador_canciones(catalogo_lleno):
    """Prueba principal Generador base: devuelve solo la canción."""
    gen = GeneradorCanciones()
    estrategia = BusquedaAlfabetica()
    estadisticos = {'sonoros': {'ritmo': {'media': 50.0}}}
    
    resultado = gen.generar(catalogo_lleno, estadisticos, estrategia)
    assert len(resultado) == 1
    assert 'cancion' in resultado[0]

def test_generador_artistas(catalogo_lleno):
    """Prueba principal Decorador Artista: envuelve al generador base y suma el artista."""
    gen_base = GeneradorCanciones()
    gen_artista = GeneradorArtistas(gen_base)
    estrategia = BusquedaAlfabetica()
    estadisticos = {'sonoros': {'ritmo': {'media': 50.0}}}
    
    resultado = gen_artista.generar(catalogo_lleno, estadisticos, estrategia)
    assert len(resultado) == 2
    assert 'cancion' in resultado[0]
    assert 'cantante' in resultado[1]

def test_generador_playlists(catalogo_lleno):
    """Prueba principal Decorador Playlist: envuelve al generador base y suma la playlist."""
    gen_base = GeneradorCanciones()
    gen_playlist = GeneradorPlaylists(gen_base)
    estrategia = BusquedaAlfabetica()
    estadisticos = {'sonoros': {'ritmo': {'media': 50.0}}}
    
    resultado = gen_playlist.generar(catalogo_lleno, estadisticos, estrategia)
    assert len(resultado) == 2
    assert 'playlist' in resultado[1]

# --- SINGLETON Y MAIN ---

def test_recomendador(catalogo_lleno):
    """Prueba principal de Recomendador: garantiza el patrón Singleton."""
    rec1 = Recomendador.obtener_instancia(catalogo_lleno)
    rec2 = Recomendador.obtener_instancia(catalogo_lleno)
    
    # Ambas variables deben apuntar exactamente al mismo espacio de memoria
    assert rec1 is rec2 

def test_usuario(catalogo_lleno):
    """Prueba principal de Usuario: interacciones y manejo de excepciones esperadas."""
    user = Usuario("1", "TestUser", catalogo_lleno)
    
    # Prueba: reproducir canción existente
    user.reproducir_cancion("A Canción")
    assert len(user._recomendador.historial_sesion) == 1
    
    # Prueba: reproducir canción inexistente
    with pytest.raises(CancionNoExisteError):
        user.reproducir_cancion("Cancion Fantasma")
        
    # Prueba: pedir recomendacion sin configurar el generador 
    # Para forzar SesionVacia, reseteamos los estadísticos del singleton 
    user._recomendador.estadisticos_sesion = {}
    with pytest.raises(SesionVaciaError):
        user.solicitar_recomendacion()