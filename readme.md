Flamas em Python
----------------

Exemplo de como acelerar Python para gerar imagens.
Implementa um gerador de imagens que pode ser configurado na linha de comando.


Testado com Python 3.8, deve funcionar em versões recentes de Python.
Para instalar, em um novo ambiente virtual:
```
pip install -r requirements.txt
```
Você precisa ter um ambiente de desenvolvimento com compilador C para instalar todas as dependências.

Compile o módulo em Cython:
```
python setup.py build_ext --inplace
```

Uso:
```
python desenha.py <algoritmo> <acelerador> <largura> <altura>
```
Onde:

Algoritmo: desenho, flamas

Acelerador: cython, python, numba

Exemplo:

Desenho de flamas, usando cython como acelerador:
```
python desenha.py flamas cython 1024 1024
```

Desenho simples, usando numba como acelerador:
```
python desenha.py flamas cython 1024 1024
```

Caso seu computador seja muito rápido ou muito lento, ajuste o tamanho da imagem.


Artigo sobre a construção deste código:
https://blog.nilo.pro.br/posts/2020-05-24-efeitos-graficos-com-python-cython-e-numba/