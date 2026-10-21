from pydantic import BaseModel, ConfigDict, Field

class ProductoEntrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True,
                              extra='forbid')
    nombre: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0, le=99999999.99,
                          allow_inf_nan=False)
    stock: int = Field(ge=0, le=2147483647, strict=True)

class ProductoSalida(ProductoEntrada):
    id: int
