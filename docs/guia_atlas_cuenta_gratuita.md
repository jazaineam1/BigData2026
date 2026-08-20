# Crear tu cuenta de MongoDB Atlas

**Tarea entre la sesión 3 y la sesión 4 · Big Data 2026-2**

---

## Por qué haces esto

La colección de noticias que construiste en la sesión 3 vive dentro de tu Colab y **se muere cuando cierras la pestaña**. El equipo de Laura no puede trabajar así: si la evidencia desaparece cada vez que alguien cierra el portátil, no hay proyecto que valga.

Esta semana la vas a poner donde el equipo entero pueda alcanzarla: en un servidor que no se apaga.

**Es gratis, son 512 MB, y no pide tarjeta de crédito.** Lo digo en la primera línea porque es la duda que hace que la gente posponga esto hasta el jueves a las 6:05 pm.

**Tiempo real: unos 45 minutos** la primera vez. No 10. Si nunca has creado una cuenta en un proveedor de nube —y en este grupo casi nadie la ha creado— vas a leer pantallas que no habías visto nunca. Es normal y no es difícil: es lento.

**Qué entregas:** un pantallazo de tu clúster creado, **el miércoles**. No el jueves.

---

## Antes de empezar: tres cosas que te van a ahorrar la noche

Estas tres son responsables de casi todos los problemas que vas a tener. Léelas ahora, no cuando falle.

### 1. Vas a crear DOS usuarios distintos, y no son el mismo

| Usuario | Para qué | Dónde se usa |
|---|---|---|
| **Usuario de la cuenta Atlas** | entrar a la página de MongoDB | el navegador |
| **Usuario de base de datos** | que Python se conecte a tu clúster | el código |

Es el malentendido número uno. Cuando el paso 4 te pida crear un usuario de base de datos, **no pongas tu correo institucional ni tu contraseña de la universidad.** Es otra cosa.

### 2. La contraseña: solo letras y números

Cuando crees el usuario de base de datos, usa **12 caracteres, solo letras y números**. Nada de `@`, `#`, `/`, `:` ni `?`.

**Por qué:** esa contraseña viaja dentro de una dirección web (`mongodb+srv://usuario:contraseña@servidor`). Un `@` en la contraseña parte la dirección por la mitad y el error que te sale **no dice nada sobre la contraseña**. Vas a perder media hora buscando en el lugar equivocado.

Y guárdala donde la vuelvas a encontrar el jueves. No en un papel.

### 3. El acceso de red: `0.0.0.0/0`, no "mi dirección actual"

Este es el que de verdad importa, y es el que casi todos van a hacer mal si no lo lees.

Cuando llegues a **Network Access**, Atlas te va a ofrecer un botón grande y cómodo que dice **"Add My Current IP Address"**. La documentación oficial de MongoDB lo recomienda. **Para nosotros no sirve.**

**Por qué:** tu Colab **no corre en tu computador**. Corre en un servidor de Google, en algún centro de datos, con una dirección que cambia cada vez que abres una sesión. Tu dirección de casa no tiene absolutamente nada que ver con la dirección desde la que Python se va a conectar. Si autorizas la tuya, el jueves en clase te va a salir `ServerSelectionTimeoutError` y no vas a entender por qué, porque *hiciste el paso*.

Hay un segundo motivo: las entradas temporales de Atlas **caducan a los 7 días**. Si la creas hoy, jueves, vence exactamente cuando la necesitas.

> **Elige "Allow Access From Anywhere" (`0.0.0.0/0`).**

Y ahora la parte que es contenido de la materia, no un atajo: **eso en un sistema real no se hace.** Abrir un servidor al mundo entero es aceptable aquí por tres razones concretas, y conviene que sepas nombrarlas:

1. los datos que vas a subir son **públicos** (noticias y contratación estatal);
2. la contraseña sigue protegiendo la base: abrir la red no es quitar la llave;
3. es un clúster de práctica, con 512 MB, que puedes borrar cuando quieras.

Si mañana subes datos de pacientes, de nómina o de clientes, **ninguna de las tres se cumple**, y esta decisión sería inaceptable. Esa distinción —cuándo una comodidad es aceptable y cuándo no— es exactamente lo que se evalúa en el curso.

---

## Los pasos

> Las pantallas de Atlas cambian cada pocos meses. Si algo no se llama exactamente como aquí, busca el botón que hace lo mismo: la secuencia no cambia.

### Paso 1 · Crear la cuenta

Entra a **[mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)**.

Regístrate con tu correo. Verifica el correo que te llega — sin eso no avanzas.

Atlas te va a hacer un par de preguntas de bienvenida (para qué lo vas a usar, qué lenguaje). Responde lo que quieras: **no cambian nada** de lo que sigue. Si te preguntan el lenguaje, di Python.

**Qué debes ver al final:** la consola de Atlas, con un proyecto creado.

### Paso 2 · Crear el clúster gratuito

Busca **Create** o **Build a Cluster**.

| Opción | Qué elegir | Por qué |
|---|---|---|
| Tipo | **M0** (dice *Free*, $0/month) | es el gratuito; los otros cobran |
| Proveedor | AWS, Google Cloud o Azure — **da igual** | los tres funcionan idéntico para lo nuestro |
| Región | la que esté **más cerca de Colombia** | menos retraso; nada más |
| Nombre | déjalo como está (`Cluster0`) | te lo vas a encontrar así en clase |

Pulsa crear. **El clúster tarda entre 3 y 7 minutos en quedar listo.** Es normal. No recargues la página en pánico.

> **Si te pide una tarjeta de crédito, algo se seleccionó mal.** Vuelve atrás y confirma que elegiste **M0 / Free**. El plan gratuito no la pide nunca.

**Qué debes ver al final:** tu clúster con estado *Active* o un check verde.

### Paso 3 · Crear el usuario de base de datos

Menú lateral → **Database Access** → **Add New Database User**.

- Método de autenticación: **Password**.
- Usuario: algo simple y que recuerdes, por ejemplo `estudiante_uce`.
- Contraseña: **12 caracteres, solo letras y números** (ver arriba por qué).
- Permisos: **Read and write to any database**.

**Anota usuario y contraseña ahora.** Atlas no te va a volver a mostrar la contraseña.

**Qué debes ver al final:** tu usuario listado en Database Access.

### Paso 4 · Abrir el acceso de red

Menú lateral → **Network Access** → **Add IP Address**.

**Pulsa "ALLOW ACCESS FROM ANYWHERE".** Debe quedar `0.0.0.0/0`.

Ignora el botón "Add My Current IP Address". Ya explicamos arriba por qué no sirve, y vale la pena que puedas explicarlo tú también.

**Qué debes ver al final:** una entrada `0.0.0.0/0` con estado *Active*. Si dice *Pending*, espera un minuto.

### Paso 5 · Copiar la cadena de conexión

En tu clúster → **Connect** → **Drivers** → Python.

Atlas te muestra algo así:

```
mongodb+srv://estudiante_uce:<db_password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Cópiala y guárdala.** De ahí solo necesitas tres piezas, y el cuaderno de la sesión 4 te las va a pedir **por separado**:

| Pieza | En el ejemplo de arriba |
|---|---|
| usuario | `estudiante_uce` |
| host | `cluster0.xxxxx.mongodb.net` |
| contraseña | la que creaste en el paso 3 |

> **Por eso te las pedimos separadas:** así no tienes que editar la dirección a mano, que es donde la gente olvida borrar los signos `<` y `>` alrededor de la contraseña. El cuaderno arma la dirección por ti.

### Paso 6 · Entregar la evidencia — el miércoles

Un pantallazo donde se vea:

- tu clúster con estado **Active**;
- la entrada **`0.0.0.0/0`** en Network Access.

**Tapa o recorta cualquier cosa que parezca una contraseña.** Nunca compartas la cadena de conexión completa: lleva tu usuario adentro.

**Por qué el miércoles y no el jueves:** si algo te falló, hay un día para arreglarlo. Si lo entregas el jueves a las 6:05 pm, la sesión 4 empieza contigo esperando y con siete compañeros esperándote.

---

## Si algo falla

Busca el **texto literal** del error en esta tabla. No hace falta que entiendas el mensaje completo: basta con encontrarlo aquí.

| Lo que dice la pantalla | Qué pasó | Qué haces |
|---|---|---|
| `ServerSelectionTimeoutError` | el acceso de red no está abierto para Colab | Network Access → agrega `0.0.0.0/0` |
| `bad auth : authentication failed` | usuario o contraseña mal | revisa el paso 3; si dudas, crea un usuario nuevo |
| Falla y tu contraseña tiene `@`, `#` o `/` | el símbolo rompe la dirección | crea otro usuario con contraseña solo de letras y números |
| `Invalid URI` o falla y ves `<` `>` | dejaste los signos alrededor de la contraseña | quítalos, o mejor: usa las tres piezas por separado |
| El clúster lleva 10 minutos "creando" | aprovisionamiento lento | espera, no crees otro; solo puedes tener uno gratis |
| Te pide tarjeta de crédito | no elegiste M0 | vuelve atrás y elige el plan Free |
| No encuentras "Database Access" | menú colapsado | ábrelo desde el icono de menú, sección Security |

**Y la regla que vale por encima de todas:** si a los 45 minutos no lo lograste, **para y escríbele al profesor el miércoles**. Hay un clúster del curso preparado para que nadie se quede sin laboratorio. Quedarte trabado en una cuenta no es parte de lo que se evalúa; interpretar datos sí.

---

## Lo que NO tienes que hacer

Para que no pierdas tiempo en cosas que no vamos a usar:

- **No** cargues los *sample datasets* que Atlas ofrece. Nosotros subimos nuestros propios datos en clase.
- **No** instales MongoDB Compass en tu computador. Usaremos el explorador web.
- **No** instales nada en tu máquina. Todo corre en el navegador.
- **No** crees más de un clúster: el plan gratuito permite uno por proyecto.

---

## Para el jueves

Llega con estas tres cosas anotadas y a mano:

1. usuario de base de datos,
2. contraseña,
3. host (`cluster0.xxxxx.mongodb.net`).

Con eso, conectarte desde Python toma menos de un minuto. Sin eso, la primera media hora de la sesión 4 se te va en trámites en vez de en datos.
