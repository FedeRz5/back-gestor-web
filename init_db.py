from app import app, db
from modelos.modelos import Usuario, Cuenta, TipoGasto, Transaccion

# Modify app config to use SQLite for development
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gestor.db"

if __name__ == "__main__":
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default expense types if they don't exist
        tipos_default = [
            {"nombre": "Alquiler", "limite": 1000.00},
            {"nombre": "Alimentos", "limite": 500.00},
            {"nombre": "Transporte", "limite": 200.00},
            {"nombre": "Otros", "limite": 300.00}
        ]
        
        for tipo in tipos_default:
            if not TipoGasto.query.filter_by(nombre_tipo=tipo["nombre"]).first():
                nuevo_tipo = TipoGasto(
                    nombre_tipo=tipo["nombre"],
                    limite_presupuesto=tipo["limite"]
                )
                db.session.add(nuevo_tipo)
        
        db.session.commit()
        print("Database initialized successfully!")
        print("Created tables: usuarios, cuentas, tipos_gasto, transacciones")
        print("Added default expense types: Alquiler, Alimentos, Transporte, Otros")
