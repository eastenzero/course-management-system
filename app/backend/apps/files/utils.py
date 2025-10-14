"""
文件管理工具函数
"""

import hashlib
import os
import mimetypes
from typing import Optional
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings


def get_client_ip(request) -> str:
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def calculate_file_hash(file_obj: UploadedFile) -> str:
    """计算文件哈希值"""
    hash_md5 = hashlib.md5()
    
    # 重置文件指针
    file_obj.seek(0)
    
    # 分块读取文件计算哈希
    for chunk in iter(lambda: file_obj.read(4096), b""):
        hash_md5.update(chunk)
    
    # 重置文件指针
    file_obj.seek(0)
    
    return hash_md5.hexdigest()


def get_file_type_from_extension(filename: str) -> str:
    """根据文件扩展名获取文件类型"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def is_image_file(filename: str) -> bool:
    """检查是否为图片文件"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    ext = os.path.splitext(filename)[1].lower()
    return ext in image_extensions


def is_video_file(filename: str) -> bool:
    """检查是否为视频文件"""
    video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
    ext = os.path.splitext(filename)[1].lower()
    return ext in video_extensions


def is_audio_file(filename: str) -> bool:
    """检查是否为音频文件"""
    audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma']
    ext = os.path.splitext(filename)[1].lower()
    return ext in audio_extensions


def is_document_file(filename: str) -> bool:
    """检查是否为文档文件"""
    document_extensions = [
        '.pdf', '.doc', '.docx', '.txt', '.rtf',
        '.xls', '.xlsx', '.ppt', '.pptx',
        '.odt', '.ods', '.odp'
    ]
    ext = os.path.splitext(filename)[1].lower()
    return ext in document_extensions


def is_archive_file(filename: str) -> bool:
    """检查是否为压缩文件"""
    archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
    ext = os.path.splitext(filename)[1].lower()
    return ext in archive_extensions


def get_file_category_from_filename(filename: str) -> str:
    """根据文件名获取文件分类"""
    if is_image_file(filename):
        return 'image'
    elif is_video_file(filename):
        return 'video'
    elif is_audio_file(filename):
        return 'audio'
    elif is_document_file(filename):
        return 'document'
    elif is_archive_file(filename):
        return 'archive'
    else:
        return 'other'


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_file_size(file_obj: UploadedFile, max_size_mb: int = 100) -> bool:
    """验证文件大小"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_obj.size <= max_size_bytes


def validate_file_extension(filename: str, allowed_extensions: list = None) -> bool:
    """验证文件扩展名"""
    if allowed_extensions is None:
        # 默认允许的文件扩展名
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # 图片
            '.pdf', '.doc', '.docx', '.txt', '.rtf',  # 文档
            '.mp4', '.avi', '.mov', '.wmv',  # 视频
            '.mp3', '.wav', '.flac',  # 音频
            '.zip', '.rar', '.7z',  # 压缩包
            '.xlsx', '.xls', '.pptx', '.ppt'  # Office文档
        ]
    
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    import re
    
    # 移除路径分隔符和其他不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def generate_thumbnail(image_path: str, thumbnail_path: str, size: tuple = (200, 200)) -> bool:
    """生成图片缩略图"""
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            # 保持宽高比
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 保存缩略图
            img.save(thumbnail_path, optimize=True, quality=85)
            
        return True
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return False


def get_image_dimensions(image_path: str) -> Optional[tuple]:
    """获取图片尺寸"""
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            return img.size
    except Exception:
        return None


def compress_image(image_path: str, output_path: str, quality: int = 85) -> bool:
    """压缩图片"""
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # 保存压缩后的图片
            img.save(output_path, 'JPEG', optimize=True, quality=quality)
            
        return True
    except Exception as e:
        print(f"Error compressing image: {e}")
        return False


def get_video_duration(video_path: str) -> Optional[float]:
    """获取视频时长（需要安装ffmpeg-python）"""
    try:
        import ffmpeg
        
        probe = ffmpeg.probe(video_path)
        duration = float(probe['streams'][0]['duration'])
        return duration
    except Exception:
        return None


def get_video_thumbnail(video_path: str, thumbnail_path: str, time: float = 1.0) -> bool:
    """从视频中提取缩略图（需要安装ffmpeg-python）"""
    try:
        import ffmpeg
        
        (
            ffmpeg
            .input(video_path, ss=time)
            .output(thumbnail_path, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return True
    except Exception as e:
        print(f"Error extracting video thumbnail: {e}")
        return False


def clean_old_files(days: int = 30):
    """清理旧的已删除文件"""
    from django.utils import timezone
    from datetime import timedelta
    from .models import UploadedFile, FileStatus
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    old_files = UploadedFile.objects.filter(
        status=FileStatus.DELETED,
        updated_at__lt=cutoff_date
    )
    
    deleted_count = 0
    for file_obj in old_files:
        try:
            # 删除物理文件
            if file_obj.file and os.path.exists(file_obj.file.path):
                os.remove(file_obj.file.path)
            
            # 删除数据库记录
            file_obj.delete()
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting file {file_obj.id}: {e}")
    
    return deleted_count


def get_storage_usage() -> dict:
    """获取存储使用情况"""
    from .models import UploadedFile, FileStatus
    from django.db.models import Sum, Count
    
    # 活跃文件统计
    active_stats = UploadedFile.objects.filter(
        status=FileStatus.ACTIVE
    ).aggregate(
        count=Count('id'),
        total_size=Sum('file_size')
    )
    
    # 已删除文件统计
    deleted_stats = UploadedFile.objects.filter(
        status=FileStatus.DELETED
    ).aggregate(
        count=Count('id'),
        total_size=Sum('file_size')
    )
    
    return {
        'active_files': {
            'count': active_stats['count'] or 0,
            'total_size': active_stats['total_size'] or 0,
            'total_size_display': format_file_size(active_stats['total_size'] or 0)
        },
        'deleted_files': {
            'count': deleted_stats['count'] or 0,
            'total_size': deleted_stats['total_size'] or 0,
            'total_size_display': format_file_size(deleted_stats['total_size'] or 0)
        }
    }
