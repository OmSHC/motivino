"""
Views for content app.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Content, Comment, Bookmark
from .serializers import ContentSerializer, ContentCreateSerializer, CommentSerializer, BookmarkSerializer
from .permissions import IsAdminOrReadOnly


class ContentListView(generics.ListAPIView):
    """
    List content with filtering and pagination.
    """
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get content filtered for current user."""
        content_type = self.request.query_params.get('content_type', 'MOTIVATION')
        limit = int(self.request.query_params.get('limit', 20))
        offset = int(self.request.query_params.get('offset', 0))

        return Content.get_content_for_user(
            user=self.request.user,
            content_type=content_type,
            limit=limit,
            offset=offset
        )
    
    def get_serializer_context(self):
        """Add request context to serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ContentDetailView(generics.RetrieveAPIView):
    """
    Retrieve specific content item.
    """
    queryset = Content.objects.filter(is_active=True, approval_status='approved')
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """Allow access to any approved and active content."""
        return Content.objects.filter(is_active=True, approval_status='approved')
    
    def get_serializer_context(self):
        """Add request context to serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated access
def get_daily_quote(request):
    """
    Get today's motivational quote.
    """
    today = timezone.now().date()

    # Try to get a quote for today, fallback to latest
    quote = Content.objects.filter(
        content_type='QUOTATION',
        is_active=True,
        published_at__date=today
    ).first()

    if not quote:
        # Fallback to latest quote
        quote = Content.objects.filter(
            content_type='QUOTATION',
            is_active=True
        ).order_by('-published_at').first()

    if quote:
        serializer = ContentSerializer(quote, context={'request': request})
        return Response(serializer.data)

    return Response({'message': 'No quote available'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_bookmark(request, content_id):
    """
    Toggle bookmark for content.
    """
    try:
        content = Content.objects.get(id=content_id, is_active=True)
    except Content.DoesNotExist:
        return Response({'error': 'Content not found'}, status=status.HTTP_404_NOT_FOUND)
    
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        content=content
    )
    
    if not created:
        bookmark.delete()
        return Response({'bookmarked': False})
    
    return Response({'bookmarked': True})


class BookmarkListView(generics.ListAPIView):
    """
    List user's bookmarked content.
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's bookmarks."""
        return Bookmark.objects.filter(user=self.request.user).order_by('-created_at')


# Admin views
class AdminContentCreateView(generics.CreateAPIView):
    """
    Create content (admin only).
    """
    queryset = Content.objects.all()
    serializer_class = ContentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)


class AdminContentUpdateView(generics.UpdateAPIView):
    """
    Update content (admin only).
    """
    queryset = Content.objects.all()
    serializer_class = ContentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class AdminContentDeleteView(generics.DestroyAPIView):
    """
    Delete content (admin only).
    """
    queryset = Content.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class AdminContentListView(generics.ListAPIView):
    """
    List all content for admin.
    """
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_serializer_context(self):
        """Add request context to serializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context



class CommentListCreateView(generics.ListCreateAPIView):
    """
    List and create comments for a specific content.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get comments for the specific content."""
        content_id = self.kwargs['content_id']
        return Comment.objects.filter(content_id=content_id, is_active=True)

    def perform_create(self, serializer):
        """Set the user and content when creating a comment."""
        content_id = self.kwargs['content_id']
        serializer.save(user=self.request.user, content_id=content_id)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific comment.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get the comment if the user owns it."""
        return Comment.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure user can only update their own comments."""
        serializer.save(user=self.request.user)
