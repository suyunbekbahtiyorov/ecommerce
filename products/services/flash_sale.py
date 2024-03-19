from rest_framework import serializers, generics, status
from rest_framework.decorators import api_view
from products.models import FlashSale, Product
from datetime import datetime, timedelta
from rest_framework.response import Response
from products.models import UserProductView


class FlashSaleListCreateView(generics.ListCreateAPIView):
    queryset = FlashSale.objects.all()

    class FlashSaleSerializer(serializers.ModelSerializer):
        class Meta:
            model = FlashSale
            fields = ('id', 'product', 'discount_percentage', 'start_time', 'end_time')

    serializer_class = FlashSaleSerializer


@api_view(['GET'])
def check_flash_sale(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has viewed this product before
    user_viewed = UserProductView.objects.filter(user=request.user, product=product).exists()
    print(product)

    # Check if the product is or will be on a flash sale within the next 24 hours
    upcoming_flash_sale = FlashSale.objects.filter(
        product=product,
        start_time__lte=datetime.now() + timedelta(hours=24)
    ).first()

    if user_viewed and upcoming_flash_sale:
        # This is where you'd ideally send an actual notification,
        # but for simplicity, we're returning a response.
        discount = upcoming_flash_sale.discount_percentage
        start_time = upcoming_flash_sale.start_time
        end_time = upcoming_flash_sale.end_time
        return Response({
            "message": f"This product will be on a {discount}% off flash sale!",
            "start_time": start_time,
            "end_time": end_time
        })
    else:
        return Response({
            "message": "No upcoming flash sales for this product."
        })

