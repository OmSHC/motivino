"""
Views for user content submission and admin approval.
"""
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Content
from .serializers import ContentSerializer, ContentCreateSerializer
from .permissions import IsAdminOrReadOnly
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_story(request):
    """
    Allow any authenticated user to submit a story for review.
    """
    try:
        # Get data from request
        title = request.data.get('title', '')
        rich_content = request.data.get('rich_content', '')
        body = request.data.get('body', '')
        content_type = request.data.get('content_type', 'MOTIVATION')
        target_grade = request.data.get('target_grade')
        target_school = request.data.get('target_school', '')
        youtube_url = request.data.get('youtube_url', '')

        # Validate required fields
        if not rich_content and not body:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate content type
        valid_types = ['MOTIVATION', 'JOKES', 'QUOTATION', 'PUZZLE', 'TONGUE_TWISTER']
        if content_type not in valid_types:
            return Response(
                {'error': f'Invalid content type. Must be one of: {", ".join(valid_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create content with pending status
        import uuid
        import hashlib
        # Generate unique hash by including user ID and timestamp
        unique_string = f"{title}{rich_content}{body}{request.user.id}{timezone.now().isoformat()}"
        unique_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()
        
        content = Content.objects.create(
            content_type=content_type,  # Use the selected content type
            title=title,
            body=body or rich_content[:200],  # Use first 200 chars if no body
            rich_content=rich_content,
            youtube_url=youtube_url,
            target_grade=target_grade if target_grade else None,
            target_school=target_school if target_school else None,
            source='user',
            submitted_by=request.user,
            approval_status='pending',  # Pending admin approval
            is_active=False,  # Not active until approved
            hash=unique_hash,  # Unique hash to prevent duplicates
        )
        
        logger.info(f"User {request.user.email} submitted story: {content.id}")
        
        return Response({
            'message': 'Story submitted successfully! It will be visible after admin approval.',
            'content_id': content.id,
            'content_type': content.content_type,
            'target_grade': content.target_grade,
            'target_school': content.target_school,
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Story submission error: {str(e)}")
        return Response(
            {'error': 'Failed to submit story. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_my_submissions(request):
    """
    Get all submissions by the current user.
    """
    try:
        submissions = Content.objects.filter(
            submitted_by=request.user
        ).order_by('-created_at')
        
        serializer = ContentSerializer(submissions, many=True, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error fetching submissions: {str(e)}")
        return Response(
            {'error': 'Failed to fetch submissions'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminOrReadOnly])
def get_pending_submissions(request):
    """
    Get all pending submissions for admin review.
    """
    try:
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending = Content.objects.filter(
            approval_status='pending'
        ).order_by('-created_at')
        
        serializer = ContentSerializer(pending, many=True, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error fetching pending submissions: {str(e)}")
        return Response(
            {'error': 'Failed to fetch pending submissions'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdminOrReadOnly])
def approve_submission(request, content_id):
    """
    Approve a pending submission (admin only).
    """
    try:
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        content = Content.objects.get(id=content_id)
        
        content.approval_status = 'approved'
        content.is_active = True
        content.reviewed_by = request.user
        content.reviewed_at = timezone.now()
        content.save()
        
        logger.info(f"Admin {request.user.email} approved content: {content_id}")
        
        return Response({
            'message': 'Content approved successfully',
            'content_id': content_id
        })
        
    except Content.DoesNotExist:
        return Response(
            {'error': 'Content not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Approval error: {str(e)}")
        return Response(
            {'error': 'Failed to approve content'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdminOrReadOnly])
def reject_submission(request, content_id):
    """
    Reject a pending submission with reason (admin only).
    """
    try:
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        content = Content.objects.get(id=content_id)
        rejection_reason = request.data.get('rejection_reason')
        
        if not rejection_reason:
            return Response(
                {'error': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content.approval_status = 'rejected'
        content.is_active = False
        content.rejection_reason = rejection_reason
        content.reviewed_by = request.user
        content.reviewed_at = timezone.now()
        content.save()
        
        logger.info(f"Admin {request.user.email} rejected content: {content_id} with reason: {rejection_reason}")
        
        return Response({
            'message': 'Content rejected',
            'content_id': content_id,
            'rejection_reason': rejection_reason
        })
        
    except Content.DoesNotExist:
        return Response(
            {'error': 'Content not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Rejection error: {str(e)}")
        return Response(
            {'error': 'Failed to reject content'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resubmit_story(request, content_id):
    """
    Resubmit a rejected story with modifications.
    """
    try:
        original_content = Content.objects.get(
            id=content_id,
            submitted_by=request.user,
            approval_status='rejected'
        )
        
        # Get updated data
        title = request.data.get('title', '')
        rich_content = request.data.get('rich_content', '')
        body = request.data.get('body', '')
        content_type = request.data.get('content_type', original_content.content_type)
        target_grade = request.data.get('target_grade')
        target_school = request.data.get('target_school', '')
        youtube_url = request.data.get('youtube_url', '')

        # Validate required fields
        if not rich_content and not body:
            return Response(
                {'error': 'Content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate content type
        valid_types = ['MOTIVATION', 'JOKES', 'QUOTATION', 'PUZZLE', 'TONGUE_TWISTER']
        if content_type not in valid_types:
            return Response(
                {'error': f'Invalid content type. Must be one of: {", ".join(valid_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique hash for new submission
        import uuid
        import hashlib
        unique_string = f"{title}{rich_content}{body}{request.user.id}{timezone.now().isoformat()}"
        unique_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()
        
        # Create new submission linked to original
        new_content = Content.objects.create(
            content_type=content_type,  # Use the selected content type
            title=title,
            body=body or rich_content[:200],
            rich_content=rich_content,
            youtube_url=youtube_url,
            target_grade=target_grade if target_grade else None,
            target_school=target_school if target_school else None,
            source='user',
            submitted_by=request.user,
            approval_status='pending',
            is_active=False,
            hash=unique_hash,
            resubmission_status='resubmitted',
            original_submission=original_content
        )
        
        # Mark original as having been resubmitted
        original_content.resubmission_status = 'original'
        original_content.save()
        
        logger.info(f"User {request.user.email} resubmitted story: {new_content.id} (original: {content_id})")
        
        return Response({
            'message': 'Story resubmitted successfully! It will be reviewed again.',
            'content_id': new_content.id,
            'content_type': new_content.content_type,
            'target_grade': new_content.target_grade,
            'target_school': new_content.target_school,
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
        
    except Content.DoesNotExist:
        return Response(
            {'error': 'Original content not found or not rejected'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Story resubmission error: {str(e)}")
        return Response(
            {'error': 'Failed to resubmit story. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
