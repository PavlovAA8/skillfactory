from django.urls import path
from .views import (AnnouncementListView, 
                    AnnouncementDetailView, 
                    AnnouncementCreate, 
                    AnnouncementUpdate, 
                    AnnouncementDelete, 
                    CommentCreateView, 
                    UserCommentsListView, 
                    ScheduledMessageCreateView
)
urlpatterns = [
        path('announcements/', AnnouncementListView.as_view(), name='announcement_list'),
        path('announcements/<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
        path('announcements/create/', AnnouncementCreate.as_view(), name='announcement_create'),
        path('announcements/<int:pk>/edit/', AnnouncementUpdate.as_view(), name='announcement_edit'),
        path('announcements/<int:pk>/delete/', AnnouncementDelete.as_view(), name='announcement_delete'),
        path('announcements/<int:pk>/comment/', CommentCreateView.as_view(), name='comment_create'),
        path('announcements/<str:username>/comments/', UserCommentsListView.as_view(), name='comments'),
        path('create-scheduled-message/', ScheduledMessageCreateView.as_view(), name='create_scheduled_message')
]