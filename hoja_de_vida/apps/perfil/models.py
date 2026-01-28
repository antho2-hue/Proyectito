from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


def validar_fecha_maxima(valor):
    """Validador que asegura que la fecha no sea posterior a enero 31, 2026"""
    fecha_maxima = date(2026, 1, 31)
    if valor > fecha_maxima:
        raise ValidationError('La fecha no puede ser posterior a 2026')


def validar_rango_fechas(valor):
    """Validador combinado para fechas: entre 1950 y 2026"""
    fecha_minima = date(1950, 1, 1)
    fecha_maxima = date(2026, 1, 31)
    if valor < fecha_minima or valor > fecha_maxima:
        raise ValidationError('La fecha debe estar entre 1950 y 2026')


def validar_fecha_nacimiento(valor):
    """Validador para fecha de nacimiento: entre 1950-2026, mayor de 18 años, no futura"""
    hoy = date.today()
    fecha_minima = date(1950, 1, 1)
    fecha_maxima = date(2026, 1, 31)
    
    # Validar rango de fechas
    if valor < fecha_minima or valor > fecha_maxima:
        raise ValidationError('La fecha de nacimiento debe estar entre 1950 y 2026')
    
    # No puede ser una fecha futura
    if valor > hoy:
        raise ValidationError('La fecha de nacimiento no puede ser posterior a hoy')
    
    # Calcular edad
    edad = hoy.year - valor.year - ((hoy.month, hoy.day) < (valor.month, valor.day))
    
    # Debe ser mayor de 18 años
    if edad < 18:
        raise ValidationError('La persona debe tener al menos 18 años de edad')


class DatosPersonales(models.Model):
    idperfil = models.AutoField(primary_key=True, db_column='idperfil')
    descripcionperfil = models.CharField(max_length=50, db_column='descripcionperfil')
    perfilactivo = models.IntegerField(db_column='perfilactivo')
    apellidos = models.CharField(max_length=60, db_column='apellidos')
    nombres = models.CharField(max_length=60, db_column='nombres')
    nacionalidad = models.CharField(max_length=20, db_column='nacionalidad')
    lugarnacimiento = models.CharField(max_length=60, db_column='lugarnacimiento')
    fechanacimiento = models.DateField(
        db_column='fechanacimiento',
        validators=[validar_fecha_nacimiento]
    )
    numerocedula = models.CharField(max_length=10, unique=True, db_column='numerocedula')

    SEXO_CHOICES = [
        ('H', 'H'),
        ('M', 'M'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, db_column='sexo')

    estadocivil = models.CharField(max_length=50, db_column='estadocivil')
    licenciaconducir = models.CharField(max_length=6, db_column='licenciaconducir')
    telefonoconvencional = models.CharField(max_length=15, db_column='telefonoconvencional')
    telefonofijo = models.CharField(max_length=15, db_column='telefonofijo')
    direcciontrabajo = models.CharField(max_length=50, db_column='direcciontrabajo')
    direcciondomiciliaria = models.CharField(max_length=50, db_column='direcciondomiciliaria')
    sitioweb = models.CharField(max_length=60, db_column='sitioweb')

    # URL segura de la foto de perfil (PNG) almacenada en Azure Blob Storage.
    foto_perfil_url = models.URLField(
        blank=True,
        null=True,
        db_column='foto_perfil_url',
        help_text='URL segura de la foto de perfil almacenada en Azure (PNG)'
    )

    # Optional background images for CV templates (stored as blob URLs)
    fondo_professional_url = models.URLField(
        blank=True,
        null=True,
        db_column='fondo_professional_url',
        help_text='URL del fondo para la plantilla Professional (imagen en blob)'
    )

    fondo_modern_url = models.URLField(
        blank=True,
        null=True,
        db_column='fondo_modern_url',
        help_text='URL del fondo para la plantilla Modern (imagen en blob)'
    )

    class Meta:
        db_table = 'DATOSPERSONALES'


class VisibilidadCV(models.Model):
    """Controles de visibilidad de secciones en el CV público"""
    perfil = models.OneToOneField(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column='idperfil',
        related_name='visibilidad_cv',
        primary_key=True
    )
    
    mostrar_datos_personales = models.BooleanField(
        default=True,
        db_column='mostrar_datos_personales',
        help_text='Mostrar información personal en el CV público'
    )
    mostrar_experiencias = models.BooleanField(
        default=True,
        db_column='mostrar_experiencias',
        help_text='Mostrar experiencia laboral en el CV público'
    )
    mostrar_cursos = models.BooleanField(
        default=True,
        db_column='mostrar_cursos',
        help_text='Mostrar cursos realizados en el CV público'
    )
    mostrar_reconocimientos = models.BooleanField(
        default=True,
        db_column='mostrar_reconocimientos',
        help_text='Mostrar reconocimientos en el CV público'
    )
    mostrar_productos_academicos = models.BooleanField(
        default=True,
        db_column='mostrar_productos_academicos',
        help_text='Mostrar productos académicos en el CV público'
    )
    mostrar_productos_laborales = models.BooleanField(
        default=True,
        db_column='mostrar_productos_laborales',
        help_text='Mostrar productos laborales en el CV público'
    )

    class Meta:
        db_table = 'VISIBILIDAD_CV'

    def save(self, *args, **kwargs):
        """Forzar que mostrar_datos_personales sea siempre True"""
        # Datos Personales es obligatorio y nunca puede ocultarse
        self.mostrar_datos_personales = True
        super().save(*args, **kwargs)
