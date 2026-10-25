import logging
from contextlib import contextmanager
from pathlib import Path
import pymysql
from fastapi import FastAPI, HTTPException, Path as ApiPath
from fastapi.responses import FileResponse, Response
from database import get_connection
from models import ProductoEntrada, ProductoSalida

app = FastAPI(title='Inventario', version='2.0')
logger = logging.getLogger('uvicorn.error')

@contextmanager
def conexion():
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()
    except pymysql.MySQLError as exc:
        if conn:
            conn.rollback()
        logger.exception('Error SQL')
        raise HTTPException(503, 'Base no disponible') from exc
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
@app.get('/', include_in_schema=False)
def inicio():
    return FileResponse(Path(__file__).with_name('index.html'))

@app.get('/salud')
def salud():
    with conexion() as conn, conn.cursor() as cur:
        cur.execute('SELECT 1 AS ok')
        return cur.fetchone()

@app.get('/productos', response_model=list[ProductoSalida])
def listar():
    with conexion() as conn, conn.cursor() as cur:
        cur.execute('SELECT id,nombre,precio,stock,categoria '
                    'FROM productos ORDER BY id')
        return cur.fetchall()

@app.get('/productos/{id}', response_model=ProductoSalida)
def consultar(id: int = ApiPath(gt=0)):
    with conexion() as conn, conn.cursor() as cur:
        cur.execute('SELECT id,nombre,precio,stock,categoria'
                    'FROM productos WHERE id=%s', (id,))
        fila = cur.fetchone()
        if fila is None:
            raise HTTPException(404, 'Producto no encontrado')
        return fila
@app.post('/productos', response_model=ProductoSalida,
          status_code=201)
def crear(datos: ProductoEntrada):
    with conexion() as conn, conn.cursor() as cur:
        cur.execute('INSERT INTO productos(nombre,precio,stock,categoria) '
                    'VALUES (%s,%s,%s,%s)',
                    (datos.nombre, datos.precio, datos.stock, datos.categoria))
        return {'id': cur.lastrowid, **datos.model_dump()}

@app.put('/productos/{id}', response_model=ProductoSalida)
def actualizar(datos: ProductoEntrada,
               id: int = ApiPath(gt=0)):
    with conexion() as conn, conn.cursor() as cur:
        cur.execute('SELECT id FROM productos WHERE id=%s '
                    'FOR UPDATE', (id,))
        if cur.fetchone() is None:
            raise HTTPException(404, 'Producto no encontrado')
        cur.execute('UPDATE productos SET nombre=%s,precio=%s,'
                    'stock=%s,categoria=%s WHERE id=%s',
                    (datos.nombre, datos.precio, datos.stock, datos.categoria, id))
        return {'id': id, **datos.model_dump()}

@app.delete('/productos/{id}', status_code=204)
def eliminar(id: int = ApiPath(gt=0)):
    with conexion() as conn, conn.cursor() as cur:
        cur.execute('DELETE FROM productos WHERE id=%s', (id,))
        if cur.rowcount == 0:
            raise HTTPException(404, 'Producto no encontrado')
    return Response(status_code=204)
