# Comparador de Imagens com Visão Computacional

Este é um aplicativo de desktop em Python que utiliza **OpenCV** e **Tkinter** para analisar duas imagens, detectar se elas se referem ao mesmo local (mesmo sob diferentes ângulos e iluminação) e traçar as linhas de correspondência entre elas.

O projeto implementa um pipeline robusto de detecção e filtragem de características, incluindo os algoritmos **ORB**, **Lowe's Ratio Test** e **RANSAC**, para garantir que apenas correspondências geometricamente válidas sejam exibidas.

## Tela do Aplicativo

*(Aqui você pode adicionar um print da tela do seu aplicativo em funcionamento)*

`[Imagem do seu aplicativo mostrando a GUI com uma imagem de resultado]`

## Funcionalidades Principais

  * **Interface Gráfica (GUI):** Uma janela de aplicativo simples e intuitiva construída com Tkinter.
  * **Seleção Interativa:** Botões para o usuário selecionar as duas imagens de comparação diretamente do seu computador.
  * **Detecção de Características (ORB):** Utiliza o algoritmo ORB (Oriented FAST and Rotated BRIEF) para encontrar milhares de pontos de interesse (keypoints) em ambas as imagens.
  * **Filtragem Robusta (RANSAC):** Emprega o "Lowe's Ratio Test" e o "RANSAC" para filtrar "falsos positivos" e encontrar apenas o conjunto de correspondências que é geometricamente consistente.
  * **Visualização de Resultados:** Exibe a imagem de resultado (com as linhas de correspondência) diretamente na janela do aplicativo.
  * **Salvamento Automático:** Salva automaticamente a imagem de resultado em alta resolução na pasta `/resultados/`.

## Pré-requisitos

Este projeto foi desenvolvido em Python 3.x. Para funcionar, você precisará das seguintes bibliotecas:

  * **opencv-python:** Para todas as operações de visão computacional (ORB, RANSAC, etc.).
  * **numpy:** A biblioteca base para cálculos numéricos (normalmente instalada com o OpenCV).
  * **pillow (PIL):** Usada para converter a imagem do formato OpenCV (NumPy) para um formato que o Tkinter possa exibir.

## Como Executar

Siga estes passos para rodar o projeto em sua máquina local:

1.  **Clone o repositório:**
    https://github.com/GustavoStorch/compara_imagem.git.

2.  **Instale as Dependências:**
    Abra seu terminal ou prompt de comando e instale as bibliotecas necessárias:

    ```bash
    pip install opencv-python pillow numpy
    ```

3.  **Execute o Script:**
    Navegue até a pasta onde você salvou o arquivo e execute-o:

    ```bash
    python main.py
    ```

4.  **Use o Aplicativo:**

      * A janela do aplicativo será aberta.
      * Clique em **"Selecionar Imagem 1"** e escolha a primeira imagem.
      * Clique em **"Selecionar Imagem 2"** e escolha a segunda imagem.
      * Clique no botão verde **"COMPARAR IMAGENS"**.

5.  **Veja os Resultados:**

      * Aguarde alguns segundos. O processamento pode levar um tempo, dependendo da quantidade de características.
      * A imagem de resultado com as linhas de correspondência aparecerá na parte inferior da janela.
      * Uma cópia em alta resolução será salva automaticamente como `resultados/resultado_comparacao.png`.

## Como Funciona (O Pipeline)

Este não é um simples comparador de pixels. O processo para "decidir" se as imagens são iguais é sofisticado:

1.  **Carregamento:** As duas imagens selecionadas são carregadas em escala de cinza (para detecção) e em cores (para exibição).
2.  **Detecção de Pontos (ORB):** O `cv2.ORB_create(nfeatures=10000)` encontra até 10.000 "pontos de interesse" (como cantos, texturas e bordas) em cada imagem.
3.  **Criação de Descritores (ORB):** Para cada ponto, o ORB cria uma "impressão digital" (um vetor descritor) que descreve matematicamente a aparência daquela região.
4.  **Combinação (Matcher):** O `BFMatcher` (Brute-Force Matcher) com `knnMatch(k=2)` compara cada "impressão digital" da Imagem 1 com todas as da Imagem 2, encontrando os 2 pares mais próximos.
5.  **Filtro 1 (Lowe's Ratio Test):** O código descarta combinações "ambíguas" — onde a melhor combinação não é significativamente melhor do que a segunda melhor. Isso elimina muitos falsos positivos.
6.  **Filtro 2 (RANSAC):** Este é o filtro mais importante. O `cv2.findHomography` com `RANSAC` tenta encontrar um único "modelo geométrico" (como rotação, translação, perspectiva) que se aplique a *todas* as correspondências do Filtro 1.
      * As correspondências que se encaixam nesse modelo são chamadas de **"inliers"** (corretas).
      * As correspondências que não se encaixam (como a "janela-porta" que vimos) são classificadas como **"outliers"** e são descartadas.
7.  **Decisão:** Se o número de "inliers" for maior que o nosso mínimo (`MIN_INLIER_MATCHES`), o aplicativo conclui que as imagens são do **mesmo local**.
8.  **Renderização:** A imagem final é desenhada mostrando apenas as linhas dos "inliers" (em verde) e é exibida no Tkinter e salva no disco.
