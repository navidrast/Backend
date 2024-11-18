from django.db import migrations, models
import django.db.models.deletion
import uuid

def migrate_notes_forward(apps, schema_editor):
    """迁移备注数据到新结构"""
    Appointment = apps.get_model('appointments', 'Appointment')
    OldAppointmentNote = apps.get_model('appointments', 'AppointmentNote')
    
    # 创建临时表
    db_alias = schema_editor.connection.alias
    
    # 备份现有数据
    old_notes = list(OldAppointmentNote.objects.using(db_alias).all())
    
    # 删除旧的关联
    OldAppointmentNote.objects.all().delete()
    
    # 创建新的备注
    for note in old_notes:
        OldAppointmentNote.objects.create(
            id=uuid.uuid4(),
            appointment=note.appointment,
            user=note.staff,
            note=note.note,
            note_type='staff',
            created_at=note.created_at
        )

class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        # 1. 重命名原来的 notes 字段
        migrations.RenameField(
            model_name='appointment',
            old_name='notes',
            new_name='customer_notes',
        ),
        
        # 2. 保存旧的备注数据
        migrations.RunPython(migrate_notes_forward),
        
        # 3. 更新 AppointmentNote 模型
        migrations.RenameField(
            model_name='appointmentnote',
            old_name='staff',
            new_name='user',
        ),
        
        # 4. 添加 note_type 字段
        migrations.AddField(
            model_name='appointmentnote',
            name='note_type',
            field=models.CharField(
                choices=[('staff', 'Staff Note'), ('customer', 'Customer Note')],
                default='staff',
                max_length=10,
                verbose_name='Note Type'
            ),
        ),
        
        # 5. 添加 updated_at 字段
        migrations.AddField(
            model_name='appointmentnote',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        
        # 6. 修改关联名称
        migrations.AlterField(
            model_name='appointmentnote',
            name='appointment',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notes',
                to='appointments.appointment',
                verbose_name='Appointment'
            ),
        ),
    ]