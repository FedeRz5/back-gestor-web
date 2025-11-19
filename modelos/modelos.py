from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())

class Cuenta(db.Model):
    __tablename__ = 'cuentas'
    id_cuenta = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    nombre_cuenta = db.Column(db.String(100), nullable=False)
    saldo = db.Column(db.Numeric(10, 2), default=0.00)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

class TipoGasto(db.Model):
    __tablename__ = 'tipos_gasto'
    id_tipo = db.Column(db.Integer, primary_key=True)
    nombre_tipo = db.Column(db.String(100), nullable=False)
    limite_presupuesto = db.Column(db.Numeric(10, 2), nullable=True)

class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    id_transaccion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_cuenta = db.Column(db.Integer, db.ForeignKey('cuentas.id_cuenta'), nullable=False)
    id_tipo = db.Column(db.Integer, db.ForeignKey('tipos_gasto.id_tipo'), nullable=True)
    descripcion = db.Column(db.String(255))
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    tipo = db.Column(db.Enum('gasto', 'ingreso'), nullable=False)
