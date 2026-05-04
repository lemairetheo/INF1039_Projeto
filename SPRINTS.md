# Sprint Planning — INF1039

4 pessoas × 6 pts = **24 pts por sprint**

| Dificuldade | Pontos |
|-------------|--------|
| Fácil | 1 |
| Média | 2 |
| Difícil | 4 |

**Equipe:** Theo · Jorge · Thiago · Matheus

---

## Sprint 5 — Fundação
> 29/04 → 04/05 | GitHub, HTML, Models

### Theo — 6 pts
- [ ] Criar o repositório GitHub + Init Django + estrutura inicial do projeto *(média — 2pt)*
- [ ] Criar README explicando como rodar o projeto *(fácil — 1pt)*
- [ ] Django: models + migrações + seed data *(média — 3pt)*

### Jorge — 6 pts
- [ ] HTML: página de Login *(fácil — 1pt)*
- [ ] CSS: estilizar Login *(média — 2pt)*
- [ ] HTML: página de Register *(média — 2pt)*
- [ ] CSS: estilizar Register *(fácil — 1pt)*

### Thiago — 6 pts
- [ ] Django: model `Course` + migrações + seed data *(média — 2pt)*
- [ ] HTML: dashboard do aluno *(fácil — 1pt)*
- [ ] HTML: página inicial (home) *(fácil — 1pt)*
- [ ] CSS: estilizar dashboard *(média — 2pt)*

### Matheus — 6 pts
- [ ] Criar página do professor no Loveable *(difícil — 4pt)*
- [ ] Criar tela de listagem de cursos no Loveable *(média — 2pt)*

---

## Sprint 6 — Views & URLs
> 06/05 → 11/05 | Conectar HTML ao Django

### Theo — 6 pts
- [ ] Django: view + URL para listagem de cursos *(fácil — 1pt)*
- [ ] Django: view + URL para detalhe de curso *(fácil — 1pt)*
- [ ] Make base html(header-footer) *(média — 2pt)*
- [ ] Passar dados reais do banco para o template de cursos *(média — 2pt)*

### Jorge — 6 pts
- [ ] Django: view + URL para Login *(fácil — 1pt)*
- [ ] Django: view + URL para Registro *(fácil — 1pt)*
- [ ] Conectar template HTML de Login ao Django *(média — 2pt)*
- [ ] Passar dados reais do banco para o template de dashboard *(média — 2pt)*


### Thiago — 6 pts
- [ ] Django: view + URL para horários *(fácil — 1pt)*
- [ ] Django: view + URL para inscrição em curso *(fácil — 1pt)*
- [ ] Conectar template HTML de horários ao Django *(média — 2pt)*
- [ ] Passar dados do banco para o template de horários *(média — 2pt)*

### Matheus — 6 pts
- [ ] Django: view + URL para notas *(fácil — 1pt)*
- [ ] Django: view + URL para perfil do aluno *(fácil — 1pt)*
- [ ] Conectar template HTML de notas ao Django *(média — 2pt)*
- [ ] Passar dados de notas do banco para o template *(média — 2pt)*

---

## Sprint 7 — Templates & Estáticos
> 13/05 → 18/05 | Herança de templates, preparação Demo Day Fase 2

### Theo — 6 pts
- [ ] Criar `base.html` com navbar e footer *(média — 2pt)*
- [ ] Fazer todas as páginas herdarem do `base.html` *(média — 2pt)*
- [ ] Configurar arquivos estáticos (CSS/JS) no Django *(média — 2pt)*

### Jorge — 6 pts
- [ ] Refatorar páginas de curso para usar `base.html` *(fácil — 1pt)*
- [ ] Melhorar CSS geral das páginas *(média — 2pt)*
- [ ] Melhorar protótipo no Figma para o Demo Day *(média — 2pt)*
- [ ] Adicionar mensagens de erro/sucesso nos formulários *(fácil — 1pt)*

### Thiago — 6 pts
- [ ] Refatorar páginas de horário para usar `base.html` *(fácil — 1pt)*
- [ ] Criar página 404 personalizada *(fácil — 1pt)*
- [ ] Testar fluxo completo e documentar bugs *(média — 2pt)*
- [ ] Preparar slides para o Demo Day Fase 2 *(média — 2pt)*

### Matheus — 6 pts
- [ ] Refatorar páginas de notas para usar `base.html` *(fácil — 1pt)*
- [ ] Melhorar CSS da página de notas *(média — 2pt)*
- [ ] Atualizar README com funcionalidades implementadas *(fácil — 1pt)*
- [ ] Preparar apresentação Demo Day Fase 2 *(média — 2pt)*

---

> **25/05 — DEMO DAY Fase 2**

---

## Sprint 8 — Autenticação
> 27/05 → 01/06 | Login, Registro, Permissões

### Theo — 6 pts
- [ ] Implementar login com `django.contrib.auth` *(média — 2pt)*
- [ ] Implementar logout *(fácil — 1pt)*
- [ ] Proteger views com `@login_required` *(fácil — 1pt)*
- [ ] Criar página de perfil do aluno logado *(média — 2pt)*

### Jorge — 6 pts
- [ ] Implementar registro de novo usuário *(média — 2pt)*
- [ ] Validar formulário de registro (senha, email único) *(média — 2pt)*
- [ ] Redirecionar corretamente após login/logout *(média — 2pt)*

### Thiago — 6 pts
- [ ] Criar grupos de usuários: aluno e professor *(média — 2pt)*
- [ ] Restringir acesso de páginas por grupo *(média — 2pt)*
- [ ] Testar fluxo login/registro e documentar *(média — 2pt)*

### Matheus — 6 pts
- [ ] Customizar o admin Django para gerenciar usuários *(média — 2pt)*
- [ ] Adicionar foto de perfil ao model de usuário *(média — 2pt)*
- [ ] Estilizar páginas de auth (login, registro) *(média — 2pt)*

---

## Sprint 9 — Inscrição em Cursos
> 03/06 → 08/06

### Theo — 6 pts
- [ ] View para aluno se inscrever em curso *(média — 2pt)*
- [ ] View para aluno cancelar inscrição *(média — 2pt)*
- [ ] Mostrar cursos disponíveis vs inscritos *(média — 2pt)*

### Jorge — 6 pts
- [ ] Limitar vagas por curso + mostrar vagas restantes *(média — 2pt)*
- [ ] View para professor ver alunos inscritos *(média — 2pt)*
- [ ] Estilizar página de inscrição *(média — 2pt)*

### Thiago — 6 pts
- [ ] Mostrar cursos inscritos no dashboard do aluno *(média — 2pt)*
- [ ] Filtrar cursos por categoria/área *(média — 2pt)*
- [ ] Adicionar barra de busca de cursos *(média — 2pt)*

### Matheus — 6 pts
- [ ] View para professor criar novo curso *(média — 2pt)*
- [ ] View para professor editar/deletar curso *(média — 2pt)*
- [ ] Validar formulário de criação de curso *(média — 2pt)*

---

## Sprint 10 — Horários
> 10/06 → 15/06

### Theo — 6 pts
- [ ] Adicionar campo de horário (dia, hora) ao model `Course` *(média — 2pt)*
- [ ] View para exibir horários dos cursos do aluno *(média — 2pt)*
- [ ] Mostrar horários em grade semanal (HTML/CSS) *(média — 2pt)*

### Jorge — 6 pts
- [ ] Detectar conflito de horários na inscrição *(média — 2pt)*
- [ ] Alertar aluno se houver conflito ao se inscrever *(média — 2pt)*
- [ ] Estilizar a grade de horários *(média — 2pt)*

### Thiago — 6 pts
- [ ] Mostrar próximas aulas no dashboard *(média — 2pt)*
- [ ] Adicionar responsividade (mobile) à página de horários *(média — 2pt)*
- [ ] Filtrar horários por semana atual/próxima *(média — 2pt)*

### Matheus — 6 pts
- [ ] View para professor definir horários do curso *(média — 2pt)*
- [ ] Atualizar seed data com horários realistas *(fácil — 1pt)*
- [ ] Testar conflitos de horário e documentar *(fácil — 1pt)*
- [ ] Estilizar formulário de horários do professor *(média — 2pt)*

---

## Sprint 11 — Notas & Avaliações
> 17/06 → 22/06

### Theo — 6 pts
- [ ] View para professor lançar notas por aluno/curso *(média — 2pt)*
- [ ] View para aluno visualizar suas notas *(média — 2pt)*
- [ ] Calcular média automática das notas *(média — 2pt)*

### Jorge — 6 pts
- [ ] Model para múltiplas avaliações (prova, trabalho, etc.) *(média — 2pt)*
- [ ] View para professor criar/editar avaliações *(média — 2pt)*
- [ ] Estilizar página de notas do aluno *(média — 2pt)*

### Thiago — 6 pts
- [ ] Mostrar notas e média no dashboard do aluno *(média — 2pt)*
- [ ] View para aluno ver histórico completo de notas *(média — 2pt)*
- [ ] Alertar aluno se estiver com nota baixa *(fácil — 1pt)*
- [ ] Atualizar seed data com notas *(fácil — 1pt)*

### Matheus — 6 pts
- [ ] Exportar notas em CSV (para professor) *(difícil — 4pt)*
- [ ] Estilizar formulário de lançamento de notas *(média — 2pt)*

---

## Sprint 12 — Polish & Deploy
> 24/06 → 29/06

### Theo — 6 pts
- [ ] Corrigir bugs encontrados nos testes finais *(média — 2pt)*
- [ ] Adicionar flash messages de feedback ao usuário *(média — 2pt)*
- [ ] Preparar script de demonstração para o Demo Day *(média — 2pt)*

### Jorge — 6 pts
- [ ] Revisão geral do CSS e consistência visual *(média — 2pt)*
- [ ] Criar landing page inicial do sistema *(média — 2pt)*
- [ ] Atualizar README com todas as funcionalidades *(média — 2pt)*

### Thiago — 6 pts
- [ ] Popular banco com dados realistas para o demo *(média — 2pt)*
- [ ] Testar fluxo completo (aluno + professor) *(média — 2pt)*
- [ ] Criar usuário de demo e documentar credenciais *(fácil — 1pt)*
- [ ] Gravar vídeo demo do sistema *(fácil — 1pt)*

### Matheus — 6 pts
- [ ] Deploy no Railway ou Render *(difícil — 4pt)*
- [ ] Configurar variáveis de ambiente para produção *(média — 2pt)*

---

> **01/07 — DEMO DAY Final**
