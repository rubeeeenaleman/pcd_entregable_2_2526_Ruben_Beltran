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
    c1 = Cancion("Canción1", date(2023, 1, 1), {"ritmo": 50.0}, {"energia": 60.0})
    c2 = Cancion("Canción2", date(2024, 1, 1), {"ritmo": 50.0}, {"energia": 60.0})
    c3 = Cancion("Canción3", date(2022, 1, 1), {"ritmo": 10.0}, {"energia": 10.0})
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
    assert cat.canciones[0].titulo == "Canción1"

