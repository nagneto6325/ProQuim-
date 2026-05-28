import hashlib
from repositories.usuario_repository import UsuarioRepository

# funcion interna para encriptar contrasenas
# usa sha256 que es suficiente para el proyecto
# en un sistema real se usaria bcrypt o argon2
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# servicio de autenticacion
# maneja login, creacion de usuarios y listado
class AuthService:
    @staticmethod
    def login(username: str, password: str) -> dict:
        # buscar el usuario por nombre
        user = UsuarioRepository.find_by_username(username)
        if not user:
            return {'success': False, 'error': 'Usuario o contrasena incorrectos'}

        # comparar el hash de la contrasena ingresada con el guardado
        if user['password'] != _hash_password(password):
            return {'success': False, 'error': 'Usuario o contrasena incorrectos'}

        # si todo ok, devolver los datos del usuario
        return {
            'success': True,
            'user': user['username'],
            'rol': user['rol'],
            'user_id': user['id']
        }

    @staticmethod
    def crear_usuario(username: str, password: str, rol: str) -> dict:
        # validar que no falten campos
        if not username or not password or not rol:
            return {'success': False, 'error': 'Todos los campos son obligatorios'}
        
        # verificar que el usuario no exista ya
        if UsuarioRepository.find_by_username(username):
            return {'success': False, 'error': 'Usuario ya existe'}
        
        # guardar el usuario con la contrasena encriptada
        user_id = UsuarioRepository.create(username, _hash_password(password), rol)
        return {'success': True, 'user_id': user_id}

    @staticmethod
    def get_usuarios():
        # devolver lista de todos los usuarios
        return UsuarioRepository.get_all()