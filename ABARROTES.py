from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import json
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones_abarrotes_flor'

USUARIO_CORRECTO = "alex@123"
CONTRASENA_CORRECTA = "alex123"

clientes_registrados = []
registro_contador = [1]

# ---------- Gestión de productos con archivo JSON ----------
PRODUCTOS_ARCHIVO = "productos.json"

def cargar_productos():
    """Carga la lista de productos desde el archivo JSON."""
    if not os.path.exists(PRODUCTOS_ARCHIVO):
        productos_ejemplo = [
            {"id": 1, "nombre": "Manzana", "descripcion": "Manzanas rojas dulces", "precio": 3.50, "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTefUHgejxyLcdttT_ovpNnkWpHNzXHDsN9RQ&s"},
            {"id": 2, "nombre": "Plátano", "descripcion": "Plátanos de seda", "precio": 2.00, "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStP3GhAe2hFpPDHhYRSFers5V2xidAaDkUJw&s"},
            {"id": 3, "nombre": "Leche Entera", "descripcion": "Leche pasteurizada", "precio": 4.20, "imagen": "https://media.falabella.com/tottusPE/43548139_1/w=1500,h=1500,fit=cover"}
        ]
        guardar_productos(productos_ejemplo)
        return productos_ejemplo
    with open(PRODUCTOS_ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_productos(productos):
    with open(PRODUCTOS_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(productos, f, indent=2, ensure_ascii=False)

# ---------- TEMPLATE DEL DASHBOARD ----------
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Abarrotes Flor</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: 'Poppins', sans-serif; background: #f4f4f4; color: #333; }
        :root {
            --card: #fff;
            --r: 16px;
            --shadow-sm: 0 6px 15px rgba(0,0,0,0.08);
            --muted: #777;
            --dark: #2a6e3f;
            --gold: #c89a3e;
        }
        header {
            background: linear-gradient(135deg, #2a6e3f 0%, #54a358 100%);
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        header .brand {
            color: white;
            font-size: 24px;
            font-weight: 700;
            text-decoration: none;
        }
        header .brand span { color: var(--gold); }
        header nav a {
            color: white;
            text-decoration: none;
            margin-left: 20px;
            font-weight: 600;
            transition: 0.2s;
        }
        header nav a:hover { text-decoration: underline; }
        .container {
            max-width: 1400px;
            margin: 20px auto;
            padding: 0 20px;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
            margin-top: 1rem;
        }
        .kpi-card {
            background: var(--card);
            padding: 1.5rem;
            border-radius: var(--r);
            box-shadow: var(--shadow-sm);
            text-align: center;
        }
        .kpi-card h3 {
            font-size: 0.85rem;
            color: var(--muted);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .kpi-card .valor {
            font-size: 2rem;
            font-weight: 800;
            color: var(--dark);
            line-height: 1.2;
        }
        .kpi-card .referencia {
            font-size: 0.75rem;
            color: var(--muted);
            margin-top: 0.5rem;
        }
        .chart-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .chart-box {
            background: var(--card);
            padding: 1.5rem;
            border-radius: var(--r);
            box-shadow: var(--shadow-sm);
        }
        .chart-box h3 {
            margin-bottom: 1rem;
            color: var(--dark);
        }
        .actualizacion {
            text-align: right;
            font-size: 0.75rem;
            color: var(--muted);
            margin-top: 1rem;
        }
        .seccion {
            background: white;
            border-radius: var(--r);
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-sm);
        }
        .seccion h2 {
            color: var(--dark);
            margin-bottom: 1rem;
            border-left: 5px solid var(--gold);
            padding-left: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f0f7f0;
            color: var(--dark);
        }
        .img-mini {
            width: 40px;
            height: 40px;
            object-fit: cover;
            border-radius: 8px;
        }
        .btn-dash {
            display: inline-block;
            background: var(--dark);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            margin-top: 15px;
            font-weight: 600;
            transition: 0.2s;
        }
        .btn-dash:hover { background: #3c8c4a; }
        .volver {
            display: inline-block;
            margin-top: 20px;
            color: var(--dark);
            text-decoration: none;
            font-weight: 600;
        }
        @media (max-width: 768px) {
            .chart-grid { grid-template-columns: 1fr; }
            header { flex-direction: column; gap: 10px; }
        }
    </style>
</head>
<body>
<header>
    <a class="brand" href="/">Abarrotes <span>Flor</span></a>
    <nav>
        <a href="/">Inicio</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/admin/productos">Productos</a>
        <a href="/logout">Cerrar sesión</a>
    </nav>
</header>

<div class="container">
    <h2 style="margin-top:1.5rem; color: #2a6e3f;">Panel de Administración</h2>

    <div class="kpi-grid">
        <div class="kpi-card">
            <h3>Productos</h3>
            <div class="valor">{{ total_productos }}</div>
            <div class="referencia">
                {% if variacion_productos > 0 %}
                    +{{ variacion_productos }} vs. inicio (7)
                {% elif variacion_productos < 0 %}
                    {{ variacion_productos }} vs. inicio (7)
                {% else %}
                    Sin cambios
                {% endif %}
            </div>
        </div>
        <div class="kpi-card">
            <h3>Precio promedio</h3>
            <div class="valor">S/ {{ "%.2f"|format(precio_promedio) }}</div>
            <div class="referencia">Meta: S/ 5.50</div>
        </div>
        <div class="kpi-card">
            <h3>Clientes</h3>
            <div class="valor">{{ total_clientes }}</div>
            <div class="referencia">Objetivo: 50</div>
        </div>
        <div class="kpi-card">
            <h3>Ventas del mes</h3>
            <div class="valor">S/ {{ "%.2f"|format(ventas_mes) }}</div>
            <div class="referencia">Mes anterior: S/ 0.00</div>
        </div>
    </div>

    <div class="chart-grid">
        <div class="chart-box">
            <h3>Ventas últimos 7 días</h3>
            <div style="position: relative; height: 260px;">
                <canvas id="lineChart"></canvas>
            </div>
        </div>
        <div class="chart-box">
            <h3>Registros Recientes (Clientes vs Productos)</h3>
            <div style="position: relative; height: 260px;">
                <canvas id="barChart"></canvas>
            </div>
        </div>
    </div>

    <div class="seccion">
        <h2>Últimos Clientes Registrados</h2>
        {% if ultimos_clientes %}
        <table>
            <thead><tr><th>ID</th><th>Nombre</th><th>Email</th><th>Teléfono</th><th>Dirección</th></tr></thead>
            <tbody>
                {% for c in ultimos_clientes %}
                <tr>
                    <td>{{ c.id }}</td>
                    <td>{{ c.nombre }}</td>
                    <td>{{ c.email }}</td>
                    <td>{{ c.telefono }}</td>
                    <td>{{ c.direccion }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No hay clientes registrados aún.</p>
        {% endif %}
        <a href="/" class="btn-dash">Ver panel de clientes</a>
    </div>

    <div class="seccion">
        <h2>Últimos Productos Agregados</h2>
        {% if ultimos_productos %}
        <table>
            <thead><tr><th>ID</th><th>Imagen</th><th>Nombre</th><th>Descripción</th><th>Precio</th></tr></thead>
            <tbody>
                {% for p in ultimos_productos %}
                <tr>
                    <td>{{ p.id }}</td>
                    <td><img src="{{ p.imagen }}" class="img-mini" onerror="this.src='https://via.placeholder.com/40'"></td>
                    <td>{{ p.nombre }}</td>
                    <td>{{ p.descripcion[:50] }}</td>
                    <td>S/ {{ p.precio }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No hay productos dinámicos aún. <a href="/admin/productos/agregar">Agrega uno</a></p>
        {% endif %}
        <a href="/admin/productos" class="btn-dash">Gestionar productos</a>
    </div>

    <div class="actualizacion">
        Última actualización: {{ hora_actual }}
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
    // Gráfico de Líneas (Ventas)
    const ctxLine = document.getElementById('lineChart').getContext('2d');
    new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: {{ dias | tojson }},
            datasets: [{
                label: 'Ventas (S/)',
                data: {{ ventas_diarias | tojson }},
                borderColor: '#2a6e3f',
                backgroundColor: 'rgba(42, 110, 63, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Gráfico de Barras (Registros Recientes)
    const ctxBar = document.getElementById('barChart').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: {{ dias | tojson }},
            datasets: [
                {
                    label: 'Nuevos Clientes',
                    data: {{ nuevos_clientes_linea | tojson }},
                    backgroundColor: '#c89a3e'
                },
                {
                    label: 'Nuevos Productos',
                    data: {{ nuevos_productos_linea | tojson }},
                    backgroundColor: '#2a6e3f'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
</script>
</body>
</html>
"""

# -----------------------------------------------------------

@app.route("/registrarse", methods=["GET", "POST"])
def registrarse():
    mensaje_ok = ""
    mensaje_error = ""

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()

        if not nombre or not email or not telefono:
            mensaje_error = "Por favor completa los campos obligatorios (*)."
        else:
            nuevo = {
                "id": registro_contador[0],
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "direccion": direccion if direccion else "—",
            }
            clientes_registrados.append(nuevo)
            registro_contador[0] += 1
            mensaje_ok = f"¡Registro exitoso! Bienvenido/a, {nombre}."

    html_reg = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registrarse — Abarrotes Flor</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            *{{ margin:0; padding:0; box-sizing:border-box; }}
            body{{ font-family:'Poppins',Arial,sans-serif; background:#f4f4f4; color:#333; line-height:1.6; }}
            header{{
                background:linear-gradient(135deg, #2a6e3f 0%, #54a358 100%);
                padding:30px 20px;
                display:flex;
                justify-content:center;
                align-items:center;
                gap:20px;
                position:relative;
                box-shadow:0 4px 15px rgba(0,0,0,0.1);
            }}
            .logo{{
                width:90px;
                height:90px;
                border-radius:50%;
                object-fit:cover;
                border:4px solid rgba(255,255,255,0.9);
                box-shadow:0 4px 12px rgba(0,0,0,0.2);
                transition:transform 0.3s;
            }}
            .logo:hover{{ transform:scale(1.05); }}
            header h1{{ font-size:32px; letter-spacing:1.5px; color:white; font-weight:700; text-shadow:2px 2px 4px rgba(0,0,0,0.3); }}
            header h2{{ font-size:15px; font-weight:300; color:rgba(255,255,255,0.9); margin-top:5px; }}
            nav{{
                background:#2a6e3f;
                display:flex;
                justify-content:center;
                padding:12px 20px;
                gap:15px;
                box-shadow:0 2px 10px rgba(0,0,0,0.1);
            }}
            nav a{{
                color:white;
                text-decoration:none;
                padding:8px 18px;
                border-radius:25px;
                font-weight:600;
                transition:all 0.3s ease;
                font-size:14px;
                background:rgba(255,255,255,0.1);
            }}
            nav a:hover{{ background:rgba(255,255,255,0.25); transform:translateY(-2px); }}
            main{{ display:flex; justify-content:center; padding:40px 20px; }}
            .card{{
                background:white;
                border-radius:20px;
                padding:40px 45px;
                width:100%;
                max-width:500px;
                box-shadow:0 10px 40px rgba(0,0,0,0.08);
                transition:all 0.3s ease;
            }}
            .card h2{{ color:#2a6e3f; margin-bottom:8px; font-size:26px; font-weight:700; }}
            .card p.sub{{ color:#777; font-size:15px; margin-bottom:28px; font-weight:300; }}
            label{{ font-weight:600; font-size:13px; color:#444; display:block; margin-bottom:6px; }}
            input{{
                width:100%;
                padding:12px 16px;
                border:1.5px solid #e0e0e0;
                border-radius:12px;
                outline:none;
                font-size:14px;
                margin-bottom:18px;
                transition:all 0.3s;
                font-family:'Poppins',sans-serif;
                background:#fafafa;
            }}
            input:focus{{ border-color:#2a6e3f; background:white; box-shadow:0 0 0 3px rgba(42,110,63,0.1); }}
            .btn{{
                width:100%;
                background:linear-gradient(135deg, #2a6e3f, #3c8c4a);
                color:white;
                border:none;
                padding:14px;
                border-radius:12px;
                font-size:16px;
                font-weight:600;
                cursor:pointer;
                transition:all 0.3s ease;
                margin-top:8px;
                letter-spacing:0.5px;
            }}
            .btn:hover{{ background:linear-gradient(135deg, #3c8c4a, #54a358); transform:translateY(-2px); box-shadow:0 6px 20px rgba(42,110,63,0.3); }}
            .ok{{ background:#d4edda; color:#155724; padding:14px 16px; border-radius:12px; margin-bottom:22px; font-weight:600; font-size:14px; border-left:5px solid #2a6e3f; }}
            .err{{ background:#f8d7da; color:#842029; padding:14px 16px; border-radius:12px; margin-bottom:22px; font-weight:600; font-size:14px; border-left:5px solid #e74c3c; }}
            .volver{{ display:block; text-align:center; margin-top:22px; color:#2a6e3f; font-size:15px; text-decoration:none; font-weight:600; transition:0.2s; }}
            .volver:hover{{ text-decoration:underline; }}
            footer{{
                background:#2a6e3f;
                color:white;
                text-align:center;
                padding:28px 20px;
                margin-top:40px;
                line-height:2;
                font-size:14px;
                font-weight:300;
            }}
            footer strong{{ font-weight:600; }}
            @media (max-width:600px){{
                .card{{ padding:30px 25px; }}
                header h1{{ font-size:26px; }}
            }}
        </style>
    </head>
    <body>
        <header>
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVZKJvLpOiAC95AOTzK1GfCKrVR6VxStjBfg&s" class="logo">
            <div>
                <h1>ABARROTES FLOR</h1>
                <h2>Frescura y calidad para tu hogar</h2>
            </div>
        </header>
        <nav>
            <a href="/">Inicio</a>
        </nav>
        <main>
            <div class="card">
                <h2>Crear cuenta</h2>
                <p class="sub">Regístrate para acceder a ofertas exclusivas</p>

                {"<div class='ok'>" + mensaje_ok + "</div>" if mensaje_ok else ""}
                {"<div class='err'>" + mensaje_error + "</div>" if mensaje_error else ""}

                <form method="POST">
                    <label>Nombre completo *</label>
                    <input type="text" name="nombre" placeholder="Ej: María García" required>

                    <label>Correo electrónico *</label>
                    <input type="email" name="email" placeholder="Ej: maria@gmail.com" required>

                    <label>Teléfono *</label>
                    <input type="text" name="telefono" placeholder="Ej: 987654321" required>

                    <label>Dirección (opcional)</label>
                    <input type="text" name="direccion" placeholder="Ej: Av. Lima 456, Miraflores">

                    <button type="submit" class="btn">Registrarme</button>
                </form>
                <a href="/" class="volver">← Volver al inicio</a>
            </div>
        </main>
        <footer>
            <p><strong>Abarrotes Flor © 2026</strong></p>
            <p>Av. Santa Rosa de Lima - Lima &nbsp;|&nbsp; Tel: 918-787-936</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(html_reg)


@app.route("/", methods=["GET", "POST"])
def pagina():

    # Usar sesión para mantener autenticación
    usuario_autenticado = session.get("autenticado", False)
    mensaje_error = ""

    # Cargar productos agregados desde el panel de administración
    productos_dinamicos = cargar_productos()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == USUARIO_CORRECTO and password == CONTRASENA_CORRECTA:
            session["autenticado"] = True
            usuario_autenticado = True
        else:
            mensaje_error = "Credenciales incorrectas. Inténtalo nuevamente."

    css = """
    *{
        margin:0;
        padding:0;
        box-sizing:border-box;
    }

    body{
        font-family:'Poppins', Arial, sans-serif;
        background:#f9fafb;
        color:#333;
        line-height:1.6;
    }

    header{
        background: linear-gradient(135deg, #2a6e3f 0%, #54a358 100%);
        padding:30px 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        position: relative;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .logo{
        width:90px;
        height:90px;
        border-radius:50%;
        object-fit:cover;
        border:4px solid rgba(255,255,255,0.9);
        box-shadow:0 4px 12px rgba(0,0,0,0.2);
        transition:transform 0.3s;
    }
    .logo:hover{
        transform:scale(1.05);
    }

    header h1{
        color:white;
        font-size:34px;
        letter-spacing:1.5px;
        font-weight:700;
        text-shadow:2px 2px 4px rgba(0,0,0,0.3);
    }

    header h2{
        color:rgba(255,255,255,0.9);
        margin-top:6px;
        font-size:16px;
        font-weight:300;
    }

    nav{
        background:#2a6e3f;
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:12px 30px;
        flex-wrap:wrap;
        gap:15px;
        box-shadow:0 2px 10px rgba(0,0,0,0.1);
    }

    .nav-links{
        display:flex;
        gap:10px;
        align-items:center;
    }

    nav a, nav .nav-btn{
        color:white;
        text-decoration:none;
        padding:8px 18px;
        border-radius:25px;
        font-weight:600;
        transition:all 0.3s ease;
        font-size:14px;
        background:rgba(255,255,255,0.1);
        cursor:pointer;
    }

    nav a:hover, nav .nav-btn:hover, nav a.active, nav .nav-btn.active{
        background:rgba(255,255,255,0.25);
        transform:translateY(-2px);
    }

    .login-form{
        display:flex;
        gap:8px;
        align-items:center;
    }

    .login-form input{
        padding:9px 14px;
        border:none;
        border-radius:25px;
        outline:none;
        font-size:13px;
        background:rgba(255,255,255,0.9);
        transition:0.2s;
        font-family:'Poppins',sans-serif;
    }
    .login-form input:focus{
        box-shadow:0 0 0 3px rgba(255,255,255,0.5);
    }

    .login-form button{
        background:#54a358;
        color:white;
        border:none;
        padding:9px 18px;
        border-radius:25px;
        cursor:pointer;
        font-weight:600;
        transition:0.2s;
        font-size:13px;
    }

    .login-form button:hover{
        background:#3c8c4a;
        transform:translateY(-1px);
    }

    .user-welcome{
        color:white;
        font-weight:600;
        background:rgba(255,255,255,0.15);
        padding:8px 18px;
        border-radius:25px;
        font-size:14px;
    }

    .alert-error{
        background:#f8d7da;
        color:#842029;
        padding:14px;
        text-align:center;
        font-weight:600;
        border-bottom:3px solid #e74c3c;
        font-size:15px;
    }

    main{
        padding:30px 20px;
        max-width:1300px;
        margin:0 auto;
    }

    section{
        background:white;
        margin-bottom:30px;
        padding:40px;
        border-radius:20px;
        box-shadow:0 8px 30px rgba(0,0,0,0.05);
        transition:box-shadow 0.3s;
    }
    section:hover{
        box-shadow:0 12px 40px rgba(0,0,0,0.08);
    }

    section h2{
        color:#2a6e3f;
        margin-bottom:20px;
        font-size:28px;
        font-weight:700;
    }

    .nosotros{
        display:flex;
        align-items:center;
        gap:30px;
        flex-wrap:wrap;
    }

    .nosotros img{
        width:500px;
        height:300px;
        border-radius:20px;
        object-fit:cover;
        box-shadow:0 6px 20px rgba(0,0,0,0.1);
    }

    .nosotros p{
        flex:1;
        line-height:1.8;
        max-width: 500px;
        text-align: justify;
        font-size: 17px;
        color:#444;
    }

    .panel-admin{
        background:#f0f7f0;
        border:2px solid #2a6e3f;
        border-radius:20px;
    }

    footer{
        background:#2a6e3f;
        color:white;
        text-align:center;
        padding:30px 20px;
        margin-top:30px;
        line-height:2;
        font-size:14px;
        font-weight:300;
    }
    footer strong{
        font-weight:600;
    }

    /* Ofertas y productos */
    .ofertas-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 25px;
        margin-top: 25px;
    }

    .oferta-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .oferta-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        border-color: #54a358;
    }

    .oferta-card img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 15px;
        margin-bottom: 18px;
    }

    .badge-oferta {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        font-size: 12px;
        font-weight: 700;
        padding: 6px 15px;
        border-radius: 25px;
        display: inline-block;
        margin-bottom: 14px;
        letter-spacing: 0.5px;
    }

    .oferta-card h3 {
        color: #2a6e3f;
        margin-bottom: 12px;
        font-size: 20px;
        font-weight: 700;
    }

    .precio-antes {
        color: #999;
        font-size: 14px;
        text-decoration: line-through;
        margin-right: 8px;
    }

    .precio-ahora {
        color: #e53935;
        font-size: 24px;
        font-weight: 700;
    }

    .precio-producto {
        font-size: 20px;
        font-weight: 700;
        color: #2a6e3f;
        margin: 10px 0 15px;
    }

    .btn-adquirir {
        display: inline-block;
        background: linear-gradient(135deg, #2a6e3f, #3c8c4a);
        color: white;
        text-decoration: none;
        padding: 10px 22px;
        border-radius: 30px;
        margin-top: auto;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }

    .btn-adquirir:hover {
        background: linear-gradient(135deg, #3c8c4a, #54a358);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(42,110,63,0.3);
    }

    /* Páginas virtuales */
    .pagina-virtual {
        display: none;
    }
    
    .pagina-virtual.activa {
        display: block;
    }

    /* ----- CARRITO DE COMPRAS (NUEVO) ----- */
    .cart-icon-container {
        position: relative;
        display: inline-flex;
        align-items: center;
        cursor: pointer;
        color: white;
        background: rgba(255,255,255,0.15);
        padding: 8px 16px;
        border-radius: 25px;
        transition: background 0.3s;
        font-weight: 600;
        font-size: 14px;
    }
    .cart-icon-container:hover {
        background: rgba(255,255,255,0.3);
    }
    .cart-badge {
        background: #e53935;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        margin-left: 8px;
    }
    #carrito-modal {
        display: none;
        position: fixed;
        right: 0;
        top: 0;
        width: 380px;
        max-width: 100%;
        height: 100%;
        background: white;
        box-shadow: -4px 0 20px rgba(0,0,0,0.15);
        z-index: 10000;
        flex-direction: column;
        animation: slideIn 0.3s ease;
    }
    #carrito-modal.abierto {
        display: flex;
    }
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    .carrito-header {
        background: #2a6e3f;
        color: white;
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .carrito-header h2 {
        font-size: 22px;
        margin: 0;
    }
    .cerrar-carrito {
        background: transparent;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
    }
    .carrito-items {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
    }
    .carrito-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #eee;
        padding: 12px 0;
    }
    .carrito-item-info {
        flex: 1;
    }
    .carrito-item-nombre {
        font-weight: 600;
    }
    .carrito-item-precio {
        color: #2a6e3f;
        font-size: 16px;
        font-weight: 700;
    }
    .carrito-item-acciones {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .carrito-cantidad {
        width: 50px;
        padding: 4px;
        border: 1px solid #ccc;
        border-radius: 8px;
        text-align: center;
    }
    .btn-eliminar {
        background: #e74c3c;
        color: white;
        border: none;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        font-size: 16px;
        cursor: pointer;
        font-weight: bold;
    }
    .carrito-footer {
        padding: 20px;
        border-top: 2px solid #2a6e3f;
    }
    .carrito-total {
        font-size: 22px;
        font-weight: 700;
        color: #2a6e3f;
        margin-bottom: 15px;
    }
    .btn-vaciar {
        background: #e74c3c;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 25px;
        width: 100%;
        font-weight: 600;
        cursor: pointer;
        transition: 0.2s;
    }
    .btn-vaciar:hover {
        background: #c0392b;
    }
    .carrito-vacio {
        text-align: center;
        color: #888;
        margin-top: 60px;
        font-size: 16px;
    }
    @media (max-width: 480px) {
        #carrito-modal {
            width: 100%;
        }
    }
    /* Responsive */
    @media (max-width: 768px) {
        .nosotros {
            flex-direction: column;
        }
        .nosotros img {
            width: 100%;
            height: auto;
        }
        nav {
            flex-direction: column;
            align-items: center;
        }
        .login-form {
            flex-wrap: wrap;
            justify-content: center;
        }
        section {
            padding: 25px;
        }
        header h1 {
            font-size: 26px;
        }
        .ofertas-grid {
            grid-template-columns: 1fr;
        }
    }
    """

    if usuario_autenticado:
        nav_auth_html = f"""
        <div style="display:flex; gap:10px; align-items:center;">
            <span class="user-welcome">
                ¡Hola, {USUARIO_CORRECTO}!
            </span>
            <a href="/dashboard" style="color:white; font-weight:600; font-size:13px; background:rgba(255,255,255,0.2); padding:8px 16px; border-radius:25px; text-decoration:none;">
                Dashboard
            </a>
            <a href="/admin/productos" style="color:white; font-weight:600; font-size:13px; background:rgba(255,255,255,0.2); padding:8px 16px; border-radius:25px; text-decoration:none;">
                Admin Productos
            </a>
            <a href="/logout" style="color:white; font-weight:600; font-size:13px; background:rgba(255,255,255,0.2); padding:8px 16px; border-radius:25px; text-decoration:none;">
                Cerrar sesión
            </a>
        </div>
        """
    else:
        nav_auth_html = """
        <div style="display:flex; gap:8px; align-items:center;">
            <form class="login-form" method="POST" style="display:flex; gap:8px;">
                <input type="email" name="email" placeholder="Correo" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Ingresar</button>
            </form>
            <a href="/registrarse" style="color:white; font-weight:600; font-size:13px; background:rgba(255,255,255,0.2); padding:8px 16px; border-radius:25px; text-decoration:none;">
                Registrarse
            </a>
        </div>
        """

    if usuario_autenticado:
        filas_registrados = ""
        if clientes_registrados:
            for i, c in enumerate(clientes_registrados):
                bg = "#f9fdf9" if i % 2 == 0 else "#ffffff"
                filas_registrados += f"""<tr style="border-bottom:1px solid #e0e0e0; background:{bg};">
                    <td style="padding:12px 14px;">{c['id']}</td>
                    <td style="padding:12px 14px; font-weight:600;">{c['nombre']}</td>
                    <td style="padding:12px 14px;">{c['email']}</td>
                    <td style="padding:12px 14px;">{c['telefono']}</td>
                    <td style="padding:12px 14px;">{c['direccion']}</td>
                </tr>"""
        else:
            filas_registrados = '<tr><td colspan="5" style="padding:20px; text-align:center; color:#888;">Aún no hay clientes registrados desde la web.</td></tr>'

        total_reg = len(clientes_registrados)

        seccion_admin_html = f"""
        <section class="panel-admin" id="panel-admin-section">

            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h2 style="margin:0;">Panel de Administración — Gestión de Clientes</h2>
                <button onclick="togglePanel()" id="btn-toggle-panel"
                    style="background:#2a6e3f; color:white; border:none; padding:8px 16px; border-radius:25px; cursor:pointer; font-weight:600; font-size:13px; transition:0.2s;">
                    ▲ Colapsar
                </button>
            </div>

            <div id="contenido-panel">

                <div style="margin-bottom:35px;">
                    <h3 style="color:#2a6e3f; margin-bottom:15px; font-size:18px;">
                        Clientes Registrados desde la Web
                        <span style="background:#2a6e3f; color:white; border-radius:20px; padding:2px 12px; font-size:14px; margin-left:8px;">{total_reg}</span>
                    </h3>
                    <div style="overflow-x:auto; border-radius:15px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                        <table style="width:100%; border-collapse:collapse; font-size:14px;">
                            <thead>
                                <tr style="background:#2a6e3f; color:white;">
                                    <th style="padding:14px 16px; text-align:left;">#</th>
                                    <th style="padding:14px 16px; text-align:left;">Nombre</th>
                                    <th style="padding:14px 16px; text-align:left;">Email</th>
                                    <th style="padding:14px 16px; text-align:left;">Teléfono</th>
                                    <th style="padding:14px 16px; text-align:left;">Dirección</th>
                                </tr>
                            </thead>
                            <tbody>{filas_registrados}</tbody>
                        </table>
                    </div>
                </div>

                <hr style="border:none; border-top:2px dashed #b2d8b5; margin-bottom:28px;">

                <h3 style="color:#2a6e3f; margin-bottom:18px; font-size:18px;">Gestión Manual de Clientes</h3>

                <div style="margin-bottom:25px; display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
                    <input
                        type="text"
                        id="buscar-cliente"
                        placeholder="Buscar por nombre o teléfono..."
                        oninput="buscarCliente()"
                        style="padding:10px 16px; border:1.5px solid #2a6e3f; border-radius:25px; outline:none; min-width:250px; font-size:14px; font-family:'Poppins',sans-serif; background:#fafafa;"
                    >
                    <button onclick="abrirModalAgregar()" style="background:linear-gradient(135deg, #2a6e3f, #3c8c4a); color:white; border:none; padding:10px 20px; border-radius:25px; cursor:pointer; font-weight:600; font-size:14px; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
                        + Agregar Cliente
                    </button>
                </div>

                <div style="overflow-x:auto; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.05);">
                    <table id="tabla-clientes" style="width:100%; border-collapse:collapse; font-size:14px;">
                        <thead>
                            <tr style="background:#2a6e3f; color:white;">
                                <th style="padding:12px 14px; text-align:left;">#</th>
                                <th style="padding:12px 14px; text-align:left;">Nombre</th>
                                <th style="padding:12px 14px; text-align:left;">Teléfono</th>
                                <th style="padding:12px 14px; text-align:left;">Dirección</th>
                                <th style="padding:12px 14px; text-align:center;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="cuerpo-tabla"></tbody>
                    </table>
                    <p id="sin-resultados" style="display:none; color:#888; text-align:center; padding:25px;">No se encontraron clientes.</p>
                </div>

            </div>

        </section>

        <!-- MODAL AGREGAR / EDITAR -->
        <div id="modal-cliente" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; justify-content:center; align-items:center; backdrop-filter: blur(3px);">
            <div style="background:white; padding:35px; border-radius:20px; width:420px; max-width:95%; box-shadow:0 15px 40px rgba(0,0,0,0.2);">
                <h3 id="modal-titulo" style="color:#2a6e3f; margin-bottom:22px; font-size:22px; font-weight:700;">Agregar Cliente</h3>

                <label style="font-weight:600; font-size:13px; color:#555;">Nombre completo *</label><br>
                <input type="text" id="inp-nombre" placeholder="Ej: Juan Perez"
                    style="width:100%; padding:10px 14px; border:1.5px solid #ddd; border-radius:12px; margin:6px 0 16px; outline:none; font-size:14px; font-family:'Poppins',sans-serif; background:#fafafa;">

                <label style="font-weight:600; font-size:13px; color:#555;">Teléfono *</label><br>
                <input type="text" id="inp-telefono" placeholder="Ej: 987654321"
                    style="width:100%; padding:10px 14px; border:1.5px solid #ddd; border-radius:12px; margin:6px 0 16px; outline:none; font-size:14px; font-family:'Poppins',sans-serif; background:#fafafa;">

                <label style="font-weight:600; font-size:13px; color:#555;">Dirección</label><br>
                <input type="text" id="inp-direccion" placeholder="Ej: Av. Lima 123"
                    style="width:100%; padding:10px 14px; border:1.5px solid #ddd; border-radius:12px; margin:6px 0 22px; outline:none; font-size:14px; font-family:'Poppins',sans-serif; background:#fafafa;">

                <div id="modal-error" style="display:none; background:#f8d7da; color:#842029; padding:10px 14px; border-radius:10px; margin-bottom:16px; font-size:13px; border-left:4px solid #e74c3c;"></div>

                <div style="display:flex; gap:10px; justify-content:flex-end;">
                    <button onclick="cerrarModal()" style="background:#eee; color:#333; border:none; padding:10px 20px; border-radius:25px; cursor:pointer; font-weight:600; transition:0.2s;">Cancelar</button>
                    <button onclick="guardarCliente()" style="background:linear-gradient(135deg, #2a6e3f, #3c8c4a); color:white; border:none; padding:10px 20px; border-radius:25px; cursor:pointer; font-weight:600; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.1);">Guardar</button>
                </div>
            </div>
        </div>

        <!-- MODAL ELIMINAR -->
        <div id="modal-eliminar" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; justify-content:center; align-items:center; backdrop-filter: blur(3px);">
            <div style="background:white; padding:35px; border-radius:20px; width:360px; max-width:95%; box-shadow:0 15px 40px rgba(0,0,0,0.2); text-align:center;">
                <h3 style="color:#b22222; margin-bottom:12px;">¿Eliminar cliente?</h3>
                <p id="confirmar-nombre" style="color:#555; margin-bottom:25px; font-size:16px;"></p>
                <div style="display:flex; gap:10px; justify-content:center;">
                    <button onclick="cerrarModalEliminar()" style="background:#eee; color:#333; border:none; padding:10px 22px; border-radius:25px; cursor:pointer; font-weight:600; transition:0.2s;">Cancelar</button>
                    <button onclick="confirmarEliminar()" style="background:#c0392b; color:white; border:none; padding:10px 22px; border-radius:25px; cursor:pointer; font-weight:600; transition:0.2s; box-shadow:0 4px 10px rgba(192,57,43,0.3);">Eliminar</button>
                </div>
            </div>
        </div>
        """
    else:
        seccion_admin_html = ""

    if mensaje_error:
        error_html = f"""
        <div class="alert-error">
            {mensaje_error}
        </div>
        """
    else:
        error_html = ""

    # Generar las tarjetas para los productos dinámicos (los que vienen del JSON)
    productos_dinamicos_html = ""
    for p in productos_dinamicos:
        productos_dinamicos_html += f"""
        <div class="oferta-card">
            <span class="badge-oferta">Nuevo</span>
            <h3>{p['nombre']}</h3>
            <img src="{p['imagen']}" alt="{p['nombre']}" onerror="this.src='https://via.placeholder.com/150'">
            <p>{p['descripcion'][:100]}</p>
            <p class="precio-producto">S/ {p['precio']:.2f}</p>
            <a href="#" class="btn-adquirir">Pedir Producto</a>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Abarrotes Flor</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            {css}
        </style>
    </head>
    <body>
        {error_html}

        <header>
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVZKJvLpOiAC95AOTzK1GfCKrVR6VxStjBfg&s" class="logo">
            <div>
                <h1>ABARROTES FLOR</h1>
                <h2>Frescura y calidad para tu hogar</h2>
            </div>
        </header>

        <nav>
            <div class="nav-links">
                <a onclick="irA('inicio')" id="btn-inicio" class="nav-btn active">Inicio</a>
                <a onclick="irA('nosotros')" id="btn-nosotros" class="nav-btn">Nosotros</a>
                <a onclick="irA('productos')" id="btn-productos" class="nav-btn">Productos</a>
                <!-- Botón carrito -->
                <span class="cart-icon-container" onclick="toggleCarrito()">
                    🛒 Carrito
                    <span id="cart-badge" class="cart-badge">0</span>
                </span>
            </div>
            {nav_auth_html}
        </nav>

        <!-- Modal del carrito -->
        <div id="carrito-modal">
            <div class="carrito-header">
                <h2>Tu Carrito</h2>
                <button class="cerrar-carrito" onclick="toggleCarrito()">&times;</button>
            </div>
            <div class="carrito-items" id="carrito-items">
                <div class="carrito-vacio">El carrito está vacío</div>
            </div>
            <div class="carrito-footer">
                <div class="carrito-total" id="carrito-total">Total: S/ 0.00</div>
                <button class="btn-vaciar" onclick="vaciarCarrito()">Vaciar Carrito</button>
            </div>
        </div>

        <main>
            {seccion_admin_html}

            <div id="vista-inicio" class="pagina-virtual activa">
                <section>
                    <h2>Ofertas de la Semana</h2>
                    <p>Aprovecha nuestros combos especiales y ahorra al máximo en las compras para tu hogar.</p>

                    <div class="ofertas-grid">
                        <!-- combos sin cambios (no se agregan al carrito, solo como info) -->
                        <div class="oferta-card">
                            <span class="badge-oferta">COMBO DESAYUNO</span>
                            <h3>Leche + Avena Integral</h3>
                            <p>Ideal para empezar tus mañanas con toda la energía.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 9.50</span>
                                <span class="precio-ahora">S/ 7.90</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Combo</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">OFERTA DE LOCURA</span>
                            <h3>Kilo de Mandarina Fresca</h3>
                            <p>Recién traídas del campo, dulces y jugosas.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 4.50</span>
                                <span class="precio-ahora">S/ 2.90</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Oferta</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">COMBO LIMPIEZA</span>
                            <h3>Detergente + Lavavajillas</h3>
                            <p>Los mejores aliados para mantener tu hogar impecable.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 16.00</span>
                                <span class="precio-ahora">S/ 13.50</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Combo</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">COMBO ESCOLAR</span>
                            <h3>Galletas + Jugo + Fruta</h3>
                            <p>El combo perfecto para la lonchera de tus hijos.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 8.00</span>
                                <span class="precio-ahora">S/ 6.50</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Combo</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">OFERTA DE LOCURA</span>
                            <h3>Papa x Kilo + Cebolla + Tomate</h3>
                            <p>Base de toda buena cocina peruana al mejor precio.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 7.00</span>
                                <span class="precio-ahora">S/ 5.50</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Oferta</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">COMBO PANADERÍA</span>
                            <h3>Pan Francés x6 + Mantequilla</h3>
                            <p>Desayuno clásico y delicioso para toda la familia.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 10.00</span>
                                <span class="precio-ahora">S/ 7.90</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Combo</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">OFERTA DE LOCURA</span>
                            <h3>Arroz 1kg + Frijoles 500g</h3>
                            <p>La dupla peruana infaltable para el almuerzo de la semana.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 11.00</span>
                                <span class="precio-ahora">S/ 8.90</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Oferta</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">COMBO SNACK</span>
                            <h3>Chifles + Maní + Gaseosa 1.5L</h3>
                            <p>El combo ideal para disfrutar con amigos y familia.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 14.00</span>
                                <span class="precio-ahora">S/ 11.50</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Combo</a>
                        </div>
                        <div class="oferta-card">
                            <span class="badge-oferta">COMBO CENA</span>
                            <h3>Fideos + Salsa de Tomate + Queso</h3>
                            <p>Una cena rápida, económica y deliciosa.</p>
                            <div style="margin-top: 15px;">
                                <span class="precio-antes">S/ 13.50</span>
                                <span class="precio-ahora">S/ 10.90</span>
                            </div>
                            <a href="#" class="btn-adquirir">Pedir Combo</a>
                        </div>
                    </div>
                </section>
            </div>

            <div id="vista-nosotros" class="pagina-virtual">
                <section>
                    <h2>Sobre Nosotros</h2>
                    <div class="nosotros">
                        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAYJG_LADeNWlACrAATh0kwE0dhm4PQRqAgg&s">
                        <p>
                            En Abarrotes Flor ofrecemos productos frescos,
                            lácteos, abarrotes y artículos esenciales
                            para tu hogar con la mejor atención y los mejores
                            precios para tu comodidad con ofertas de locura.
                        </p>
                    </div>
                </section>

                <section>
                    <h2>¿Por qué elegirnos?</h2>
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:25px; margin-top:25px;">
                        <div style="text-align:center; padding:30px 25px; background:#f9fdf9; border-radius:20px; border:1px solid #c8e6c9; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                            <div style="font-size:42px; margin-bottom:14px;">🌿</div>
                            <h3 style="color:#2a6e3f; margin-bottom:10px; font-size:18px;">Productos Frescos</h3>
                            <p style="color:#555; line-height:1.7;">Seleccionamos cada producto directamente con los mejores proveedores de Lima y regiones.</p>
                        </div>
                        <div style="text-align:center; padding:30px 25px; background:#f9fdf9; border-radius:20px; border:1px solid #c8e6c9; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                            <div style="font-size:42px; margin-bottom:14px;">💰</div>
                            <h3 style="color:#2a6e3f; margin-bottom:10px; font-size:18px;">Precios Justos</h3>
                            <p style="color:#555; line-height:1.7;">Ofrecemos los mejores precios del barrio con ofertas semanales para que tu bolsillo alcance más.</p>
                        </div>
                        <div style="text-align:center; padding:30px 25px; background:#f9fdf9; border-radius:20px; border:1px solid #c8e6c9; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                            <div style="font-size:42px; margin-bottom:14px;">🤝</div>
                            <h3 style="color:#2a6e3f; margin-bottom:10px; font-size:18px;">Atención Cercana</h3>
                            <p style="color:#555; line-height:1.7;">Somos un negocio familiar que conoce a sus clientes. Te atendemos con cariño y confianza.</p>
                        </div>
                        <div style="text-align:center; padding:30px 25px; background:#f9fdf9; border-radius:20px; border:1px solid #c8e6c9; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                            <div style="font-size:42px; margin-bottom:14px;">🏪</div>
                            <h3 style="color:#2a6e3f; margin-bottom:10px; font-size:18px;">Local Propio</h3>
                            <p style="color:#555; line-height:1.7;">Contamos con un local amplio y ordenado en Av. Santa Rosa de Lima, fácil de encontrar.</p>
                        </div>
                        <div style="text-align:center; padding:30px 25px; background:#f9fdf9; border-radius:20px; border:1px solid #c8e6c9; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                            <div style="font-size:42px; margin-bottom:14px;">⏰</div>
                            <h3 style="color:#2a6e3f; margin-bottom:10px; font-size:18px;">Horario Amplio</h3>
                            <p style="color:#555; line-height:1.7;">Abrimos de lunes a sábado de 7:00 AM a 9:00 PM para que siempre nos encuentres disponibles.</p>
                        </div>
                        <div style="text-align:center; padding:30px 25px; background:#f9fdf9; border-radius:20px; border:1px solid #c8e6c9; transition:0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                            <div style="font-size:42px; margin-bottom:14px;">📦</div>
                            <h3 style="color:#2a6e3f; margin-bottom:10px; font-size:18px;">Variedad Total</h3>
                            <p style="color:#555; line-height:1.7;">Desde frutas y verduras hasta lácteos, abarrotes, snacks y productos de limpieza en un solo lugar.</p>
                        </div>
                    </div>
                </section>
            </div>

            <div id="vista-productos" class="pagina-virtual">
                <section>
                    <h2>Nuestros Productos</h2>
                    <p>Los productos con la mayor frescura y calidad directo a tu mesa.</p>

                    <div class="ofertas-grid">
                        <!-- TODOS LOS PRODUCTOS ORIGINALES AQUÍ -->
                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Manzana</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTefUHgejxyLcdttT_ovpNnkWpHNzXHDsN9RQ&s" alt="manzana">
                            <p>Manzanas seleccionadas, dulces y crujientes.</p>
                            <p class="precio-producto">S/ 3.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Plátano</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStP3GhAe2hFpPDHhYRSFers5V2xidAaDkUJw&s" alt="platano">
                            <p>Plátanos ricos en potasio en su madurez ideal.</p>
                            <p class="precio-producto">S/ 2.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Mandarina</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQuYcbfyDFJhMYa3Kv3RjnlT_m_fjhVKH8kwQ&s" alt="mandarina">
                            <p>Mandarinas jugosas y dulces, recién llegadas.</p>
                            <p class="precio-producto">S/ 2.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Naranja</h3>
                            <img src="https://img.freepik.com/vector-gratis/fondo-naranja-acuarela_52683-10330.jpg?w=360" alt="naranja">
                            <p>Naranjas para jugo o para comer, muy frescas.</p>
                            <p class="precio-producto">S/ 3.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Papaya</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQaAXtZXW0NwXfeThZW9BbWaT36At6cOjfv4Q&s" alt="papaya">
                            <p>Papaya madura y dulce, ideal para el desayuno.</p>
                            <p class="precio-producto">S/ 5.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Mango</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSe4OzPMUZFtQ-TJxNf5k37h07WhwkJjgkezQ&s" alt="mango">
                            <p>Mangos jugosos de temporada, dulces y aromáticos.</p>
                            <p class="precio-producto">S/ 4.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Uva</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTnxd34tV-o8Jj4jzMzIgeV-rKRk0UU5RCRg&s" alt="uva">
                            <p>Uvas verdes sin pepa, frescas y crujientes.</p>
                            <p class="precio-producto">S/ 6.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Fresa</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTe2kS5KTJqHvC9KQjVwFXsTL8PTJryKhSB4g&s" alt="fresa">
                            <p>Fresas seleccionadas, perfectas para jugos y postres.</p>
                            <p class="precio-producto">S/ 4.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Piña</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTe7looVC_9fWTCfWNkiEWjQQ1oY3Kqc1sIKw&s" alt="piña">
                            <p>Piña entera o en rodajas, dulce y tropical.</p>
                            <p class="precio-producto">S/ 5.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">FRUTA FRESCA</span>
                            <h3>Pera</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQUIBpLacU-to2ZYt1K1ca787cJRml8xMmd-w&s" alt="pera">
                            <p>Peras suaves y jugosas, ideales para la lonchera.</p>
                            <p class="precio-producto">S/ 3.80</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Tomate</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZCXxDyXhL2MDRrGS8h5re1vNdYwqa9DvuHg&s" alt="tomate">
                            <p>Tomates frescos de primera calidad para tus guisos.</p>
                            <p class="precio-producto">S/ 2.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Cebolla</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTPFLV-d-xeWVqv6UEpttSs8ARIgH0b6niuQ&s" alt="cebolla">
                            <p>Cebollas blancas y rojas para tus preparaciones.</p>
                            <p class="precio-producto">S/ 1.80</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Papa</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4lkwrluya9UQS4RcO5N6YJYNrRLecOLekIQ&s" alt="papa">
                            <p>Papas peruanas de las mejores variedades.</p>
                            <p class="precio-producto">S/ 2.20</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Zanahoria</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRDH74leA8h3ufNgIkjOCJJPzWFEvKcEAy2cQ&s" alt="zanahoria">
                            <p>Zanahorias frescas y crujientes, ricas en vitaminas.</p>
                            <p class="precio-producto">S/ 1.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Lechuga</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzm8RNveW6_YmoZfMWjvAmE9A6UxGWqr-AKw&s" alt="lechuga">
                            <p>Lechuga fresca para tus ensaladas diarias.</p>
                            <p class="precio-producto">S/ 1.20</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Espinaca</h3>
                            <img src="https://www.gastronomiavasca.net/uploads/image/file/3368/espinacas.jpg" alt="espinaca">
                            <p>Espinaca tierna, ideal para jugos y saltados.</p>
                            <p class="precio-producto">S/ 1.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Beterraga</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSZ7nj6j1td97MgksoIpH8dlE4EtAyFZVmZDw&s" alt="beterraga">
                            <p>Beterraga fresca, perfecta para ensaladas y jugos.</p>
                            <p class="precio-producto">S/ 2.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Pimiento</h3>
                            <img src="https://plazavea.vteximg.com.br/arquivos/ids/226561-418-418/pimiento-morron.jpg" alt="pimiento">
                            <p>Pimientos rojos y verdes para tus guisos y salsas.</p>
                            <p class="precio-producto">S/ 2.80</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Apio</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2WmhMbLIk7Oj7lSCplpxZ1UnWmEAYs6r78w&s" alt="apio">
                            <p>Apio fresco, ideal para sopas y jugos verdes.</p>
                            <p class="precio-producto">S/ 1.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">VERDURA</span>
                            <h3>Pepino</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS5R5jLKiqyJaBsMyHftLj9dKinvamEY47v0g&s" alt="pepino">
                            <p>Pepinos frescos y crujientes, perfectos para ensaladas.</p>
                            <p class="precio-producto">S/ 1.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LÁCTEOS</span>
                            <h3>Leche Entera</h3>
                            <img src="https://media.falabella.com/tottusPE/43548139_1/w=1500,h=1500,fit=cover" alt="leche entera">
                            <p>Leche de vaca pura, cremosa y pasteurizada.</p>
                            <p class="precio-producto">S/ 4.20</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LÁCTEOS</span>
                            <h3>Yogurt Natural</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhj8HKSomAu92gEXHV02zKt88lrLAlqsi4WQ&s" alt="yogurt natural">
                            <p>Yogurt cremoso sin azúcar, ideal para el desayuno.</p>
                            <p class="precio-producto">S/ 5.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LÁCTEOS</span>
                            <h3>Queso Fresco</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmtiamp3BMghqtvuHqtSxW8mNo9GL5R3XhcQ&s" alt=" queso fresco">
                            <p>Queso blanco suave, perfecto para acompañar tus comidas.</p>
                            <p class="precio-producto">S/ 7.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LÁCTEOS</span>
                            <h3>Mantequilla</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQm63WJ5_oW3bNhG_Ju35zyFWuhmuU60Dj13g&s" alt="mantequilla">
                            <p>Mantequilla cremosa, ideal para repostería y cocina.</p>
                            <p class="precio-producto">S/ 6.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LÁCTEOS</span>
                            <h3>Leche Evaporada</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqhiCw9JX1XfGHth7vhh2aa5FKDK50FI60VA&s" alt="leche evaporada">
                            <p>Leche evaporada para preparar sopas, arroz con leche y más.</p>
                            <p class="precio-producto">S/ 3.80</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Arroz Extra</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSc_q2xxLjOKNxlOF3yV64-VWYri5xJ3D5yTg&s" alt="arroz extra">
                            <p>Arroz blanco de grano largo, cocción perfecta.</p>
                            <p class="precio-producto">S/ 5.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Azúcar Rubia</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT5Sf99Kd8Tv8J_9zAYudffJMjCqe9LF0VsUQ&s" alt="azucar rubia">
                            <p>Azúcar rubia para endulzar tus bebidas y postres.</p>
                            <p class="precio-producto">S/ 3.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Aceite Vegetal</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQuDcamT4KrbJfCMiTJ-rshq2j9sdm4Exiipg&s" alt="aceite vegetal">
                            <p>Aceite vegetal para freír y cocinar sin problema.</p>
                            <p class="precio-producto">S/ 8.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Fideos Spaghetti</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQeWQoWPX31fTydcstq9IZnfwin6ZYxbu6tw&s" alt="fideos spaghetti">
                            <p>Fideos largos de sémola, ideales para pastas y guisos.</p>
                            <p class="precio-producto">S/ 3.20</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Sal de Mesa</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR0xLJeebtlNE44kzkNenDORV9qOBKNRXGyzQ&s" alt="sal de mesa">
                            <p>Sal refinada yodada para sazonar tus comidas.</p>
                            <p class="precio-producto">S/ 1.20</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Lentejas</h3>
                            <img src="https://plazavea.vteximg.com.br/arquivos/ids/27552452-418-418/995413.jpg" alt="lentejas">
                            <p>Lentejas secas, ideales para sopas nutritivas.</p>
                            <p class="precio-producto">S/ 4.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Frijoles</h3>
                            <img src="https://plazavea.vteximg.com.br/arquivos/ids/27552442-418-418/3840.jpg" alt="frijoles">
                            <p>Frijoles negros y canarios, perfectos para guisos.</p>
                            <p class="precio-producto">S/ 4.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Avena en Hojuelas</h3>
                            <img src="https://plazavea.vteximg.com.br/arquivos/ids/30578622-512-512/20281906.jpg" alt="avena hojuelas">
                            <p>Avena integral en hojuelas para un desayuno energético.</p>
                            <p class="precio-producto">S/ 5.20</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Harina de Trigo</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRre3u22pwQIQ-tHcQqEDcfDCpmdTJ-jDhAxQ&s" alt="harina de trigo">
                            <p>Harina blanca para repostería y preparaciones caseras.</p>
                            <p class="precio-producto">S/ 3.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">ABARROTES</span>
                            <h3>Maicena</h3>
                            <img src="https://oechsle.vteximg.com.br/arquivos/ids/1891043-1000-1000/image-6ebf9d5c43d94af6a03aadc0af3c619d.jpg?v=637495416279100000" alt="maicena">
                            <p>Fécula de maíz para espesar salsas y preparar postres.</p>
                            <p class="precio-producto">S/ 2.80</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">BEBIDAS</span>
                            <h3>Agua de Mesa 625ml</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTWiHJ4UPFSIQIl6tTRWujx-bCwjoRMBLvbbA&s" alt="agua de mesa">
                            <p>Agua cielo sin gas, perfecta para mantenerte hidratado.</p>
                            <p class="precio-producto">S/ 1.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">BEBIDAS</span>
                            <h3>Gaseosa 1.5L</h3>
                            <img src="https://sumon.com.pe/wp-content/uploads/2024/10/gasesosa-coca-cola-1-5lt.webp" alt="gaseosa 1.5L">
                            <p>Gaseosa fría en distintos sabores para toda la familia.</p>
                            <p class="precio-producto">S/ 5.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">BEBIDAS</span>
                            <h3>Jugo de Naranja</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2uGvCgKi8GWZvfoagIK4-VI1YdSKX6MGI0A&s" alt="jugo de naranja">
                            <p>Jugo de naranja natural exprimido en el momento.</p>
                            <p class="precio-producto">S/ 3.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">BEBIDAS</span>
                            <h3>Chicha Morada</h3>
                            <img src="https://wongfood.vtexassets.com/arquivos/ids/807366/CHICHA-MORADA-XUMO-BOT-VIDRIO-1L-1-351711573.jpg?v=639016006110800000" alt="chicha morada">
                            <p>Chicha morada preparada con maíz morado y especias.</p>
                            <p class="precio-producto">S/ 6.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">BEBIDAS</span>
                            <h3>Infusión de Manzanilla</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSHLdbsNaiuIZD4EOHjxLZkYo-sbtu7B3jC9w&s" alt="manzanilla">
                            <p>Bolsitas de manzanilla para una tarde relajante.</p>
                            <p class="precio-producto">S/ 2.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LIMPIEZA</span>
                            <h3>Detergente 500g</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS-LDjjc1EHgRhR9sQvMcTJ1_dBw7utanz0mg&s" alt="detergente 500g">
                            <p>Detergente en polvo ACE de alta eficacia para tu ropa.</p>
                            <p class="precio-producto">S/ 7.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LIMPIEZA</span>
                            <h3>Lavavajillas</h3>
                            <img src="https://promart.vteximg.com.br/arquivos/ids/7993503-1000-1000/102500.jpg?v=638524264421330000" alt="lavajillas">
                            <p>Lavavajillas líquido desengrasante, aromas variados.</p>
                            <p class="precio-producto">S/ 4.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LIMPIEZA</span>
                            <h3>Lejía 1L</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRx_R4V0qXV9HjiqLS_WuxiJM6EXLH9VJCjWw&s" alt="lejia 1L">
                            <p>Lejía blanqueadora para desinfectar tu hogar.</p>
                            <p class="precio-producto">S/ 3.20</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LIMPIEZA</span>
                            <h3>Papel Higiénico x4</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2_xjdJ0T_fGhumDAdU5aHx1N1_GI8P6sIbw&s" alt="papel hugienico">
                            <p>Papel higiénico suave y resistente, pack de 4 rollos.</p>
                            <p class="precio-producto">S/ 6.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LIMPIEZA</span>
                            <h3>Jabón de Barra</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4g0pG6wT5MHVlgOxcg-idT8JRof4Gqa097g&s" alt="jabon en barra">
                            <p>Jabón antibacterial para manos y cuerpo.</p>
                            <p class="precio-producto">S/ 2.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LIMPIEZA</span>
                            <h3>Esponja de Cocina</h3>
                            <img src="https://www.ferropolis.pe/cdn/shop/products/esponja-amarilla-lisa.jpg?v=1674145743" alt="esponja de cocina">
                            <p>Esponja doble función para limpiar ollas y platos.</p>
                            <p class="precio-producto">S/ 1.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">LIMPIEZA</span>
                            <h3>Bolsas de Basura x10</h3>
                            <img src="https://promart.vteximg.com.br/arquivos/ids/567575-1000-1000/23833.jpg?v=637393511424200000" alt="bolsa de basura">
                            <p>Bolsas resistentes para basura doméstica, pack de 10.</p>
                            <p class="precio-producto">S/ 3.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">SNACKS</span>
                            <h3>Galletas de Vainilla</h3>
                            <img src="https://plazavea.vteximg.com.br/arquivos/ids/29033244-450-450/243940.jpg?v=638501473521030000" alt="galletas de vainilla">
                            <p>Galletas crujientes de vainilla, ideales para el café.</p>
                            <p class="precio-producto">S/ 3.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">SNACKS</span>
                            <h3>Chifles</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRw_pgy3mXYdwBDPxhe7Wu7Ksbur0qXGWdtqA&s" alt="chifles">
                            <p>Chifles crujientes de plátano verde con sal sabor leche de tigre, snack peruano.</p>
                            <p class="precio-producto">S/ 2.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">SNACKS</span>
                            <h3>Maní Salado</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRt7QT24xjGhdc8qm41N1Kvs-Fy1JedDJjMaw&s" alt="mani salado">
                            <p>Maní tostado y salado, perfecto para picar.</p>
                            <p class="precio-producto">S/ 3.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">SNACKS</span>
                            <h3>Chocolate con Leche</h3>
                            <img src="https://metroio.vtexassets.com/arquivos/ids/517940/Chocolate-con-Leche-Nestl-Classic-80g-1-260829.jpg?v=638470065747070000" alt="chocolate con leche">
                            <p>Tableta de chocolate cremoso al leche.</p>
                            <p class="precio-producto">S/ 4.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">SNACKS</span>
                            <h3>Caramelos Surtidos</h3>
                            <img src="https://metroio.vtexassets.com/arquivos/ids/512813/Caramelos-Arcor-Surtido-1kg-1-256166.jpg?v=638433669915630000" alt="caramelos surtidos">
                            <p>Bolsa de caramelos surtidos para toda la familia.</p>
                            <p class="precio-producto">S/ 9.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CARNES</span>
                            <h3>Pollo Entero</h3>
                            <img src="https://metroio.vtexassets.com/arquivos/ids/290311/Pollo-Entero-Fresco-Metro-x-kg-2-183284.jpg?v=638179316343400000" alt="pollo entero">
                            <p>Pollo fresco de granja, listo para preparar.</p>
                            <p class="precio-producto">S/ 14.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CARNES</span>
                            <h3>Carne de Res</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxixH3zN265n1867ZCMK0-cflyRjQRJBAXXQ&s" alt="carne de res">
                            <p>Carne de res seleccionada para guisos y bistecs.</p>
                            <p class="precio-producto">S/ 22.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CARNES</span>
                            <h3>Jamonada</h3>
                            <img src="https://metroio.vtexassets.com/arquivos/ids/371001/Jamonada-de-Cerdo-Rico-200g-1-16558145.jpg?v=638180587496400000" alt="jamonada">
                            <p>Jamonada de cerdo en rodajas, ideal para sándwiches.</p>
                            <p class="precio-producto">S/ 5.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CARNES</span>
                            <h3>Hot Dogs x6</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR4aNlrLhyfzffLZhPNBAtbQuOk_C-SEDz8ZA&s" alt="hotdogs x6">
                            <p>Salchichas de pollo y cerdo en pack de 6 unidades.</p>
                            <p class="precio-producto">S/ 6.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">PANADERÍA</span>
                            <h3>Pan de Molde</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSNyVjWFskJ-zu0UbXVkK0nOgzRBHwV4QQpQ&s" alt="pan de molde">
                            <p>Pan de molde suave para sándwiches y tostadas.</p>
                            <p class="precio-producto">S/ 5.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">PANADERÍA</span>
                            <h3>Pan Francés x6</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSuCrd8NnPqlSZOFkchPzqm5_8rDsOvNKvpRQ&s" alt="pan frances">
                            <p>Pan francés crujiente recién horneado, pack de 6.</p>
                            <p class="precio-producto">S/ 2.00</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CONDIMENTOS</span>
                            <h3>Ají Amarillo en Pasta</h3>
                            <img src="https://plazavea.vteximg.com.br/arquivos/ids/29320941-450-450/1073429001.jpg?v=638591631832930000" alt="aji amarillo en pasta">
                            <p>Pasta de ají amarillo peruano para dar sabor a tus guisos.</p>
                            <p class="precio-producto">S/ 4.50</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CONDIMENTOS</span>
                            <h3>Mayonesa 400g</h3>
                            <img src="https://peruvianboxofficial.com/cdn/shop/products/image_e9060667-3505-410c-9bba-0f77d50d8120_1200x1200.jpg?v=1619222464" alt="mayonesa 400g">
                            <p>Mayonesa cremosa para ensaladas y sándwiches.</p>
                            <p class="precio-producto">S/ 12.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CONDIMENTOS</span>
                            <h3>Salsa de Soja</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRs50VsXKbF1ZMlduTGiqCWaX5Rt6Dm-c_5bg&s" alt="salsa de soja">
                            <p>Salsa de soja para dar sabor a saltados y marinados.</p>
                            <p class="precio-producto">S/ 8.90</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        <div class="oferta-card">
                            <span class="badge-oferta">CONDIMENTOS</span>
                            <h3>Vinagre Blanco 500ml</h3>
                            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQycYW4dZrpde_TaxdG0_HR7CkxN0T5YmlN8A&s" alt=" vinagre blanco 500ml">
                            <p>Vinagre blanco para aderezar ensaladas y conservas.</p>
                            <p class="precio-producto">S/ 3.40</p>
                            <a href="#" class="btn-adquirir">Pedir Producto</a>
                        </div>

                        {productos_dinamicos_html}   <!-- PRODUCTOS AGREGADOS DESDE EL PANEL -->
                    </div>
                </section>
            </div>
        </main>

        <footer>
            <p><strong>Abarrotes Flor © 2026</strong></p>
            <p>Av. Santa Rosa de Lima - Lima</p>
            <p>Teléfono: 918-787-936</p>
            <p>Horario: Lunes a Sábado de 7:00 AM a 9:00 PM</p>
        </footer>

        <script>
            // Navegación entre páginas
            function irA(pagina) {{
                document.getElementById('vista-inicio').classList.remove('activa');
                document.getElementById('vista-productos').classList.remove('activa');
                document.getElementById('vista-nosotros').classList.remove('activa');

                document.getElementById('btn-inicio').classList.remove('active');
                document.getElementById('btn-productos').classList.remove('active');
                document.getElementById('btn-nosotros').classList.remove('active');

                document.getElementById('vista-' + pagina).classList.add('activa');
                document.getElementById('btn-' + pagina).classList.add('active');
            }}

            // ----- CARRITO -----
            var carrito = [];

            function addToCartDesdeBoton(boton) {{
                var card = boton.closest('.oferta-card');
                if (!card) return;
                var nombre = card.querySelector('h3').textContent.trim();
                var precioTexto = card.querySelector('.precio-producto') ? 
                                  card.querySelector('.precio-producto').textContent.trim() :
                                  null;
                if (!precioTexto) {{
                    alert("No se pudo obtener el precio.");
                    return;
                }}
                var precio = parseFloat(precioTexto.replace('S/', '').trim());
                if (isNaN(precio)) {{
                    alert("Precio no válido.");
                    return;
                }}
                var existente = carrito.find(item => item.nombre === nombre && item.precio === precio);
                if (existente) {{
                    existente.cantidad += 1;
                }} else {{
                    carrito.push({{
                        nombre: nombre,
                        precio: precio,
                        cantidad: 1
                    }});
                }}
                renderizarCarrito();
                mostrarNotificacion(nombre + " agregado al carrito");
            }}

            function toggleCarrito() {{
                var modal = document.getElementById('carrito-modal');
                if (modal.classList.contains('abierto')) {{
                    modal.classList.remove('abierto');
                }} else {{
                    modal.classList.add('abierto');
                    renderizarCarrito();
                }}
            }}

            function renderizarCarrito() {{
                var contenedor = document.getElementById('carrito-items');
                var totalSpan = document.getElementById('carrito-total');
                var badge = document.getElementById('cart-badge');
                
                var total = 0;
                var cantidadTotal = 0;
                carrito.forEach(function(item) {{
                    total += item.precio * item.cantidad;
                    cantidadTotal += item.cantidad;
                }});
                
                badge.textContent = cantidadTotal;
                totalSpan.textContent = 'Total: S/ ' + total.toFixed(2);

                if (carrito.length === 0) {{
                    contenedor.innerHTML = '<div class="carrito-vacio">El carrito está vacío</div>';
                    return;
                }}

                var html = '';
                carrito.forEach(function(item, index) {{
                    html += `
                        <div class="carrito-item">
                            <div class="carrito-item-info">
                                <div class="carrito-item-nombre">${{item.nombre}}</div>
                                <div class="carrito-item-precio">S/ ${{item.precio.toFixed(2)}} c/u</div>
                                <div>Subtotal: S/ ${{(item.precio * item.cantidad).toFixed(2)}}</div>
                            </div>
                            <div class="carrito-item-acciones">
                                <input type="number" class="carrito-cantidad" value="${{item.cantidad}}" min="1" 
                                    onchange="actualizarCantidad(${{index}}, this.value)">
                                <button class="btn-eliminar" onclick="eliminarDelCarrito(${{index}})">×</button>
                            </div>
                        </div>
                    `;
                }});
                contenedor.innerHTML = html;
            }}

            function actualizarCantidad(index, nuevaCantidad) {{
                var cant = parseInt(nuevaCantidad);
                if (isNaN(cant) || cant < 1) {{
                    cant = 1;
                }}
                carrito[index].cantidad = cant;
                renderizarCarrito();
            }}

            function eliminarDelCarrito(index) {{
                carrito.splice(index, 1);
                renderizarCarrito();
            }}

            function vaciarCarrito() {{
                if (confirm('¿Estás seguro de vaciar el carrito?')) {{
                    carrito = [];
                    renderizarCarrito();
                }}
            }}

            function mostrarNotificacion(mensaje) {{
                var notif = document.createElement('div');
                notif.textContent = mensaje;
                notif.style.position = 'fixed';
                notif.style.bottom = '20px';
                notif.style.right = '20px';
                notif.style.background = '#2a6e3f';
                notif.style.color = 'white';
                notif.style.padding = '12px 20px';
                notif.style.borderRadius = '25px';
                notif.style.zIndex = '99999';
                notif.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
                notif.style.fontWeight = '600';
                document.body.appendChild(notif);
                setTimeout(function() {{
                    notif.style.opacity = '0';
                    notif.style.transition = 'opacity 0.5s';
                    setTimeout(function() {{ document.body.removeChild(notif); }}, 500);
                }}, 1500);
            }}

            // Asignar evento a todos los botones "Pedir Producto" dentro de #vista-productos
            document.addEventListener('DOMContentLoaded', function() {{
                var productosSection = document.getElementById('vista-productos');
                if (productosSection) {{
                    var botones = productosSection.querySelectorAll('.btn-adquirir');
                    botones.forEach(function(boton) {{
                        boton.addEventListener('click', function(e) {{
                            e.preventDefault();
                            addToCartDesdeBoton(this);
                        }});
                    }});
                }}
            }});

            // Funciones admin (sin cambios)
            var clientes = [];
            var nextId = 1;
            var editandoId = null;
            var eliminandoId = null;

            function renderTabla(lista) {{
                var tbody = document.getElementById('cuerpo-tabla');
                var sinResultados = document.getElementById('sin-resultados');
                tbody.innerHTML = '';
                if (!lista || lista.length === 0) {{
                    sinResultados.style.display = 'block';
                    return;
                }}
                sinResultados.style.display = 'none';
                for (var i = 0; i < lista.length; i++) {{
                    var c = lista[i];
                    var fila = document.createElement('tr');
                    fila.style.borderBottom = '1px solid #e0e0e0';
                    fila.style.background = (i % 2 === 0) ? '#f9fdf9' : '#ffffff';
                    var idCliente = c.id;
                    fila.innerHTML =
                        '<td style="padding:12px 14px;">' + c.id + '</td>' +
                        '<td style="padding:12px 14px; font-weight:600;">' + c.nombre + '</td>' +
                        '<td style="padding:12px 14px;">' + c.telefono + '</td>' +
                        '<td style="padding:12px 14px;">' + (c.direccion || '—') + '</td>' +
                        '<td style="padding:12px 14px; text-align:center;">' +
                            '<button onclick="abrirModalEditar(' + idCliente + ')" style="background:#2980b9; color:white; border:none; padding:7px 15px; border-radius:25px; cursor:pointer; font-size:13px; margin-right:6px; transition:0.2s;">Editar</button>' +
                            '<button onclick="abrirModalEliminar(' + idCliente + ')" style="background:#c0392b; color:white; border:none; padding:7px 15px; border-radius:25px; cursor:pointer; font-size:13px; transition:0.2s;">Eliminar</button>' +
                        '</td>';
                    tbody.appendChild(fila);
                }}
            }}

            function buscarCliente() {{
                var q = document.getElementById('buscar-cliente').value.toLowerCase().trim();
                if (q === '') {{
                    renderTabla(clientes);
                    return;
                }}
                var filtrados = [];
                for (var i = 0; i < clientes.length; i++) {{
                    var c = clientes[i];
                    if (c.nombre.toLowerCase().indexOf(q) !== -1 || c.telefono.indexOf(q) !== -1) {{
                        filtrados.push(c);
                    }}
                }}
                renderTabla(filtrados);
            }}

            function abrirModalAgregar() {{
                editandoId = null;
                document.getElementById('modal-titulo').textContent = 'Agregar Cliente';
                document.getElementById('inp-nombre').value = '';
                document.getElementById('inp-telefono').value = '';
                document.getElementById('inp-direccion').value = '';
                document.getElementById('modal-error').style.display = 'none';
                document.getElementById('modal-cliente').style.display = 'flex';
            }}

            function abrirModalEditar(id) {{
                var cliente = null;
                for (var i = 0; i < clientes.length; i++) {{
                    if (clientes[i].id === id) {{ cliente = clientes[i]; break; }}
                }}
                if (!cliente) return;
                editandoId = id;
                document.getElementById('modal-titulo').textContent = 'Editar Cliente';
                document.getElementById('inp-nombre').value = cliente.nombre;
                document.getElementById('inp-telefono').value = cliente.telefono;
                document.getElementById('inp-direccion').value = cliente.direccion || '';
                document.getElementById('modal-error').style.display = 'none';
                document.getElementById('modal-cliente').style.display = 'flex';
            }}

            function cerrarModal() {{
                document.getElementById('modal-cliente').style.display = 'none';
            }}

            function guardarCliente() {{
                var nombre = document.getElementById('inp-nombre').value.trim();
                var telefono = document.getElementById('inp-telefono').value.trim();
                var direccion = document.getElementById('inp-direccion').value.trim();
                var errorDiv = document.getElementById('modal-error');

                if (nombre === '' || telefono === '') {{
                    errorDiv.textContent = 'El nombre y el teléfono son obligatorios.';
                    errorDiv.style.display = 'block';
                    return;
                }}
                errorDiv.style.display = 'none';

                if (editandoId === null) {{
                    clientes.push({{ id: nextId, nombre: nombre, telefono: telefono, direccion: direccion }});
                    nextId++;
                }} else {{
                    for (var i = 0; i < clientes.length; i++) {{
                        if (clientes[i].id === editandoId) {{
                            clientes[i].nombre = nombre;
                            clientes[i].telefono = telefono;
                            clientes[i].direccion = direccion;
                            break;
                        }}
                    }}
                }}
                cerrarModal();
                buscarCliente();
            }}

            function abrirModalEliminar(id) {{
                eliminandoId = id;
                var cliente = null;
                for (var i = 0; i < clientes.length; i++) {{
                    if (clientes[i].id === id) {{ cliente = clientes[i]; break; }}
                }}
                if (!cliente) return;
                document.getElementById('confirmar-nombre').textContent = 'Se eliminará a: ' + cliente.nombre;
                document.getElementById('modal-eliminar').style.display = 'flex';
            }}

            function cerrarModalEliminar() {{
                document.getElementById('modal-eliminar').style.display = 'none';
                eliminandoId = null;
            }}

            function confirmarEliminar() {{
                if (eliminandoId === null) return;
                var nuevos = [];
                for (var i = 0; i < clientes.length; i++) {{
                    if (clientes[i].id !== eliminandoId) {{
                        nuevos.push(clientes[i]);
                    }}
                }}
                clientes = nuevos;
                cerrarModalEliminar();
                buscarCliente();
            }}

            document.addEventListener('click', function(e) {{
                var modalCliente = document.getElementById('modal-cliente');
                var modalEliminar = document.getElementById('modal-eliminar');
                if (modalCliente && e.target === modalCliente) {{ cerrarModal(); }}
                if (modalEliminar && e.target === modalEliminar) {{ cerrarModalEliminar(); }}
            }});

            renderTabla(clientes);

            var panelAbierto = true;
            function togglePanel() {{
                var contenido = document.getElementById('contenido-panel');
                var btn = document.getElementById('btn-toggle-panel');
                if (panelAbierto) {{
                    contenido.style.display = 'none';
                    btn.innerHTML = '▼ Expandir';
                    panelAbierto = false;
                }} else {{
                    contenido.style.display = 'block';
                    btn.innerHTML = '▲ Colapsar';
                    panelAbierto = true;
                }}
            }}
        </script>
    </body>
    </html>
    """

    return render_template_string(html)


# ---------- Rutas para administración de productos ----------
@app.route("/admin/productos")
def admin_productos():
    if not session.get("autenticado"):
        return redirect(url_for("pagina"))
    productos = cargar_productos()
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Admin Productos - Abarrotes Flor</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Poppins', sans-serif; background: #f4f4f4; margin:0; padding:20px; }
            .container { max-width: 1200px; margin: auto; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { color: #2a6e3f; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #2a6e3f; color: white; }
            img { width: 50px; height: 50px; object-fit: cover; border-radius: 8px; }
            .btn { display: inline-block; padding: 8px 16px; margin: 2px; border-radius: 25px; text-decoration: none; font-weight: 600; }
            .btn-edit { background: #f39c12; color: white; }
            .btn-delete { background: #e74c3c; color: white; }
            .btn-add { background: #2a6e3f; color: white; margin-bottom: 20px; }
            .volver { display: inline-block; margin-top: 20px; color: #2a6e3f; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Administrar Productos</h1>
            <a href="/admin/productos/agregar" class="btn btn-add">+ Agregar producto</a>
            <table>
                <thead>
                    <tr><th>ID</th><th>Imagen</th><th>Nombre</th><th>Descripción</th><th>Precio</th><th>Acciones</th><tr>
                </thead>
                <tbody>
    """
    for p in productos:
        html += f"""
            <tr>
                <td>{p['id']}</td>
                <td><img src="{p['imagen']}" alt="{p['nombre']}"></td>
                <td>{p['nombre']}</td>
                <td>{p['descripcion']}</td>
                <td>S/ {p['precio']:.2f}</td>
                <td>
                    <a href="/admin/productos/editar/{p['id']}" class="btn btn-edit">Editar</a>
                    <a href="/admin/productos/eliminar/{p['id']}" class="btn btn-delete" onclick="return confirm('¿Eliminar {p['nombre']}?')">Eliminar</a>
                </td>
            </tr>
        """
    html += """
                </tbody>
            </table>
            <a href="/" class="volver">← Volver a la tienda</a>
        </div>
    </body>
    </html>
    """
    return html

@app.route("/admin/productos/agregar", methods=["GET", "POST"])
def agregar_producto():
    if not session.get("autenticado"):
        return redirect(url_for("pagina"))
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio = request.form.get("precio", "").strip()
        imagen = request.form.get("imagen", "").strip()
        if not nombre or not precio:
            return "Error: nombre y precio son obligatorios", 400
        try:
            precio = float(precio)
        except:
            return "Error: precio debe ser un número", 400
        productos = cargar_productos()
        nuevo_id = max([p["id"] for p in productos], default=0) + 1
        productos.append({
            "id": nuevo_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "precio": precio,
            "imagen": imagen if imagen else "https://via.placeholder.com/150"
        })
        guardar_productos(productos)
        return redirect(url_for("admin_productos"))
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Agregar Producto</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Poppins', sans-serif; background: #f4f4f4; padding: 40px; }
            .form-card { max-width: 500px; margin: auto; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            label { font-weight: 600; display: block; margin-top: 15px; }
            input, textarea { width: 100%; padding: 10px; margin-top: 5px; border-radius: 12px; border: 1px solid #ccc; }
            button { background: #2a6e3f; color: white; border: none; padding: 12px 20px; border-radius: 25px; margin-top: 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="form-card">
            <h2>Agregar Producto</h2>
            <form method="POST">
                <label>Nombre *</label>
                <input type="text" name="nombre" required>
                <label>Descripción</label>
                <textarea name="descripcion" rows="3"></textarea>
                <label>Precio (S/) *</label>
                <input type="number" step="0.01" name="precio" required>
                <label>URL de la imagen</label>
                <input type="url" name="imagen" placeholder="https://ejemplo.com/imagen.jpg">
                <button type="submit">Guardar Producto</button>
            </form>
            <a href="/admin/productos">← Cancelar</a>
        </div>
    </body>
    </html>
    """)

@app.route("/admin/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    if not session.get("autenticado"):
        return redirect(url_for("pagina"))
    productos = cargar_productos()
    producto = next((p for p in productos if p["id"] == id), None)
    if not producto:
        return "Producto no encontrado", 404
    if request.method == "POST":
        producto["nombre"] = request.form.get("nombre", "").strip()
        producto["descripcion"] = request.form.get("descripcion", "").strip()
        try:
            producto["precio"] = float(request.form.get("precio", 0))
        except:
            pass
        producto["imagen"] = request.form.get("imagen", "").strip()
        guardar_productos(productos)
        return redirect(url_for("admin_productos"))
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Editar Producto</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Poppins', sans-serif; background: #f4f4f4; padding: 40px; }
            .form-card { max-width: 500px; margin: auto; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            label { font-weight: 600; display: block; margin-top: 15px; }
            input, textarea { width: 100%; padding: 10px; margin-top: 5px; border-radius: 12px; border: 1px solid #ccc; }
            button { background: #2a6e3f; color: white; border: none; padding: 12px 20px; border-radius: 25px; margin-top: 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="form-card">
            <h2>Editar Producto</h2>
            <form method="POST">
                <label>Nombre *</label>
                <input type="text" name="nombre" value="{{ producto.nombre }}" required>
                <label>Descripción</label>
                <textarea name="descripcion" rows="3">{{ producto.descripcion }}</textarea>
                <label>Precio (S/) *</label>
                <input type="number" step="0.01" name="precio" value="{{ producto.precio }}" required>
                <label>URL de la imagen</label>
                <input type="url" name="imagen" value="{{ producto.imagen }}">
                <button type="submit">Actualizar</button>
            </form>
            <a href="/admin/productos">← Cancelar</a>
        </div>
    </body>
    </html>
    """, producto=producto)

@app.route("/admin/productos/eliminar/<int:id>")
def eliminar_producto(id):
    if not session.get("autenticado"):
        return redirect(url_for("pagina"))
    productos = cargar_productos()
    productos = [p for p in productos if p["id"] != id]
    guardar_productos(productos)
    return redirect(url_for("admin_productos"))

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if not session.get("autenticado"):
        return redirect(url_for("pagina"))

    total_clientes = len(clientes_registrados)
    productos = cargar_productos()
    total_productos_dinamicos = len(productos)
    total_productos_estaticos = 60  # ← AJUSTA SEGÚN TUS PRODUCTOS FIJOS
    total_productos = total_productos_estaticos + total_productos_dinamicos

    if productos:
        precio_promedio = sum(p["precio"] for p in productos) / len(productos)
    else:
        precio_promedio = 0.0

    ventas_mes = round(random.uniform(100, 500), 2)

    hoy = datetime.now()
    dias = [(hoy - timedelta(days=i)).strftime("%d/%m") for i in range(6, -1, -1)]

    ventas_diarias = [round(random.uniform(10, 80), 2) for _ in range(7)]

    if total_clientes == 0:
        nuevos_clientes_linea = [0] * 7
    else:
        base = total_clientes // 7
        resto = total_clientes % 7
        nuevos_clientes_linea = [base + (1 if i < resto else 0) for i in range(7)]

    if total_productos_dinamicos == 0:
        nuevos_productos_linea = [0] * 7
    else:
        base = total_productos_dinamicos // 7
        resto = total_productos_dinamicos % 7
        nuevos_productos_linea = [base + (1 if i < resto else 0) for i in range(7)]

    variacion_productos = int(total_productos * 0.1)

    ultimos_clientes = clientes_registrados[-5:] if clientes_registrados else []
    ultimos_productos = sorted(productos, key=lambda x: x['id'], reverse=True)[:5] if productos else []

    hora_actual = datetime.now().strftime("%H:%M:%S")

    return render_template_string(DASHBOARD_TEMPLATE,
                                   total_productos=total_productos,
                                   precio_promedio=precio_promedio,
                                   total_clientes=total_clientes,
                                   ventas_mes=ventas_mes,
                                   variacion_productos=variacion_productos,
                                   dias=dias,
                                   ventas_diarias=ventas_diarias,
                                   nuevos_clientes_linea=nuevos_clientes_linea,
                                   nuevos_productos_linea=nuevos_productos_linea,
                                   hora_actual=hora_actual,
                                   ultimos_clientes=ultimos_clientes,
                                   ultimos_productos=ultimos_productos)

# ---------- Cerrar sesión ----------
@app.route("/logout")
def logout():
    session.pop("autenticado", None)
    return redirect(url_for("pagina"))

# -----------------------------------------------------------

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
