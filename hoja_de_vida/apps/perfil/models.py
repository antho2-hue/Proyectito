from django.db import models


class DatosPersonales(models.Model):
    idperfil = models.AutoField(primary_key=True, db_column='idperfil')
    descripcionperfil = models.CharField(max_length=50, db_column='descripcionperfil')
    perfilactivo = models.IntegerField(db_column='perfilactivo')
    apellidos = models.CharField(max_length=60, db_column='apellidos')
    nombres = models.CharField(max_length=60, db_column='nombres')
    nacionalidad = models.CharField(max_length=20, db_column='nacionalidad')
    lugarnacimiento = models.CharField(max_length=60, db_column='lugarnacimiento')
    fechanacimiento = models.DateField(db_column='fechanacimiento')
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
