from rest_framework import serializers

from core.models import User
from mlm.models import Tariff, StructureNode
from billing.models import Payment, Bonus


class RegisterPartnerSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    inviter_code = serializers.CharField(max_length=32)
    tariff_code = serializers.CharField(max_length=32, default="starter-100")

    def validate_inviter_code(self, value: str) -> str:
        try:
            inviter = User.objects.get(referral_code=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("Inviter not found") from exc
        self.context['inviter'] = inviter
        return value

    def validate_tariff_code(self, value: str) -> str:
        try:
            tariff = Tariff.objects.get(code=value, is_active=True)
        except Tariff.DoesNotExist as exc:
            raise serializers.ValidationError("Tariff is not available") from exc
        self.context['tariff'] = tariff
        return value


class CompleteRegistrationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value: int) -> int:
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("User not found") from exc
        self.context['user'] = user
        return value


class QueueEntrySerializer(serializers.ModelSerializer):
    inviter = serializers.SerializerMethodField()
    tariff = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            'id', 'user', 'amount', 'status', 'created_at', 'tariff', 'inviter',
        )

    def get_inviter(self, obj: Payment) -> str | None:
        inviter = obj.user.invited_by
        return inviter.username if inviter else None

    def get_tariff(self, obj: Payment) -> dict:
        return {
            "code": obj.tariff.code,
            "name": obj.tariff.name,
            "entry_amount": str(obj.tariff.entry_amount),
        }


class BonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonus
        fields = ('id', 'bonus_type', 'amount', 'created_at', 'source_user')


class StructureNodeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    parent = serializers.StringRelatedField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = StructureNode
        fields = ('user', 'parent', 'position', 'level', 'tariff', 'children')

    def get_children(self, obj: StructureNode):
        queryset = obj.children
        return [StructureNodeSerializer(child).data for child in queryset]
