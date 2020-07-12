from flask import Flask, make_response, request, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)

db = SQLAlchemy()


##Definiendo los modelos de la base de datos

class Usuario(db.Model):
    __tablename__ = 'usuario'
    idusuario = db.Column(db.Integer, primary_key = True)
    nomusuario = db.Column(db.String)
    contra = db.Column(db.String)
    
    def tojson(self):
        return { 
            "id": self.idusuario,
            "nombre de usuario" : self.nomusuario,
            "contraseña" : self.contra,
        }

class Categoria(db.Model):
    __tablename__ = 'categoria'
    cat_id = db.Column(db.Integer, primary_key = True)
    idusuario = db.Column(db.Integer)
    nombre = db.Column('nombre', db.String)
    limite = db.Column('limite', db.Float)
    
    def tojson(self):
        return { 
            "cat_id": self.cat_id,
            "idusuario" : self.idusuario,
            "nombre" : self.nombre,
            "limite" : self.limite
        }

class Articulo(db.Model):
    __tablename__ = 'articulo'
    articulo_id = db.Column(db.Integer, primary_key = True)
    cat_id = db.Column(db.Integer)
    nombre = db.Column('nombre', db.String)
    precio = db.Column('precio', db.Float)
    observacion = db.Column('observacion', db.String)
    
    def tojson(self):
        return { 
            "articulo_id": self.articulo_id,
            "nombre" : self.nombre,
	    "precio" : float(self.precio),
	    "observacion" : self.observacion
        }

#definiendo las rutas de la API


def crear_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']='arielchocogamerxxx'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    POSTGRES = {
    'user': 'opbpdvzgubrsdn',
    'pw': '0d68736699f8d1adccbf506b77f2ed48f27708502df74f0805ebf39a5804a91e',
    'db': 'd53h946aspmgf9',
    'host': 'ec2-54-211-210-149.compute-1.amazonaws.com',
    'port': '5432',
    }
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://opbpdvzgubrsdn:0d68736699f8d1adccbf506b77f2ed48f27708502df74f0805ebf39a5804a91e@ec2-54-211-210-149.compute-1.amazonaws.com:5432/d53h946aspmgf9' % POSTGRES
    jwt = JWTManager(app)
    db.init_app(app)

    @app.route('/login', methods=['POST'])
    def iniciarsesion():
        print(request.authorization)
        login = request.authorization
        if not login or not login.username or not login.password:
            return make_response('Faltan datos', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
        usuario = Usuario.query.filter_by(nomusuario=login.username).first()
        if (usuario.contra == login.password):
            token = create_access_token(identity= {"id" : usuario.idusuario})
            return {"token" : token, "id" : usuario.idusuario}, 200
        return make_response('La autenticación fallo',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

    @app.route('/registrar', methods=['POST'])
    def registrarusuario():
        nomusuario = request.json.get('usuario')
        contra = request.json.get('contra')
        if nomusuario is None or contra is None:
            return jsonify({'Mensaje' : 'falta username o contra'}), 400
        if Usuario.query.filter_by(nomusuario= nomusuario).first() is not None:
            return jsonify({'Mensaje' : 'Usuario existente'}), 400
        usuario = Usuario(nomusuario = nomusuario, contra = contra)
        token = create_access_token(identity= {"idusuario" : usuario.idusuario})
        db.session.add(usuario)
        db.session.commit()
        return jsonify({'resultado' : 'correcto', "token" : token, "idusuario" : usuario.idusuario}), 200


    @app.route('/listas/<int:idusuario>/<int:cat_id>', methods=['GET'])
    def getlistasuser(idusuario, cat_id):
        articulos = Articulo.query.filter_by(cat_id = cat_id).all()
        larticulos = []

        for articulo in articulos:
            larticulos.append(articulo.tojson())
        return jsonify(larticulos)

    @app.route('/categorias/<int:idusuario>', methods=['GET'])
    def getcategorias(idusuario):
        categorias = Categoria.query.all()
        lcat = []
        for categoria in categorias:
            lcat.append(categoria.tojson())
        return jsonify(lcat)


    @app.route('/bcategoria', methods=['POST'])
    def borrarcat():
        cat_id = request.json.get('cat_id')
        
        categoria = Categoria.query.filter_by(cat_id = cat_id).first()
        if categoria is None:
            return(jsonify({'mensaje' : 'La categoria no existe'}))
        articulos = Articulo.query.filter_by(cat_id = cat_id).all()
        for articulo in articulos:
            db.session.delete(articulo)
            db.session.commit()
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({'resultado' : 'correcto'}), 200


    @app.route('/acategoria', methods=['POST'])
    def acat():
        idusuario = request.json.get('idusuario')
        nombre =  request.json.get('nombre')
        limite =  request.json.get('limite')
        categoria = Categoria(idusuario= idusuario, nombre = nombre, limite=limite)
        db.session.add(categoria)
        db.session.commit()
        return jsonify({'resultado' : 'correcto'}), 200


    @app.route('/darticulo', methods=['POST'])
    def dart():
        cat_id = request.json.get('cat_id')
        nombre =  request.json.get('nombre')
        articulo = Articulo.query.filter_by(cat_id = cat_id, nombre = nombre).first()
        if articulo is None:
            return jsonify({'Error' : 'El articulo no existe en la categoria'})
        db.session.delete(articulo)
        db.session.commit()
        return jsonify({'resultado' : 'correcto'}), 200


    @app.route('/aarticulo', methods=['POST'])
    def aart():
        cat_id = request.json.get('cat_id')
        nombre =  request.json.get('nombre')
        precio = request.json.get('precio')
        observacion = request.json.get('observacion')
        articulo = Articulo.query.filter_by(cat_id = cat_id, nombre = nombre).first()
        if articulo is not None:
            return jsonify({'Error' : 'El articulo ya esta en la categoria'})
        nuevoart = Articulo(cat_id = cat_id, nombre = nombre, precio = precio, observacion = observacion)
        db.session.add(nuevoart)
        db.session.commit()
        return jsonify({'resultado' : 'correcto'}), 200


    @app.route('/', methods=['GET'])
    def root():
        return "API MOVILES"
    app.config['CONFIG'] = True
    return app