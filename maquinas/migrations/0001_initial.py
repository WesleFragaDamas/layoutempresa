# Generated by Django 5.2.1 on 2025-05-20 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Maquina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_computador', models.CharField(help_text='Ex: LAB01-PC05, DIRETORIA-NOTE01', max_length=100, unique=True, verbose_name='Nome do Computador')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='Ex: 192.168.1.15', null=True, unique=True, verbose_name='Endereço IP')),
                ('mac_address', models.CharField(blank=True, help_text='Ex: 00:1A:2B:3C:4D:5E', max_length=17, null=True, unique=True, verbose_name='Endereço MAC')),
                ('setor', models.CharField(blank=True, help_text='Ex: Financeiro, TI, RH', max_length=50, null=True, verbose_name='Setor')),
                ('usuario_principal', models.CharField(blank=True, max_length=100, null=True, verbose_name='Usuário Principal')),
                ('observacoes', models.TextField(blank=True, help_text='Qualquer informação adicional relevante sobre a máquina.', null=True, verbose_name='Observações')),
                ('posicao_x', models.IntegerField(default=0, help_text='Coordenada X no layout visual (em pixels)', verbose_name='Posição X')),
                ('posicao_y', models.IntegerField(default=0, help_text='Coordenada Y no layout visual (em pixels)', verbose_name='Posição Y')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data da Última Atualização')),
            ],
            options={
                'verbose_name': 'Máquina',
                'verbose_name_plural': 'Máquinas',
                'ordering': ['nome_computador'],
            },
        ),
    ]
