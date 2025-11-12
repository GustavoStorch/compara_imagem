import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os  

def comparar_imagens_cv(path1, path2):
    RATIO_TEST_THRESHOLD = 0.85 
    MIN_INLIER_MATCHES = 10
    try:
        img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)
        
        img1_color = cv2.imread(path1)
        img2_color = cv2.imread(path2)

        if img1 is None or img2 is None:
            raise IOError("Não foi possível ler as imagens.")
            
    except Exception as e:
        messagebox.showerror("Erro ao Carregar Imagem", f"Não foi possível ler os arquivos: {e}")
        return None

    # Detectar pontos (ORB)
    orb = cv2.ORB_create(nfeatures=10000) 
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # Combinar pontos (Matcher)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
        print("\nResultado: Não há pontos de interesse suficientes.")
        return cv2.drawMatches(img1_color, kp1, img2_color, kp2, [], None)

    matches = bf.knnMatch(des1, des2, k=2)

    # Filtro 1: Ratio Test
    good_matches = []
    if matches and all(len(m) == 2 for m in matches):
        for m, n in matches:
            if m.distance < RATIO_TEST_THRESHOLD * n.distance:
                good_matches.append(m)
    else:
        print("Aviso: knnMatch não retornou pares k=2.")

    print(f"Combinações 'boas' após Ratio Test: {len(good_matches)}")

    # Filtro 2: RANSAC
    if len(good_matches) > MIN_INLIER_MATCHES:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1, 1, 2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if mask is not None:
            matchesMask = mask.ravel().tolist()
            num_inliers = np.sum(matchesMask)
            print(f"Combinações 'inliers' (RANSAC): {int(num_inliers)}")

            if num_inliers > MIN_INLIER_MATCHES:
                print(f"\nResultado: MESMO local.")
                draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, matchesMask=matchesMask, flags=2)
                img_matches = cv2.drawMatches(img1_color, kp1, img2_color, kp2, good_matches, None, **draw_params)
            else:
                print(f"\nResultado: Locais DIFERENTES (poucos inliers).")
                img_matches = cv2.drawMatches(img1_color, kp1, img2_color, kp2, [], None)
        else:
            print(f"\nResultado: RANSAC falhou.")
            img_matches = cv2.drawMatches(img1_color, kp1, img2_color, kp2, [], None) 
    else:
        print(f"\nResultado: Locais DIFERENTES (poucos good_matches).")
        img_matches = cv2.drawMatches(img1_color, kp1, img2_color, kp2, [], None) 
    
    return img_matches

img1_path = ""
img2_path = ""

def selecionar_img1():
    global img1_path
    path = filedialog.askopenfilename(
        title="Selecione a Imagem 1",
        filetypes=[("Arquivos de Imagem", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    if path:
        img1_path = path
        lbl_img1.config(text=f"Img 1: {path.split('/')[-1]}", fg="green")

def selecionar_img2():
    global img2_path
    path = filedialog.askopenfilename(
        title="Selecione a Imagem 2",
        filetypes=[("Arquivos de Imagem", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    if path:
        img2_path = path
        lbl_img2.config(text=f"Img 2: {path.split('/')[-1]}", fg="green")

def iniciar_comparacao():
    if not img1_path or not img2_path:
        messagebox.showwarning("Imagens Faltando", "Por favor, selecione as duas imagens antes de comparar.")
        return

    lbl_status.config(text="Comparando... Por favor, aguarde.", fg="blue")
    root.update_idletasks()

    img_resultado_cv = comparar_imagens_cv(img1_path, img2_path)
    
    if img_resultado_cv is None:
        lbl_status.config(text="Erro no processamento.", fg="red")
        return

    try:
        PASTA_SAIDA = 'resultados'
        if not os.path.exists(PASTA_SAIDA):
            os.makedirs(PASTA_SAIDA)
        
        ARQUIVO_SAIDA = os.path.join(PASTA_SAIDA, 'resultado_comparacao.png')
        
        cv2.imwrite(ARQUIVO_SAIDA, img_resultado_cv)
        print(f"Imagem de resultado salva em: {ARQUIVO_SAIDA}")
        
        lbl_status.config(text=f"Comparação Concluída! Salvo em {ARQUIVO_SAIDA}", fg="green")

    except Exception as e:
        messagebox.showwarning("Erro ao Salvar", f"Não foi possível salvar a imagem em '{ARQUIVO_SAIDA}'.\nErro: {e}")
        lbl_status.config(text="Comparação Concluída! (Falha ao salvar)", fg="orange")

    max_largura = 1200
    h, w = img_resultado_cv.shape[:2]
    if w > max_largura:
        ratio = max_largura / w
        nova_altura = int(h * ratio)
        img_redimensionada = cv2.resize(img_resultado_cv, (max_largura, nova_altura), interpolation=cv2.INTER_AREA)
    else:
        img_redimensionada = img_resultado_cv

    img_rgb = cv2.cvtColor(img_redimensionada, cv2.COLOR_BGR2RGB)
    
    pil_image = Image.fromarray(img_rgb)
    
    tk_image = ImageTk.PhotoImage(pil_image)

    lbl_resultado.config(image=tk_image)
    
    lbl_resultado.image = tk_image 
    
root = tk.Tk()
root.title("Comparador de Imagens - RANSAC/ORB")
root.geometry("1280x800") 

frame_controles = tk.Frame(root, pady=10)
frame_controles.pack()

btn_img1 = tk.Button(frame_controles, text="Selecionar Imagem 1", command=selecionar_img1, width=20)
btn_img1.pack(side=tk.LEFT, padx=10)

lbl_img1 = tk.Label(frame_controles, text="Nenhuma", fg="gray", width=30)
lbl_img1.pack(side=tk.LEFT, padx=5)

btn_img2 = tk.Button(frame_controles, text="Selecionar Imagem 2", command=selecionar_img2, width=20)
btn_img2.pack(side=tk.LEFT, padx=10)

lbl_img2 = tk.Label(frame_controles, text="Nenhuma", fg="gray", width=30)
lbl_img2.pack(side=tk.LEFT, padx=5)

frame_acao = tk.Frame(root, pady=10)
frame_acao.pack()

btn_comparar = tk.Button(
    frame_acao, 
    text="COMPARAR IMAGENS", 
    command=iniciar_comparacao, 
    font=('Helvetica', 12, 'bold'), 
    bg="#4CAF50", 
    fg="white",
    width=30,
    height=2
)
btn_comparar.pack()

lbl_status = tk.Label(root, text="Selecione duas imagens e clique em 'Comparar'", font=('Helvetica', 10, 'italic'))
lbl_status.pack(pady=5)

frame_resultado = tk.Frame(root, relief=tk.SUNKEN, borderwidth=1, bg="gray")
frame_resultado.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

lbl_resultado = tk.Label(frame_resultado, bg="gray")
lbl_resultado.pack(fill=tk.BOTH, expand=True)

root.mainloop()