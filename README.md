# INF1039 Project

---

## English

### Requirements
- Python 3.11+

### Setup & Run

**1. Clone the repository**
```bash
git clone <repository-url>
cd INF1039_Projeto
```

**2. Create and activate the virtual environment**
```bash
python3 -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Apply database migrations**
```bash
python manage.py migrate
```

**5. (Optional) Create an admin superuser**
```bash
python manage.py createsuperuser
```

**6. Run the development server**
```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000`  
Admin panel: `http://127.0.0.1:8000/admin`

> The `db.sqlite3` file and `venv/` folder are in `.gitignore` — each developer creates their own local database after running `migrate`.

---

## Português

### Requisitos
- Python 3.11+

### Configuração e execução

**1. Clonar o repositório**
```bash
git clone <url-do-repositorio>
cd INF1039_Projeto
```

**2. Criar e ativar o ambiente virtual**
```bash
python3 -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Instalar as dependências**
```bash
pip install -r requirements.txt
```

**4. Aplicar as migrações do banco de dados**
```bash
python manage.py migrate
```

**5. (Opcional) Criar um superusuário para o admin**
```bash
python manage.py createsuperuser
```

**6. Rodar o servidor de desenvolvimento**
```bash
python manage.py runserver
```

Acesse no navegador: `http://127.0.0.1:8000`  
Painel admin: `http://127.0.0.1:8000/admin`

> O arquivo `db.sqlite3` e a pasta `venv/` estão no `.gitignore` — cada desenvolvedor cria o próprio banco local após rodar o `migrate`.
