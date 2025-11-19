import datetime
import os
import base64
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from decimal import Decimal
from modelos.modelos import db, Usuario, Cuenta, TipoGasto, Transaccion

app = Flask(__name__)
# Use SQLite for development (comment out for MySQL in production)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "gestor.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/gestor"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "clave_secreta"
# Cookies de sesión para desarrollo: usar Lax para que el navegador no las bloquee
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

Bootstrap(app)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": [FRONTEND_ORIGIN]}}
)


# Variable global para controlar la visibilidad


@app.route("/", methods=["GET", "POST"])
def inicio():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario_id = session["usuario_id"]
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io
    import base64


    mes=datetime.datetime.now().month - 1 
    
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    # Datos para el gráfico de barras
    totalIngreso = 0
    totalEgreso = 0
    categorias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    ingresos = [0] * len(categorias)
    egresos = [0] * len(categorias)

    for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id).all():
        if transaccion.tipo == "gasto":
            egresos[transaccion.fecha.weekday()] += transaccion.monto
            totalIngreso += transaccion.monto
        elif transaccion.tipo == "ingreso":
            ingresos[transaccion.fecha.weekday()] += transaccion.monto
            totalEgreso += transaccion.monto
    fig, ax = plt.subplots()

# Ajustar la posición de las barras
    x = range(len(categorias))  # Posiciones base para las categorías
    ancho_barra = 0.4  # Ancho de cada barra

# Dibujar las barras con un desplazamiento

    colorEgresos="#3D63FF"
    colorIngresos="#D25AC8"

    ax.bar([pos - ancho_barra / 2 for pos in x], ingresos, width=ancho_barra, label="Ingresos", color= colorIngresos)
    ax.bar([pos + ancho_barra / 2 for pos in x], egresos, width=ancho_barra, label="Egresos",   color= colorEgresos, alpha=0.7)

# Ajustar etiquetas y leyenda
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.set_title("Transacciones de la semana")
    ax.legend()

# Convertir gráfico de barras a HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    grafico_barras_html = f'<img src="data:image/png;base64,{image_base64}" />'
    buf.close()
    plt.close(fig)


     # Datos para el gráfico de torta
    import math
    import matplotlib.pyplot as plt

# Calculando los valores
    etiquetas = ["Alquiler", "Alimentos", "Transporte", "Otros"]
    if transacciones := Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all() == []:
        valores = [0,0,0,0]
    else:
        valores = [
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=1).all()) or 0,
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=2).all()) or 0,
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=3).all()) or 0,
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=4).all()) or 0
]
        
    # Eliminar posiciones con valor 0 o vacías
    etiquetas = [etiqueta for etiqueta, valor in zip(etiquetas, valores) if valor != 0 and valor != ""]
    
    valores = [valor for valor in valores if valor != 0 and valor != ""]

# Reemplazar NaN por 0

# Crear gráfico
    fig, ax = plt.subplots()
    ax.set_title("Distribución de Egresos")
    colores = ["#3D63FF", "#D45F5F", "#30B9FE", "#38E184"]
    ax.pie(valores, labels=etiquetas, autopct="%1.1f%%", colors=colores)
    plt.show()

    # Convertir gráfico de torta a HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    grafico_torta_html = f'<img src="data:image/png;base64,{image_base64}" />'
    buf.close()
    plt.close(fig)

    tipos_gastos = obtener_categorias()
    
   
    lista_gastos = []
    lista_ingresos = []
    transacciones_gastos = Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").order_by(Transaccion.fecha.desc()).limit(3).all()
    transacciones_ingresos = Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").order_by(Transaccion.fecha.desc()).limit(3).all()

    for transaccion in transacciones_gastos:
        categoria = TipoGasto.query.filter_by(id_tipo=transaccion.id_tipo).first().nombre_tipo
        monto = transaccion.monto
        lista_gastos.append({"categoria": categoria, "monto": monto})

    for transaccion in transacciones_ingresos:
        monto = transaccion.monto
        lista_ingresos.append({"monto": monto})

    # Asegurarse de que las listas tengan exactamente 3 elementos
    while len(lista_gastos) < 3:
        lista_gastos.append({"categoria": "", "monto": 0})

    while len(lista_ingresos) < 3:
        lista_ingresos.append({"monto": 0})
        


    return render_template(
        "inicio.html",
        usuario=session["usuario"],
        grafico_barras_html=grafico_barras_html,
        grafico_torta_html=grafico_torta_html,
        tipos_gastos=tipos_gastos,
        lista_ingresos=lista_ingresos,
        lista_gastos=lista_gastos,
        totalIngreso=totalIngreso,
        totalEgreso=totalEgreso,
        disponible=totalEgreso-totalIngreso,
        mes=meses[mes]
        
    )


def obtener_categorias():
    categorias = TipoGasto.query.all()
    return categorias

# Utilidad para serializar entidades a JSON
def serialize_transaccion(t: Transaccion):
    return {
        "id_transaccion": t.id_transaccion,
        "id_usuario": t.id_usuario,
        "id_cuenta": t.id_cuenta,
        "id_tipo": t.id_tipo,
        "descripcion": t.descripcion or "",
        "monto": float(t.monto),
        "fecha": (t.fecha.isoformat() if isinstance(t.fecha, datetime.datetime) else str(t.fecha)),
        "tipo": t.tipo,
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Busca al usuario por correo
        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Autenticación exitosa
            session["usuario"] = user.nombre
            session["usuario_id"] = user.id_usuario
            return redirect(url_for("inicio"))
        else:
            error = "Correo o contraseña incorrectos."

    return render_template("login.html", error=error)


@app.route("/registro", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Verificar que las contraseñas coinciden
        if password != confirm_password:
            error = "Las contraseñas no coinciden."
        else:
            # Verificar si el correo ya está registrado
            user = Usuario.query.filter_by(email=email).first()
            if user:
                error = "El correo electrónico ya está registrado."
            else:
                # Guardar el nuevo usuario
                hashed_password = generate_password_hash(
                    password, method="pbkdf2:sha256"
                )
                new_user = Usuario(
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    password=hashed_password,
                )
                db.session.add(new_user)
                idUsuario=Usuario.query.filter_by(email=email).first().id_usuario
                new_account = Cuenta(
                    nombre_cuenta=nombre,
                    saldo=0.00,
                    id_usuario=idUsuario,
                )
                db.session.add(new_account)
               
                db.session.commit()

                flash("Te has registrado correctamente. Ahora puedes iniciar sesión.")
                return redirect(url_for("login"))

    return render_template("registro.html", error=error)


@app.route('/detalle/<caso>', methods=["GET"])
def detalle(caso):
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario_id = session["usuario_id"]
    mes=datetime.datetime.now().month - 1 
    
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]

    totalIngreso = 0
    totalEgreso = 0
    lista = []  # Inicializar la variable lista
    tipos_gastos = obtener_categorias()
    if caso == "ingresos":
       for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").all():
        monto = transaccion.monto
        lista.append({"categoria": "Ingresos", "monto": monto, "fecha": transaccion.fecha, "descripcion":"---"})
        
    elif caso == "egresos":
        for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all():
            categoria = TipoGasto.query.filter_by(id_tipo=transaccion.id_tipo).first().nombre_tipo
            if transaccion.descripcion == "":
                descripcion = "---"
            else:
                descripcion = transaccion.descripcion
                categoria = "Sin categoría"
            monto = transaccion.monto
            
            lista.append({"categoria": categoria, "monto": monto, "fecha": transaccion.fecha, "descripcion": descripcion})
    totalEgreso = sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all())
    totalIngreso = sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").all())
    return render_template(
        "ingresos.html",
        usuario=session["usuario"],
        lista=lista,
        mes=meses[mes],
        totalIngreso=totalIngreso,
        tipos_gastos=tipos_gastos,
        totalEgreso=totalEgreso,
        disponible=totalIngreso-totalEgreso
    
    )






    
    return render_template("ingresos.html", lista=lista, tipo=tipo)

    
    
    


@app.route("/agregar_gasto", methods=["POST"])
def agregar_gasto():
    if request.method == "POST":
        descripcion = request.form["descripcion"]
        monto = request.form["monto"]
        tipo_gasto = request.form["categoria"]
        # fecha = request.form['fecha']

        # Asegúrate de que el usuario esté logueado
        if "usuario_id" in session:
            usuario_id = session["usuario_id"]
            idCuenta=Cuenta.query.filter_by(id_usuario=usuario_id).first().id_cuenta
            
            # Validación: monto numérico y mayor a 0
            try:
                monto_val = float(monto)
            except Exception:
                flash("Monto inválido")
                return redirect(request.referrer or url_for("inicio"))
            if monto_val <= 0:
                flash("El monto debe ser mayor a 0")
                return redirect(request.referrer or url_for("inicio"))
        
            # Crear la nueva transacción de gasto
            nueva_transaccion = Transaccion(
                id_usuario=usuario_id,
                id_cuenta=idCuenta,  # Ajusta según corresponda
                descripcion=descripcion,
                monto=monto,
                tipo="gasto",  # O ajusta según corresponda
                id_tipo=tipo_gasto,  # Asegúrate de que tipo_gasto sea el ID de un tipo válido
            )
            
            montonuevo = float(Cuenta.query.filter_by(id_usuario=usuario_id).first().saldo) - float(monto)
            db.session.query(Cuenta).filter_by(id_usuario=usuario_id).update({"saldo": montonuevo})
            db.session.add(nueva_transaccion)
            db.session.commit()

            flash("Gasto agregado correctamente.")
            return redirect(request.referrer or url_for("inicio"))  # Redirigir al inicio después de agregar el gasto

    # Si el método es GET, solo mostrar el formulario (no hay tal formulario, es un modal, revisar)
    # return render_template('agregar_gasto.html')


@app.route("/agregar_ingreso", methods=["POST"])
def agregar_ingreso():
    if request.method == "POST":
        monto = request.form["monto"]

        # Asegúrate de que el usuario esté logueado
        if "usuario_id" in session:
            usuario_id = session["usuario_id"]
            cuenta=Cuenta.query.filter_by(id_usuario=usuario_id).first()
            # Validación: monto numérico y mayor a 0
            try:
                monto_val = float(monto)
            except Exception:
                flash("Monto inválido")
                return redirect(request.referrer or url_for("inicio"))
            if monto_val <= 0:
                flash("El monto debe ser mayor a 0")
                return redirect(request.referrer or url_for("inicio"))
            # Crear la nueva transacción de gasto
            nueva_transaccion = Transaccion(
                id_usuario=usuario_id,
                id_cuenta=cuenta.id_cuenta,  # Ajusta según corresponda
                # Ajusta según corresponda
                monto=monto,
                tipo="ingreso",  # O ajusta según corresponda
            )
            montonuevo = float(cuenta.saldo) + float(monto)
            db.session.query(Cuenta).filter_by(id_usuario=usuario_id).update({"saldo": montonuevo})
            db.session.add(nueva_transaccion)
            db.session.commit()

            flash("Ingreso agregado correctamente.")
            return redirect(request.referrer or url_for("inicio")) # Redirigir al inicio después de agregar el gasto


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# -----------------------------
# API JSON para frontend React
# -----------------------------

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400
    user = Usuario.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session["usuario"] = user.nombre
        session["usuario_id"] = user.id_usuario
        return jsonify({
            "id_usuario": user.id_usuario,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "email": user.email,
        })
    return jsonify({"error": "Credenciales inválidas"}), 401


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password") or password
    if not all([nombre, apellido, email, password]):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    if password != confirm_password:
        return jsonify({"error": "Las contraseñas no coinciden"}), 400
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El correo electrónico ya está registrado"}), 409
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    new_user = Usuario(nombre=nombre, apellido=apellido, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    # crear cuenta
    cuenta = Cuenta(nombre_cuenta=nombre, saldo=0.00, id_usuario=new_user.id_usuario)
    db.session.add(cuenta)
    db.session.commit()
    return jsonify({"message": "Registro exitoso"}), 201


@app.route("/api/user", methods=["GET"])
def api_user():
    if "usuario_id" not in session:
        return jsonify({"authenticated": False}), 200
    u = Usuario.query.get(session["usuario_id"])
    # provide avatar url if a file exists under static/img/avatars/user_<id>.(png|jpg|jpeg|gif)
    avatars_dir = os.path.join(app.root_path, "static", "img", "avatars")
    avatar_url = None
    for ext in ("png", "jpg", "jpeg", "gif"):
        avatar_path = os.path.join(avatars_dir, f"user_{u.id_usuario}.{ext}")
        if os.path.exists(avatar_path):
            avatar_url = f"/img/avatars/user_{u.id_usuario}.{ext}"
            break
    return jsonify({
        "authenticated": True,
        "user": {
            "id_usuario": u.id_usuario,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "email": u.email,
            "avatar_url": avatar_url,
        }
    })


@app.route("/api/user", methods=["PUT", "OPTIONS"])
@cross_origin(supports_credentials=True, origins=FRONTEND_ORIGIN)
def api_update_user():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    data = request.get_json(silent=True) or {}
    u = Usuario.query.get(session["usuario_id"])
    if not u:
        return jsonify({"error": "Usuario no encontrado"}), 404

    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")
    password = data.get("password")
    avatar_b64 = data.get("avatar_base64")

    # Validar email si cambió
    if email and email != u.email:
        if Usuario.query.filter_by(email=email).first():
            return jsonify({"error": "El correo electrónico ya está en uso"}), 409
        u.email = email

    if nombre is not None:
        u.nombre = nombre
    if apellido is not None:
        u.apellido = apellido
    if password:
        try:
            u.password = generate_password_hash(password, method="pbkdf2:sha256")
        except Exception:
            pass

    # avatar_base64: optional data URL or plain base64
    if avatar_b64:
        try:
            avatars_dir = os.path.join(app.root_path, "static", "img", "avatars")
            os.makedirs(avatars_dir, exist_ok=True)

            # If client sent a data URL like "data:image/png;base64,..." preserve MIME to choose extension
            mime = None
            raw_b64 = avatar_b64
            if raw_b64.startswith("data:"):
                # format: data:<mime>;base64,<data>
                try:
                    header, raw_b64 = raw_b64.split(",", 1)
                    mime = header.split(";", 1)[0].split(":", 1)[1]
                except Exception:
                    raw_b64 = avatar_b64.split(",", 1)[1] if "," in avatar_b64 else avatar_b64

            # Choose extension based on mime when available
            ext = "png"
            if mime:
                if "jpeg" in mime or "jpg" in mime:
                    ext = "jpg"
                elif "png" in mime:
                    ext = "png"
                elif "gif" in mime:
                    ext = "gif"

            imgdata = base64.b64decode(raw_b64)
            avatar_file = os.path.join(avatars_dir, f"user_{u.id_usuario}.{ext}")
            # write to the correct extension
            with open(avatar_file, "wb") as f:
                f.write(imgdata)

            # Optionally, remove older variants of the avatar with different extensions
            for old_ext in ("png", "jpg", "jpeg", "gif"):
                old_file = os.path.join(avatars_dir, f"user_{u.id_usuario}.{old_ext}")
                if old_ext != ext and os.path.exists(old_file):
                    try:
                        os.remove(old_file)
                    except Exception:
                        pass
        except Exception as e:
            app.logger.exception("Error guardando avatar")
            return jsonify({"error": "No se pudo guardar la imagen"}), 500

    db.session.add(u)
    db.session.commit()
    # devolver user actualizado
    # return the avatar URL for any supported extension
    avatars_dir = os.path.join(app.root_path, "static", "img", "avatars")
    avatar_url = None
    for ext in ("png", "jpg", "jpeg", "gif"):
        avatar_path = os.path.join(avatars_dir, f"user_{u.id_usuario}.{ext}")
        if os.path.exists(avatar_path):
            avatar_url = f"/img/avatars/user_{u.id_usuario}.{ext}"
            break
    return jsonify({
        "message": "Usuario actualizado",
        "user": {"id_usuario": u.id_usuario, "nombre": u.nombre, "apellido": u.apellido, "email": u.email, "avatar_url": avatar_url}
    }), 200


# New endpoint: accept multipart file upload for avatar (more reliable than sending base64 inside JSON)
@app.route('/api/user/avatar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True, origins=FRONTEND_ORIGIN)
def api_upload_avatar():
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    f = request.files['avatar']
    if f.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        filename = f.filename
        mimetype = f.mimetype or ''
        ext = 'png'
        if 'jpeg' in mimetype or filename.lower().endswith(('.jpg', '.jpeg')):
            ext = 'jpg'
        elif 'png' in mimetype or filename.lower().endswith('.png'):
            ext = 'png'
        elif 'gif' in mimetype or filename.lower().endswith('.gif'):
            ext = 'gif'

        avatars_dir = os.path.join(app.root_path, 'static', 'img', 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)

        avatar_file = os.path.join(avatars_dir, f'user_{session["usuario_id"]}.{ext}')
        f.save(avatar_file)

        # limpiar otros formatos viejos
        for old_ext in ('png', 'jpg', 'jpeg', 'gif'):
            old_file = os.path.join(avatars_dir, f'user_{session["usuario_id"]}.{old_ext}')
            if old_file != avatar_file and os.path.exists(old_file):
                try:
                    os.remove(old_file)
                except Exception:
                    pass

        avatar_url = f'/img/avatars/user_{session["usuario_id"]}.{ext}'
        return jsonify({'message': 'Avatar guardado', 'avatar_url': avatar_url}), 200

    except Exception as e:
        app.logger.exception('Error guardando avatar multipart')
        return jsonify({'error': 'No se pudo guardar el archivo'}), 500



@app.route("/api/summary", methods=["GET"])
def api_summary():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    usuario_id = session["usuario_id"]
    categorias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    ingresos = [0] * len(categorias)
    egresos = [0] * len(categorias)
    total_ingreso = 0
    total_egreso = 0
    for t in Transaccion.query.filter_by(id_usuario=usuario_id).all():
        if t.tipo == "gasto":
            egresos[t.fecha.weekday()] += float(t.monto)
            total_egreso += float(t.monto)
        elif t.tipo == "ingreso":
            ingresos[t.fecha.weekday()] += float(t.monto)
            total_ingreso += float(t.monto)

    # pie por categorías de gastos
    etiquetas = ["Alquiler", "Alimentos", "Transporte", "Otros"]
    valores = [
        float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=1).all()) or 0),
        float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=2).all()) or 0),
        float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=3).all()) or 0),
        float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=4).all()) or 0),
    ]
    # recientes
    recientes_gastos = [serialize_transaccion(t) for t in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").order_by(Transaccion.fecha.desc()).limit(3).all()]
    recientes_ingresos = [serialize_transaccion(t) for t in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").order_by(Transaccion.fecha.desc()).limit(3).all()]

    return jsonify({
        "semana": {"categorias": categorias, "ingresos": ingresos, "egresos": egresos},
        "torta": {"etiquetas": etiquetas, "valores": valores},
        "totales": {"ingresos": total_ingreso, "egresos": total_egreso, "disponible": total_ingreso - total_egreso},
        "recientes": {"gastos": recientes_gastos, "ingresos": recientes_ingresos},
    })


@app.route("/api/detalle", methods=["GET"])
def api_detalle():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    usuario_id = session["usuario_id"]
    caso = request.args.get("caso", "ingresos")
    lista = []
    if caso == "ingresos":
        for t in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").all():
            lista.append({
                "id_transaccion": t.id_transaccion,
                "id_tipo": t.id_tipo,
                "categoria": "Ingresos",
                "monto": float(t.monto),
                "fecha": (t.fecha.isoformat() if isinstance(t.fecha, datetime.datetime) else str(t.fecha)),
                "descripcion": t.descripcion if t.descripcion else "---",
            })
    else:
        for t in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all():
            categoria = TipoGasto.query.filter_by(id_tipo=t.id_tipo).first()
            categoria_nombre = (categoria.nombre_tipo if categoria else "Sin categoría")
            descripcion = t.descripcion if t.descripcion else "---"
            lista.append({
                "id_transaccion": t.id_transaccion,
                "id_tipo": t.id_tipo,
                "categoria": categoria_nombre,
                "monto": float(t.monto),
                "fecha": (t.fecha.isoformat() if isinstance(t.fecha, datetime.datetime) else str(t.fecha)),
                "descripcion": descripcion,
            })
    total_egreso = float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all()) or 0)
    total_ingreso = float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").all()) or 0)
    return jsonify({
        "lista": lista,
        "totales": {"ingresos": total_ingreso, "egresos": total_egreso, "disponible": total_ingreso - total_egreso},
    })


# Eliminar una transacción
@app.route("/api/transaccion/<int:id_transaccion>", methods=["DELETE", "OPTIONS"])
@cross_origin(supports_credentials=True, origins=FRONTEND_ORIGIN)
def api_delete_transaccion(id_transaccion):
    ...

    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    t = Transaccion.query.get(id_transaccion)
    if not t or t.id_usuario != session["usuario_id"]:
        return jsonify({"error": "Transacción no encontrada o no permitida"}), 404

    cuenta = Cuenta.query.get(t.id_cuenta)
    # Revertir el efecto en el saldo según el tipo
    try:
        monto = Decimal(str(t.monto))
    except Exception:
        monto = Decimal("0.0")

    # Ensure cuenta.saldo is Decimal before arithmetic
    try:
        saldo_actual = Decimal(str(cuenta.saldo))
    except Exception:
        saldo_actual = Decimal("0.0")

    if t.tipo == "gasto":
        nuevo_saldo = saldo_actual + monto
    else:
        nuevo_saldo = saldo_actual - monto

    cuenta.saldo = nuevo_saldo

    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Transacción eliminada"}), 200


# Editar una transacción (monto, descripcion, id_tipo)
@app.route("/api/transaccion/<int:id_transaccion>", methods=["PUT", "OPTIONS"])
@cross_origin(supports_credentials=True, origins=FRONTEND_ORIGIN)
def api_edit_transaccion(id_transaccion):
    ...

    try:
        if "usuario_id" not in session:
            return jsonify({"error": "No autenticado"}), 401
        t = Transaccion.query.get(id_transaccion)
        if not t or t.id_usuario != session["usuario_id"]:
            return jsonify({"error": "Transacción no encontrada o no permitida"}), 404

        data = request.get_json(silent=True) or {}
        nuevo_monto = data.get("monto")
        nueva_desc = data.get("descripcion")
        nuevo_id_tipo = data.get("id_tipo")

        cuenta = Cuenta.query.get(t.id_cuenta)

        # Ajustar saldo según la diferencia usando Decimal para evitar mezclar float/Decimal
        if nuevo_monto is not None and nuevo_monto != "":
            try:
                nuevo_monto_dec = Decimal(str(nuevo_monto))
            except Exception:
                return jsonify({"error": "Monto inválido"}), 400

            # Validación: monto debe ser mayor a 0
            if nuevo_monto_dec <= 0:
                return jsonify({"error": "El monto debe ser mayor a 0"}), 400

            antiguo = Decimal(str(t.monto))
            # delta = nuevo - antiguo (ambos Decimal)
            delta = nuevo_monto_dec - antiguo
            try:
                saldo_actual = Decimal(str(cuenta.saldo))
            except Exception:
                saldo_actual = Decimal("0.0")
            if t.tipo == "gasto":
                # mayores gastos disminuyen más el saldo (gasto reduce saldo)
                nuevo_saldo = saldo_actual - delta
            else:
                nuevo_saldo = saldo_actual + delta
            cuenta.saldo = nuevo_saldo
            # Guardar el monto como Decimal para preservar precisión
            t.monto = nuevo_monto_dec

        if nueva_desc is not None:
            t.descripcion = nueva_desc
        if nuevo_id_tipo is not None:
            t.id_tipo = nuevo_id_tipo

        db.session.add(t)
        db.session.commit()

        return jsonify(serialize_transaccion(t)), 200
    except Exception as e:
        app.logger.exception("Error editando transacción")
        return jsonify({"error": str(e)}), 500


@app.route("/api/agregar_gasto", methods=["POST"])
def api_agregar_gasto():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    data = request.get_json(silent=True) or {}
    descripcion = data.get("descripcion", "")
    monto = data.get("monto")
    tipo_gasto = data.get("categoria") or data.get("id_tipo")
    if monto is None or tipo_gasto is None:
        return jsonify({"error": "monto y categoria son requeridos"}), 400
    # validar monto
    try:
        monto_dec = Decimal(str(monto))
    except Exception:
        return jsonify({"error": "Monto inválido"}), 400
    if monto_dec <= 0:
        return jsonify({"error": "El monto debe ser mayor a 0"}), 400

    usuario_id = session["usuario_id"]
    cuenta = Cuenta.query.filter_by(id_usuario=usuario_id).first()
    nueva_transaccion = Transaccion(
        id_usuario=usuario_id,
        id_cuenta=cuenta.id_cuenta,
        descripcion=descripcion,
        monto=float(monto_dec),
        tipo="gasto",
        id_tipo=tipo_gasto,
    )
    try:
        saldo_actual = Decimal(str(cuenta.saldo))
    except Exception:
        saldo_actual = Decimal("0.0")
    nuevo_saldo = float(saldo_actual - monto_dec)
    db.session.query(Cuenta).filter_by(id_usuario=usuario_id).update({"saldo": nuevo_saldo})
    db.session.add(nueva_transaccion)
    db.session.commit()
    return jsonify({"message": "Gasto agregado", "transaccion": serialize_transaccion(nueva_transaccion)})


@app.route("/api/agregar_ingreso", methods=["POST"])
def api_agregar_ingreso():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    data = request.get_json(silent=True) or {}
    monto = data.get("monto")
    descripcion = data.get("descripcion", "")
    if monto is None:
        return jsonify({"error": "monto es requerido"}), 400
    # validar monto
    try:
        monto_dec = Decimal(str(monto))
    except Exception:
        return jsonify({"error": "Monto inválido"}), 400
    if monto_dec <= 0:
        return jsonify({"error": "El monto debe ser mayor a 0"}), 400

    usuario_id = session["usuario_id"]
    cuenta = Cuenta.query.filter_by(id_usuario=usuario_id).first()
    nueva_transaccion = Transaccion(
        id_usuario=usuario_id,
        id_cuenta=cuenta.id_cuenta,
        monto=float(monto_dec),
        tipo="ingreso",
        descripcion=descripcion,
    )
    # Use Decimal arithmetic to avoid float/Decimal mixing
    try:
        saldo_actual = Decimal(str(cuenta.saldo))
    except Exception:
        saldo_actual = Decimal("0.0")
    nuevo_saldo = saldo_actual + monto_dec
    cuenta.saldo = nuevo_saldo
    db.session.add(nueva_transaccion)
    db.session.commit()
    return jsonify({"message": "Ingreso agregado", "transaccion": serialize_transaccion(nueva_transaccion)})


@app.route("/api/tipos_gasto", methods=["GET"])
def api_tipos_gasto():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    tipos = TipoGasto.query.all()
    return jsonify([{"id_tipo": t.id_tipo, "nombre_tipo": t.nombre_tipo} for t in tipos])


@app.route("/api/logout", methods=["POST", "GET"])
def api_logout():
    session.pop("usuario", None)
    session.pop("usuario_id", None)
    return jsonify({"message": "Sesión cerrada"})


@app.route("/api/ahorros/resumen", methods=["GET"])
def api_ahorros_resumen():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    
    usuario_id = session["usuario_id"]
    
    # Calcular totales de ingresos y egresos
    total_ingresos = float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").all()) or 0)
    total_egresos = float(sum(x.monto for x in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all()) or 0)
    
    # Ahorros = ingresos - egresos
    total_ahorros = total_ingresos - total_egresos
    
    # Porcentaje de ahorro respecto a ingresos (evitar división por cero)
    porcentaje_ahorro = (total_ahorros / total_ingresos * 100) if total_ingresos > 0 else 0
    
    return jsonify({
        "total": total_ahorros,
        "porcentaje": round(porcentaje_ahorro, 2)
    })


@app.route("/api/ahorros/metas", methods=["GET"])
def api_ahorros_metas():
    if "usuario_id" not in session:
        return jsonify({"error": "No autenticado"}), 401
    
    # Por ahora devolvemos metas de ejemplo, ya que no tienes tabla de metas en la BD
    # Puedes expandir esto más tarde agregando una tabla MetaAhorro
    metas_ejemplo = [
        {
            "id": 1,
            "nombre": "Vacaciones",
            "objetivo": 50000,
            "acumulado": 15000,
            "progreso": 30,
            "fecha": "2025-12-31"
        },
        {
            "id": 2,
            "nombre": "Fondo de emergencia",
            "objetivo": 100000,
            "acumulado": 25000,
            "progreso": 25,
            "fecha": "2026-06-30"
        }
    ]
    
    return jsonify(metas_ejemplo)


# Database configuration is already set above


db.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)