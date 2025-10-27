# Guardrails Validators Reference

Esta guía muestra todos los validators instalados automáticamente en el Dockerfile y cómo usarlos.

## 📦 Validators Instalados

El servicio incluye los siguientes validators pre-instalados:

### 1. RegexMatch

**Propósito:** Valida que el texto coincida con un patrón regex

**Configuración Requerida:**

- `regex` (string): Expresión regular a validar

**Ejemplo:**

```json
{
  "text": "Call me at 123-456-7890",
  "guardrails": [
    {
      "name": "RegexMatch",
      "config": {
        "regex": "\\d{3}-\\d{3}-\\d{4}"
      }
    }
  ]
}
```

**Casos de Uso:**

- Validar formatos de teléfono
- Validar emails
- Validar códigos postales
- Cualquier patrón específico

---

### 2. CompetitorCheck

**Propósito:** Detecta menciones de competidores

**Configuración Requerida:**

- `competitors` (array): Lista de nombres de competidores

**Ejemplo:**

```json
{
  "text": "Our product is better than the competition",
  "guardrails": [
    {
      "name": "CompetitorCheck",
      "config": {
        "competitors": ["Apple", "Microsoft", "Google", "Amazon"]
      }
    }
  ]
}
```

**Casos de Uso:**

- Filtrar contenido de marketing
- Moderar respuestas de chatbots
- Validar contenido corporativo

---

### 3. ToxicLanguage

**Propósito:** Detecta lenguaje tóxico u ofensivo

**Configuración Requerida:**

- `threshold` (float): Umbral de toxicidad (0.0 a 1.0)
- `validation_method` (string): "sentence" o "full"

**Ejemplo:**

```json
{
  "text": "This is a wonderful and respectful message",
  "guardrails": [
    {
      "name": "ToxicLanguage",
      "config": {
        "threshold": 0.5,
        "validation_method": "sentence"
      }
    }
  ]
}
```

**Casos de Uso:**

- Moderar comentarios
- Filtrar contenido generado por usuarios
- Validar respuestas de AI

---

### 4. DetectPII

**Propósito:** Detecta información personal identificable (PII)

**Configuración Requerida:**

- Ninguna (config vacío: `{}`)

**Ejemplo:**

```json
{
  "text": "This is a general discussion about technology",
  "guardrails": [
    {
      "name": "DetectPII",
      "config": {}
    }
  ]
}
```

**Detecta:**

- Números de seguro social
- Direcciones de email
- Números de teléfono
- Direcciones físicas
- Nombres de personas
- Números de tarjetas de crédito

**Casos de Uso:**

- Protección de datos personales
- Cumplimiento GDPR/CCPA
- Anonimización de datos

---

### 5. RestrictToTopic

**Propósito:** Asegura que el texto se mantenga en temas específicos

**Configuración Requerida:**

- `valid_topics` (array): Lista de temas válidos

**Ejemplo:**

```json
{
  "text": "Python is a great programming language for web development",
  "guardrails": [
    {
      "name": "RestrictToTopic",
      "config": {
        "valid_topics": ["programming", "technology", "software development"]
      }
    }
  ]
}
```

**Casos de Uso:**

- Mantener conversaciones enfocadas
- Filtrar respuestas fuera de contexto
- Validar contenido temático

---

### 6. GibberishText

**Propósito:** Detecta texto incoherente o sin sentido (gibberish)

**Configuración Requerida:**

- `threshold` (float): Umbral de confianza (0.0 a 1.0), default 0.5
- `validation_method` (string): "sentence" o "full"

**Ejemplo:**

```json
{
  "text": "Azure is a cloud computing service created by Microsoft",
  "guardrails": [
    {
      "name": "GibberishText",
      "config": {
        "threshold": 0.5,
        "validation_method": "sentence"
      }
    }
  ]
}
```

**Detecta:**

- Texto sin sentido o incoherente
- Oraciones que no tienen lógica
- Palabras aleatorias sin conexión
- Frases mal formadas

**Ejemplos de texto gibberish:**

- "Floppyland love great coffee okay"
- "Fox fox fox"
- "Banana purple computer flying"

**Casos de Uso:**

- Validar coherencia de texto generado por LLMs
- Filtrar respuestas sin sentido
- Asegurar calidad de contenido generado
- Detectar fallos en generación de texto

---

### 7. SecretsPresent

**Propósito:** Detecta secretos, API keys, tokens en el texto

**Configuración Requerida:**

- Ninguna (config vacío: `{}`)

**Ejemplo:**

```json
{
  "text": "Here is some safe content without secrets",
  "guardrails": [
    {
      "name": "SecretsPresent",
      "config": {}
    }
  ]
}
```

**Detecta:**

- API keys
- Tokens de acceso
- Passwords
- Claves privadas
- AWS keys
- GitHub tokens

**Casos de Uso:**

- Prevenir filtración de credenciales
- Validar logs antes de publicar
- Seguridad en CI/CD

---

### 8. ValidURL

**Propósito:** Valida que el texto contenga URLs válidas

**Configuración Requerida:**

- Ninguna (config vacío: `{}`)

**Ejemplo:**

```json
{
  "text": "Visit our website at https://example.com",
  "guardrails": [
    {
      "name": "ValidURL",
      "config": {}
    }
  ]
}
```

**Casos de Uso:**

- Validar enlaces en contenido
- Verificar URLs en formularios
- Filtrar URLs malformadas

---

## 🔗 Combinar Múltiples Validators

Puedes usar múltiples validators en una sola request:

```json
{
  "text": "Our innovative product is amazing!",
  "guardrails": [
    {
      "name": "CompetitorCheck",
      "config": {
        "competitors": ["Apple", "Google"]
      }
    },
    {
      "name": "ToxicLanguage",
      "config": {
        "threshold": 0.5,
        "validation_method": "sentence"
      }
    },
    {
      "name": "DetectPII",
      "config": {}
    }
  ]
}
```

**El servicio validará contra TODOS los guardrails y retornará todos los que fallen.**

---

## 📊 Ejemplos de Respuestas

### Éxito (Todo pasa)

```json
{
  "passed": true,
  "failed_guardrails": []
}
```

### Fallo (Uno o más fallan)

```json
{
  "passed": false,
  "failed_guardrails": [
    {
      "name": "CompetitorCheck",
      "error": "Found the following competitors: [['Apple']]. Please avoid naming those competitors next time"
    },
    {
      "name": "ToxicLanguage",
      "error": "The following sentences in your response were found to be toxic:\n- Offensive text here"
    }
  ]
}
```

### Error de Configuración

```json
{
  "detail": {
    "message": "Invalid guardrail configuration(s)",
    "errors": ["RegexMatch: Missing required configuration parameters: regex"]
  }
}
```

---

## 🆕 Agregar Más Validators

Para agregar validators adicionales al Dockerfile:

1. Edita el `Dockerfile`
2. Agrega la línea de instalación:

```dockerfile
RUN guardrails hub install hub://guardrails/nombre_del_validator --quiet || echo "Failed to install nombre_del_validator"
```

3. Reconstruye la imagen:

```bash
docker-compose up -d --build
```

**Validators disponibles:**

- Ver catálogo completo: https://hub.guardrailsai.com/

---

## 🧪 Probar Validators

Usa el script de prueba incluido:

```bash
# Local
./test_validators.sh http://localhost:8000

# Railway
./test_validators.sh https://tu-app.up.railway.app
```

---

## 📚 Recursos

- [Guardrails Hub](https://hub.guardrailsai.com/) - Catálogo completo
- [Guardrails Docs](https://www.guardrailsai.com/docs) - Documentación oficial
- [Guardrails Index](https://index.guardrailsai.com) - Benchmark de rendimiento

---

## ⚠️ Notas Importantes

1. **Algunos validators requieren API keys:**

   - Configúralas como variables de entorno
   - No las incluyas en el código

2. **Performance:**

   - Más validators = más tiempo de procesamiento
   - Usa solo los necesarios para tu caso de uso

3. **Actualizaciones:**

   - Los validators se actualizan regularmente
   - Reconstruye la imagen periódicamente para obtener las últimas versiones

4. **Custom Validators:**
   - Puedes crear tus propios validators
   - Ver documentación: https://www.guardrailsai.com/docs/custom-validators
