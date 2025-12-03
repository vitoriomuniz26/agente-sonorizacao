# Importações necessárias do Flask
from flask import Flask, render_template, request, send_file, url_for
import os
import io
import uuid # Para gerar nomes de ficheiro únicos
from werkzeug.utils import secure_filename # Para segurança no nome do ficheiro
import base64 # Para descodificar a imagem desenhada

# Nossas importações para IA, planilhas e PDF
import gspread
import json
import openai
from dotenv import load_dotenv
from fpdf import FPDF
from PIL import Image

# Cria a nossa aplicação web
app = Flask(__name__)

# --- Configurações ---
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# MAX_CONTENT_LENGTH removed to allow large canvas images
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Funções Auxiliares ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- FUNÇÕES DO BACKEND (buscar_catalogo, gerar_proposta_ia) ---

def buscar_catalogo_da_planilha():
    """Se conecta à planilha do Google e retorna os produtos."""
    try:
        gc = gspread.service_account(filename='credentials.json')
        planilha = gc.open("dados-agente") 
        aba = planilha.sheet1
        produtos = aba.get_all_records()
        print("✅ Catálogo de produtos carregado da planilha.")
        return produtos
    except Exception as e:
        print(f"❌ Erro ao carregar catálogo: {e}")
        return None

# ### FUNÇÃO ATUALIZADA ###: Aceita o novo prompt estruturado
def gerar_proposta_ia(pedido_tecnico_estruturado: str, catalogo_produtos: list) -> dict:
    """Gera a proposta usando a IA da OpenAI (GPT-4o), focada em texto."""
    print("🤖 Iniciando a geração da proposta com o cérebro OpenAI...")
    try:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ Chave de API da OpenAI não encontrada.")
            return None
        
        client = openai.OpenAI(api_key=api_key)
        system_message = """
        Você é um projetista sênior de sistemas de sonorização ambiente. Sua tarefa é criar uma proposta técnica e comercial detalhada com base nos dados estruturados fornecidos.

        **Regras Estritas de Seleção de Equipamentos:**
        1.  **Produtos Obrigatórios:** SEMPRE inclua na proposta:
            - ARANDELAS (caixas de embutir no teto)
            - AMPLIFICADOR (AMP)
        
        2.  **Gerenciamento de Zonas e Amplificadores:**
            - A quantidade de zonas solicitada = quantidade de canais necessários no amplificador
            - Cada amplificador tem no máximo 4 canais/zonas
            - Se o projeto tiver mais de 4 zonas, você DEVE incluir múltiplos amplificadores
            - Exemplo: 6 zonas = 2 amplificadores (um de 4 canais + um de 2 canais, ou dois de 4 canais)
        
        3.  **Tipos de Caixas:**
            - ARANDELA = caixa de EMBUTIR (vai no teto, dentro do forro)
            - Todos os outros modelos de caixas = SOBREPOR (vão na parede)
        
        4.  **Análise do Pedido:** Analise os dados do projeto, incluindo medidas, tipo de teto, e observações. Use as medidas (comprimento x largura) para calcular a área e sugerir a quantidade de caixas.
        
        5.  **Seleção de Produtos:** Utilize estritamente os produtos do catálogo JSON fornecido. Use o nome exato do produto do catálogo, não o código.
        
        6.  **Formato da Resposta:** Sua resposta final DEVE SER APENAS um objeto JSON válido, sem texto adicional ou markdown. A estrutura do JSON deve ser exatamente esta:
            {
                "analise_projeto": "Um parágrafo explicando suas escolhas técnicas com base nos dados fornecidos, mencionando claramente quantas zonas, quantos amplificadores e por quê.",
                "itens_proposta": [
                    {
                        "produto": "Nome Exato do Produto do Catálogo",
                        "quantidade": 0,
                        "preco_unitario": 0.0,
                        "subtotal": 0.0
                    }
                ],
                "valor_total": 0.0
            }
        """
        # O 'user_content' agora recebe o pedido já estruturado
        user_content = f"""
        Base de Conhecimento (Catálogo de Produtos):
        ```json
        {json.dumps(catalogo_produtos, indent=2, ensure_ascii=False)}
        ```

        **Pedido do Técnico (Estruturado):**
        "{pedido_tecnico_estruturado}"
        """
        print("🧠 Conectando ao GPT-4o...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        print("💡 Resposta recebida da IA!")
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            proposta_texto = response.choices[0].message.content
            proposta_json = json.loads(proposta_texto)
            return proposta_json
        else:
            print("❌ A IA retornou uma resposta vazia.")
            return None
    except Exception as e:
        print(f"❌ Erro na chamada da IA (OpenAI): {e}")
        return None

# ### FUNÇÃO ATUALIZADA ###: Agora aceita a imagem desenhada
def gerar_pdf_proposta(proposta: dict, nome_cliente: str, imagem_desenhada_bytes: bytes = None) -> bytes:
    """Gera o PDF com layout profissional e planta desenhada."""
    try:
        pdf = FPDF(unit="mm")
        pdf.set_margins(20, 20, 20)
        pdf.set_auto_page_break(True, margin=20)
        brand_r, brand_g, brand_b = 124, 58, 237

        pdf.add_page()

        logo_path = os.path.join('static', 'audioagorasonorização+-640w (2).png')
        logo_w = 65
        page_width = pdf.w
        x_logo = (page_width - logo_w) / 2
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=x_logo, y=20, w=logo_w)
            pdf.set_y(20 + (logo_w * 0.35) + 30)
        else:
            pdf.set_y(20)

        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(brand_r, brand_g, brand_b)
        pdf.cell(0, 10, "Proposta de Sonorização Ambiente", 0, 1, "C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(245, 247, 251)
        pdf.set_draw_color(220, 224, 229)
        start_y = pdf.get_y() + 2
        pdf.cell(0, 10, "Dados do Cliente", 0, 1)
        grid_y = start_y + 12
        x = pdf.l_margin
        content_w = page_width - pdf.l_margin - pdf.r_margin
        gap = 4
        col_w = (content_w - gap) / 2
        box_h = 18
        pdf.set_font("Arial", "", 11)
        nome = str(proposta.get('nome_cliente', nome_cliente))
        doc = str(proposta.get('documento_cliente', ''))
        end = str(proposta.get('endereco_cliente', ''))
        pdf.rect(x, grid_y, col_w, box_h)
        pdf.set_xy(x + 2, grid_y + 3)
        pdf.multi_cell(col_w - 4, 6, f"Nome\n{nome}")
        right_x = x + col_w + gap
        pdf.rect(right_x, grid_y, col_w, box_h)
        pdf.set_xy(right_x + 2, grid_y + 3)
        pdf.multi_cell(col_w - 4, 6, f"CPF/CNPJ\n{doc}")
        row2_y = grid_y + box_h + gap
        pdf.rect(x, row2_y, content_w, box_h)
        pdf.set_xy(x + 2, row2_y + 3)
        pdf.multi_cell(content_w - 4, 6, f"Endereço\n{end}")
        pdf.set_y(row2_y + box_h + 8)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Resumo do Projeto", 0, 1)
        pdf.set_font("Arial", "", 11)
        analise = str(proposta.get('analise_projeto', ''))
        content_w = page_width - pdf.l_margin - pdf.r_margin
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(content_w, 6, analise)
        pdf.ln(2)

        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(brand_r, brand_g, brand_b)
        pdf.cell(0, 8, "Itens da Proposta", 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 11)
        table_w = page_width - pdf.l_margin - pdf.r_margin
        prod_w = round(table_w * 0.54, 2)
        qty_w = round(table_w * 0.10, 2)
        price_w = round(table_w * 0.18, 2)
        sub_w = round(table_w - (prod_w + qty_w + price_w), 2)
        pdf.set_x(pdf.l_margin)
        pdf.cell(prod_w, 8, "Produto", 1, 0, "C")
        pdf.cell(qty_w, 8, "Qtd", 1, 0, "C")
        pdf.cell(price_w, 8, "Preço Unit.", 1, 0, "C")
        pdf.cell(sub_w, 8, "Subtotal", 1, 1, "C")
        pdf.set_font("Arial", "", 11)
        for item in proposta.get('itens_proposta', []):
            produto = str(item.get('produto', 'N/A'))
            quantidade = str(item.get('quantidade', 0))
            preco_unit = f"R$ {item.get('preco_unitario', 0.0):.2f}"
            subtotal = f"R$ {item.get('subtotal', 0.0):.2f}"
            pdf.set_x(pdf.l_margin)
            pdf.cell(prod_w, 8, produto, 1, 0)
            pdf.cell(qty_w, 8, quantidade, 1, 0, "C")
            pdf.cell(price_w, 8, preco_unit, 1, 0, "R")
            pdf.cell(sub_w, 8, subtotal, 1, 1, "R")

        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(240, 240, 255)
        total_label_w = prod_w + qty_w + price_w
        total_value_w = sub_w
        pdf.set_x(pdf.l_margin)
        pdf.cell(total_label_w, 8, "Total dos Itens", 1, 0, 'L')
        pdf.cell(total_value_w, 8, f"R$ {proposta.get('valor_total_itens', 0.0):.2f}", 1, 1, "R")
        pdf.set_x(pdf.l_margin)
        pdf.cell(total_label_w, 8, "Integração do Sistema", 1, 0, 'L')
        pdf.cell(total_value_w, 8, f"R$ {proposta.get('valor_integracao', 0.0):.2f}", 1, 1, "R")
        pdf.set_x(pdf.l_margin)
        pdf.cell(total_label_w, 10, "Total Geral", 1, 0, 'L')
        pdf.cell(total_value_w, 10, f"R$ {proposta.get('valor_total', 0.0):.2f}", 1, 1, "R")

        pdf.ln(6)

        if imagem_desenhada_bytes:
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.set_text_color(brand_r, brand_g, brand_b)
            pdf.cell(0, 10, "Planta do Ambiente com Posicionamento", 0, 1, "C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(6)
            try:
                pdf.image(io.BytesIO(imagem_desenhada_bytes), x=20, y=pdf.get_y(), w=page_width - 40, type='PNG')
            except Exception:
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, "Erro ao processar a imagem da planta desenhada.", 0, 1)

        return pdf.output()
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return None

# --- ROTAS DA APLICAÇÃO WEB ---

@app.route('/')
def homepage():
    """Renderiza a página inicial com o formulário."""
    return render_template('index.html')

# ### ROTA ATUALIZADA ###: Apanha os novos campos do formulário
@app.route('/gerar_proposta', methods=['POST'])
def rota_gerar_proposta():
    """
    PASSO 1: Recebe o briefing estruturado, guarda a imagem, chama a IA
    e exibe a página de revisão.
    """
    print("PASSO 1: Recebida requisição inicial...")
    
    # --- Apanha TODOS os novos dados do formulário ---
    nome_cliente = request.form.get('nome_cliente')
    documento_cliente = request.form.get('documento_cliente', 'Não informado')
    endereco_cliente = request.form.get('endereco_cliente', 'Não informado')
    
    comprimento = request.form.get('comprimento', 'Não informado')
    largura = request.form.get('largura', 'Não informado')
    altura = request.form.get('altura', 'Não informado')
    
    tipo_teto = request.form.get('tipo_teto')
    tipo_caixa = request.form.get('tipo_caixa')
    zonas = request.form.get('zonas', '1')
    
    observacoes = request.form.get('observacoes', 'Nenhuma')

    # --- Constrói o "Super-Prompt" para a IA ---
    pedido_tecnico_estruturado = f"""
    **Dados do Cliente:**
    - Nome: {nome_cliente}
    - Documento (CPF/CNPJ): {documento_cliente}
    - Endereço: {endereco_cliente}

    **Detalhes do Ambiente Principal:**
    - Comprimento: {comprimento} metros
    - Largura: {largura} metros
    - Altura (Pé-direito): {altura} metros
    - Tipo de Teto: {tipo_teto}
    - Tipo de Caixas Desejado: {tipo_caixa}
    - Quantidade de Zonas de Áudio: {zonas}

    **Observações Adicionais do Técnico:**
    {observacoes}
    """

    # --- Lógica de Upload da Imagem (Não muda) ---
    imagem_planta_url = None
    if 'planta_imagem' in request.files:
        ficheiro = request.files['planta_imagem']
        if ficheiro and ficheiro.filename != '' and allowed_file(ficheiro.filename):
            try:
                extensao = ficheiro.filename.rsplit('.', 1)[1].lower()
                nome_seguro = secure_filename(f"{uuid.uuid4()}.{extensao}")
                caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
                
                imagem = Image.open(ficheiro.stream)
                imagem.save(caminho_salvar)
                
                imagem_planta_url = url_for('static', filename=f'uploads/{nome_seguro}')
                print(f"🖼️ Imagem da planta guardada em: {caminho_salvar}")
            except Exception as e:
                print(f"⚠️ Erro ao processar ou guardar a imagem: {e}")
                
    catalogo = buscar_catalogo_da_planilha()
    if not catalogo:
        return "Erro: Não foi possível carregar o catálogo.", 500

    # --- Passa o novo "super-prompt" para a IA ---
    proposta_sugerida = gerar_proposta_ia(pedido_tecnico_estruturado, catalogo)
    if not proposta_sugerida:
        return "Erro: A IA não conseguiu gerar uma proposta.", 500
    
    print("✅ Proposta da IA recebida. A exibir página de revisão...")
    return render_template('review.html', 
                           nome_cliente=nome_cliente, 
                           proposta=proposta_sugerida, 
                           catalogo_completo=catalogo,
                           imagem_planta_url=imagem_planta_url,
                           documento_cliente=documento_cliente,
                           endereco_cliente=endereco_cliente,
                           comprimento=comprimento,
                           largura=largura,
                           altura=altura,
                           tipo_teto=tipo_teto,
                           tipo_caixa=tipo_caixa,
                           zonas=zonas,
                           observacoes=observacoes)


@app.route('/criar_pdf', methods=['POST'])
def rota_criar_pdf():
    """
    Passo 2: Recebe os dados editados E a imagem desenhada, e gera o PDF final.
    """
    print("PASSO 2: Recebidos dados editados para gerar PDF final...")
    proposta_final = {}
    proposta_final['nome_cliente'] = request.form.get('nome_cliente')
    proposta_final['documento_cliente'] = request.form.get('documento_cliente')
    proposta_final['endereco_cliente'] = request.form.get('endereco_cliente')
    proposta_final['comprimento'] = request.form.get('comprimento')
    proposta_final['largura'] = request.form.get('largura')
    proposta_final['altura'] = request.form.get('altura')
    proposta_final['tipo_teto'] = request.form.get('tipo_teto')
    proposta_final['tipo_caixa'] = request.form.get('tipo_caixa')
    proposta_final['zonas'] = request.form.get('zonas')
    proposta_final['observacoes'] = request.form.get('observacoes')
    proposta_final['analise_projeto'] = request.form.get('analise_projeto')
    from decimal import Decimal, ROUND_HALF_UP
    itens = []
    valor_total_calculado = Decimal('0.00')
    produtos = request.form.getlist('produto')
    quantidades = request.form.getlist('quantidade')
    precos = request.form.getlist('preco_unitario')
    
    for i in range(len(produtos)):
        try:
            quantidade = int(quantidades[i])
            preco = Decimal(precos[i] or '0').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            subtotal = (Decimal(quantidade) * preco).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            itens.append({
                "produto": produtos[i],
                "quantidade": quantidade,
                "preco_unitario": float(preco),
                "subtotal": float(subtotal)
            })
            valor_total_calculado = (valor_total_calculado + subtotal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except (ValueError, IndexError):
            continue
            
    proposta_final['itens_proposta'] = itens
    proposta_final['valor_total_itens'] = float(valor_total_calculado)
    try:
        valor_integracao_dec = Decimal(str(request.form.get('valor_integracao') or '0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception:
        valor_integracao_dec = Decimal('0.00')
    proposta_final['valor_integracao'] = float(valor_integracao_dec)
    total_geral = (valor_total_calculado + valor_integracao_dec).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    proposta_final['valor_total'] = float(total_geral)

    # --- LÓGICA PARA RECEBER A IMAGEM DESENHADA ---
    imagem_desenhada_bytes = None
    imagem_base64 = request.form.get('imagem_desenhada')
    
    if imagem_base64:
        try:
            dados_imagem = imagem_base64.split(',')[1]
            imagem_desenhada_bytes = base64.b64decode(dados_imagem)
            print("🖼️ Imagem desenhada recebida e descodificada com sucesso.")
        except Exception as e:
            print(f"⚠️ Erro ao descodificar a imagem desenhada: {e}")

    pdf_bytes = gerar_pdf_proposta(proposta_final, proposta_final['nome_cliente'], imagem_desenhada_bytes) 
    if not pdf_bytes:
        return "Erro: Não foi possível gerar o arquivo PDF final.", 500
        
    print(f"✅ PDF final para '{proposta_final['nome_cliente']}' gerado com sucesso! Enviando...")
    nome_arquivo = f"proposta_{proposta_final['nome_cliente'].replace(' ', '_').lower()}.pdf"
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=False,
        download_name=nome_arquivo
    )

if __name__ == '__main__':
    app.run(debug=True)