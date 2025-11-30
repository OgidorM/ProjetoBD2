# CineMagic - Portal do Cliente

Este é um portal completo voltado para o cliente final, desenvolvido como uma Single Page Application (SPA) em um único arquivo HTML.

## 🎬 Visão Geral

O CineMagic é uma plataforma de cinema online onde os clientes podem:
- Explorar filmes em cartaz
- Comprar bilhetes de cinema
- Selecionar lugares
- Descobrir cinemas próximos
- Comprar snacks e bebidas
- Gerenciar carrinho de compras

## ✨ Características

### 🎨 Design Moderno
- Tema escuro inspirado em plataformas de streaming
- Interface responsiva com Bootstrap 5.3.3
- Gradientes e animações suaves
- Design cinematográfico profissional
- Totalmente adaptável para mobile e desktop

### 🎥 Funcionalidades Implementadas

#### 1. **Catálogo de Filmes**
   - Grid visual de filmes em cartaz
   - Sistema de pesquisa em tempo real
   - Filtros por categoria (Ação, Comédia, Drama, Terror, Ficção Científica, Animação)
   - Detalhes completos de cada filme:
     - Sinopse
     - Duração
     - Classificação etária
     - Avaliação (sistema de estrelas)
     - Realizador
     - Preço do bilhete

#### 2. **Compra de Bilhetes**
   - Processo de reserva em 2 etapas:
     - **Etapa 1:** Seleção de cinema, data e horário
     - **Etapa 2:** Seleção interativa de lugares
   - Mapa visual de lugares da sala (8 filas x 10 colunas)
   - Indicação de lugares disponíveis, ocupados e selecionados
   - Cálculo automático do total
   - Validação de seleção mínima

#### 3. **Rede de Cinemas**
   - Lista completa de 5 cinemas em Portugal:
     - Lisboa, Porto, Coimbra, Faro, Braga
   - Informações detalhadas:
     - Localização e endereço completo
     - Número de salas
     - Telefone de contacto
     - Avaliação (0-5 estrelas)
   - Pesquisa por cidade
   - Acesso direto à programação

#### 4. **Loja de Snacks**
   - Catálogo de 10 produtos:
     - **Pipocas:** Pequenas (3.50€) e Grandes (5.00€)
     - **Refrigerantes:** Pequeno (2.50€) e Grande (4.00€)
     - **Snacks:** Nachos (4.50€), Hot Dog (5.50€)
     - **Doces:** Chocolate (2.00€), Gomas (2.50€)
     - **Bebidas:** Água Mineral (1.50€)
     - **Combos:** Combo Casal (15.00€)
   - Adicionar produtos ao carrinho com um clique
   - Feedback visual de adição

#### 5. **Carrinho de Compras**
   - Gestão completa de itens
   - Bilhetes e produtos no mesmo carrinho
   - Ajuste de quantidades (+ / -)
   - Remoção individual de itens
   - Informações detalhadas:
     - Para bilhetes: filme, cinema, data, horário, lugares
     - Para produtos: quantidade, preço unitário
   - Cálculo de total em tempo real
   - Contador visual no menu (badge)
   - Processo de checkout simulado

## 📊 Dados Mock

A aplicação utiliza dados mockados (fictícios) para demonstração:

### Filmes
- 8 filmes em diferentes categorias
- Preços entre 6.50€ e 9.00€
- Durações entre 92 e 142 minutos
- Avaliações de 4.0 a 4.9 estrelas

### Cinemas
- 5 cinemas em cidades diferentes
- Entre 5 e 10 salas por cinema
- Endereços e telefones realistas

### Produtos
- 10 produtos diferentes
- Preços de 1.50€ a 15.00€
- Categorias: Snacks, Bebidas, Comida, Doces, Combos

### Sessões
- Horários: 10:00, 13:00, 16:00, 19:00, 22:00
- Lugares gerados aleatoriamente (70% disponíveis)

## 🚀 Como Usar

### Opção 1: Abrir Diretamente no Navegador (Recomendado)

Simplesmente abra o arquivo `index.html` no seu navegador:

```bash
# Linux
firefox index.html
# ou
google-chrome index.html

# macOS
open index.html

# Windows
start index.html
```

### Opção 2: Servir com Python HTTP Server

```bash
cd clientes_front
python -m http.server 8080
```

Acesse: `http://localhost:8080`

### Opção 3: Integrar com Django

1. Configure o arquivo como template estático
2. Adicione rota no `urls.py`:

```python
from django.views.generic import TemplateView

urlpatterns = [
    path('portal/', TemplateView.as_view(template_name='clientes_front/index.html')),
]
```

## 🎯 Fluxo de Uso do Cliente

1. **Página Inicial (Hero)**
   - Apresentação visual atrativa
   - Botões de ação para filmes e loja

2. **Explorar Filmes**
   - Navegar pelo catálogo
   - Filtrar por categoria
   - Pesquisar por título
   - Ver detalhes do filme

3. **Comprar Bilhete**
   - Selecionar cinema e horário
   - Escolher lugares no mapa
   - Adicionar ao carrinho

4. **Comprar Snacks**
   - Navegar pela loja
   - Adicionar produtos
   - Ajustar quantidades

5. **Finalizar Compra**
   - Revisar carrinho
   - Confirmar compra
   - Receber confirmação

## 🎨 Paleta de Cores

```css
--primary-color: #e50914    /* Vermelho Netflix-style */
--secondary-color: #221f1f  /* Cinza escuro */
--accent-color: #f5a623     /* Dourado/Laranja */
--dark-bg: #141414          /* Preto suave */
--card-bg: #2f2f2f          /* Cinza card */
```

## 📱 Responsividade

A aplicação é totalmente responsiva e se adapta a:
- ✅ Desktop (1920px+)
- ✅ Laptop (1366px - 1920px)
- ✅ Tablet (768px - 1366px)
- ✅ Mobile (320px - 768px)

### Ajustes Mobile
- Mapa de lugares reduzido para 6 colunas
- Hero com título menor
- Cards em coluna única
- Menu hambúrguer

## 🔧 Tecnologias Utilizadas

- **HTML5** - Estrutura semântica
- **CSS3** - Estilização avançada com:
  - CSS Grid e Flexbox
  - Gradientes lineares
  - Transições e animações
  - Media queries
- **JavaScript (ES6+)** - Lógica da aplicação:
  - Arrow functions
  - Template literals
  - Array methods (map, filter, reduce, find)
  - Spread operator
  - DOM manipulation
- **Bootstrap 5.3.3** - Framework CSS
- **Bootstrap Icons 1.11.1** - Ícones vetoriais

## 📦 Estrutura do Código

```javascript
// Mock Data
- movies[]        // 8 filmes
- cinemas[]       // 5 cinemas
- products[]      // 10 produtos

// Global State
- cart[]          // Carrinho de compras
- currentMovie    // Filme sendo visualizado
- selectedSeats[] // Lugares selecionados
- selectedSession // Horário selecionado

// Main Functions
- Navigation: showSection()
- Movies: renderMovies(), filterMovies(), showMovieDetails()
- Tickets: showTicketBooking(), generateSeats(), toggleSeat()
- Cinemas: renderCinemas(), filterCinemas()
- Products: renderProducts(), addProductToCart()
- Cart: showCart(), renderCart(), updateQuantity(), checkout()
```

## 🔐 Notas de Segurança

Este é um protótipo com dados mockados. Para produção:

- [ ] Implementar autenticação de utilizadores
- [ ] Integrar com backend real (API REST)
- [ ] Adicionar validação de pagamentos
- [ ] Implementar sistema de reservas real
- [ ] Adicionar proteção CSRF
- [ ] Sanitizar inputs do utilizador
- [ ] Usar HTTPS
- [ ] Implementar rate limiting

## 🚧 Melhorias Futuras

- [ ] Sistema de login/registo
- [ ] Perfil do utilizador
- [ ] Histórico de compras
- [ ] Sistema de avaliações
- [ ] Trailers de filmes (integração YouTube)
- [ ] Programa de fidelidade
- [ ] Cupões de desconto
- [ ] Pagamento online real
- [ ] Notificações por email
- [ ] Partilha em redes sociais
- [ ] Sistema de recomendação de filmes
- [ ] Modo escuro/claro (toggle)
- [ ] Suporte multi-idioma
- [ ] PWA (Progressive Web App)
- [ ] Impressão de bilhetes (PDF)

## 🎭 Experiência do Utilizador

### Animações e Transições
- Hover effects em todos os cards
- Transições suaves de 0.3s
- Escalas e elevações nos hovers
- Feedback visual em todas as ações

### Acessibilidade
- Contraste adequado de cores
- Ícones descritivos
- Texto legível (mínimo 14px)
- Botões com áreas clicáveis adequadas

### Usabilidade
- Navegação intuitiva
- Processo de compra simplificado
- Feedback visual constante
- Estados claros (selecionado, ocupado, etc.)
- Mensagens de confirmação

## 📞 Informações de Contacto (Mockadas)

- **Email:** info@cinemagic.pt
- **Telefone:** +351 123 456 789
- **Redes Sociais:** Facebook, Instagram, Twitter

## 🏆 Destaques da Implementação

1. **Single File Application** - Tudo em um único arquivo HTML
2. **Zero Dependencies** - Apenas CDNs do Bootstrap
3. **Performance** - JavaScript vanilla otimizado
4. **Mock Completo** - Dados realistas para demonstração
5. **UX Moderna** - Interface inspirada em Netflix/Prime Video
6. **Código Limpo** - Bem comentado e organizado

## 📄 Licença

Este é um projeto educacional para demonstração de conceitos de desenvolvimento web front-end.

---

**CineMagic** - A Sua Experiência de Cinema © 2025

