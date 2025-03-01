# Generated by Django 5.1.2 on 2024-10-29 14:21

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='服务名称')),
                ('description', models.TextField(verbose_name='服务描述')),
                ('duration', models.PositiveIntegerField(help_text='以分钟为单位', validators=[django.core.validators.MinValueValidator(1)], verbose_name='服务时长')),
                ('image', models.ImageField(blank=True, null=True, upload_to='services/', verbose_name='服务图片')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '服务项目',
                'verbose_name_plural': '服务项目',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ServicePrice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('dog_size', models.CharField(choices=[('S', '小型犬 (8kg以下)'), ('M', '中型犬 (8-15kg)'), ('L', '大型犬 (16-25kg)')], max_length=1, verbose_name='狗狗体型')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='价格')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='services.service', verbose_name='服务项目')),
            ],
            options={
                'verbose_name': '服务价格',
                'verbose_name_plural': '服务价格',
                'ordering': ['service', 'dog_size'],
                'unique_together': {('service', 'dog_size')},
            },
        ),
    ]
