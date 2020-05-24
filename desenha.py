# Autor: Nilo Ney Coutinho Menezes
# Site: https://python.nilo.pro.br
# 24 - 05 - 2020
#
# Testado com Python 3.8.0
#

import sys
import numpy
import time
import random
import tkinter as tk

from datetime import datetime
from queue import Queue
from threading import Thread
from PIL import Image, ImageTk, ImageColor
from numba import jit, vectorize

from compute import draw2, drawUp, desenhaflamas


# Explicação do Algoritmo de flamas em C
# https://lodev.org/cgtutor/fire.html

# Tamanho da imagem em pontos
LARGURA = 1024
ALTURA = 1024

# Valores mínimos e máximos para altura e largura
MIN_V = 500
MAX_V = 2048


class TimeIt:
    """Classe para medir o tempo de execução de alguns blocos.
       Deve ser usada como gerenciados de contexto, com blocks with"""
    def __init__(self, name, silent=False):
        self.name = name
        self.start = 0
        self.end = 0
        self.silent = silent

    def __enter__(self):
        self.start = datetime.now()

    def __exit__(self, *args, **kwargs):
        self.end = datetime.now()
        if not self.silent:
            segundos = self.elapsed().total_seconds()
            if segundos == 0:
                return
            fps = 1.0 / segundos
            print(f"Elapsed {self.name}: {self.elapsed()} Frames: {fps}")

    def elapsed(self):
        return self.end - self.start


def build_fire_palette():
    palette = numpy.zeros((256, 3), dtype=numpy.uint8)
    for x in range(256):
        h = x // 3
        saturation = 100
        b = min(256, x * 2) / 256.0 * 100.0
        css = f"hsl({h},{saturation}%,{b}%)"
        palette[x] = ImageColor.getrgb(css)
    return palette


@jit(nopython=True, parallel=True, fastmath=True, nogil=True)
def drawNumba(data, c, largura, altura):
    for y in numpy.arange(0, altura):
        for x in numpy.arange(0, largura):
            data[y, x] = [0, 0, y // (c + 1)]


@jit(nopython=True, parallel=True, fastmath=True, nogil=True)
def desenhaPythonFlamas(data, c, largura, altura, fogo):
    for x in range(LARGURA):
        fogo[ALTURA - 1, x] = int(min(random.random() * 2048, 2048))

    for y in range(1, ALTURA - 2):
        for x in range(0, LARGURA):
            v = int((fogo[(y + 1) % ALTURA, x] +
                     fogo[(y + 1) % ALTURA, (x - 1) % LARGURA] +
                     fogo[(y + 1) % ALTURA, (x + 1) % LARGURA] +
                     fogo[(y + 2) % ALTURA, x]) * 32) / 129
            fogo[y, x] = v
    for y in range(altura):
        for x in range(largura):
            data[y, x] = fogo[y, x] % 256


class Desenha(Thread):
    def __init__(self, queue, queueStop, func, preFunc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.queueStop = queueStop
        self.running = True
        self.func = func
        self.preFunc = preFunc or func

    def run(self):
        try:
            data = numpy.zeros((ALTURA, LARGURA, 3), dtype=numpy.uint8)
            c = 0
            with TimeIt("PreLoop") as t:
                self.preFunc(data, c, LARGURA, ALTURA)
            while self.running:
                with TimeIt("Loop") as t:
                    # with TimeIt("ForLoop") as t:
                    self.func(data, c, LARGURA, ALTURA)
                    # with TimeIt("FROM ARRAY") as t1:
                    image = Image.fromarray(data)
                    # with TimeIt("Convert") as t2:
                    converted_image = ImageTk.PhotoImage(image)
                    # with TimeIt("Queue") as t3:
                    self.queue.put((c, converted_image))
                    c += 1
        finally:
            self.running = False
            self.queueStop.put((0, 'FEITO'))

    def stop(self):
        self.running = False


class DesenhaComPalette(Desenha):
    def run(self):
        try:
            palette = build_fire_palette()
            data = numpy.zeros((ALTURA, LARGURA), dtype=numpy.uint8)
            fogo = numpy.zeros((ALTURA, LARGURA), dtype=numpy.uint32)
            c = 0
            while self.running:
                with TimeIt("Loop") as t:
                    # with TimeIt("ForLoop") as t:
                    self.func(data, c, LARGURA, ALTURA, fogo)
                    # with TimeIt("FROM ARRAY") as t1:
                    image = Image.fromarray(data, mode="P")
                    image.putpalette(palette)
                    # with TimeIt("Convert") as t2:
                    converted_image = ImageTk.PhotoImage(image)
                    # with TimeIt("Queue") as t3:
                    self.queue.put((c, converted_image))
                    c += 1
        finally:
            self.running = False
            self.queueStop.put((0, 'FEITO'))


class App(tk.Tk):
    def __init__(self, desenhador, func, preFunc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_windows()
        self.queue = Queue()
        self.queueStop = Queue()
        self.setup_thread(desenhador, func, preFunc)
        self.buffer = None
        self.running = True
        self.dead = False
        self.after(1, self.check_queue)

    def setup_windows(self):
        self.title('Gerador de Imagens')
        self.status = tk.StringVar(self, value='Aguardando')
        tk.Label(self, textvariable=self.status).pack()
        self.canvas = tk.Canvas(self, width=LARGURA, height=ALTURA)
        self.image = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.terminate)

    def setup_thread(self, desenhador, func, preFunc):
        self.desenhador = desenhador(self.queue, self.queueStop, func, preFunc)
        self.desenhador.start()

    def check_queue(self):
        if not self.queue.empty():
            contador, self.buffer = self.queue.get()
            self.status.set(f"Frame: {contador}")
            self.canvas.itemconfig(self.image, image=self.buffer)
            self.queue.task_done()
        if self.running:
            self.after(10, self.check_queue)

    def check_thread_dead(self):
        if self.queueStop.empty() and not self.dead:
            self.after(1, self.check_thread_dead)
            return
        self.queueStop.get()
        self.dead = True
        self.desenhador.join()
        self.destroy()

    def terminate(self, e=None):
        self.running = False
        if not self.dead:
            self.desenhador.stop()
            self.check_thread_dead()


if len(sys.argv) < 5:
    print("Uso: python desenha.py <algoritmo> <acelerador> <largura> <altura>")
    print("Algoritmo: desenho, flamas")
    print("Acelerador: cython, python, numba")

ALGORITMO = sys.argv[1].lower()
ACELERADOR = sys.argv[2].lower()
LARGURA = int(sys.argv[3])
ALTURA = int(sys.argv[4])

print(f"ALGORITMO: {ALGORITMO}")
print(f"ACELERADOR: {ACELERADOR}")
print(f"LARGURA: {LARGURA} ALTURA: {ALTURA}")

CONFIGURACAO = {
    "flamas": {"desenhador": DesenhaComPalette,
               "otimizacao": {"python": (desenhaPythonFlamas.py_func, None),
                              "cython": (desenhaflamas, None),
                              "numba": (desenhaPythonFlamas, None)
                              }},
    "desenho": {"desenhador": Desenha,
                "otimizacao": {"python": (drawNumba.py_func, None),
                               "cython": (drawUp, draw2),
                               "numba": (drawNumba, None)
                               }}
}

if ALGORITMO not in CONFIGURACAO:
    print(f"Algoritmo {ALGORITMO} inválido", file=sys.stderr)
    sys.exit(1)

if ACELERADOR not in CONFIGURACAO[ALGORITMO]["otimizacao"]:
    print(f"Acelerador {ACELERADOR} inválido", file=sys.stderr)
    sys.exit(2)

if ALTURA < MIN_V or LARGURA < MIN_V or ALTURA > MAX_V or LARGURA > MAX_V:
    print(f"Altura e largura devem ser valores entre {MIN_V} e {MAX_V}.")
    sys.exit(3)

desenhador = CONFIGURACAO[ALGORITMO]["desenhador"]
func = CONFIGURACAO[ALGORITMO]["otimizacao"][ACELERADOR][0]
prefunc = CONFIGURACAO[ALGORITMO]["otimizacao"][ACELERADOR][1]

app = App(desenhador=desenhador, func=func, preFunc=prefunc)
app.mainloop()
