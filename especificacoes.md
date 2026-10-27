# especificações do sistema web

## 1. Visão Geral do Projeto
 O sistena é uma plataforma web local para moradores de residencia universitaria, que vai ter algumas aplicações que facilitam o dia-a-dia dos moradores, servindo como:
* - um mural de avisos digitais para eventuais acontecimentos da própria residencia (administrado somente por estudantes de jornalismo).
* - Uma interface para imprimir em uma impressora compartilhada que, ao ser realizado o pagamento, a impressora imprime automaticamente.
* - uma página para os vendedores publicarem seus itens e serem contatados pelo whatsapp com mais facilidade.
* - Fotos dos residentes
* - Albuns de fotos da residencia
* - futuras novas adições
## 2. Stack Tecnológica
* **Backend:** Python com framework Django.
* **Banco de Dados:** PostgreSQL.
* **Frontend:** HTML, CSS e templates do Django (sem frameworks complexos de JS no momento).
* **Infraestrutura/Hospedagem:** Servidor local rodando em máquina própria (500GB HD/SSD, RAM DDR3) conectada à rede da residência.

## 3. Design e Interface (UI/UX)
* **Referência Visual:** Protótipo aprovado no Canva (https://classificadosdaresi.my.canva.site/).
* **Identidade Visual:** Utilizar as cores oficiais da UFRN e da Residência, além da logomarca pré-definida no protótipo.

## 4. Atores e Permissões
* **Usuario comum (visitante não autenticado)** 
 * Pode acessar a página inicial, ler as noticias; acessar a lojinha virtual, pegar o contato do vendedor e outros(futuro).
 * Pode acessar a página da impressora para consultar e saber dos valores (não pode imprimir nem enviar arquivos)
 * **Estudante (usuário autenticado):** 
  * Pode usar a impressora
  * votar e comentar em posts (não implementado ainda)
  * Solicitar seu item na lojinha virtual
 * **Administradores (Estudante com permissões extras):**
  * Pode fazer login no painel administrativo oculto (/admin)
  * Vai poder aceitar itens novos na lojinha virtual
  * Adicionar ou remover as noticias (somente as próprias permissões)
  * Gerencias posts(fotos, noticias, etc)
  * adicionar ou remover fotos
  * Mudar o status da impressora (funcionando/em manutenção)
  
## 5. Requisitos funcionais
  * Qualquer usuário deve ser capaz de acessar as noticias e visualiza-las
  * O estudante deve ser capaz de entrar na página para imprimir -> inserir o(s) arquivo(s)
  * Sistema deve receber a solicitação de impressão de estudante e retornar um QRCODE para realizar o pagamento(tenho o cartão para realizar automaticamente
   * O sistema após receber o pagamento enviar a impressão para a impressora, caso contrario retorna um erro de inatividade(10 minutos). 
## 6. Estrutura de URLs (Rotas)
* `/` -> Página Inicial (resumo das Notícias).
* `/noticia/<id>` -> Página de leitura de uma notícia específica.
* `/impressora` -> Página de interface da impressora compartilhada.
* `/impressora/imprimir` -> página de inserir documentos e realizar o pagamento 
* `/admin` -> Painel de controle nativo do Django para administradores.

## 6. Regras técnicas
* Backend em Django, Banco PostgreSQL, sem frameworks de JavaScript no frontend, cores da UFRN.

1. Onde vamos guardar os novos ingredientes? (Banco de Dados)
Na sua versão, você acabou removendo a seção de "Modelagem de Dados". O banco de dados é a "despensa" do nosso sistema. O Django precisa saber exatamente quais prateleiras criar no PostgreSQL.

Exemplo Base: Para a Notícia, sabemos que precisamos de uma prateleira para o titulo, conteudo, data e autor.

Pergunta para você ajustar o fogo: O que precisamos guardar no banco de dados para a Lojinha e para o Álbum de Fotos? (Ex: Um item da lojinha precisa de Nome, Preço, Foto e Telefone do vendedor?)

2. O caminho até as novas mesas (Estrutura de URLs)
Na sua seção 6, você mapeou muito bem as rotas das notícias e da impressora (/, /impressora, etc.). Mas, se o visitante quiser ver a lojinha ou as fotos, ele digita o que no navegador?

Pergunta para você ajustar o fogo: Quais serão as URLs (rotas) para acessar a Lojinha e os Álbuns de fotos?

3. O tempo de cozimento do pagamento (Lógica da Impressora)
Esse é o ponto mais complexo da sua especificação técnica. Você colocou no Requisito Funcional: "O sistema após receber o pagamento enviar a impressão [...] retorna um erro de inatividade (10 minutos)".

A Lógica Base: O Django (e a web em geral) funciona com requisições rápidas: você clica, ele carrega a tela e encerra o trabalho. Ficar "esperando 10 minutos" checando se um pagamento caiu exige um mecanismo de "tarefas em segundo plano" (como um cronjob no Linux ou uma biblioteca chamada Celery), além de uma comunicação com a API de algum banco/gateway de pagamento (tipo MercadoPago, Asaas ou Stripe) para gerar o QR Code do PIX e verificar o status.

Pergunta para você ajustar o fogo: Como você pretende que o site saiba que o pagamento caiu? Você planeja integrar uma API de PIX real desde o primeiro dia, ou para a "versão 1.0" seria melhor algo mais simples (ex: o usuário faz o PIX pro administrador, e o administrador clica num botão "Liberar Impressão")?
