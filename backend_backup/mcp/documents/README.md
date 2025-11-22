# MCP Documents Service

Service MCP pour la gestion de documents Word (DOCX), export PDF et intégration Google Docs.

## Installation

```bash
cd backend/mcp/documents
pip install -r requirements.txt
```

## Démarrage

```bash
python server.py
```

Le service démarre sur `http://localhost:8007`

## Endpoints

### Word Documents

#### POST /documents/create_docx
Créer un nouveau document Word à partir de zéro.

**Request:**
```json
{
  "title": "Mon Document",
  "content": [
    {
      "text": "Ceci est un titre",
      "style": "Heading1",
      "alignment": "center",
      "bold": false,
      "italic": false
    },
    {
      "text": "Ceci est un paragraphe normal.",
      "style": "Normal",
      "alignment": "left",
      "bold": false,
      "italic": false,
      "font_size": 12
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "document_base64": "UEsDBBQABgAI...",
  "filename": "Mon Document.docx",
  "size_bytes": 12345
}
```

**Styles disponibles:**
- `Normal` - Paragraphe normal
- `Heading1`, `Heading2`, `Heading3` - Titres de niveau 1, 2, 3

**Alignements disponibles:**
- `left`, `center`, `right`, `justify`

---

#### POST /documents/fill_docx_template
Remplir un template Word avec des valeurs de remplacement.

**Request:**
```json
{
  "template_base64": "UEsDBBQABgAI...",
  "replacements": {
    "nom": "Jean Dupont",
    "date": "2025-11-21",
    "montant": "1500€"
  }
}
```

Le template doit contenir des placeholders au format `{{nom}}`, `{{date}}`, etc.

**Response:**
```json
{
  "success": true,
  "document_base64": "UEsDBBQABgAI...",
  "filename": "filled_template.docx",
  "replacements_count": 3
}
```

---

### PDF Export

#### POST /documents/export_pdf
Exporter du contenu vers un fichier PDF.

**Request:**
```json
{
  "title": "Mon Rapport PDF",
  "content": [
    {
      "text": "Introduction",
      "style": "Heading1",
      "alignment": "center"
    },
    {
      "text": "Ceci est le contenu du rapport.",
      "style": "Normal",
      "alignment": "justify"
    }
  ],
  "page_size": "A4"
}
```

**page_size:** `letter` (défaut) ou `A4`

**Response:**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQ...",
  "filename": "Mon Rapport PDF.pdf",
  "size_bytes": 8765
}
```

---

### Google Docs

**Note:** Les endpoints Google Docs nécessitent des credentials OAuth2 valides.

#### POST /documents/google/create
Créer un nouveau document Google Docs.

**Request:**
```json
{
  "title": "Mon Google Doc",
  "credentials_json": "{\"token\": \"...\", \"refresh_token\": \"...\", ...}"
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "abc123xyz789",
  "title": "Mon Google Doc",
  "url": "https://docs.google.com/document/d/abc123xyz789/edit"
}
```

---

#### POST /documents/google/update
Mettre à jour (remplacer) le contenu d'un document Google Docs.

**Request:**
```json
{
  "document_id": "abc123xyz789",
  "content": "Nouveau contenu qui remplace tout.",
  "credentials_json": "{\"token\": \"...\", ...}"
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "abc123xyz789",
  "url": "https://docs.google.com/document/d/abc123xyz789/edit"
}
```

---

#### POST /documents/google/append
Ajouter du contenu à la fin d'un document Google Docs.

**Request:**
```json
{
  "document_id": "abc123xyz789",
  "content": "Contenu à ajouter à la fin.",
  "credentials_json": "{\"token\": \"...\", ...}"
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "abc123xyz789",
  "url": "https://docs.google.com/document/d/abc123xyz789/edit"
}
```

---

### Health Check

#### GET /health
Vérifier l'état du service.

**Response:**
```json
{
  "status": "healthy",
  "service": "mcp-documents",
  "timestamp": "2025-11-21T10:30:00",
  "google_docs_available": true
}
```

---

#### GET /
Informations sur le service et liste des endpoints.

**Response:**
```json
{
  "service": "MCP Documents Service",
  "version": "1.0.0",
  "endpoints": {
    "word": [
      "POST /documents/create_docx",
      "POST /documents/fill_docx_template"
    ],
    "pdf": [
      "POST /documents/export_pdf"
    ],
    "google": [
      "POST /documents/google/create",
      "POST /documents/google/update",
      "POST /documents/google/append"
    ]
  },
  "google_docs_available": true
}
```

---

## Exemples d'utilisation

### Créer un document Word

```python
import requests
import base64

url = "http://localhost:8007/documents/create_docx"
payload = {
    "title": "Rapport Mensuel",
    "content": [
        {
            "text": "Rapport Mensuel - Novembre 2025",
            "style": "Heading1",
            "alignment": "center"
        },
        {
            "text": "Résumé Exécutif",
            "style": "Heading2",
            "alignment": "left"
        },
        {
            "text": "Ce mois-ci, nous avons constaté une croissance de 15% par rapport au mois précédent.",
            "style": "Normal",
            "alignment": "justify",
            "bold": False,
            "italic": False
        }
    ]
}

response = requests.post(url, json=payload)
result = response.json()

# Sauvegarder le fichier
doc_bytes = base64.b64decode(result["document_base64"])
with open("rapport_mensuel.docx", "wb") as f:
    f.write(doc_bytes)
```

### Remplir un template

```python
import requests
import base64

# Charger le template
with open("template.docx", "rb") as f:
    template_b64 = base64.b64encode(f.read()).decode()

url = "http://localhost:8007/documents/fill_docx_template"
payload = {
    "template_base64": template_b64,
    "replacements": {
        "client_nom": "ACME Corporation",
        "date": "21/11/2025",
        "montant_total": "25,000€",
        "reference": "INV-2025-1234"
    }
}

response = requests.post(url, json=payload)
result = response.json()

# Sauvegarder le fichier rempli
doc_bytes = base64.b64decode(result["document_base64"])
with open("facture_remplie.docx", "wb") as f:
    f.write(doc_bytes)
```

### Exporter en PDF

```python
import requests
import base64

url = "http://localhost:8007/documents/export_pdf"
payload = {
    "title": "Contrat de Service",
    "content": [
        {
            "text": "CONTRAT DE SERVICE",
            "style": "Heading1",
            "alignment": "center"
        },
        {
            "text": "Article 1 - Objet du contrat",
            "style": "Heading2",
            "alignment": "left"
        },
        {
            "text": "Le présent contrat a pour objet la fourniture de services...",
            "style": "Normal",
            "alignment": "justify"
        }
    ],
    "page_size": "A4"
}

response = requests.post(url, json=payload)
result = response.json()

# Sauvegarder le PDF
pdf_bytes = base64.b64decode(result["pdf_base64"])
with open("contrat.pdf", "wb") as f:
    f.write(pdf_bytes)
```

---

## Format des données

### Content Object

Chaque élément de contenu peut avoir les propriétés suivantes :

```json
{
  "text": "Texte du paragraphe",
  "style": "Normal|Heading1|Heading2|Heading3",
  "alignment": "left|center|right|justify",
  "bold": true|false,
  "italic": true|false,
  "font_size": 12
}
```

**Propriétés:**
- `text` (obligatoire) : Le texte du paragraphe
- `style` (optionnel, défaut: "Normal") : Le style du paragraphe
- `alignment` (optionnel, défaut: "left") : L'alignement du texte
- `bold` (optionnel, défaut: false) : Texte en gras
- `italic` (optionnel, défaut: false) : Texte en italique
- `font_size` (optionnel) : Taille de la police en points

---

## Intégration avec Google Docs

Pour utiliser les endpoints Google Docs, vous devez :

1. Créer un projet dans Google Cloud Console
2. Activer l'API Google Docs
3. Créer des credentials OAuth2
4. Obtenir un token d'accès valide

Le `credentials_json` doit contenir :
```json
{
  "token": "ya29.xxx",
  "refresh_token": "1//xxx",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "xxx.apps.googleusercontent.com",
  "client_secret": "xxx",
  "scopes": ["https://www.googleapis.com/auth/documents"]
}
```

---

## Dépendances

- **fastapi** : Framework web
- **uvicorn** : Serveur ASGI
- **python-docx** : Manipulation de fichiers Word
- **docxcompose** : Composition de documents
- **reportlab** : Génération de PDF
- **google-api-python-client** : Intégration Google Docs
- **Pillow** : Traitement d'images

---

## Port et configuration

- Port par défaut : **8007**
- Host : **0.0.0.0** (accessible depuis l'extérieur)

Pour changer le port :
```python
uvicorn.run(app, host="0.0.0.0", port=VOTRE_PORT)
```

---

## Tests

Pour tester le service :

```bash
# Health check
curl http://localhost:8007/health

# Info du service
curl http://localhost:8007/

# Créer un document simple
curl -X POST http://localhost:8007/documents/create_docx \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Document",
    "content": [
      {"text": "Hello World", "style": "Heading1", "alignment": "center"}
    ]
  }'
```

---

## Support et erreurs

Le service retourne des codes HTTP standards :

- **200** : Succès
- **400** : Requête invalide
- **500** : Erreur serveur
- **501** : Fonctionnalité non disponible (ex: Google Docs sans credentials)
- **502** : Erreur de l'API externe (ex: Google API)

Les réponses d'erreur incluent un message détaillé :
```json
{
  "detail": "Description de l'erreur"
}
```
