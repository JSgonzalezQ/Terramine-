"""
╔══════════════════════════════════════════════════════════════╗
║          TERRAMINE: LEGACY OF RUNES                          ║
║          Proyecto Universitario - Python 3.11                ║
║          Demuestra: POO, Herencia, Polimorfismo,             ║
║          Encapsulamiento, Excepciones, Aleatoriedad          ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import string
import re
import time

# ─────────────────────────────────────────────
#  INTENTAR CARGAR PYGAME.MIXER
# ─────────────────────────────────────────────
try:
    import pygame.mixer as mixer
    mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False


# ══════════════════════════════════════════════════════════════
#  EXCEPCIONES PERSONALIZADAS
# ══════════════════════════════════════════════════════════════

class RunaError(Exception):
    """Clase base para errores relacionados con runas."""
    pass

class LongitudInvalidaError(RunaError):
    """Se lanza cuando la runa no cumple la longitud mínima."""
    def __str__(self):
        return "⚠ La Runa es demasiado corta. El núcleo hexagonal requiere al menos 8 símbolos."

class EntradaInvalidaError(RunaError):
    """Se lanza cuando la runa contiene caracteres no permitidos."""
    def __str__(self):
        return "⚠ Símbolos extraños detectados. La runa contiene energía inestable."

class RunaCorruptaError(RunaError):
    """Se lanza cuando la runa no cumple las reglas de forja."""
    def __str__(self):
        return "☠ La energía de la runa colapsó. Estructura rúnica inválida."

class EnergiaInsuficienteError(Exception):
    """Se lanza cuando el jugador no tiene suficiente energía."""
    def __str__(self):
        return "⚡ Energía insuficiente. Debes recuperar fuerzas antes de continuar."


# ══════════════════════════════════════════════════════════════
#  CLASE: RUNA
# ══════════════════════════════════════════════════════════════

class Runa:
    """
    Representa una Runa Ancestral del universo Terramine.
    Encapsula la lógica de generación y validación.
    """

    SIMBOLOS_PERMITIDOS = "@#$%&*?!"
    MIN_LONGITUD = 8

       # ── Generación aleatoria ──────────────────
    def generar(self) -> str:
        """Genera una runa temática y válida."""

        bases = [
            "Hexa",
            "Rune",
            "Terra",
            "Ether",
            "Nova",
            "Crys",
            "Astra",
            "Vortex",
            "Nexus",
            "Pyro"
        ]

        simbolos = "@#$%&*?!"

        while True:

            palabra = random.choice(bases)

            numero = str(random.randint(10, 99))

            simbolo = random.choice(simbolos)

            letra_extra = random.choice(string.ascii_uppercase)

            candidato = f"{palabra}{simbolo}{numero}{letra_extra}"

            try:
                self.validar(candidato)

                self._codigo = candidato
                self._valida = True

                return self._codigo

            except RunaError:
                continue # Vuelve a intentar si no cumple reglas

       # ── Validación ────────────────────────────
    def validar(self, codigo: str) -> bool:
        """
        Valida una runa según las leyes ancestrales.
        """

        # Elimina espacios automáticamente
        codigo = codigo.replace(" ", "")

        # Longitud mínima
        if len(codigo) < self.MIN_LONGITUD:
            raise LongitudInvalidaError()

        # Debe tener:
        # mayúscula, minúscula, número y símbolo
        tiene_mayus = any(c.isupper() for c in codigo)
        tiene_minus = any(c.islower() for c in codigo)
        tiene_num   = any(c.isdigit() for c in codigo)

        # Acepta cualquier símbolo NO alfanumérico
        tiene_symbol = any(not c.isalnum() for c in codigo)

        if not (tiene_mayus and tiene_minus and tiene_num and tiene_symbol):
            raise RunaCorruptaError()

        self._codigo = codigo
        self._valida = True

        return True
    
    # ── Propiedades ───────────────────────────
    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def es_valida(self) -> bool:
        return self._valida


# ══════════════════════════════════════════════════════════════
#  CLASE: INVENTARIO
# ══════════════════════════════════════════════════════════════

class Inventario:
    """Gestiona los objetos que porta el Cazador de Runas."""

    CAPACIDAD_MAXIMA = 10

    def __init__(self):
        self._objetos: list[str] = []   # Lista encapsulada

    def agregar(self, objeto: str) -> bool:
        """Agrega un objeto si hay espacio en la mochila."""
        if len(self._objetos) < self.CAPACIDAD_MAXIMA:
            self._objetos.append(objeto)
            return True
        return False
    
    def usar_objeto(self, objeto: str) -> bool:
        """
        Usa y elimina un objeto del inventario.
        """

        if objeto in self._objetos:
            self._objetos.remove(objeto)
            return True

        return False


    def mostrar(self) -> str:
        """Devuelve una representación visual de la mochila."""
        if not self._objetos:
            return "  [ Mochila vacía ]"
        lineas = []
        for i, obj in enumerate(self._objetos, 1):
            lineas.append(f"  {i}. {obj}")
        return "\n".join(lineas)

    @property
    def cantidad(self) -> int:
        return len(self._objetos)

    @property
    def objetos(self) -> list:
        return list(self._objetos)  # Copia defensiva


# ══════════════════════════════════════════════════════════════
#  CLASE: JUGADOR
# ══════════════════════════════════════════════════════════════

class Jugador:
    """
    Representa al Cazador de Runas.
    Encapsula todos los atributos del personaje con propiedades.
    """

    # Tabla de títulos según nivel
    TITULOS = {
        1: "Aprendiz Runario",
        2: "Explorador Hexagonal",
        3: "Maestro Runario",
        4: "MAESTRO RUNARIO SUPREMO ★",
    }

    def __init__(self, nombre: str):
        self._nombre    = nombre
        self._vida      = 100
        self._vida_max  = 100
        self._energia   = 100
        self._energia_max = 100
        self._nivel     = 1
        self._puntos    = 0
        self._oro       = 50
        self._runas_forjadas = 0
        self._inventario = Inventario()
        self._bioma_actual = "Minas de Cristal"

    # ── Propiedades (encapsulamiento) ─────────
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def vida(self) -> int:
        return self._vida

    @property
    def vida_max(self) -> int:
        return self._vida_max

    @property
    def energia(self) -> int:
        return self._energia

    @property
    def energia_max(self) -> int:
        return self._energia_max

    @property
    def nivel(self) -> int:
        return self._nivel

    @property
    def puntos(self) -> int:
        return self._puntos

    @property
    def oro(self) -> int:
        return self._oro

    @property
    def titulo(self) -> str:
        return self.TITULOS.get(self._nivel, self.TITULOS[4])

    @property
    def inventario(self) -> Inventario:
        return self._inventario

    @property
    def bioma_actual(self) -> str:
        return self._bioma_actual

    @bioma_actual.setter
    def bioma_actual(self, bioma: str):
        self._bioma_actual = bioma

    # ── Métodos de juego ──────────────────────
    def ganar_puntos(self, cantidad: int):
        """Suma puntos y verifica subida de nivel."""
        self._puntos += cantidad
        self._actualizar_nivel()

    def gastar_energia(self, cantidad: int):
        """Gasta energía, lanzando excepción si es insuficiente."""
        if self._energia < cantidad:
            raise EnergiaInsuficienteError()
        self._energia -= cantidad

    def recuperar_energia(self, cantidad: int):
        self._energia = min(self._energia + cantidad, self._energia_max)

    def recibir_dano(self, cantidad: int):
        self._vida = max(0, self._vida - cantidad)

    def recuperar_vida(self, cantidad: int):
        self._vida = min(self._vida + cantidad, self._vida_max)

    def ganar_oro(self, cantidad: int):
        self._oro += cantidad
        
    def gastar_oro(self, cantidad: int):
        """Reduce cristales del jugador."""
        if self._oro >= cantidad:
            self._oro -= cantidad

    def registrar_runa(self):
        self._runas_forjadas += 1

    def _actualizar_nivel(self):
        """Sube de nivel según los puntos acumulados."""
        if self._puntos >= 500:
            self._nivel = 4
        elif self._puntos >= 200:
            self._nivel = 3
        elif self._puntos >= 75:
            self._nivel = 2
        else:
            self._nivel = 1

    def barra(self, actual: int, maximo: int, largo: int = 10) -> str:
        """Genera una barra de progreso visual tipo HUD."""
        lleno = int((actual / maximo) * largo)
        vacio = largo - lleno
        return "█" * lleno + "░" * vacio

    def esta_vivo(self) -> bool:
        return self._vida > 0


# ══════════════════════════════════════════════════════════════
#  CLASES: COFRES (Herencia + Polimorfismo)
# ══════════════════════════════════════════════════════════════

class Cofre:
    """
    Clase PADRE que representa un cofre ancestral.
    Define la interfaz base para todos los tipos de cofres.
    """

    def __init__(self, nombre: str, rareza: str, puntos_base: int):
        self._nombre      = nombre
        self._rareza      = rareza
        self._puntos_base = puntos_base
        self._abierto     = False

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def rareza(self) -> str:
        return self._rareza

    def abrir(self, jugador: 'Jugador') -> tuple[str, int]:
        """
        Método polimórfico: cada subclase implementa su propio efecto.
        Devuelve (mensaje, puntos_ganados).
        """
        raise NotImplementedError("Las subclases deben implementar abrir()")

    def _marcar_abierto(self):
        self._abierto = True


class CofreComun(Cofre):
    """Cofre básico. Recompensa modesta y segura."""

    def __init__(self):
        super().__init__("Cofre Común", "COMÚN", 20)

    def abrir(self, jugador: 'Jugador') -> tuple[str, int]:
        self._marcar_abierto()
        oro = random.randint(5, 15)
        jugador.ganar_oro(oro)
        jugador.inventario.agregar("Fragmento Rúnico")
        jugador.recuperar_energia(10)
        mensaje = (
            f"🪨 El {self.nombre} cruje al abrirse...\n"
            f"   Encontraste {oro} cristales y un Fragmento Rúnico.\n"
            f"   Tu energía se restaura levemente. (+10⚡)"
        )
        return mensaje, self._puntos_base


class CofreRaro(Cofre):
    """Cofre inusual. Mejor recompensa con algo de riesgo."""

    def __init__(self):
        super().__init__("Cofre Raro", "RARO", 50)

    def abrir(self, jugador: 'Jugador') -> tuple[str, int]:
        self._marcar_abierto()
        oro = random.randint(20, 40)
        jugador.ganar_oro(oro)
        jugador.inventario.agregar("Núcleo Antiguo")
        jugador.recuperar_vida(15)
        mensaje = (
            f"💎 El {self.nombre} emite un destello azul...\n"
            f"   ¡Un Núcleo Antiguo materializa ante ti!\n"
            f"   Obtienes {oro} cristales y recuperas vitalidad. (+15❤)"
        )
        return mensaje, self._puntos_base


class CofreLegendario(Cofre):
    """Cofre legendario. Grandes recompensas garantizadas."""

    def __init__(self):
        super().__init__("Cofre Legendario", "LEGENDARIO", 100)

    def abrir(self, jugador: 'Jugador') -> tuple[str, int]:
        self._marcar_abierto()
        oro = random.randint(60, 100)
        jugador.ganar_oro(oro)
        jugador.inventario.agregar("Cristal Primordial")
        jugador.recuperar_vida(30)
        jugador.recuperar_energia(30)
        mensaje = (
            f"✨ ¡El {self.nombre} DESPIERTA!\n"
            f"   Luz hexagonal inunda la caverna...\n"
            f"   ¡Un Cristal Primordial es tuyo!\n"
            f"   Recibes {oro} cristales. Vida y energía restauradas. (+30❤/⚡)"
        )
        return mensaje, self._puntos_base


class CofreMaldito(Cofre):
    """Cofre maldito. Gran riesgo, gran recompensa."""

    def __init__(self):
        super().__init__("Cofre Maldito", "MALDITO", 80)

    def abrir(self, jugador: 'Jugador') -> tuple[str, int]:
        self._marcar_abierto()
        exito = random.random() > 0.4   # 60% de éxito

        if exito:
            oro = random.randint(50, 90)
            jugador.ganar_oro(oro)
            jugador.inventario.agregar("Runa Oscura")
            mensaje = (
                f"☠ El {self.nombre} palpita con energía oscura...\n"
                f"   ¡Sobreviviste a la maldición!\n"
                f"   Una Runa Oscura y {oro} cristales son tuyos."
            )
            return mensaje, self._puntos_base
        else:
            dano = random.randint(15, 30)
            jugador.recibir_dano(dano)
            mensaje = (
                f"☠ El {self.nombre} libera su maldición...\n"
                f"   La energía corrupta te golpea. (-{dano}❤)\n"
                f"   Pero encontraste fragmentos entre las sombras."
            )
            return mensaje, self._puntos_base // 2
# ══════════════════════════════════════════════════════════════
#  BIOMAS
# ══════════════════════════════════════════════════════════════

BIOMAS = {

    "Minas de Cristal": {
        "emoji": "💎",
        "color": "#00E5FF",
        "descripcion":
            "Cristales azules iluminan túneles antiguos.\n"
            "El eco metálico de las minas resuena a la distancia."
    },

    "Bosque Hexagonal": {
        "emoji": "🌲",
        "color": "#00FF99",
        "descripcion":
            "Árboles geométricos rodean ruinas olvidadas.\n"
            "La energía natural fluye entre símbolos rúnicos."
    },

    "Abismo Magnético": {
        "emoji": "⚡",
        "color": "#FF0066",
        "descripcion":
            "Fragmentos metálicos flotan en la oscuridad.\n"
            "La gravedad parece distorsionarse constantemente."
    },

    "Ruinas de Etherion": {
        "emoji": "🏛",
        "color": "#FFD700",
        "descripcion":
            "Tecnología ancestral cubierta de polvo y símbolos.\n"
            "Viejos mecanismos aún reaccionan a las runas."
    },

    "Cavernas de Ceniza": {
        "emoji": "🔥",
        "color": "#FF6600",
        "descripcion":
            "El calor consume el aire de las cavernas.\n"
            "Restos de magma iluminan el camino."
    },

    "Templo del Núcleo": {
        "emoji": "🌟",
        "color": "#CC99FF",
        "descripcion":
            "Una energía silenciosa envuelve el templo.\n"
            "Aquí descansa el secreto del Cofre Primordial."
    }
}


# ══════════════════════════════════════════════════════════════
#  CLASE: GESTOR DE AUDIO
# ══════════════════════════════════════════════════════════════

class GestorAudio:
    """
    Gestiona el audio del juego con degradación elegante.
    Si pygame no está disponible o los archivos no existen,
    los métodos simplemente no hacen nada (sin crash).
    Para activar el audio, coloca archivos .wav en la carpeta
    'sounds/' con los nombres: valida, corrupta, cofre, click,
    victoria, derrota.
    """

    SONIDOS = {
        "valida":   "sounds/valida.wav",
        "corrupta": "sounds/corrupta.wav",
        "cofre":    "sounds/cofre.wav",
        "click":    "sounds/click.wav",
        "victoria": "sounds/victoria.wav",
        "derrota":  "sounds/derrota.wav",
    }

    def __init__(self):
        self._cache: dict = {}
        self._disponible = SOUND_AVAILABLE
        if self._disponible:
            self._precargar()

    def _precargar(self):
        """Intenta precargar todos los sonidos definidos."""
        for clave, ruta in self.SONIDOS.items():
            try:
                import pygame.mixer as mx
                self._cache[clave] = mx.Sound(ruta)
            except Exception:
                pass  # Archivo no encontrado — continúa sin él

    def reproducir(self, clave: str, volumen: float = 0.6):
        """Reproduce un sonido por su clave. Falla silenciosamente."""
        if not self._disponible or clave not in self._cache:
            return
        try:
            self._cache[clave].set_volume(volumen)
            self._cache[clave].play()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#  INTERFAZ GRÁFICA: TERRAMINE
# ══════════════════════════════════════════════════════════════

class TerramineApp:
    """
    Clase principal de la interfaz gráfica.
    Orquesta todos los sistemas del juego.
    """

    # ── Paleta de colores retro-futurista ─────
    COLOR_BG        = "#0A0A0F"
    COLOR_PANEL     = "#0D1117"
    COLOR_BORDE     = "#1C2333"
    COLOR_TEXTO     = "#C9D1D9"
    COLOR_ACENTO    = "#00BFFF"
    COLOR_ACENTO2   = "#39FF14"
    COLOR_PELIGRO   = "#FF4444"
    COLOR_ORO       = "#FFD700"
    COLOR_RARO      = "#B44FE8"
    COLOR_MUTED     = "#484F58"
    COLOR_BTN       = "#161B22"
    COLOR_BTN_HOV   = "#1C2333"

    PUNTOS_META = 500   # Puntos para desbloquear el Cofre Primordial

    def __init__(self, root: tk.Tk):
        self.root = root
        self.jugador: Jugador | None = None
        self._fase = "inicio"       # inicio | juego | fin
        self._expedicion_activa = False
        self.audio = GestorAudio()  # Sistema de audio (falla silenciosamente)

        self._configurar_ventana()
        self._construir_pantalla_inicio()

    # ─────────────────────────────────────────
    #  CONFIGURACIÓN DE VENTANA
    # ─────────────────────────────────────────
    def _configurar_ventana(self):
        self.root.title("TERRAMINE: LEGACY OF RUNES")
        self.root.geometry("960x720")
        self.root.minsize(900, 680)
        self.root.configure(bg=self.COLOR_BG)
        self.root.resizable(True, True)

        # Fuentes
        self.font_titulo  = tkfont.Font(family="Courier New", size=22, weight="bold")
        self.font_subtit  = tkfont.Font(family="Courier New", size=12, weight="bold")
        self.font_normal  = tkfont.Font(family="Courier New", size=10)
        self.font_hud     = tkfont.Font(family="Courier New", size=9,  weight="bold")
        self.font_btn     = tkfont.Font(family="Courier New", size=10, weight="bold")
        self.font_grande  = tkfont.Font(family="Courier New", size=13, weight="bold")

    # ─────────────────────────────────────────
    #  PANTALLA DE INICIO
    # ─────────────────────────────────────────
    def _construir_pantalla_inicio(self):
        self._limpiar_ventana()
        self._fase = "inicio"

        # Marco contenedor centrado
        marco = tk.Frame(self.root, bg=self.COLOR_BG)
        marco.place(relx=0.5, rely=0.5, anchor="center")

        # ── Logo ASCII ────────────────────────
        logo = (
        "╔═══════════════════════════════════════════════════════════════════════════╗\n"
        "║ ████████╗███████╗██████╗ ██████╗  █████╗ ███╗   ███╗██╗███╗   ██╗███████╗ ║\n"
        "║ ╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║██╔════╝ ║\n"
        "║    ██║   █████╗  ██████╔╝██████╔╝███████║██╔████╔██║██║██╔██╗ ██║█████╗   ║\n"
        "║    ██║   ██╔══╝  ██╔══██╗██╔══██╗██╔══██║██║╚██╔╝██║██║██║╚██╗██║██╔══╝   ║\n"
        "║    ██║   ███████╗██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║██║██║ ╚████║███████╗ ║\n"
        "║    ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝ ║\n"
        "╚═══════════════════════════════════════════════════════════════════════════╝"
        )
        tk.Label(
            marco, text=logo,
            bg=self.COLOR_BG, fg=self.COLOR_ACENTO,
            font=self.font_hud, justify="center"
        ).pack(pady=(0, 8))

        tk.Label(
            marco,
            text="— Forja tu destino. Descifra las Runas Ancestrales. —",
            bg=self.COLOR_BG, fg=self.COLOR_MUTED,
            font=self.font_normal
        ).pack(pady=(0, 30))

        # ── Entrada de nombre ─────────────────
        tk.Label(
            marco, text="IDENTIFICAR CAZADOR:",
            bg=self.COLOR_BG, fg=self.COLOR_ACENTO2,
            font=self.font_subtit
        ).pack()

        self.entry_nombre = tk.Entry(
            marco,
            bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
            insertbackground=self.COLOR_ACENTO,
            font=self.font_grande, width=24,
            bd=0, highlightthickness=2,
            highlightbackground=self.COLOR_BORDE,
            highlightcolor=self.COLOR_ACENTO,
            justify="center"
        )
        self.entry_nombre.pack(pady=10, ipady=6)
        self.entry_nombre.focus()
        self.entry_nombre.bind("<Return>", lambda e: self._iniciar_juego())

        # ── Botón iniciar ─────────────────────
        self._boton(marco, "⚡  INICIAR EXPEDICIÓN", self._iniciar_juego,
                    color=self.COLOR_ACENTO).pack(pady=8, ipadx=20, ipady=8)

        # ── Lore intro ────────────────────────
        lore = (
            "En las profundidades del universo Terramine,\n"
            "antiguas civilizaciones ocultaron sus secretos\n"
            "tras Runas Ancestrales imposibles de descifrar.\n\n"
            "Tú eres el último Cazador de Runas.\n"
            "Forja. Explora. Desbloquea el Cofre Primordial."
        )
        tk.Label(
            marco, text=lore,
            bg=self.COLOR_BG, fg=self.COLOR_MUTED,
            font=self.font_normal, justify="center"
        ).pack(pady=20)

    # ─────────────────────────────────────────
    #  INICIAR JUEGO
    # ─────────────────────────────────────────
    def _iniciar_juego(self):

        nombre = self.entry_nombre.get().strip()

        if not nombre:

            self.audio.reproducir("corrupta")

            self._mostrar_error_inicio(
                "⚠ Debes identificar a tu Cazador antes de iniciar."
            )

            return

        self.jugador = Jugador(nombre)

        self._fase = "juego"

        self._construir_juego()

        self.audio.reproducir("valida")

        # Espera a que tkinter termine de construir
        self.root.after(100, self._mostrar_intro)

    # ─────────────────────────────────────────
    #  MOSTRAR ERROR EN PANTALLA DE INICIO
    # ─────────────────────────────────────────
    def _mostrar_error_inicio(self, mensaje: str):
        """Muestra un mensaje de error temporal en la pantalla de inicio."""
        lbl_error = tk.Label(
            self.root,
            text=mensaje,
            bg=self.COLOR_BG,
            fg=self.COLOR_PELIGRO,
            font=self.font_normal
        )
        lbl_error.place(relx=0.5, rely=0.93, anchor="center")
        # Se destruye automáticamente después de 3 segundos
        self.root.after(3000, lbl_error.destroy)

    # ─────────────────────────────────────────
    #  INTRODUCCIÓN DEL JUEGO
    # ─────────────────────────────────────────
    def _mostrar_intro(self):

        nombre = self.jugador.nombre

        self._escribir_narrativa(
            f"═══════════════════════════════════════\n"
            f"  BIENVENIDO, {nombre.upper()}\n"
            f"  Título: {self.jugador.titulo}\n"
            f"═══════════════════════════════════════\n\n"
            f"Las antiguas crónicas de Terramine te aguardan.\n"
            f"El eco de runas ancestrales resuena en el aire.\n\n"
            f"Tu primera expedición comienza en:\n"
            f"⛏ {self.jugador.bioma_actual}\n\n"
            f"{BIOMAS[self.jugador.bioma_actual]['descripcion']}\n\n"
            f"Forja una Runa para abrir los cofres que encuentres.\n"
            f"Acumula {self.PUNTOS_META} puntos para desbloquear el COFRE PRIMORDIAL.\n",
            self.COLOR_ORO
        )

        self._actualizar_hud()

        self._mostrar_ayuda()


    # ─────────────────────────────────────────
    #  CONSTRUIR INTERFAZ DE JUEGO
    # ─────────────────────────────────────────
    def _construir_juego(self):
        self._limpiar_ventana()

        # ── Layout en grid (3 columnas) ───────
        self.root.columnconfigure(0, weight=0)   # HUD lateral
        self.root.columnconfigure(1, weight=1)   # Área central
        self.root.columnconfigure(2, weight=0)   # Botones
        self.root.rowconfigure(0, weight=1)

        # ══ PANEL IZQUIERDO: HUD ══════════════
        self.frame_hud = tk.Frame(
            self.root, bg=self.COLOR_PANEL,
            bd=0, highlightthickness=1,
            highlightbackground=self.COLOR_BORDE,
            width=200
        )
        self.frame_hud.grid(row=0, column=0, sticky="nsew", padx=(8,4), pady=8)
        self.frame_hud.grid_propagate(True)
        self._construir_hud()

        # ══ PANEL CENTRAL: NARRATIVA ══════════
        frame_centro = tk.Frame(self.root, bg=self.COLOR_BG)
        frame_centro.grid(row=0, column=1, sticky="nsew", pady=8)
        frame_centro.rowconfigure(0, weight=0)
        frame_centro.rowconfigure(1, weight=1)
        frame_centro.columnconfigure(0, weight=1)

        # Título del área narrativa
        tk.Label(
            frame_centro,
            text="◈ REGISTRO DE EXPEDICIÓN",
            bg=self.COLOR_BG, fg=self.COLOR_MUTED,
            font=self.font_hud
        ).grid(row=0, column=0, sticky="nw", padx=4, pady=(0,2))

        # Caja de texto narrativa
        self.texto_narrativa = tk.Text(
            frame_centro,
            bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
            font=self.font_normal, wrap="word",
            highlightthickness=1,
            highlightbackground=self.COLOR_BORDE,
            insertbackground=self.COLOR_ACENTO,
            selectbackground=self.COLOR_BORDE,
            padx=12, pady=10
        )
        self.texto_narrativa.grid(row=1, column=0, sticky="nsew", padx=4)
        frame_centro.rowconfigure(1, weight=1)

        # Scrollbar
        scroll = tk.Scrollbar(frame_centro, command=self.texto_narrativa.yview,
                              bg=self.COLOR_PANEL, troughcolor=self.COLOR_BG)
        scroll.grid(row=1, column=1, sticky="ns", pady=0)
        self.texto_narrativa.configure(yscrollcommand=scroll.set)

        # ── Campo de entrada de Runa ──────────
        frame_entrada = tk.Frame(frame_centro, bg=self.COLOR_BG)
        frame_entrada.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=(6,0))
        frame_entrada.columnconfigure(1, weight=1)

        tk.Label(
            frame_entrada, text="RUNA ▶",
            bg=self.COLOR_BG, fg=self.COLOR_ACENTO,
            font=self.font_subtit
        ).grid(row=0, column=0, padx=(0,6))

        self.entry_runa = tk.Entry(
            frame_entrada,
            bg=self.COLOR_BTN, fg=self.COLOR_ACENTO2,
            insertbackground=self.COLOR_ACENTO2,
            font=self.font_grande, bd=0,
            highlightthickness=1,
            highlightbackground=self.COLOR_BORDE,
            highlightcolor=self.COLOR_ACENTO2
        )
        self.entry_runa.grid(row=0, column=1, sticky="ew", ipady=6)
        self.entry_runa.bind("<Return>", lambda e: self._forjar_runa())

        # ══ PANEL DERECHO: BOTONES ════════════
        frame_btns = tk.Frame(
            self.root, bg=self.COLOR_PANEL,
            bd=0, highlightthickness=1,
            highlightbackground=self.COLOR_BORDE,
            width=170
        )
        frame_btns.grid(row=0, column=2, sticky="nsew", padx=(4,8), pady=8)
        frame_btns.grid_propagate(False)
        self._construir_panel_botones(frame_btns)

        self._actualizar_hud()
    # ─────────────────────────────────────────
    #  HUD
    # ─────────────────────────────────────────
    def _construir_hud(self):
        """Construye el panel HUD izquierdo."""
        p = self.frame_hud

        # Cabecera HUD
        tk.Label(p, text="◈ HUD RUNARIO",
                 bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
                 font=self.font_subtit).pack(pady=(12,6))

        self._sep(p)

        # Variables de texto para actualizar dinámicamente
        self._v_nombre  = tk.StringVar()
        self._v_titulo  = tk.StringVar()
        self._v_nivel   = tk.StringVar()
        self._v_vida    = tk.StringVar()
        self._v_bvida   = tk.StringVar()
        self._v_energia = tk.StringVar()
        self._v_bener   = tk.StringVar()
        self._v_oro     = tk.StringVar()
        self._v_puntos  = tk.StringVar()
        self._v_bioma   = tk.StringVar()
        self._v_meta    = tk.StringVar()

        items_hud = [
            ("CAZADOR", self._v_nombre,  self.COLOR_TEXTO),
            ("TÍTULO",  self._v_titulo,  self.COLOR_ORO),
            ("NIVEL",   self._v_nivel,   self.COLOR_ACENTO2),
        ]
        for etq, var, color in items_hud:
            self._fila_hud(p, etq, var, color)

        self._sep(p)

        # Barras de vida / energía
        self._etiq_hud(p, "VIDA", self.COLOR_PELIGRO)
        tk.Label(p, textvariable=self._v_vida,
                 bg=self.COLOR_PANEL, fg=self.COLOR_PELIGRO,
                 font=self.font_hud).pack(anchor="w", padx=12)
        tk.Label(p, textvariable=self._v_bvida,
                 bg=self.COLOR_PANEL, fg=self.COLOR_PELIGRO,
                 font=self.font_hud).pack(anchor="w", padx=12, pady=(0,4))

        self._etiq_hud(p, "ENERGÍA", self.COLOR_ACENTO)
        tk.Label(p, textvariable=self._v_energia,
                 bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
                 font=self.font_hud).pack(anchor="w", padx=12)
        tk.Label(p, textvariable=self._v_bener,
                 bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
                 font=self.font_hud).pack(anchor="w", padx=12, pady=(0,4))

        self._sep(p)

        items_hud2 = [
            ("CRISTALES", self._v_oro,    self.COLOR_ORO),
            ("PUNTAJE",   self._v_puntos, self.COLOR_ACENTO2),
        ]
        for etq, var, color in items_hud2:
            self._fila_hud(p, etq, var, color)

        self._sep(p)

        self._etiq_hud(p, "BIOMA", self.COLOR_MUTED)
        tk.Label(p, textvariable=self._v_bioma,
                 bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
                 font=self.font_hud, wraplength=170, justify="left"
                 ).pack(anchor="w", padx=12, pady=(0,4))

        self._sep(p)

        self._etiq_hud(p, "META PRIMORDIAL", self.COLOR_ORO)
        tk.Label(p, textvariable=self._v_meta,
                 bg=self.COLOR_PANEL, fg=self.COLOR_ORO,
                 font=self.font_hud).pack(anchor="w", padx=12, pady=(0,8))

    def _etiq_hud(self, parent, texto, color):
        tk.Label(parent, text=texto,
                 bg=self.COLOR_PANEL, fg=color,
                 font=tkfont.Font(family="Courier New", size=8, weight="bold")
                 ).pack(anchor="w", padx=12, pady=(4,0))

    def _fila_hud(self, parent, etiqueta, var, color):
        self._etiq_hud(parent, etiqueta, self.COLOR_MUTED)
        tk.Label(parent, textvariable=var,
                 bg=self.COLOR_PANEL, fg=color,
                 font=self.font_hud, wraplength=170, justify="left"
                 ).pack(anchor="w", padx=12, pady=(0,2))

    def _sep(self, parent):
        tk.Frame(parent, bg=self.COLOR_BORDE, height=1).pack(fill="x", padx=8, pady=4)

    def _actualizar_hud(self):
        """Refresca todos los valores del HUD con datos del jugador."""
        if not self.jugador:
            return
        j = self.jugador
        self._v_nombre.set(j.nombre)
        self._v_titulo.set(j.titulo)
        self._v_nivel.set(f"Nivel {j.nivel}")
        self._v_vida.set(f"{j.vida}/{j.vida_max}")
        self._v_bvida.set(j.barra(j.vida, j.vida_max))
        self._v_energia.set(f"{j.energia}/{j.energia_max}")
        self._v_bener.set(j.barra(j.energia, j.energia_max))
        self._v_oro.set(f"◆ {j.oro}")
        self._v_puntos.set(f"⭐ {j.puntos}")
        self._v_bioma.set(j.bioma_actual)
        progreso = min(j.puntos, self.PUNTOS_META)
        self._v_meta.set(f"{progreso}/{self.PUNTOS_META} pts\n{j.barra(progreso, self.PUNTOS_META)}")

    # ─────────────────────────────────────────
    #  PANEL DE BOTONES
    # ─────────────────────────────────────────
    def _construir_panel_botones(self, parent):
        tk.Label(parent, text="◈ ACCIONES",
                 bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
                 font=self.font_subtit).pack(pady=(12,6))

        self._sep(parent)

        acciones = [
            ("⚒  FORJAR RUNA",       self._forjar_runa,         self.COLOR_ACENTO2),
            ("🎲  AUTO-FORJAR",       self._auto_forjar,        self.COLOR_ACENTO),
            ("🗺  EXPLORAR", self._nueva_expedicion, self.COLOR_ACENTO),
            ("🎒  VER MOCHILA",       self._ver_mochila,        self.COLOR_MUTED),
            ("📊  ESTADÍSTICAS",      self._ver_estadisticas,   self.COLOR_MUTED),
            ("🔄  RECUPERAR",         self._recuperar,          self.COLOR_ACENTO2),
            ("❓  AYUDA",             self._mostrar_ayuda,      self.COLOR_ACENTO),
            ("🚪  SALIR",             self._salir,              self.COLOR_PELIGRO),
        ]



        for texto, cmd, color in acciones:
            self._boton(parent, texto, cmd, color=color).pack(
                fill="x", padx=10, pady=3, ipady=5
            )

        self._sep(parent)

        # Leyenda de rareza
        tk.Label(parent, text="RAREZA DE COFRES:",
                 bg=self.COLOR_PANEL, fg=self.COLOR_MUTED,
                 font=tkfont.Font(family="Courier New", size=8)).pack(pady=(4,0))
        for txt, col in [("● COMÚN", self.COLOR_TEXTO),
                         ("● RARO",  self.COLOR_ACENTO),
                         ("● LEGENDARIO", self.COLOR_ORO),
                         ("● MALDITO",    self.COLOR_PELIGRO)]:
            tk.Label(parent, text=txt,
                     bg=self.COLOR_PANEL, fg=col,
                     font=tkfont.Font(family="Courier New", size=8)
                     ).pack(anchor="w", padx=14)

    # ─────────────────────────────────────────
    #  HELPER: BOTÓN ESTILIZADO
    # ─────────────────────────────────────────
    def _boton(self, parent, texto, comando, color=None) -> tk.Button:
        color = color or self.COLOR_TEXTO
        btn = tk.Button(
            parent, text=texto,
            command=lambda: (self.audio.reproducir("click"), comando()),
            bg=self.COLOR_BTN, fg=color,
            activebackground=self.COLOR_BTN_HOV, activeforeground=color,
            font=self.font_btn, bd=0, cursor="hand2",
            highlightthickness=1,
            highlightbackground=self.COLOR_BORDE,
            anchor="w", padx=8
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=self.COLOR_BTN_HOV))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.COLOR_BTN))
        return btn

    # ─────────────────────────────────────────
    #  NARRATIVA
    # ─────────────────────────────────────────
    def _escribir_narrativa(self, texto: str, color: str = None):
        """Escribe texto en el área narrativa con color opcional."""
        self.texto_narrativa.config(state="normal")

        tag = None
        if color:
            tag = f"color_{color.replace('#','')}"
            self.texto_narrativa.tag_configure(tag, foreground=color)

        self.texto_narrativa.insert("end", texto + "\n", tag or "")
        self.texto_narrativa.config(state="disabled")
        self.texto_narrativa.see("end")

    def _sep_narrativa(self):
        self._escribir_narrativa("─" * 45, self.COLOR_BORDE)

    # ─────────────────────────────────────────
    #  ACCIÓN: FORJAR RUNA
    # ─────────────────────────────────────────
    def _forjar_runa(self):
        if not self._verificar_jugador_vivo():
            return

        codigo = self.entry_runa.get().strip()
        if not codigo:
            self._escribir_narrativa(
                "⚒ Debes ingresar una Runa en el campo de texto.\n"
                "  O usa AUTO-FORJAR para generar una automáticamente.",
                self.COLOR_MUTED
            )
            return

        self._sep_narrativa()
        self._escribir_narrativa(f"⚒ Forjando runa: [{codigo}]...", self.COLOR_ACENTO2)

        try:
            runa = Runa()
            runa.validar(codigo)
            
             # Éxito
             
            self.audio.reproducir("valida")

            self._escribir_narrativa(
                "✨ La runa ancestral fue aceptada.",
                self.COLOR_ACENTO2
            )

            self.jugador.registrar_runa()

            # ─────────────────────────────
            # SI EXISTE UN COFRE
            # ─────────────────────────────

            if hasattr(self, "cofre_actual") and self.cofre_actual:

                # Abrir cofre consume energía
                self.jugador.gastar_energia(10)

                self._sep_narrativa()

                self._escribir_narrativa(
                    f"⚒ El sello del {self.cofre_actual.nombre} comienza a romperse...",
                    self.COLOR_ORO
                )

                mensaje, puntos = self.cofre_actual.abrir(self.jugador)

                self._escribir_narrativa(
                     mensaje,
                self.COLOR_TEXTO
                
                )
                
                self.jugador.ganar_puntos(puntos)
                
                self._escribir_narrativa(
                    
                        f"⭐ +{puntos} puntos de expedición.",
                
                self.COLOR_ACENTO2
                
                )

                # RECOMPENSAS SEGÚN COFRE

                if isinstance(self.cofre_actual, CofreComun):

                    self.jugador.ganar_oro(15)
                    self.jugador.ganar_puntos(10)

                    self._escribir_narrativa(
                        "💰 Obtienes cristales y fragmentos básicos.",
                        self.COLOR_ORO
                    )

                elif isinstance(self.cofre_actual, CofreRaro):

                    self.jugador.ganar_oro(30)
                    self.jugador.ganar_puntos(25)
                    self.jugador.recuperar_energia(20)

                    self._escribir_narrativa(
                        "⚡ El núcleo del cofre restaura parte de tu energía.",
                        self.COLOR_ACENTO
                    )

                elif isinstance(self.cofre_actual, CofreLegendario):

                    self.jugador.ganar_oro(60)
                    self.jugador.ganar_puntos(50)
                    self.jugador.recuperar_vida(30)

                    self._escribir_narrativa(
                        "🌟 Descubres una reliquia legendaria.",
                        self.COLOR_ACENTO2
                    )

                elif isinstance(self.cofre_actual, CofreMaldito):

                    self.jugador.recibir_dano(20)

                    self._escribir_narrativa(
                        "☠ El cofre estaba corrupto.",
                        self.COLOR_PELIGRO
                    )

                # Eliminar cofre activo
                self.cofre_actual = None

            else:

                self._escribir_narrativa(
                    "⚠ No hay cofres sellados en esta expedición.",
                    self.COLOR_MUTED
                )

            self.entry_runa.delete(0, "end")

        except LongitudInvalidaError as e:
            self.audio.reproducir("corrupta")
            self._escribir_narrativa(str(e), self.COLOR_PELIGRO)

        except EntradaInvalidaError as e:
            self.audio.reproducir("corrupta")
            self._escribir_narrativa(str(e), self.COLOR_PELIGRO)

        except RunaCorruptaError as e:
            self.audio.reproducir("corrupta")
            self._escribir_narrativa(str(e), self.COLOR_PELIGRO)
            self.jugador.recibir_dano(5)
            self._escribir_narrativa("   La energía corrupta te golpea. (-5❤)", self.COLOR_PELIGRO)

        except EnergiaInsuficienteError as e:
            self._escribir_narrativa(str(e), self.COLOR_PELIGRO)

        self._actualizar_hud()
        self._verificar_meta()

    # ─────────────────────────────────────────
    #  ACCIÓN: AUTO-FORJAR
    # ─────────────────────────────────────────
    def _auto_forjar(self):
        if not self._verificar_jugador_vivo():
            return

        self._sep_narrativa()
        self._escribir_narrativa("⚙ Activando núcleo runario automático...", self.COLOR_ACENTO)

        try:
            self.jugador.gastar_energia(15)
            runa = Runa()
            codigo = runa.generar()

            self.jugador.ganar_puntos(20)
            self.jugador.ganar_oro(random.randint(5, 12))
            self.jugador.registrar_runa()

            self.audio.reproducir("valida")
            self._escribir_narrativa(
                f"✨ Runa ancestral generada: [{codigo}]\n"
                f"   El cristal palpita con energía estable. (+20 pts / +oro)",
                self.COLOR_ACENTO2
            )

        except EnergiaInsuficienteError as e:
            self._escribir_narrativa(str(e), self.COLOR_PELIGRO)

        self._actualizar_hud()
        self._verificar_meta()

    # ─────────────────────────────────────────
    #  ACCIÓN: NUEVA EXPEDICIÓN (cambiar bioma)
    # ─────────────────────────────────────────
    def _nueva_expedicion(self):
        if not self._verificar_jugador_vivo():
            return

        biomas = list(BIOMAS.keys())
        nuevo_bioma = random.choice(biomas)
        self.jugador.bioma_actual = nuevo_bioma
        info = BIOMAS[nuevo_bioma]

        self._sep_narrativa()
        self._escribir_narrativa(
            f"{info['emoji']} Expedición al: {nuevo_bioma}",
            info["color"]
        )
        self._escribir_narrativa(info["descripcion"], self.COLOR_TEXTO)

        # Evento aleatorio
        self._evento_aleatorio()
        self._actualizar_hud()

    # ─────────────────────────────────────────
    #  EVENTOS ALEATORIOS
    # ─────────────────────────────────────────
    def _evento_aleatorio(self):
        """Genera un evento narrativo aleatorio al explorar."""

        eventos = [

            (
                "💨 Un viento frío recorre la caverna. Encuentras cristales dispersos.",
                lambda j: j.ganar_oro(random.randint(5, 15)),
                self.COLOR_MUTED
            ),

            (
                "⚡ Una descarga rúnica recarga tu energía.",
                lambda j: j.recuperar_energia(25),
                self.COLOR_ACENTO
            ),

            (
                "🦴 Una trampa ancestral se activa. Recibes daño.",
                lambda j: j.recibir_dano(random.randint(5, 20)),
                self.COLOR_PELIGRO
            ),

            (
                "🌟 Hallas un fragmento de runa flotante. Ganas puntos.",
                lambda j: j.ganar_puntos(10),
                self.COLOR_ACENTO2
            ),

            (
                "🍄 Un hongo luminoso restaura tu vitalidad.",
                lambda j: j.recuperar_vida(20),
                self.COLOR_ACENTO2
            ),

            (
                self._evento_cofre_bioma(),
                None,
                self.COLOR_ORO
            )
        ]

        msg, efecto, color = random.choice(eventos)

        self._escribir_narrativa(f"\n{msg}", color)

        # EVENTO NORMAL
        if efecto:
            efecto(self.jugador)

        # EVENTO DE COFRE
        else:

            self.cofre_actual = random.choice([
                CofreComun(),
                CofreRaro(),
                CofreLegendario(),
                CofreMaldito()
            ])

            self._escribir_narrativa(
                f"\n🧰 Has descubierto un {self.cofre_actual.nombre}.",
                self.COLOR_ORO
            )

            self._escribir_narrativa(
                "⚒ Antiguos sellos rúnicos bloquean la cerradura.",
                self.COLOR_ACENTO
            )

            self._escribir_narrativa(
                "La energía del cofre reacciona a tu presencia.",
                self.COLOR_MUTED
            )

            self._escribir_narrativa(
                "Debes forjar una runa ancestral para romper el sello.",
                self.COLOR_TEXTO
            )

    def _evento_cofre_bioma(self):
        """
        Genera narrativa contextual según el bioma actual.
        """

        bioma = self.jugador.bioma_actual

        eventos = {

            "Minas de Cristal":
                "💎 Entre cristales azules encuentras un cofre cubierto de polvo.\n"
                "Runas antiguas recorren lentamente su superficie.",

            "Bosque Hexagonal":
                "🌲 Las raíces geométricas rodean un extraño cofre enterrado.\n"
                "La naturaleza parece protegerlo.",

            "Abismo Magnético":
                "⚡ Un cofre suspendido flota entre fragmentos metálicos.\n"
                "El sello rúnico vibra violentamente.",

            "Ruinas de Etherion":
                "🏛 Antiguos mecanismos reaccionan al acercarte.\n"
                "Un cofre olvidado emerge entre las ruinas.",

            "Cavernas de Ceniza":
                "🔥 El calor revela un cofre ennegrecido por magma.\n"
                "La cerradura emite energía inestable.",

            "Templo del Núcleo":
                "🌟 El templo responde a tu presencia.\n"
                "Un cofre ancestral descansa frente al altar."
        }

        return eventos.get(
            bioma,
            "🎁 Encuentras un misterioso cofre sellado."
        )
    
    # ─────────────────────────────────────────
    #  ACCIÓN: ABRIR COFRE
    # ─────────────────────────────────────────
    def _abrir_cofre(self):
        if not self._verificar_jugador_vivo():
            return

        # Selección aleatoria ponderada de cofre
        pesos = [50, 30, 10, 10]
        tipo = random.choices(
            [CofreComun, CofreRaro, CofreLegendario, CofreMaldito],
            weights=pesos, k=1
        )[0]
        cofre: Cofre = tipo()

        self._sep_narrativa()
        self._escribir_narrativa(
            f"🎁 ¡Encontraste un {cofre.nombre}! [{cofre.rareza}]",
            self._color_rareza(cofre.rareza)
        )

        try:
            self.jugador.gastar_energia(20)
            mensaje, puntos = cofre.abrir(self.jugador)
            self.jugador.ganar_puntos(puntos)
            self.audio.reproducir("cofre")
            self._escribir_narrativa(mensaje, self.COLOR_TEXTO)
            self._escribir_narrativa(
                f"   ⭐ +{puntos} puntos de expedición.",
                self.COLOR_ACENTO2
            )

        except EnergiaInsuficienteError as e:
            self._escribir_narrativa(str(e), self.COLOR_PELIGRO)

        self._actualizar_hud()
        self._verificar_meta()

    def _color_rareza(self, rareza: str) -> str:
        mapa = {
            "COMÚN":     self.COLOR_TEXTO,
            "RARO":      self.COLOR_ACENTO,
            "LEGENDARIO":self.COLOR_ORO,
            "MALDITO":   self.COLOR_PELIGRO,
        }
        return mapa.get(rareza, self.COLOR_TEXTO)

    # ─────────────────────────────────────────
    #  ACCIÓN: VER MOCHILA
    # ─────────────────────────────────────────
    def _ver_mochila(self):
        self._sep_narrativa()
        self._escribir_narrativa("🎒 MOCHILA DE EXPEDICIÓN:", self.COLOR_ACENTO)
        self._escribir_narrativa(self.jugador.inventario.mostrar(), self.COLOR_TEXTO)
        self._escribir_narrativa(
            f"   Objetos: {self.jugador.inventario.cantidad}/{Inventario.CAPACIDAD_MAXIMA}",
            self.COLOR_MUTED
        )

    # ─────────────────────────────────────────
    #  ACCIÓN: VER ESTADÍSTICAS
    # ─────────────────────────────────────────
    def _ver_estadisticas(self):
        j = self.jugador
        self._sep_narrativa()
        stats = (
            f"📊 ESTADÍSTICAS DEL CAZADOR\n\n"
            f"  Nombre   : {j.nombre}\n"
            f"  Título   : {j.titulo}\n"
            f"  Nivel    : {j.nivel}\n"
            f"  Vida     : {j.vida}/{j.vida_max}\n"
            f"  Energía  : {j.energia}/{j.energia_max}\n"
            f"  Cristales: {j.oro}\n"
            f"  Puntaje  : {j.puntos}\n"
            f"  Bioma    : {j.bioma_actual}\n"
            f"  Objetos  : {j.inventario.cantidad}\n"
        )
        self._escribir_narrativa(stats, self.COLOR_TEXTO)

    # ─────────────────────────────────────────
    #  AYUDA / TUTORIAL
    # ─────────────────────────────────────────
    def _mostrar_ayuda(self):
        self._sep_narrativa()

        tutorial = (
            "════════ TUTORIAL RUNARIO ════════\n\n"

            "⚒ FORJAR RUNA\n"
            "Escribe una runa manualmente.\n"
            "Debe contener:\n"
            "✔ Mayúscula\n"
            "✔ Minúscula\n"
            "✔ Número\n"
            "✔ Símbolo especial\n"
            

            "Ejemplo válido:\n"
            "Hexa#92Q\n\n"

            "🎲 AUTO-FORJAR\n"
            "Genera automáticamente una runa válida.\n\n"

            "🎁 COFRES SELLADOS\n"
            "Los cofres aparecen durante expediciones\n"
            "Necesitas una runa válida para romper sus sellos\n"
            "- puntos\n"
            "- cristales\n"
            "- reliquias\n\n"

            "🗺 NUEVA EXPEDICIÓN\n"
            "Explora nuevos biomas y eventos.\n\n"

            "🔄 RECUPERAR\n"
            "Restaura vida y energía usando cristales.\n\n"

            "🏆 OBJETIVO FINAL\n"
            "Consigue 500 puntos para desbloquear\n"
            "el COFRE PRIMORDIAL.\n"
        )

        self._escribir_narrativa(tutorial, self.COLOR_ACENTO)

    # ─────────────────────────────────────────
    #  ACCIÓN: RECUPERAR
    # ─────────────────────────────────────────
    def _recuperar(self):
        if self.jugador.oro < 20:
            self._sep_narrativa()
            self._escribir_narrativa(
                "⚠ No tienes suficientes cristales para recuperarte.\n"
                "  Necesitas al menos 20 cristales.",
                self.COLOR_PELIGRO
            )
            return

        self.jugador._oro = 20
        self.jugador.recuperar_vida(40)
        self.jugador.recuperar_energia(40)

        self._sep_narrativa()

        self._escribir_narrativa(
            "🔄 Usas cristales energéticos para recuperarte.\n"
            "   (-20 cristales) Vida y energía restauradas. (+40❤/⚡)",
            self.COLOR_ACENTO2
        )

        self._actualizar_hud()

    # ─────────────────────────────────────────
    #  VERIFICAR META FINAL
    # ─────────────────────────────────────────
    def _verificar_meta(self):
        """Verifica si el jugador alcanzó los puntos para el final épico."""
        if self.jugador.puntos >= self.PUNTOS_META and self._fase != "fin":
            self._fase = "fin"
            self._final_epico()

    def _final_epico(self):
        """Muestra la pantalla del final épico."""
        self.audio.reproducir("victoria")

        self._sep_narrativa()
        final = (
            "╔════════════════════════════════════════════╗\n"
            "║                                            ║\n"
            "║   ✨  COFRE PRIMORDIAL DESBLOQUEADO  ✨   ║\n"
            "║                                            ║\n"
            "║   Las runas ancestrales han reconocido     ║\n"
            "║   tu valía como Cazador de Runas.          ║\n"
            "║                                            ║\n"
            "║   La luz hexagonal llena el universo       ║\n"
            "║   de Terramine por primera vez en          ║\n"
            "║   mil eras de oscuridad.                   ║\n"
            "║                                            ║\n"
            "║   ★  ERES EL  ★                           ║\n"
            "║   MAESTRO RUNARIO SUPREMO                  ║\n"
            "║                                            ║\n"
            "╚════════════════════════════════════════════╝"
        )
        self._escribir_narrativa(final, self.COLOR_ORO)
        self._escribir_narrativa(
            f"\n  Cazador: {self.jugador.nombre}\n"
            f"  Puntaje Final: {self.jugador.puntos} pts\n"
            f"  Cristales: {self.jugador.oro}\n",
            self.COLOR_ACENTO2
        )
        self._actualizar_hud()
        
        self._escribir_narrativa(
            "\n🌌 Las antiguas puertas de Terramine se abren lentamente.\n"
            "El eco de las runas desaparece en la distancia.",
            self.COLOR_MUTED
        )

        self._escribir_narrativa(
            "\n✨ Tu legado permanecerá grabado entre los Maestros Runarios.",
            self.COLOR_ACENTO
        )

        self._escribir_narrativa(
            "\n═══ FIN DE LA EXPEDICIÓN ═══",
            self.COLOR_ORO
        )

    # ─────────────────────────────────────────
    #  VERIFICAR JUGADOR VIVO
    # ─────────────────────────────────────────
    def _verificar_jugador_vivo(self) -> bool:
        if not self.jugador.esta_vivo():
            self.audio.reproducir("derrota")
            self._sep_narrativa()
            self._escribir_narrativa(
                "💀 Has caído en las profundidades de Terramine.\n"
                "   Tu energía vital se agotó.\n"
                "   Usa RECUPERAR o reinicia el juego.",
                self.COLOR_PELIGRO
            )
            return False
        return True

    # ─────────────────────────────────────────
    #  SALIR
    # ─────────────────────────────────────────
    def _salir(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Salir de Terramine")
        ventana.configure(bg=self.COLOR_BG)
        ventana.geometry("360x180")
        ventana.resizable(False, False)
        ventana.grab_set()

        tk.Label(
            ventana,
            text="¿Abandonar la expedición?",
            bg=self.COLOR_BG, fg=self.COLOR_TEXTO,
            font=self.font_subtit
        ).pack(pady=30)

        frame_btns = tk.Frame(ventana, bg=self.COLOR_BG)
        frame_btns.pack()

        self._boton(frame_btns, "Sí, salir", self.root.destroy,
                    color=self.COLOR_PELIGRO).pack(side="left", padx=10, ipadx=10, ipady=6)
        self._boton(frame_btns, "Continuar", ventana.destroy,
                    color=self.COLOR_ACENTO2).pack(side="left", padx=10, ipadx=10, ipady=6)

    # ─────────────────────────────────────────
    #  UTILIDAD: LIMPIAR VENTANA
    # ─────────────────────────────────────────
    def _limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Reset grid
        for i in range(5):
            self.root.columnconfigure(i, weight=0)
        for i in range(5):
            self.root.rowconfigure(i, weight=0)


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    app = TerramineApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()