from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r'^[0-9+\-\s()]{7,20}$',
    message='Ingresa un telefono valido.',
)


class TimeStampedModel(models.Model):
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Cliente(TimeStampedModel):
    TIPO_DOCUMENTO = [
        ('CC', 'Cedula de ciudadania'),
        ('CE', 'Cedula de extranjeria'),
        ('NIT', 'NIT'),
        ('PAS', 'Pasaporte'),
    ]

    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOCUMENTO, default='CC')
    documento = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, validators=[phone_validator])
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=180, blank=True)
    ciudad = models.CharField(max_length=80, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

    def __str__(self):
        return f'{self.nombre} - {self.documento}'

    def get_absolute_url(self):
        return reverse('cliente_detail', kwargs={'pk': self.pk})


class CategoriaProducto(TimeStampedModel):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'categoria de producto'
        verbose_name_plural = 'categorias de productos'

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('categoria_detail', kwargs={'pk': self.pk})


class Producto(TimeStampedModel):
    nombre = models.CharField(max_length=120)
    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=80)
    serial = models.CharField(max_length=80, unique=True)
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name='productos',
    )
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['marca', 'modelo', 'serial']
        verbose_name = 'producto'
        verbose_name_plural = 'productos'

    def __str__(self):
        return f'{self.nombre} {self.marca} {self.modelo} ({self.serial})'

    def get_absolute_url(self):
        return reverse('producto_detail', kwargs={'pk': self.pk})


class Venta(TimeStampedModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='ventas')
    fecha_venta = models.DateField(default=timezone.localdate)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    numero_factura = models.CharField(max_length=60, unique=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_venta']
        verbose_name = 'venta'
        verbose_name_plural = 'ventas'

    def __str__(self):
        return f'Factura {self.numero_factura} - {self.cliente.nombre}'

    def get_absolute_url(self):
        return reverse('venta_detail', kwargs={'pk': self.pk})


class Garantia(TimeStampedModel):
    ESTADOS = [
        ('vigente', 'Vigente'),
        ('vencida', 'Vencida'),
        ('anulada', 'Anulada'),
    ]

    venta = models.OneToOneField(Venta, on_delete=models.PROTECT, related_name='garantia')
    fecha_inicio = models.DateField(default=timezone.localdate)
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=12, choices=ESTADOS, default='vigente')
    condiciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_fin']
        verbose_name = 'garantia'
        verbose_name_plural = 'garantias'

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha fin debe ser posterior a la fecha inicio.'})
        if self.venta_id and self.fecha_inicio and self.venta.fecha_venta > self.fecha_inicio:
            raise ValidationError({'fecha_inicio': 'La garantia no puede iniciar antes de la venta.'})

    @property
    def esta_vigente(self):
        return self.estado == 'vigente' and self.fecha_fin >= timezone.localdate()

    def __str__(self):
        return f'Garantia {self.venta.numero_factura} ({self.get_estado_display()})'

    def get_absolute_url(self):
        return reverse('garantia_detail', kwargs={'pk': self.pk})


class EstadoCaso(TimeStampedModel):
    codigo = models.SlugField(max_length=40, unique=True)
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#2563eb')
    orden = models.PositiveSmallIntegerField(default=1)
    es_final = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'estado de caso'
        verbose_name_plural = 'estados de casos'

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('estado_detail', kwargs={'pk': self.pk})


class CasoReparacion(TimeStampedModel):
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Critica'),
    ]

    garantia = models.ForeignKey(Garantia, on_delete=models.PROTECT, related_name='casos')
    descripcion_falla = models.TextField()
    estado_actual = models.ForeignKey(EstadoCaso, on_delete=models.PROTECT, related_name='casos_actuales')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    tecnico_responsable = models.CharField(max_length=120, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_ingreso']
        verbose_name = 'caso de reparacion'
        verbose_name_plural = 'casos de reparacion'

    def clean(self):
        if self.fecha_cierre and self.fecha_cierre < self.fecha_ingreso:
            raise ValidationError({'fecha_cierre': 'La fecha de cierre no puede ser anterior al ingreso.'})
        if self.garantia_id and self.garantia.estado == 'anulada':
            raise ValidationError({'garantia': 'No se puede abrir un caso sobre una garantia anulada.'})

    @property
    def cliente(self):
        return self.garantia.venta.cliente

    @property
    def producto(self):
        return self.garantia.venta.producto

    def __str__(self):
        return f'Caso #{self.pk or "nuevo"} - {self.producto.serial if self.pk else "producto"}'

    def get_absolute_url(self):
        return reverse('caso_detail', kwargs={'pk': self.pk})


class Diagnostico(TimeStampedModel):
    caso = models.ForeignKey(CasoReparacion, on_delete=models.CASCADE, related_name='diagnosticos')
    tecnico = models.CharField(max_length=120)
    diagnostico = models.TextField()
    solucion = models.TextField(blank=True)
    requiere_repuesto = models.BooleanField(default=False)
    costo_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'diagnostico'
        verbose_name_plural = 'diagnosticos'

    def __str__(self):
        return f'Diagnostico caso #{self.caso_id} - {self.tecnico}'

    def get_absolute_url(self):
        return reverse('diagnostico_detail', kwargs={'pk': self.pk})


class Evidencia(TimeStampedModel):
    TIPOS = [
        ('ingreso', 'Ingreso'),
        ('diagnostico', 'Diagnostico'),
        ('reparacion', 'Reparacion'),
        ('entrega', 'Entrega'),
    ]

    caso = models.ForeignKey(CasoReparacion, on_delete=models.CASCADE, related_name='evidencias')
    tipo = models.CharField(max_length=15, choices=TIPOS, default='ingreso')
    imagen = models.FileField(upload_to='evidencias/%Y/%m/')
    descripcion = models.CharField(max_length=220)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'evidencia'
        verbose_name_plural = 'evidencias'

    def clean(self):
        if self.imagen:
            ext = self.imagen.name.rsplit('.', 1)[-1].lower()
            if ext not in {'jpg', 'jpeg', 'png', 'webp', 'pdf'}:
                raise ValidationError({'imagen': 'Solo se permiten archivos JPG, PNG, WEBP o PDF.'})

    def __str__(self):
        return f'Evidencia {self.get_tipo_display()} - caso #{self.caso_id}'

    def get_absolute_url(self):
        return reverse('evidencia_detail', kwargs={'pk': self.pk})


class HistorialEstado(models.Model):
    caso = models.ForeignKey(CasoReparacion, on_delete=models.CASCADE, related_name='historial_estados')
    estado = models.ForeignKey(EstadoCaso, on_delete=models.PROTECT, related_name='historiales')
    fecha = models.DateTimeField(default=timezone.now)
    comentario = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'historial de estado'
        verbose_name_plural = 'historial de estados'

    def __str__(self):
        return f'{self.caso_id} - {self.estado.nombre} - {self.fecha:%Y-%m-%d}'

    def get_absolute_url(self):
        return reverse('historial_detail', kwargs={'pk': self.pk})


class Entrega(TimeStampedModel):
    caso = models.OneToOneField(CasoReparacion, on_delete=models.PROTECT, related_name='entrega')
    fecha_entrega = models.DateTimeField(default=timezone.now)
    entregado_a = models.CharField(max_length=120)
    documento_entrega = models.CharField(max_length=30)
    recibido_conforme = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_entrega']
        verbose_name = 'entrega'
        verbose_name_plural = 'entregas'

    def clean(self):
        if self.caso_id and self.fecha_entrega < self.caso.fecha_ingreso:
            raise ValidationError({'fecha_entrega': 'La entrega no puede ocurrir antes del ingreso del caso.'})

    def __str__(self):
        return f'Entrega caso #{self.caso_id} a {self.entregado_a}'

    def get_absolute_url(self):
        return reverse('entrega_detail', kwargs={'pk': self.pk})

# Create your models here.
