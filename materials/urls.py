from django.urls import include, path



from api.mejlis.views import (
    CreateOrderView,
    OrderByMaterialTypeView,
    OrderByStatusView,
    OrderListView,
    OrderDetailView,
    OrderUpdateView,
    OrderDeleteView,
    OrderStatusUpdateView,
)

urlpatterns = [
    # # --- Mejlis Materials Orders ---
    # path("materials/mejlis/", CreateOrderView.as_view(), name="create-mejlis-order"),  # POST
    # path("materials/mejlis/list/", OrderListView.as_view(), name="list-mejlis-orders"),  # GET
    # path("materials/mejlis/<int:pk>/", OrderDetailView.as_view(), name="mejlis-order-detail"),  # GET, PUT, PATCH, DELETE

    # --- General Orders ---
    path("orders/mejlis/create", CreateOrderView.as_view(), name="create-order"),  # POST
    path("orders/mejlis/list/", OrderListView.as_view(), name="list-orders"),  # GET all
    path("orders/mejlis/getbyid/<int:id>/", OrderDetailView.as_view(), name="order-detail"),  # GET one
    path("orders/mejlis/<int:id>/update/", OrderUpdateView.as_view(), name="update-order"),  # PUT / PATCH
    path("orders/mejlis/<int:id>/delete/", OrderDeleteView.as_view(), name="delete-order"),  # DELETE
    path("orders/mejlis/updatestatus/<int:id>/status/", OrderStatusUpdateView.as_view(), name="order-status-update"),  # PATCH (status only)
    path("orders/material/<str:material_type>/", OrderByMaterialTypeView.as_view(), name="orders-by-material-type"),
     path("orders/status/<str:status>/", OrderByStatusView.as_view(), name="orders-by-status"),

]
