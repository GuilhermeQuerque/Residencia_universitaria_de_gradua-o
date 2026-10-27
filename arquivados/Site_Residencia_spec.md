# Site da residencia universitaria
O site visa atualizar os residentes sobre acontecimentos, facilitar comunicações entre vendedores e compradores, oferecer outros servicos que os residentes possam estar precisando atualmente, como votação(DCE, Reitor, etc), requisisão de autorização, requisisão para coisas futuras

Residência Universitária de Graduação da UFRN (Campus III / Campus Central) é um complexo de assistência estudantil da PROAE localizado em Natal/RN, composto por alojamentos coletivos e áreas comuns (salas de estudo, cozinha, lavanderia e convivência) regidos por normas estritas de acesso e convivência. Para a especificação técnica (Spec) do site e sistema de gestão da residência, a plataforma deve ser estruturada em torno dos seguintes requisitos essenciais:

Perfis de Acesso (RBAC): Controle de permissões dividido entre Moradores (solicitações e cadastros), Administração/Conselho da Residência (aprovações, avisos e relatórios) e Portaria/Segurança (leitura e validação rápida de entrada e saída).

Módulo de Controle de Visitantes: Fluxo digital para solicitação e emissão de autorizações de visita.

Gestão de Espaços e Infraestrutura: Sistema para agendamento de uso de equipamentos compartilhados (como máquinas da lavanderia), escala de limpeza e abertura de chamados de manutenção predial ou de rede para os quartos e blocos.

Comunicação e Transparência: Mural digital para publicação de atas de assembleias, avisos da PROAE, consulta ao regimento interno e repositório de documentos/planilhas da gestão.

Requisitos Não-Funcionais e Infraestrutura: Interface mobile-first (responsiva para uso fácil pelos moradores no celular e pela portaria), conformidade com a LGPD (proteção de dados sensíveis e documentos de moradores e visitantes) e arquitetura leve preparada para fácil deploy e manutenção no servidor próprio da residência (servidor_residencia), incluindo rotinas de backup e logs de auditoria.


## construção
 Como é um grande projeto e não tem definição de coisas futuras, uma boa forma de realizar projeto é build as you go, onde:
 	o agente vai Seguir o spec e realizando os códigos enquanto o programador vai definir o rumo do site pelo spec. 

## Pagina 1 - "Pagina inicial/Noticias":
	A primeira página vai ser a página onde os Residentes vão publicar as noticias que podem ser:
	- Algum evento da propria Residencia (festas, Manifestações, )
	- Algum desligamento de energia ou detetização que fica em destaques.
	- Noticias comuns do dia-a-dia.
	- Informs de desjejum, almoço e janta do RU.
	- Datas sobre recebimento de bolsas e/ou auxilio 4° refeição.
	- Regras, costumes e lazer.

### Sempre determinada pelos jornalistas (adm_noticias definida na página de administrador do django) ###
 
## Formato da página:
por ser uma página introdutoria, pode começar bem simples como um site de noticias comum: (Estou usando o site do G1 Globo como base Link: https://g1.globo.com/ )

 - Banner superior - Cotem o botão do menu lateral (ON_CLICK abre menu lateral) com as as utilidades do site de forma geral. 
 1. Na barra lateral, opção da página atual vai abrir um dropdown que pode conter os pontos especiais da página ou algum sub-pagina (pagina filho) da página.

 - Noticias iniciais: Contem um gride com 3 quadrados ontem vai ter as noticias principais ordenada por ordem de adição podendo ser modificada pelo jornalista que tem prioridade (definido pelo banco de dados) 
	1. Maior quadrado - No centro a esquerda (dividindo espaço para dois retangulos menores): 
		- Vai conter as noticias mais relevantes no momento da categoria escolhida. Relevancia é definida pelo jornalista ao publicar a notícia atribuindo a noticia uma tag importante que caso já exista item com essa tag, ela é substituida pela atual podendo ter somente um item marcado com a tag "importante" por vez.
	2. Acima - Lado direito em cima do maior quad: Noticia com data de publicação mais recente ou com prioridade nivel 1 
	3. Abaixo - || || em baixo do maior quadrado: segue a mesma regra do retangulo de cima, mas com a prioridade nível 2 
		- Prioridade segue ordem decrescente da maior prioridade 1 para a menor prioridade Pmin;
		- Prioridade é definida pelo usuario ao inserir a noticia, Como padrão é adicionada como nivel 1 (no banco de dados vai ser adicionada como ultimo, mas o sql vai requisitar em ordem decrescente, fazendo ficar organizado da forma certa).
 - Notícias passadas: Comtem uma lista com outras noticias em ordem de prioridade ou da forma como o jornalista ajustar.
 
