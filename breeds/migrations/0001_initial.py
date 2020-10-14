# Generated by Django 3.1.1 on 2020-10-14 02:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Breed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('origin', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=300)),
                ('hometype', models.CharField(choices=[('landed', 'Landed'), ('condominium', 'Condominium')], max_length=11)),
            ],
        ),
        migrations.CreateModel(
            name='Human',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O', max_length=1)),
                ('date_of_birth', models.DateField()),
                ('description', models.CharField(blank=True, max_length=300)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='breeds.home')),
            ],
        ),
        migrations.CreateModel(
            name='Cat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='O', max_length=1)),
                ('date_of_birth', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(blank=True, max_length=300)),
                ('breed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cats', to='breeds.breed')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cats', to='breeds.human')),
            ],
        ),
    ]
