# Simulador de Índice Hash Estático

## Sobre o Projeto

Este sistema é uma aplicação desenvolvida em Python que simula o funcionamento de um índice hash estático sobre uma tabela de dados armazenada em páginas na memória[cite: 1]. O projeto tem foco educacional na disciplina de Banco de Dados, permitindo visualizar a estruturação física e lógica das informações, além de avaliar o ganho de desempenho no uso de indexação.

### Estrutura

Estrutura de diretórios.

```sh
app
├───ui # Interface gráfica do sistema
│   └───app.py
└───main.py # ponte de comunicação entre processos
```

## Executar

```sh
python main.py
```

## Funcionalidades

* **Carga de Dados:** Leitura e processamento de um arquivo de texto contendo cerca de 466 mil palavras únicas do idioma inglês[cite: 1].
* **Paginação Simulada:** Divisão dos registros em páginas de memória com tamanho definido pelo usuário[cite: 1].
* **Indexação Customizada:** Implementação de uma função hash própria (sem uso de bibliotecas nativas) para distribuir as chaves em *buckets*[cite: 1].
* **Resolução de Conflitos:** Algoritmos dedicados para tratamento de colisões e *bucket overflow* (transbordamento)[cite: 1].
* **Motor de Busca:** Comparação de tempo de execução e custo (quantidade de páginas lidas) entre a busca utilizando o Índice Hash e a busca sequencial (*Table Scan*)[cite: 1].
* **Métricas:** Cálculo e exibição de estatísticas, como taxa de colisões e taxa de overflow[cite: 1].
* **Interface Gráfica:** Visualização interativa das páginas, dos buckets e do processo de busca[cite: 1].

## Tecnologias Utilizadas

* **Linguagem:** Python 3.13
* **Interface Gráfica:** Qt com edifice e PySide6.
