# Documentação do Arquivo `level.py`

O arquivo `level.py` é responsável por definir a classe `Level`, que gerencia a configuração, o carregamento e a estrutura física de cada um dos níveis no jogo do Angry Birds. Ele cria e posiciona os porcos (`Pig`), os blocos verticais (`columns`), os blocos horizontais (`beams`) e define as pontuações necessárias para ganhar estrelas em cada fase.

---

## Estrutura da Classe `Level`

### Construtor (`__init__`)
```python
def __init__(self, pigs, columns, beams, space):
```
Inicializa um novo nível com as referências dos objetos do jogo e configura os limites de pontuação padrão:
* `pigs` (list): Lista global de porcos no jogo.
* `columns` (list): Lista global de colunas (estruturas verticais de madeira).
* `beams` (list): Lista global de vigas (estruturas horizontais de madeira).
* `space` (pymunk.Space): O espaço físico do motor Pymunk onde os objetos são simulados.
* `number` (int): Índice do nível atual (começa em `0`).
* `number_of_birds` (int): Quantidade de pássaros disponíveis para o jogador.
* `bool_space` (bool): Define se o jogo está no modo espacial (gravidade alterada e maior número de pássaros).
* **Pontuações de Estrela (`one_star`, `two_star`, `three_star`)**: Limites mínimos de pontuação para obter 1, 2 ou 3 estrelas respectivamente (padrão: 30.000, 40.000 e 60.000).

---

## Métodos Auxiliares de Construção

Para facilitar a criação dos cenários, a classe conta com métodos que geram estruturas geométricas repetitivas de madeira:

### `open_flat(x, y, n)`
Gera `n` andares de uma estrutura aberta. Cada andar consiste em duas colunas verticais separadas e uma viga horizontal em cima.
* `x`, `y`: Posição inicial no mapa.
* `n`: Número de repetições verticais da estrutura.

### `closed_flat(x, y, n)`
Gera `n` andares de uma estrutura fechada. Semelhante ao `open_flat`, mas adiciona uma viga também no chão/base de cada andar, fechando o retângulo.
* `x`, `y`: Posição inicial no mapa.
* `n`: Número de repetições verticais.

### `horizontal_pile(x, y, n)`
Empilha `n` vigas de madeira horizontalmente uma em cima da outra.
* `x`, `y`: Posição inicial da base da pilha.
* `n`: Quantidade de vigas.

### `vertical_pile(x, y, n)`
Empilha `n` colunas de madeira verticalmente uma em cima da outra.
* `x`, `y`: Posição inicial da base da pilha.
* `n`: Quantidade de colunas.

---

## Configuração do Nível (`finalize_level_setup`)

```python
def finalize_level_setup(self):
```
Método chamado ao final da construção de cada nível para padronizar as configurações de execução:
* Define `number_of_birds` como `8` (`SPACE_BIRD_COUNT`) se o modo espaço estiver ativo (`bool_space=True`), ou `4` (`NORMAL_BIRD_COUNT`) caso contrário.
* Reinicializa os thresholds de pontuação para as estrelas.

---

## Carregamento Dinâmico (`load_level`)

```python
def load_level(self):
```
Carrega a fase correspondente ao valor armazenado em `self.number`.
* Utiliza a função do Python `getattr(self, "build_" + str(self.number))` para invocar dinamicamente o método correspondente à fase (ex: `build_0`, `build_1`).
* Se o nível não existir (lançando um `AttributeError`), o jogo reinicia o contador para o nível `0` e o carrega.

---

## Níveis Implementados (`build_0` a `build_11`)

O arquivo implementa 12 fases distintas (do nível 0 ao 11), variando a disposição física dos elementos e os pontos de vida dos porcos:

| Nível | Descrição Estrutural | Elementos Principais |
| :--- | :--- | :--- |
| **0** | Estrutura básica de dois andares com vigas e colunas simples. | 2 Porcos (vida reduzida a 5), 4 colunas, 2 vigas. |
| **1** | Porco posicionado no solo com colunas e vigas simples ao lado. | 1 Porco, 4 colunas, 1 viga. |
| **2** | Estruturas separadas com porcos em alturas diferentes. | 2 Porcos, 3 colunas, 2 vigas. |
| **3** | Nível complexo com pirâmide de madeira e porcos de alta durabilidade. | 3 Porcos (vida = 25), várias colunas e vigas entrelaçadas. |
| **4** | Nível minimalista de física com foco em porcos flutuantes/suspensos. | 3 Porcos posicionados no ar. |
| **5** | Pilhas horizontais densas de madeira protegendo os porcos. | 2 Porcos, 13 vigas horizontais empilhadas, 2 colunas. |
| **6** | Estrutura vertical maciça com porcos protegidos e alta vida. | 3 Porcos (um com vida = 40), pilhas verticais e 1 estrutura fechada. |
| **7** | Porcos protegidos por uma estrutura aberta tripla e pilhas verticais paralelas. | 3 Porcos (vida = 30), 1 estrutura aberta de 3 andares, 2 pilhas verticais. |
| **8** | Escadaria de estruturas abertas (`open_flat`) de tamanhos decrescentes (3, 2, 1 andares). | 3 Porcos (vida = 30), estruturas abertas em formato de degraus. |
| **9** | Cenário simétrico com estruturas abertas nas extremidades e porcos ao centro. | 2 Porcos (vida = 20), 4 conjuntos de estruturas abertas. |
| **10** | Duas pilhas verticais altas, pilhas horizontais nas laterais e porcos bem distribuídos. | 3 Porcos (vida = 20), pilhas verticais e horizontais diversas. |
| **11** | Nível final complexo mesclando pilhas horizontais e verticais em múltiplos andares. | 4 Porcos (um com vida = 30), pilhas horizontais, verticais e 1 viga suspensa. |
