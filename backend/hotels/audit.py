from .models import AuditLog

def record_audit(*,actor,action,instance,reason='',previous=None,new=None):
    return AuditLog.objects.create(actor=actor,action=action,entity_type=instance.__class__.__name__,entity_id=str(instance.pk),reason=reason,previous_state=previous,new_state=new)
